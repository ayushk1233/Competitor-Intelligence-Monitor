import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.temporal.enums import (
    TemporalChangeCategory,
    TemporalChangeDirection,
    TemporalConfidenceLevel
)
from backend.temporal.models import (
    TemporalEvidence,
    TemporalChange,
    TemporalAnalysis,
    TimelineComparison,
    TemporalComparisonResult
)
from backend.memory.models import TimelineEvent

def test_enum_serialization():
    assert TemporalChangeCategory.PRICING.value == "pricing"
    assert TemporalChangeDirection.MODIFIED.value == "modified"
    assert TemporalConfidenceLevel.HIGH.value == "high"

def test_evidence_model_validation():
    # Valid evidence
    ev = TemporalEvidence(
        category=TemporalChangeCategory.MESSAGING,
        description="Messaging changed",
        evidence="New messaging found",
        source_run_id="run_123",
        confidence_score=0.85,
        confidence_level=TemporalConfidenceLevel.HIGH
    )
    assert ev.confidence_score == 0.85
    
    # Invalid confidence score (out of bounds)
    with pytest.raises(ValidationError):
        TemporalEvidence(
            category=TemporalChangeCategory.MESSAGING,
            description="Messaging changed",
            evidence="New messaging found",
            source_run_id="run_123",
            confidence_score=1.5,
            confidence_level=TemporalConfidenceLevel.HIGH
        )
        
    # Invalid enum
    with pytest.raises(ValidationError):
        TemporalEvidence(
            category="INVALID",
            description="Messaging changed",
            evidence="New messaging found",
            source_run_id="run_123",
            confidence_score=0.8,
            confidence_level=TemporalConfidenceLevel.HIGH
        )

def test_nested_object_validation():
    ev = TemporalEvidence(
        category=TemporalChangeCategory.PRICING,
        description="Prices increased",
        evidence="Found on pricing page",
        source_run_id="run_456",
        confidence_score=0.9,
        confidence_level=TemporalConfidenceLevel.HIGH
    )
    
    change = TemporalChange(
        category=TemporalChangeCategory.PRICING,
        direction=TemporalChangeDirection.MODIFIED,
        summary="Price increase",
        business_impact="Will increase churn",
        reasoning="Consistent increase across all tiers",
        confidence_score=0.9,
        confidence_level=TemporalConfidenceLevel.HIGH,
        evidence=[ev]
    )
    
    assert len(change.evidence) == 1
    assert change.evidence[0].source_run_id == "run_456"

def test_json_round_trip():
    ev = TemporalEvidence(
        category=TemporalChangeCategory.MESSAGING,
        description="desc",
        evidence="ev",
        source_run_id="id1",
        confidence_score=0.5,
        confidence_level=TemporalConfidenceLevel.MEDIUM
    )
    change = TemporalChange(
        category=TemporalChangeCategory.MESSAGING,
        direction=TemporalChangeDirection.STRENGTHENED,
        summary="sum",
        business_impact="impact",
        reasoning="rsn",
        confidence_score=0.5,
        confidence_level=TemporalConfidenceLevel.MEDIUM,
        evidence=[ev]
    )
    analysis = TemporalAnalysis(
        company_name="Acme",
        analysis_timestamp=datetime.now(),
        changes=[change],
        overall_summary="Overall",
        confidence_score=0.6,
        confidence_level=TemporalConfidenceLevel.MEDIUM,
        timeline_version="v1"
    )
    
    json_data = analysis.model_dump_json()
    reloaded = TemporalAnalysis.model_validate_json(json_data)
    
    assert reloaded.company_name == "Acme"
    assert reloaded.changes[0].direction == TemporalChangeDirection.STRENGTHENED
