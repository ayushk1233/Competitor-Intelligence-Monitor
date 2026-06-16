import pytest
from backend.eval.evidence_scorer import score_evidence_quality
from backend.models.schemas import CompetitorAnalysis

def test_evidence_quality_high():
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
        recent_launches=[],
        growth_signals=[],
        risk_flags=[],
        momentum_score=9,
        core_offering_evidence=["evidence 1"],
        pricing_evidence=["evidence 2"],
        hiring_evidence=["evidence 3"],
        keywords_evidence=["evidence 4"],
        core_offering_source_url="https://test.com/",
        pricing_source_url="https://test.com/pricing"
    )
    score = score_evidence_quality(analysis)
    assert score == 1.0

def test_evidence_quality_low():
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
        recent_launches=[],
        growth_signals=[],
        risk_flags=[],
        momentum_score=9,
        core_offering_evidence=["evidence 1"],
        core_offering_source_url="https://test.com/"
    )
    score = score_evidence_quality(analysis)
    assert score < 0.5
