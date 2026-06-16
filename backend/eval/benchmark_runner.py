import asyncio
import json
import os
import time
from collections import defaultdict
from unittest.mock import patch

from backend.models.schemas import CompetitorPages, PageData
from backend.services.analysis_service import AnalysisService

# Track all data
class BenchmarkTracker:
    def __init__(self, company_name):
        self.company_name = company_name
        self.artifacts_dir = f"artifacts/{company_name.lower()}"
        os.makedirs(self.artifacts_dir, exist_ok=True)
        
        self.pipeline_metrics = {
            "raw_chars": 0,
            "cleaned_chars": 0,
            "ranked_chars": 0,
            "signals_extracted": 0,
            "signals_preserved": 0,
            "signals_dropped": 0,
            "noise_removed_count": 0,
            "runtime_seconds": 0
        }
        
    def save_json(self, filename, data):
        with open(os.path.join(self.artifacts_dir, filename), "w") as f:
            json.dump(data, f, indent=2)

def mock_llm_hook(tracker, real_call):
    async def wrapper(prompt, *, system_prompt=None, model=None, temperature=0.0, max_tokens=8000, call_type="analysis"):
        # Identify agent
        agent_name = "unknown"
        if "validation" in str(system_prompt).lower() or "validation" in str(prompt).lower() or "company identification" in str(system_prompt).lower():
            agent_name = "validation"
        elif "tone" in str(system_prompt).lower() or "messaging style" in str(system_prompt).lower() or call_type == "tone":
            agent_name = "tone"
        elif "icp" in str(system_prompt).lower() or "ideal customer" in str(system_prompt).lower() or call_type == "icp":
            agent_name = "icp"
        elif "momentum" in str(system_prompt).lower() or "velocity" in str(system_prompt).lower() or call_type == "momentum":
            agent_name = "momentum"
        elif "synthesis" in str(system_prompt).lower() or "competitor analysis framework" in str(system_prompt).lower() or call_type == "synthesis" or "analyst" in str(system_prompt).lower():
            agent_name = "synthesis"
            
        # Save input
        tracker.save_json(f"{agent_name}_input.json", {
            "system_prompt": system_prompt,
            "user_prompt": prompt,
            "model": model
        })
        
        # Call REAL OpenRouter
        response = await real_call(
            prompt, system_prompt=system_prompt, model=model,
            temperature=temperature, max_tokens=max_tokens, call_type=call_type
        )
        
        # Save output
        tracker.save_json(f"{agent_name}_output.json", {
            "response": response
        })
        
        return response
    return wrapper

def mock_extract(tracker, real_extract):
    def wrapper(*args, **kwargs):
        res = real_extract(*args, **kwargs)
        tracker.save_json("signals_extracted.json", res)
        count = sum(len(v) for v in res.values() if isinstance(v, list))
        tracker.pipeline_metrics["signals_extracted"] = count
        return res
    return wrapper

def mock_compress(tracker, real_compress):
    def wrapper(*args, **kwargs):
        res = real_compress(*args, **kwargs)
        tracker.save_json("signals_compressed.json", res)
        return res
    return wrapper
    
def mock_route(tracker, real_route):
    def wrapper(*args, **kwargs):
        res = real_route(*args, **kwargs)
        tracker.save_json("signals_routed.json", res)
        return res
    return wrapper

def mock_sanitize(tracker, real_sanitize):
    def wrapper(*args, **kwargs):
        # ensure diagnostics=True is used to get metrics
        kwargs["diagnostics"] = True
        sanitized, metrics = real_sanitize(*args, **kwargs)
        tracker.pipeline_metrics["signals_preserved"] = metrics["signals_preserved"]
        tracker.pipeline_metrics["signals_dropped"] = metrics["signals_dropped"]
        return sanitized, metrics
    return wrapper

