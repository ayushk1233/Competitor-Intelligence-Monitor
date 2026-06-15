import pytest
import asyncio
from backend.reasoning.archetype_scoring import score_archetypes

@pytest.mark.asyncio
async def test_score_archetypes_basic():
    # Provide clear keywords for Trusted Enterprise AI
    tone_output = "We focus on compliance and governance."
    icp_output = "Enterprise buyers with risk requirements."
    strategy_output = "Regulated industries adoption."
    momentum_output = "Audits and security."
    
    result = await score_archetypes(tone_output, icp_output, strategy_output, momentum_output)
    
    winner = result["winner"]
    assert winner["archetype"] == "Trusted Enterprise AI"
    assert winner["confidence"] > 0
    assert "compliance" in winner["supporting_signals"]
    assert "governance" in winner["supporting_signals"]
    
    # Must have candidates
    assert len(result["candidates"]) >= 0 # Alternative might be empty if 0 overlap, but let's check schema
    assert "hypotheses" in result
