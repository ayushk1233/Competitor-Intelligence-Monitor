import pytest
from backend.signals.rules import calculate_severity, normalize_category
from backend.signals.enums import SignalSeverity
from backend.temporal.enums import TemporalChangeCategory

def test_calculate_severity():
    assert calculate_severity(0.95) == SignalSeverity.CRITICAL
    assert calculate_severity(0.90) == SignalSeverity.CRITICAL
    assert calculate_severity(0.85) == SignalSeverity.HIGH
    assert calculate_severity(0.75) == SignalSeverity.HIGH
    assert calculate_severity(0.60) == SignalSeverity.MEDIUM
    assert calculate_severity(0.50) == SignalSeverity.MEDIUM
    assert calculate_severity(0.40) == SignalSeverity.LOW
    assert calculate_severity(0.0) == SignalSeverity.LOW

def test_normalize_category():
    assert normalize_category("pricing") == TemporalChangeCategory.PRICING
    assert normalize_category("PRICING") == TemporalChangeCategory.PRICING
    assert normalize_category("invalid_cat") == TemporalChangeCategory.UNKNOWN
