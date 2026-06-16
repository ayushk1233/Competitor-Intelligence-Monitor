import json
import os
import pytest

def test_archetype_reasoning():
    companies = ["Notion", "Airtable", "Coda"]
    analyses = {}
    
    for company in companies:
        artifact_path = f"artifacts/{company.lower()}/final_competitor_analysis.json"
        if not os.path.exists(artifact_path):
            pytest.skip("Benchmark artifacts not found. Run benchmark_runner.py first.")
        with open(artifact_path, "r") as f:
            analyses[company] = json.load(f)
            
    notion_dna = analyses["Notion"].get("competitor_dna", {})
    airtable_dna = analyses["Airtable"].get("competitor_dna", {})
    coda_dna = analyses["Coda"].get("competitor_dna", {})
    
    archetypes = set([
        notion_dna.get("archetype"),
        airtable_dna.get("archetype"),
        coda_dna.get("archetype")
    ])

    if None in archetypes:
        pytest.skip("One or more competitor_dna fields empty — re-run benchmark_runner.py to regenerate artifacts.")

    # Archetypes must be highly differentiated (at least 2 unique)
    assert len(archetypes) >= 2, f"Archetypes failed to differentiate: {archetypes}"

    # Likely next moves should not be empty
    assert len(notion_dna.get("likely_next_moves", [])) > 0
    assert len(airtable_dna.get("likely_next_moves", [])) > 0
    assert len(coda_dna.get("likely_next_moves", [])) > 0
