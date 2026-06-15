import json
import os

from backend.intelligence.content_quality import clean_content
from backend.models.schemas import PageData
from backend.retrieval.context_builder import build_ranked_context
from backend.retrieval.signal_extractor import extract_signals

def evaluate_context_integrity(company_name, snapshots):
    raw_chars = 0
    cleaned_chars = 0
    noise_removed_count = 0
    noise_removed_examples = []
    
    cleaned_pages_as_dicts = []
    
    # 1. Clean Content Pipeline
    for snap in snapshots:
        content = snap.get("content_text", "")
        if not content:
            continue
            
        raw_chars += len(content)
        cleaned_content, metrics = clean_content(content)
        
        cleaned_chars += len(cleaned_content)
        noise_removed_count += metrics["noise_removed_count"]
        noise_removed_examples.extend(metrics["noise_removed_examples"])
        
        cleaned_pages_as_dicts.append({
            "url": snap["source_url"],
            "page_type": snap["page_type"],
            "content": cleaned_content
        })
        
    # 2. Extract signals BEFORE ranking
    full_cleaned_content_str = "\n\n".join([p["content"] for p in cleaned_pages_as_dicts if p["content"]])
    signals_before = extract_signals(full_cleaned_content_str)
    
    signals_before_count = sum(len(v) for v in signals_before.values() if isinstance(v, list))
    
    # 3. Build ranked context (truncation)
    cleaned_chunks = build_ranked_context(cleaned_pages_as_dicts)
    ranked_chars = sum(len(c) for c in cleaned_chunks)
    
    # 4. Extract signals AFTER ranking (to verify we didn't lose them, or to track loss)
    ranked_content_str = "\n\n".join(cleaned_chunks)
    signals_after = extract_signals(ranked_content_str)
    
    signals_after_count = sum(len(v) for v in signals_after.values() if isinstance(v, list))
    
    return {
        "company": company_name,
        "raw_chars": raw_chars,
        "cleaned_chars": cleaned_chars,
        "ranked_chars": ranked_chars,
        "signals_before_ranking": signals_before_count,
        "signals_after_ranking": signals_after_count,
        "noise_removed_count": noise_removed_count,
        "noise_removed_examples": list(set(noise_removed_examples))[:10]
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
        print(f"Evaluating context integrity for {company}...")
        result = evaluate_context_integrity(company, snapshots_data.get(company, []))
        
        out_path = os.path.join(reports_dir, f"context_integrity_{company.lower()}.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Saved {out_path}")
        print(json.dumps(result, indent=2))
        print("-" * 50)

if __name__ == "__main__":
    main()
