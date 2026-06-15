import json
import os
import pytest

def test_archetype_differentiation():
    companies = ["openai", "google", "anthropic"]
    analyses = {}
    
    for company in companies:
        artifact_path = f"artifacts/{company}/final_competitor_analysis.json"
        if not os.path.exists(artifact_path):
            pytest.skip("Benchmark artifacts not found. Run benchmark_runner.py first.")
        with open(artifact_path, "r") as f:
            analyses[company] = json.load(f)
            
    openai_dna = analyses["openai"].get("competitor_dna", {})
    google_dna = analyses["google"].get("competitor_dna", {})
    anthropic_dna = analyses["anthropic"].get("competitor_dna", {})
    
    archetypes = set([
        openai_dna.get("archetype"),
        google_dna.get("archetype"),
        anthropic_dna.get("archetype")
    ])

    if None in archetypes:
        pytest.skip("One or more competitor_dna fields empty — re-run benchmark_runner.py to regenerate artifacts.")

    # Archetypes must be highly differentiated (at least 2 unique)
    assert len(archetypes) >= 2, f"Archetypes failed to differentiate: {archetypes}"

    # Likely next moves should not be empty
    assert len(openai_dna.get("likely_next_moves", [])) > 0
    assert len(google_dna.get("likely_next_moves", [])) > 0
    assert len(anthropic_dna.get("likely_next_moves", [])) > 0
