import json
from pathlib import Path

def is_similar(text1: str, text2: str) -> bool:
    """Check if two strings are similar enough to be considered the same signal."""
    t1 = text1.lower()[:50]
    t2 = text2.lower()[:50]
    return t1 in t2 or t2 in t1

def detect_corruption(trace: dict) -> dict:
    report = {
        "drops": [],
        "mutations": [],
        "synthesis_hallucinations": []
    }
    
    stage_3 = trace.get("stage_3_compressed_signals", {}).get("after_compression", {})
    stage_5 = trace.get("stage_5_analyze_momentum", {})
    stage_6 = trace.get("stage_6_final_analysis", {}).get("final_competitor_analysis", {})
    
    categories = [
        ("launch_signals", "launch_signals_used"),
        ("shipping_velocity_signals", "shipping_velocity_signals_used"),
        ("adoption_signals", "adoption_signals_used"),
        ("hiring_signals", "hiring_signals_used"),
        ("partnership_signals", "partnership_signals_used"),
    ]
    
    # Check for drops and mutations between Stage 3 (Compressed) and Stage 5 (Momentum Output)
    for s3_cat, s5_cat in categories:
        s3_list = stage_3.get(s3_cat, [])
        s5_list = stage_5.get(s5_cat, [])
        
        # Check drops
        for s3_item in s3_list:
            if not any(is_similar(s3_item, s5_item) for s5_item in s5_list):
                report["drops"].append({
                    "category": s3_cat,
                    "signal": s3_item,
                    "stage": "Stage 3 -> Stage 5"
                })
                
        # Check mutations (hallucinations by Momentum Agent)
        for s5_item in s5_list:
            if not any(is_similar(s5_item, s3_item) for s3_item in s3_list):
                report["mutations"].append({
                    "category": s5_cat,
                    "signal": s5_item,
                    "stage": "Stage 5 (Momentum Agent)"
                })
                
    # Check for Synthesis Hallucinations (Stage 6 vs Stage 5)
    recent_launches = stage_6.get("recent_launches", [])
    s5_launches = stage_5.get("launch_signals_used", [])
    
    for rl in recent_launches:
        if not any(is_similar(rl, s5_l) for s5_l in s5_launches):
            report["synthesis_hallucinations"].append({
                "category": "recent_launches",
                "signal": rl,
                "stage": "Stage 6 (Final Synthesis)"
            })
            
    return report

def main():
    reports_dir = Path("backend/eval/reports")
    companies = ["openai", "anthropic", "google"]
    
    summary = {}
    
    for company in companies:
        trace_file = reports_dir / f"signal_trace_{company}.json"
        if not trace_file.exists():
            continue
            
        with open(trace_file, "r") as f:
            trace = json.load(f)
            
        report = detect_corruption(trace)
        
        out_file = reports_dir / f"corruption_report_{company}.json"
        with open(out_file, "w") as f:
            json.dump(report, f, indent=2)
            
        summary[company] = {
            "total_drops": len(report["drops"]),
            "total_mutations": len(report["mutations"]),
            "total_synthesis_hallucinations": len(report["synthesis_hallucinations"])
        }
        print(f"Corruption report for {company}: {summary[company]}")

    with open(reports_dir / "corruption_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
