import pytest
import json
import os
from backend.reasoning.archetype_scoring import score_archetypes

@pytest.mark.asyncio
async def test_archetype_generalization():
    benchmark_path = "backend/eval/archetype_benchmark.json"
    with open(benchmark_path, "r") as f:
        companies = json.load(f)
        
    for c in companies:
        evidence = c["evidence"]
        result = await score_archetypes(evidence, "", "", "")
        
        winner = result["winner"]
        assert winner["confidence"] > 0
        assert len(winner["supporting_signals"]) > 0
        
        # Check specific expected generalisations
        if c["company"] == "HubSpot":
            assert winner["archetype"] == "SMB Growth Platform"
        elif c["company"] == "Salesforce":
            assert winner["archetype"] == "Enterprise Workflow Platform"
        elif c["company"] == "Datadog":
            assert winner["archetype"] == "AI Platform Builder"
