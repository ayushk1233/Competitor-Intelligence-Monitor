import asyncio
import json
import os
from collections import defaultdict
from unittest.mock import patch

from backend.eval.replay_runner import run_replay_for_company
from backend.intelligence.content_quality import is_noise_chunk
from backend.models.schemas import CompetitorPages, PageData
from backend.retrieval.signal_extractor import split_into_sentences
from backend.services.analysis_service import AnalysisService

async def mock_call_openrouter(*args, **kwargs):
    return "{}"  # Return empty JSON to satisfy downstream agents

class PipelineTracer:
    def __init__(self):
        self.extract_signals_called = 0
        self.compress_signals_called = 0
        self.sanitize_called = 0
        self.route_called = 0
        
        self.extracted = {}
        self.compressed = {}
        self.sanitized = {}
        self.routed = {}

    def hook_extract(self, original_fn):
        def wrapper(*args, **kwargs):
            self.extract_signals_called += 1
            res = original_fn(*args, **kwargs)
            self.extracted = res
            return res
        return wrapper

    def hook_compress(self, original_fn):
        def wrapper(*args, **kwargs):
            self.compress_signals_called += 1
            res = original_fn(*args, **kwargs)
            self.compressed = res
            return res
        return wrapper

    def hook_sanitize(self, original_fn):
        def wrapper(*args, **kwargs):
            self.sanitize_called += 1
            res = original_fn(*args, **kwargs)
            if isinstance(res, tuple):
                self.sanitized = res[0]
            else:
                self.sanitized = res
            return res
        return wrapper

    def hook_route(self, original_fn):
        def wrapper(*args, **kwargs):
            self.route_called += 1
            res = original_fn(*args, **kwargs)
            self.routed = res
            return res
        return wrapper

def count_signals(signals_dict):
    if not signals_dict:
        return 0
    return sum(len(v) for v in signals_dict.values() if isinstance(v, list))

def count_routed(routed_dict):
    if not routed_dict:
        return 0
    return sum(len(v) for v in routed_dict.values() if isinstance(v, list))

async def run_production_trace(company_name, pages):
    tracer = PipelineTracer()
    
    import backend.services.analysis_service
    import backend.reasoning.orchestrator
    
    orig_extract = backend.services.analysis_service.extract_signals
    orig_compress = backend.services.analysis_service.compress_signals
    orig_sanitize = backend.reasoning.orchestrator.sanitize_momentum_evidence
    orig_route = backend.reasoning.orchestrator.route_evidence
    
    with patch("backend.services.analysis_service.extract_signals", tracer.hook_extract(orig_extract)), \
         patch("backend.services.analysis_service.compress_signals", tracer.hook_compress(orig_compress)), \
         patch("backend.reasoning.orchestrator.sanitize_momentum_evidence", tracer.hook_sanitize(orig_sanitize)), \
         patch("backend.reasoning.orchestrator.route_evidence", tracer.hook_route(orig_route)), \
         patch("backend.services.analysis_service.call_openrouter", side_effect=mock_call_openrouter), \
         patch("backend.reasoning.momentum_reasoner.call_openrouter", side_effect=mock_call_openrouter), \
         patch("backend.reasoning.synthesis_reasoner.call_openrouter", side_effect=mock_call_openrouter), \
         patch("backend.reasoning.icp_reasoner.call_openrouter", side_effect=mock_call_openrouter), \
         patch("backend.reasoning.tone_reasoner.call_openrouter", side_effect=mock_call_openrouter):
             
        analyzer = AnalysisService()
        competitor_pages = CompetitorPages(
            name=company_name, 
            domain=f"{company_name.lower()}.com", 
            pages=pages
        )
        
        try:
            await analyzer.analyze_competitor(competitor_pages)
        except Exception as e:
            # We might hit a JSON parse error because mock returns "{}"
            pass
            
    return tracer

def calculate_noise_ratios(pages):
    ratios = []
    for page in pages:
        text = page.content or ""
        sentences = split_into_sentences(text)
        
        noise_chunks = 0
        signal_chunks = 0
        for s in sentences:
            if not s.strip():
                continue
            if is_noise_chunk(s):
                noise_chunks += 1
            else:
                signal_chunks += 1
                
        total = noise_chunks + signal_chunks
        ratio = (noise_chunks / total * 100) if total > 0 else 0
        ratios.append({
            "page": page.url,
            "signal_chunks": signal_chunks,
            "noise_chunks": noise_chunks,
            "noise_ratio": f"{ratio:.1f}%"
        })
    return ratios

def run_diff(company_name, snapshots_data):
    snapshots = snapshots_data.get(company_name, [])
    
    # 1. Calculate Noise Ratios
    pages = []
    for snap in snapshots:
        pages.append(PageData(
            url=snap["source_url"],
            content=snap["content_text"],
            page_type=snap["page_type"],
            fetch_success=True
        ))
        
    noise_ratios = calculate_noise_ratios(pages)
    
    # 2. Run Replay
    # To get Replay intermediate state, we can hook just like we did for Production
    replay_tracer = PipelineTracer()
    import backend.eval.replay_runner
    
    orig_extract = backend.eval.replay_runner.extract_signals
    orig_compress = backend.eval.replay_runner.compress_signals
    orig_sanitize = backend.eval.replay_runner.sanitize_momentum_evidence
    orig_route = backend.eval.replay_runner.route_evidence
    
    with patch("backend.eval.replay_runner.extract_signals", replay_tracer.hook_extract(orig_extract)), \
         patch("backend.eval.replay_runner.compress_signals", replay_tracer.hook_compress(orig_compress)), \
         patch("backend.eval.replay_runner.sanitize_momentum_evidence", replay_tracer.hook_sanitize(orig_sanitize)), \
         patch("backend.eval.replay_runner.route_evidence", replay_tracer.hook_route(orig_route)):
             
        backend.eval.replay_runner.run_replay_for_company(company_name, snapshots_data)

    # 3. Run Production Trace
    prod_tracer = asyncio.run(run_production_trace(company_name, pages))
    
    diff = []
    
    diff.append({
        "stage": "extract_signals",
        "replay_signals": count_signals(replay_tracer.extracted),
        "production_signals": count_signals(prod_tracer.extracted)
    })
    
    diff.append({
        "stage": "compress_signals",
        "replay_signals": count_signals(replay_tracer.compressed),
        "production_signals": count_signals(prod_tracer.compressed)
    })
    
    diff.append({
        "stage": "sanitize_momentum_evidence",
        "replay_signals": count_signals(replay_tracer.sanitized),
        "production_signals": count_signals(prod_tracer.sanitized)
    })
    
    diff.append({
        "stage": "route_evidence",
        "replay_routed_chunks": count_routed(replay_tracer.routed),
        "production_routed_chunks": count_routed(prod_tracer.routed)
    })
    
    return {
        "company": company_name,
        "pipeline_diff": diff,
        "noise_ratios": noise_ratios
    }

def main():
    snapshots_path = "tests/mock_snapshots.json"
    if not os.path.exists(snapshots_path):
        print(f"Error: {snapshots_path} not found")
        return
        
    with open(snapshots_path, "r") as f:
        snapshots_data = json.load(f)
        
    reports_dir = "backend/eval/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    companies = ["Openai", "Anthropic", "Google"]
    
    for company in companies:
        print(f"Running diff for {company}...")
        result = run_diff(company, snapshots_data)
        
        out_path = os.path.join(reports_dir, f"pipeline_diff_{company.lower()}.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Saved {out_path}")
        print(json.dumps(result, indent=2))
        print("-" * 50)

if __name__ == "__main__":
    main()
