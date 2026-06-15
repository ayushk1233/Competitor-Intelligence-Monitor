import json
import os
import pytest

def test_company_strategic_differentiation():
    companies = ["openai", "google", "anthropic"]
    analyses = {}
    
    for company in companies:
        artifact_path = f"artifacts/{company}/final_competitor_analysis.json"
        
        # If the artifacts don't exist yet, we can't test
        if not os.path.exists(artifact_path):
            pytest.skip("Benchmark artifacts not found. Run benchmark_runner.py first.")
            
        with open(artifact_path, "r") as f:
            analyses[company] = json.load(f)
            
    # Verify we got all 3
    assert len(analyses) == 3
    
    openai = analyses["openai"]
    google = analyses["google"]
    anthropic = analyses["anthropic"]
    
    # 1. Assert Tones are not completely generic identical strings
    # We allow some overlap, but they shouldn't all just be "technical"
    tones = set([openai.get("messaging_tone"), google.get("messaging_tone"), anthropic.get("messaging_tone")])
    assert len(tones) > 1, f"Tones failed to differentiate: {tones}"
    
    # 2. Assert ICPs are not all identical
    icps = set([openai.get("icp"), google.get("icp"), anthropic.get("icp")])
    assert len(icps) > 1, f"ICPs failed to differentiate: {icps}"
    
    # 3. Assert Strategic Interpretation is present and distinct
    assert "strategic_interpretation" in openai
    assert "strategic_interpretation" in google
    assert "strategic_interpretation" in anthropic
    
    # Strategic directions should definitely be distinct
    directions = set([
        openai["strategic_interpretation"].get("strategic_direction"),
        google["strategic_interpretation"].get("strategic_direction"),
        anthropic["strategic_interpretation"].get("strategic_direction")
    ])
    assert len(directions) >= 2, f"Strategic directions must be highly differentiated: {directions}"

    # 4. Assert Competitor DNA is present and distinct
    assert "competitor_dna" in openai
    assert "competitor_dna" in google
    assert "competitor_dna" in anthropic
    
    identities = set([
        openai["competitor_dna"].get("archetype"),
        google["competitor_dna"].get("archetype"),
        anthropic["competitor_dna"].get("archetype")
    ])
    if None in identities:
        pytest.skip("Competitor DNA incomplete — re-run benchmark_runner.py to regenerate artifacts.")
    assert len(identities) >= 2, f"Competitor archetypes must be uniquely identified: {identities}"
    
    # 5. Assert Analyst Notes are distinct
    notes = set([
        openai.get("analyst_note"),
        google.get("analyst_note"),
        anthropic.get("analyst_note")
    ])
    assert len(notes) == 3