async def run_benchmark_for_company(company_name, snapshots):
    tracker = BenchmarkTracker(company_name)
    start_time = time.time()
    
    pages = []
    raw_chars = 0
    for snap in snapshots:
        pages.append(PageData(
            url=snap["source_url"],
            content=snap["content_text"],
            page_type=snap["page_type"],
            fetch_success=True
        ))
        raw_chars += len(snap.get("content_text") or "")
        
    tracker.pipeline_metrics["raw_chars"] = raw_chars
    
    import backend.services.analysis_service
    import backend.reasoning.orchestrator
    import backend.services.llm_service
    
    real_extract = backend.services.analysis_service.extract_signals
    real_compress = backend.services.analysis_service.compress_signals
    real_route = backend.reasoning.orchestrator.route_evidence
    real_sanitize = backend.reasoning.orchestrator.sanitize_momentum_evidence
    real_llm = backend.services.llm_service.call_openrouter
    
    # We also need to capture noise count and ranked chars.
    # We will hook clean_content and build_ranked_context natively inside the patch.
    real_clean = backend.services.analysis_service.clean_content
    def hook_clean(*args, **kwargs):
        text, metrics = real_clean(*args, **kwargs)
        tracker.pipeline_metrics["cleaned_chars"] += len(text)
        tracker.pipeline_metrics["noise_removed_count"] += metrics["noise_removed_count"]
        return text, metrics
        
    real_build = backend.services.analysis_service.build_ranked_context
    def hook_build(*args, **kwargs):
        res = real_build(*args, **kwargs)
        tracker.pipeline_metrics["ranked_chars"] = sum(len(c) for c in res)
        return res
    
    with patch("backend.services.analysis_service.extract_signals", mock_extract(tracker, real_extract)), \
         patch("backend.services.analysis_service.compress_signals", mock_compress(tracker, real_compress)), \
         patch("backend.reasoning.orchestrator.route_evidence", mock_route(tracker, real_route)), \
         patch("backend.reasoning.orchestrator.sanitize_momentum_evidence", mock_sanitize(tracker, real_sanitize)), \
         patch("backend.services.analysis_service.clean_content", hook_clean), \
         patch("backend.services.analysis_service.build_ranked_context", hook_build), \
         patch("backend.services.analysis_service.call_openrouter", mock_llm_hook(tracker, real_llm)), \
         patch("backend.reasoning.momentum_reasoner.call_openrouter", mock_llm_hook(tracker, real_llm)), \
         patch("backend.reasoning.synthesis_reasoner.call_openrouter", mock_llm_hook(tracker, real_llm)), \
         patch("backend.reasoning.icp_reasoner.call_openrouter", mock_llm_hook(tracker, real_llm)), \
         patch("backend.reasoning.tone_reasoner.call_openrouter", mock_llm_hook(tracker, real_llm)):
             
        analyzer = AnalysisService()
        competitor_pages = CompetitorPages(
            name=company_name, 
            domain=f"{company_name.lower()}.com", 
            pages=pages
        )
        
        analysis = await analyzer.analyze_competitor(competitor_pages)
        
    tracker.pipeline_metrics["runtime_seconds"] = round(time.time() - start_time, 2)
    tracker.save_json("pipeline_metrics.json", tracker.pipeline_metrics)
    
    if analysis:
        tracker.save_json("final_competitor_analysis.json", analysis.model_dump())
        
        # Build Report
        report = {
            "company": company_name,
            "momentum_score": analysis.momentum_score,
            "messaging_tone": analysis.messaging_tone,
            "icp": analysis.icp,
            "strategic_keywords": analysis.strategic_keywords,
            "growth_signals": analysis.growth_signals,
            "recent_launches": analysis.recent_launches,
            "risk_flags": analysis.risk_flags,
            "analyst_note": analysis.analyst_note
        }
        tracker.save_json("benchmark_report.json", report)
        return analysis.model_dump(), tracker.pipeline_metrics
    return None, tracker.pipeline_metrics

def main():
    snapshots_path = "tests/mock_snapshots.json"
    golden_path = "tests/golden_analyses.json"
    
    with open(snapshots_path, "r") as f:
        snapshots_data = json.load(f)
        
    with open(golden_path, "r") as f:
        golden_data = json.load(f)
        
    companies = ["Notion", "Airtable", "Coda"]
    
    all_reports = {}
    
    for company in companies:
        print(f"\n========================================")
        print(f"BENCHMARKING: {company}")
        print(f"========================================\n")
        
        snaps = snapshots_data.get(company, [])
        new_analysis, metrics = asyncio.run(run_benchmark_for_company(company, snaps))
        
        if not new_analysis:
            print(f"Failed to generate analysis for {company}")
            continue
            
        old_analysis = golden_data.get(company, {})
        
        diff = {
            "momentum_before": old_analysis.get("momentum_score", 0),
            "momentum_after": new_analysis.get("momentum_score", 0),
            "launches_before": len(old_analysis.get("recent_launches", [])),
            "launches_after": len(new_analysis.get("recent_launches", [])),
            "partnerships_before": len([s for s in old_analysis.get("growth_signals", []) if "partner" in s.lower()]),
            "partnerships_after": len([s for s in new_analysis.get("growth_signals", []) if "partner" in s.lower()]),
            "keywords_before": len(old_analysis.get("strategic_keywords", [])),
            "keywords_after": len(new_analysis.get("strategic_keywords", [])),
            "noise_removed": True
        }
        
        tracker = BenchmarkTracker(company)
        tracker.save_json("quality_diff.json", diff)
        
        all_reports[company] = {
            "old": old_analysis,
            "new": new_analysis,
            "diff": diff
        }
        
    print("\n\n" + "="*50)
    print("FINAL SUMMARY")
    print("="*50)
    
    for company, data in all_reports.items():
        old = data["old"]
        new = data["new"]
        
        print(f"\n{company.upper()}")
        print(f"Momentum: {old.get('momentum_score')} → {new.get('momentum_score')}")
        print(f"Tone: {old.get('messaging_tone')} → {new.get('messaging_tone')}")
        
        print("\nTop Launches Detected:")
        for l in new.get("recent_launches", [])[:3]:
            print(f"- {l}")
            
        print("\nTop Partnerships Detected:")
        partnerships = [s for s in new.get("growth_signals", []) if "partner" in s.lower()]
        for p in partnerships[:3]:
            print(f"- {p}")
            
        print("\nAnalyst Note:")
        print(new.get("analyst_note", ""))
        print("-" * 50)

if __name__ == "__main__":
    main()
