import json
import os
from pathlib import Path
from backend.retrieval.signal_extractor import extract_signals
from backend.retrieval.signal_compressor import compress_signals
from backend.retrieval.evidence_router import route_evidence

def find_source_snapshot(sentence: str, snapshots: list) -> dict:
    """Find which snapshot a sentence came from."""
    for snap in snapshots:
        if sentence in snap["content_text"]:
            return snap
        # Sometimes normalization happens
        if sentence.lower() in snap["content_text"].lower():
            return snap
    return None

def generate_signal_trace(company_name: str) -> dict:
    trace = {}
    
    # Load snapshots
    with open("tests/mock_snapshots.json", "r") as f:
        snapshots_data = json.load(f)
    
    if company_name not in snapshots_data:
        raise ValueError(f"No mock snapshots found for {company_name}")
        
    snapshots = snapshots_data[company_name]
    
    # ---------------------------------------------------------
    # STAGE 1: Raw Page Snapshot
    # ---------------------------------------------------------
    stage_1 = []
    chunks = []
    for snap in snapshots:
        stage_1.append({
            "page_type": snap["page_type"],
            "source_url": snap["source_url"],
            "content_preview": snap["content_text"][:100] + "..." if snap["content_text"] else ""
        })
        if snap["content_text"]:
            chunks.append(snap["content_text"])
            
    trace["stage_1_raw_snapshots"] = stage_1
    
    # ---------------------------------------------------------
    # STAGE 2: Extracted Signals
    # ---------------------------------------------------------
    combined_text = "\n\n".join(chunks)
    extracted = extract_signals(combined_text)
    
    stage_2 = []
    for sig_type, sig_list in extracted.items():
        for sentence in sig_list:
            source = find_source_snapshot(sentence, snapshots)
            stage_2.append({
                "signal_type": sig_type,
                "sentence": sentence,
                "page": source["page_type"] if source else "unknown",
                "url": source["source_url"] if source else "unknown"
            })
            
    trace["stage_2_extracted_signals"] = {
        "launch_signals": [s for s in stage_2 if s["signal_type"] == "launch_signals"],
        "shipping_velocity_signals": [s for s in stage_2 if s["signal_type"] == "shipping_velocity_signals"],
        "adoption_signals": [s for s in stage_2 if s["signal_type"] == "adoption_signals"],
        "hiring_signals": [s for s in stage_2 if s["signal_type"] == "hiring_signals"],
        "partnership_signals": [s for s in stage_2 if s["signal_type"] == "partnership_signals"],
        "all_signals": stage_2
    }
    
    # ---------------------------------------------------------
    # STAGE 3: Compressed Signals
    # ---------------------------------------------------------
    compressed = compress_signals(extracted)
    
    trace["stage_3_compressed_signals"] = {
        "before_compression": extracted,
        "after_compression": compressed
    }
    
    # ---------------------------------------------------------
    # STAGE 4: Route Evidence
    # ---------------------------------------------------------
    routed = route_evidence(chunks)
    
    trace["stage_4_routed_evidence"] = {
        "momentum_agent_input": routed.get("momentum", []),
        "tone_agent_input": routed.get("tone", []),
        "icp_agent_input": routed.get("icp", [])
    }
    
    # ---------------------------------------------------------
    # STAGE 5: Analyze Momentum (Agent Output)
    # ---------------------------------------------------------
    with open("tests/golden_analyses.json", "r") as f:
        golden_data = json.load(f)
        
    if company_name not in golden_data:
        raise ValueError(f"No golden analysis found for {company_name}")
        
    analysis = golden_data[company_name]
    agent_outputs = analysis.get("agent_outputs", {})
    momentum_output_str = agent_outputs.get("momentum", "{}")
    
    try:
        momentum_output = json.loads(momentum_output_str)
    except json.JSONDecodeError:
        momentum_output = {}
        
    momentum_evidence = momentum_output.get("momentum_evidence", {})
    
    trace["stage_5_analyze_momentum"] = {
        "launch_signals_used": momentum_evidence.get("launch_signals", []),
        "adoption_signals_used": momentum_evidence.get("adoption_signals", []),
        "hiring_signals_used": momentum_evidence.get("hiring_signals", []),
        "partnership_signals_used": momentum_evidence.get("partnership_signals", []),
        "reasoning": momentum_output.get("reasoning", ""),
        "score": momentum_output.get("momentum_score", 0)
    }
    
    # ---------------------------------------------------------
    # STAGE 6: Final CompetitorAnalysis Mismatches
    # ---------------------------------------------------------
    final_output_str = agent_outputs.get("final", "{}")
    try:
        final_output = json.loads(final_output_str)
    except json.JSONDecodeError:
        final_output = {}
        
    trace["stage_6_final_analysis"] = {
        "momentum_agent_output": momentum_output,
        "final_competitor_analysis": final_output
    }
    
    return trace

def main():
    companies = ["Openai", "Anthropic", "Google"]
    reports_dir = Path("backend/eval/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    for company in companies:
        print(f"Generating trace for {company}...")
        trace = generate_signal_trace(company)
        
        out_file = reports_dir / f"signal_trace_{company.lower()}.json"
        with open(out_file, "w") as f:
            json.dump(trace, f, indent=2)
            
        print(f"Saved trace to {out_file}")

if __name__ == "__main__":
    main()
