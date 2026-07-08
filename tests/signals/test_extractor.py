import pytest
import uuid
from datetime import datetime, timezone
from backend.temporal.models import (
    TemporalAnalysis, TemporalChange, ReasoningContext, 
    TimelineComparison, ComparisonMetadata
)
from backend.temporal.enums import (
    TemporalChangeCategory, TemporalChangeDirection, TemporalConfidenceLevel
)
from backend.memory.models import TimelineEvent
from backend.signals.extractor import StrategicSignalExtractor
from backend.signals.enums import SignalSeverity

def build_mock_analysis(changes: list[TemporalChange]) -> TemporalAnalysis:
    return TemporalAnalysis(
        company_name="Acme",
        analysis_timestamp=datetime.now(timezone.utc),
        changes=changes,
        overall_summary="Summary",
        confidence_score=0.9,
        confidence_level=TemporalConfidenceLevel.HIGH,
        timeline_version="v1"
    )

def build_mock_context() -> ReasoningContext:
    now = datetime.now(timezone.utc)
    return ReasoningContext(
        comparison=TimelineComparison(
            company_name="Acme",
            latest_event=TimelineEvent(
                run_id="run_latest",
                company_name="Acme",
                analyzed_at=now,
                executive_briefing="Briefing",
                structured_summary="Summary",
                supporting_chunks=[]
            ),
            previous_event=TimelineEvent(
                run_id="run_prev",
                company_name="Acme",
                analyzed_at=now,
                executive_briefing="Briefing",
                structured_summary="Summary",
                supporting_chunks=[]
            ),
            historical_context=[],
            metadata=ComparisonMetadata(
                total_events=2,
                historical_depth=0,
                days_between_latest_and_previous=0,
                timeline_span_days=0
            )
        ),
        prompt_version="v1",
        model_name="test-model",
        analysis_version="temporal-engine-v1"
    )

def test_extractor_success():
    changes = [
        TemporalChange(
            category=TemporalChangeCategory.PRICING,
            direction=TemporalChangeDirection.ADDED,
            summary="New tier",
            business_impact="Increase ARPU",
            reasoning="Reasoning",
            confidence_score=0.95,
            confidence_level=TemporalConfidenceLevel.HIGH,
            evidence=[]
        ),
        TemporalChange(
            category=TemporalChangeCategory.PRODUCT,
            direction=TemporalChangeDirection.MODIFIED,
            summary="New feature",
            business_impact="More engagement",
            reasoning="Reasoning",
            confidence_score=0.8,
            confidence_level=TemporalConfidenceLevel.MEDIUM,
            evidence=[]
        )
    ]
    analysis = build_mock_analysis(changes)
    context = build_mock_context()
    
    extractor = StrategicSignalExtractor()
    signals = extractor.extract(analysis, context)
    
    assert len(signals) == 2
    assert signals[0].category == TemporalChangeCategory.PRICING
    assert signals[0].severity == SignalSeverity.CRITICAL
    assert signals[0].business_impact == "Increase ARPU"
    assert signals[1].category == TemporalChangeCategory.PRODUCT
    assert signals[1].severity == SignalSeverity.HIGH
    assert signals[1].business_impact == "More engagement"

def test_deterministic_ids():
    changes = [
        TemporalChange(
            category=TemporalChangeCategory.POSITIONING,
            direction=TemporalChangeDirection.STRENGTHENED,
            summary="Stronger positioning",
            business_impact="Better market fit",
            reasoning="Reasoning",
            confidence_score=0.9,
            confidence_level=TemporalConfidenceLevel.HIGH,
            evidence=[]
        )
    ]
    analysis = build_mock_analysis(changes)
    context = build_mock_context()
    
    extractor = StrategicSignalExtractor()
    signals1 = extractor.extract(analysis, context)
    signals2 = extractor.extract(analysis, context)
    
    assert signals1[0].signal_id == signals2[0].signal_id
    assert signals1[0].signal_fingerprint == signals2[0].signal_fingerprint

def test_empty_changes():
    analysis = build_mock_analysis([])
    context = build_mock_context()
    
    extractor = StrategicSignalExtractor()
    signals = extractor.extract(analysis, context)
    
    assert len(signals) == 0
