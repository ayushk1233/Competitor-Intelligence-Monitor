import json
import pytest
from datetime import datetime, timezone, timedelta

from backend.memory.models import TimelineEvent
from backend.temporal.models import TimelineComparison, ComparisonMetadata
from backend.temporal.prompts.builder import TemporalPromptBuilder
from backend.temporal.prompts.parser import TemporalResponseParser
from backend.temporal.exceptions import TemporalReasoningError

def build_comparison(with_history=True) -> TimelineComparison:
    now = datetime.now(timezone.utc)
    
    metadata = ComparisonMetadata(
        total_events=3 if with_history else 2,
        historical_depth=1 if with_history else 0,
        days_between_latest_and_previous=1,
        timeline_span_days=2 if with_history else 1
    )
    
    return TimelineComparison(
        company_name="TestCorp",
        latest_event=TimelineEvent(
            run_id="run_latest",
            company_name="TestCorp",
            analyzed_at=now,
            executive_briefing="Briefing latest",
            structured_summary="Summary latest",
            supporting_chunks=[]
        ),
        previous_event=TimelineEvent(
            run_id="run_previous",
            company_name="TestCorp",
            analyzed_at=now - timedelta(days=1),
            executive_briefing="Briefing previous",
            structured_summary="Summary previous",
            supporting_chunks=[]
        ),
        historical_context=[
            TimelineEvent(
                run_id="run_history",
                company_name="TestCorp",
                analyzed_at=now - timedelta(days=2),
                executive_briefing="Briefing history",
                structured_summary="Summary history",
                supporting_chunks=[]
            )
        ] if with_history else [],
        metadata=metadata
    )

def test_prompt_builder_deterministic():
    comparison = build_comparison()
    builder = TemporalPromptBuilder()
    
    prompt1 = builder.build(comparison)
    prompt2 = builder.build(comparison)
    
    assert prompt1 == prompt2
    assert "Briefing latest" in prompt1
    assert "Briefing previous" in prompt1
    assert "Briefing history" in prompt1
    assert "Total Events: 3" in prompt1

def test_prompt_builder_empty_history():
    comparison = build_comparison(with_history=False)
    builder = TemporalPromptBuilder()
    
    prompt = builder.build(comparison)
    assert "No historical context available." in prompt
    assert "Total Events: 2" in prompt

def test_parser_success():
    parser = TemporalResponseParser()
    valid_json = """
    ```json
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
    ```
    """
    
    analysis = parser.parse(valid_json, "TestCorp")
    
    assert analysis.company_name == "TestCorp"
    assert analysis.confidence_score == 0.9
    assert len(analysis.changes) == 1
    assert analysis.changes[0].category == "pricing"

def test_parser_malformed_json():
    parser = TemporalResponseParser()
    invalid_json = "This is not JSON"
    
    with pytest.raises(TemporalReasoningError) as exc:
        parser.parse(invalid_json, "TestCorp")
    assert "Failed to parse LLM response as JSON" in str(exc.value)

def test_parser_invalid_enum():
    parser = TemporalResponseParser()
    invalid_json = """
    {
        "overall_summary": "Summary",
        "confidence_score": 0.9,
        "confidence_level": "high",
        "changes": [
            {
                "category": "invalid_category",
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
    
    with pytest.raises(TemporalReasoningError) as exc:
        parser.parse(invalid_json, "TestCorp")
    assert "failed domain model validation" in str(exc.value)

def test_parser_missing_fields():
    parser = TemporalResponseParser()
    # Missing 'changes' field
    invalid_json = """
    {
        "overall_summary": "Summary",
        "confidence_score": 0.9,
        "confidence_level": "high"
    }
    """
    
    with pytest.raises(TemporalReasoningError) as exc:
        parser.parse(invalid_json, "TestCorp")
    assert "failed domain model validation" in str(exc.value)
