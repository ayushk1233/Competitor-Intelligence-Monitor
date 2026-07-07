import pytest
from unittest.mock import MagicMock, AsyncMock

from backend.temporal.engine import TemporalEngine
from backend.temporal.comparator import TimelineComparator
from backend.temporal.exceptions import TimelineComparisonError, TemporalReasoningError
from tests.temporal.test_comparator import build_timeline
from tests.temporal.test_llm import MockLLMProvider
from backend.temporal.llm import TemporalLLM

@pytest.mark.asyncio
async def test_engine_success():
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
    comparator = TimelineComparator()
    
    engine = TemporalEngine(comparator=comparator, llm=llm, model_name="test-model")
    timeline = build_timeline(3)
    
    result = await engine.analyze_timeline(timeline)
    
    assert result.comparison.company_name == "Acme"
    assert result.analysis.company_name == "Acme"
    assert len(result.analysis.changes) == 1

@pytest.mark.asyncio
async def test_engine_comparator_failure():
    provider = MockLLMProvider(response="{}")
    llm = TemporalLLM(provider)
    comparator = TimelineComparator()
    
    engine = TemporalEngine(comparator=comparator, llm=llm)
    timeline = build_timeline(1)  # Only 1 event, triggers error
    
    with pytest.raises(TimelineComparisonError):
        await engine.analyze_timeline(timeline)

@pytest.mark.asyncio
async def test_engine_llm_failure():
    provider = MockLLMProvider(response=None) # Timeout
    llm = TemporalLLM(provider)
    comparator = TimelineComparator()
    
    engine = TemporalEngine(comparator=comparator, llm=llm)
    timeline = build_timeline(3)
    
    with pytest.raises(TemporalReasoningError):
        await engine.analyze_timeline(timeline)

@pytest.mark.asyncio
async def test_engine_parser_failure():
    provider = MockLLMProvider(response="Bad JSON")
    llm = TemporalLLM(provider)
    comparator = TimelineComparator()
    
    engine = TemporalEngine(comparator=comparator, llm=llm)
    timeline = build_timeline(3)
    
    with pytest.raises(TemporalReasoningError):
        await engine.analyze_timeline(timeline)

@pytest.mark.asyncio
async def test_engine_unexpected_error():
    # Make LLMProvider raise an unexpected non-domain exception
    class BadProvider:
        async def generate(self, prompt, model_name):
            raise ValueError("Something completely unexpected")
            
    llm = TemporalLLM(BadProvider())
    comparator = TimelineComparator()
    engine = TemporalEngine(comparator=comparator, llm=llm)
    timeline = build_timeline(3)
    
    with pytest.raises(TemporalReasoningError) as exc:
        await engine.analyze_timeline(timeline)
    assert "Unexpected error" in str(exc.value)
