import pytest
import uuid
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.temporal.enums import (
    TemporalChangeCategory, TemporalChangeDirection, TemporalConfidenceLevel
)
from backend.signals.enums import SignalSeverity
from backend.signals.models import StrategicSignal

def test_strategic_signal_validation():
    signal = StrategicSignal(
        signal_id=uuid.uuid4(),
        signal_fingerprint="fingerprint_hash",
        company_name="Acme",
        category=TemporalChangeCategory.PRICING,
        direction=TemporalChangeDirection.ADDED,
        summary="summary",
        business_impact="impact",
        confidence_score=0.9,
        confidence_level=TemporalConfidenceLevel.HIGH,
        severity=SignalSeverity.CRITICAL,
        evidence=[],
        originating_run_id="run_123",
        prompt_version="v1",
        model_name="test-model",
        detected_at=datetime.now(timezone.utc)
    )
    
    assert signal.company_name == "Acme"
    
    with pytest.raises(ValidationError):
        StrategicSignal(
            signal_id="not-a-uuid",
            signal_fingerprint="fingerprint_hash",
            company_name="Acme",
            category=TemporalChangeCategory.PRICING,
            direction=TemporalChangeDirection.ADDED,
            summary="summary",
            business_impact="impact",
            confidence_score=0.9,
            confidence_level=TemporalConfidenceLevel.HIGH,
            severity=SignalSeverity.CRITICAL,
            evidence=[],
            originating_run_id="run_123",
            prompt_version="v1",
            model_name="test-model",
            detected_at=datetime.now(timezone.utc)
        )
