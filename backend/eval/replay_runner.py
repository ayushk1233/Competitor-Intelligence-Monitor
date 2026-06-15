import json
import os
from pathlib import Path
from backend.eval.models import ReplayResult
from backend.retrieval.signal_extractor import extract_signals
from backend.retrieval.signal_compressor import compress_signals
from backend.retrieval.evidence_router import route_evidence
from backend.reasoning.orchestrator import sanitize_momentum_evidence
from backend.intelligence.content_quality import clean_content

def mock_analyze_momentum(signals: dict) -> int:
    """Deterministic, heuristic-based scoring to validate evidence flow without LLM costs."""
    base_score = 1
    
    launches = signals.get("launch_signals", [])
    partnerships = signals.get("partnership_signals", [])
    adoptions = signals.get("adoption_signals", [])
    hiring = signals.get("hiring_signals", [])
    velocity = signals.get("shipping_velocity_signals", [])
    
    score = base_score
    score += len(launches) * 2
    score += len(partnerships) * 2
    score += len(adoptions) * 1
    score += len(hiring) * 1
    score += len(velocity) * 1
    
    return min(10, score)

def run_replay_for_company(company_name: str, snapshots_data: dict) -> ReplayResult:
    snapshots = snapshots_data.get(company_name, [])
    if not snapshots:
        raise ValueError(f"No snapshots for {company_name}")
        
    chunks = [s["content_text"] for s in snapshots if s.get("content_text")]
    combined_text = "\n\n".join(chunks)
    
    # 0. Clean Content
    cleaned_text, clean_metrics = clean_content(combined_text)
    
    # 1. Extraction
    extracted = extract_signals(cleaned_text)
    
    # 2. Compression
    compressed = compress_signals(extracted)
    
    # 3. Sanitization (with diagnostics)
    sanitized, metrics = sanitize_momentum_evidence(compressed, diagnostics=True)
    
    # 4. Routing
    routed = route_evidence(chunks)
    
    # 5. Momentum Replay (Deterministic)
    momentum_score = mock_analyze_momentum(sanitized)
    
    return ReplayResult(
        company_name=company_name,
        
        content_retention_ratio=clean_metrics["content_retention_ratio"],
        noise_removed_count=clean_metrics["noise_removed_count"],
        cleaned_content_preview=cleaned_text[:200] + "...",
        removed_content_preview=clean_metrics["noise_removed_examples"],
        
        signals_extracted=metrics["signals_extracted"],
        signals_preserved=metrics["signals_preserved"],
        signals_dropped=metrics["signals_dropped"],
        launch_signals=sanitized.get("launch_signals", []),
        shipping_signals=sanitized.get("shipping_velocity_signals", []),
        adoption_signals=sanitized.get("adoption_signals", []),
        hiring_signals=sanitized.get("hiring_signals", []),
        partnership_signals=sanitized.get("partnership_signals", []),
        momentum_score=momentum_score,
        drop_reasons=metrics["rejected_reasons"],
        routing_summary={
            "tone_chunks": len(routed.get("tone", [])),
            "icp_chunks": len(routed.get("icp", []))
        }
    )

def main():
    snapshots_path = "tests/mock_snapshots.json"
    if not os.path.exists(snapshots_path):
        print(f"Error: {snapshots_path} not found")
        return
        
    with open(snapshots_path, "r") as f:
        snapshots_data = json.load(f)
        
    reports_dir = Path("backend/eval/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    companies = ["Openai", "Anthropic", "Google"]
    
    for company in companies:
        try:
            print(f"Running replay for {company}...")
            result = run_replay_for_company(company, snapshots_data)
            
            out_path = reports_dir / f"replay_{company.lower()}.json"
            with open(out_path, "w") as f:
                json.dump(result.model_dump(), f, indent=2)
            
            print(f"Saved replay report to {out_path}")
            print(f"  Preserved: {result.signals_preserved}/{result.signals_extracted} signals")
            print(f"  Momentum Score: {result.momentum_score}")
            
        except Exception as e:
            print(f"Failed to run replay for {company}: {e}")

if __name__ == "__main__":
    main()
