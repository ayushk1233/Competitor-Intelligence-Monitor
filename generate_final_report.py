import json
import os
import asyncio
from backend.reasoning.archetype_scoring import score_archetypes

async def main():
    report = []
    
    # 1. Load the benchmark companies (HubSpot, Salesforce, Datadog, etc.)
    with open("backend/eval/archetype_benchmark.json", "r") as f:
        benchmarks = json.load(f)
        
    for b in benchmarks:
        if b["company"] not in ["HubSpot", "Salesforce"]:
            continue
        res = await score_archetypes(b["evidence"], "", "", "")
        report.append({
            "company": b["company"],
            "winner": res["winner"]["archetype"],
            "confidence": res["winner"]["confidence"],
            "supporting_signals": res["winner"]["supporting_signals"],
            "alternative_archetypes": res["candidates"],
            "growth_model": res["winner"]["growth_model"],
            "primary_moat": res["winner"]["primary_moat"]
        })
        
    # 2. Load the AI companies from artifacts
    for company in ["openai", "google", "anthropic"]:
        with open(f"artifacts/{company}/final_competitor_analysis.json", "r") as f:
            data = json.load(f)
            dna = data.get("competitor_dna", {})
            report.append({
                "company": company.capitalize(),
                "winner": dna.get("archetype", "Unknown"),
                "confidence": dna.get("confidence", 0.0),
                "supporting_signals": dna.get("supporting_signals", []),
                "alternative_archetypes": dna.get("alternative_archetypes", []),
                "growth_model": dna.get("growth_model", ""),
                "primary_moat": dna.get("primary_moat", "")
            })
            
    with open("artifacts/archetypes/archetype_scoring_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print("Report generated!")

if __name__ == "__main__":
    asyncio.run(main())
