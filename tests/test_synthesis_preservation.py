import asyncio
import pytest
from backend.reasoning.synthesis_reasoner import synthesize_intelligence
import json

@pytest.mark.asyncio
async def test_synthesis_preservation():
    context = "Sample context."
    momentum = '{"momentum_score": 8, "evidence": ["Strong AI launches"]}'
    tone = '{"messaging_tone": "technical", "evidence": ["Developer platform"]}'
    icp = '{"icp_summary": "enterprise engineering teams", "icp_keywords": ["engineers", "enterprise"], "evidence": ["enterprise focus"]}'
    
    result = await synthesize_intelligence(context, momentum, tone, icp)
    
    # Extract json properly, same logic as analyzer
    result = result.replace("```json", "").replace("```", "").strip()
    parsed = json.loads(result)
    
    assert "icp_keywords" in parsed
    assert "icp_evidence" in parsed
    assert "tone_evidence" in parsed
    assert "momentum_evidence" in parsed
    assert "momentum_score" in parsed
    assert parsed["momentum_score"] == 8
