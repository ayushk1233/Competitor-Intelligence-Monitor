import pytest
from backend.reasoning.archetype_scoring import score_archetypes

@pytest.mark.asyncio
async def test_archetype_explainability():
    tone_output = "We have an amazing api and sdk."
    icp_output = "targeting developers."
    strategy_output = "expanding the ecosystem and platform."
    momentum_output = ""
    
    result = await score_archetypes(tone_output, icp_output, strategy_output, momentum_output)
    winner = result["winner"]
    
    # Must answer WHY (supporting signals)
    assert len(winner["supporting_signals"]) > 0
    
    # Must expose confidence
    assert "confidence" in winner
    assert isinstance(winner["confidence"], float)
    
    # Must expose alternative archetypes
    assert "candidates" in result
    assert isinstance(result["candidates"], list)
