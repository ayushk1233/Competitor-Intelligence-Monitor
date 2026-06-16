import pytest
from backend.eval.false_negative_detector import score_false_negatives
from backend.models.schemas import CompetitorAnalysis

def test_false_negative_pass():
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
        pricing_signals="Pricing starts at $10/mo.",
        hiring_signals="Hiring engineers.",
        recent_launches=["New product X"],
        growth_signals=["Expanded to EU"],
        risk_flags=[],
        momentum_score=9,
        hiring_evidence=["Careers page: software engineer"],
        pricing_evidence=["Pricing page: $10/mo"]
    )
    score = score_false_negatives(analysis)
    assert score == 1.0

def test_false_negative_fail_hiring():
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
        hiring_signals="No hiring detected",
        recent_launches=[],
        growth_signals=[],
        risk_flags=[],
        momentum_score=9,
        hiring_evidence=["Careers page: software engineer"]
    )
    score = score_false_negatives(analysis)
    assert score < 1.0

def test_false_negative_fail_growth():
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
        recent_launches=["New product X"],
        growth_signals=["No public evidence found"],
        risk_flags=[],
        momentum_score=9
    )
    score = score_false_negatives(analysis)
    assert score < 1.0
