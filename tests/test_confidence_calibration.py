import pytest
from backend.eval.confidence_validator import score_confidence_calibration
from backend.models.schemas import CompetitorAnalysis

def test_confidence_calibration_pass():
    analysis = CompetitorAnalysis(
        name="Test",
        domain="test.com",
        strategic_keywords=["test"],
        core_offering="Test",
        analyst_note="Test",
        icp="Test",
        pages_analyzed=["homepage"],
        analysis_success=True,
        messaging_tone="visionary",
        pricing_signals="not detected",
        hiring_signals="not detected",
        momentum_score=9,
        recent_launches=[],
        growth_signals=[],
        risk_flags=[],
        confidence_scores={
            "core_offering": 80,
            "icp": 70,
            "tone": 90,
            "pricing": 50
        }
    )
    score = score_confidence_calibration(analysis)
    assert score == 1.0

def test_confidence_calibration_fail_exact_matches():
    analysis = CompetitorAnalysis(
        name="Test",
        domain="test.com",
        strategic_keywords=["test"],
        core_offering="Test",
        analyst_note="Test",
        icp="Test",
        pages_analyzed=["homepage"],
        analysis_success=True,
        messaging_tone="visionary",
        pricing_signals="not detected",
        hiring_signals="not detected",
        momentum_score=9,
        recent_launches=[],
        growth_signals=[],
        risk_flags=[],
        confidence_scores={
            "core_offering": 92,  # Anchored value
            "icp": 88,            # Anchored value
            "tone": 85,           # Anchored value
            "pricing": 75         # Anchored value
        }
    )
    score = score_confidence_calibration(analysis)
    assert score < 1.0

def test_confidence_calibration_fail_repeated():
    analysis = CompetitorAnalysis(
        name="Test",
        domain="test.com",
        strategic_keywords=["test"],
        core_offering="Test",
        analyst_note="Test",
        icp="Test",
        pages_analyzed=["homepage"],
        analysis_success=True,
        messaging_tone="visionary",
        pricing_signals="not detected",
        hiring_signals="not detected",
        momentum_score=9,
        recent_launches=[],
        growth_signals=[],
        risk_flags=[],
        confidence_scores={
            "core_offering": 80,
            "icp": 80,
            "tone": 80,
            "pricing": 80
        }
    )
    score = score_confidence_calibration(analysis)
    assert score < 1.0
