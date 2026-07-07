import pytest
from unittest.mock import AsyncMock

from backend.temporal.models import ReasoningContext
from backend.temporal.llm import TemporalLLM
from backend.temporal.exceptions import TemporalReasoningError
from tests.temporal.test_prompt_builder import build_comparison

class MockLLMProvider:
    def __init__(self, response: str | None = None):
        self.response = response
        self.called_prompt = None
        self.called_model = None
        
    async def generate(self, prompt: str, model_name: str) -> str | None:
        self.called_prompt = prompt
        self.called_model = model_name
        return self.response

@pytest.mark.asyncio
async def test_temporal_llm_success():
    valid_json = """
    {
        "overall_summary": "Summary",
        "confidence_score": 0.9,
        "confidence_level": "high",
        "changes": [
            {
                "category": "pricing",
                "direction": "added",
                "summary": "Pricing change",
                "business_impact": "impact",
                "reasoning": "New tier added",
                "confidence_score": 0.8,
                "confidence_level": "medium",
                "evidence": []
            }
        ]
    }
    """
    provider = MockLLMProvider(response=valid_json)
    llm = TemporalLLM(provider)
    
    comparison = build_comparison()
    context = ReasoningContext(
        comparison=comparison,
        prompt_version="v1",
        model_name="test-model"
    )
    
    analysis = await llm.analyze(context)
    
    assert analysis.company_name == "TestCorp"
    assert provider.called_model == "test-model"
    assert "Briefing latest" in provider.called_prompt

@pytest.mark.asyncio
async def test_temporal_llm_timeout():
    provider = MockLLMProvider(response=None)
    llm = TemporalLLM(provider)
    
    comparison = build_comparison()
    context = ReasoningContext(
        comparison=comparison,
        prompt_version="v1",
        model_name="test-model"
    )
    
    with pytest.raises(TemporalReasoningError) as exc:
        await llm.analyze(context)
    assert "timeout or exhaustion" in str(exc.value)

@pytest.mark.asyncio
async def test_temporal_llm_parser_failure():
    provider = MockLLMProvider(response="Not JSON")
    llm = TemporalLLM(provider)
    
    comparison = build_comparison()
    context = ReasoningContext(
        comparison=comparison,
        prompt_version="v1",
        model_name="test-model"
    )
    
    with pytest.raises(TemporalReasoningError) as exc:
        await llm.analyze(context)
    assert "Failed to parse LLM response as JSON" in str(exc.value)
