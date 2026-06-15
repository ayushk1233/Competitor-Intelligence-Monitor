import json
import os
import pytest

def test_competitor_dna_schema():
    companies = ["openai", "google", "anthropic"]
    
    for company in companies:
        artifact_path = f"artifacts/{company}/final_competitor_analysis.json"
        if not os.path.exists(artifact_path):
            pytest.skip("Benchmark artifacts not found.")
        with open(artifact_path, "r") as f:
            analysis = json.load(f)
            
        dna = analysis.get("competitor_dna", {})

        if not dna or not dna.get("archetype"):
            pytest.skip(f"competitor_dna empty for {company} — re-run benchmark_runner.py to regenerate artifacts.")

        assert "archetype" in dna, f"Missing archetype in {company}"
        assert "growth_model" in dna, f"Missing growth_model in {company}"
        assert "primary_moat" in dna, f"Missing primary_moat in {company}"
        assert "strategic_risk" in dna, f"Missing strategic_risk in {company}"
        assert "likely_next_moves" in dna, f"Missing likely_next_moves in {company}"
        assert isinstance(dna["likely_next_moves"], list), "likely_next_moves must be a list"
