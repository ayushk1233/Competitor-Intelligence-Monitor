import pytest
from backend.eval.intelligence_scorer import score_strategic_accuracy
from backend.models.schemas import CompetitorAnalysis

def test_strategic_accuracy_pass():
    expected_pass = ["commercially established", "platform ecosystem"]
    expected_fail = ["early commercialization", "developer tools only"]
    
    analysis = CompetitorAnalysis(
        name="Openai",
        domain="openai.com",
        strategic_keywords=["commercially established", "platform ecosystem"],
        core_offering="Commercially established AI platform.",
        analyst_note="They have built a massive ecosystem for enterprises.",
        icp="Enterprises",
        pages_analyzed=["homepage"],
        analysis_success=True,
        messaging_tone="visionary",
        pricing_signals="not detected",
        hiring_signals="not detected",
        momentum_score=9,
        recent_launches=[],
        growth_signals=[],
        risk_flags=[]
    )
    
    score = score_strategic_accuracy(expected_pass, expected_fail, analysis)
    assert score > 0.1

def test_strategic_accuracy_fail():
    expected_pass = ["commercially established", "platform ecosystem"]
    expected_fail = ["early commercialization", "developer tools only"]
    
    analysis = CompetitorAnalysis(
        name="Openai",
        domain="openai.com",
        strategic_keywords=["tools"],
        core_offering="Developer tools only for early stage startups.",
        analyst_note="They are in early commercialization phase.",
        icp="Developers",
        pages_analyzed=["homepage"],
        analysis_success=True,
        messaging_tone="startup",
        pricing_signals="not detected",
        hiring_signals="not detected",
        momentum_score=5,
        recent_launches=[],
        growth_signals=[],
        risk_flags=[]
    )
    
    score = score_strategic_accuracy(expected_pass, expected_fail, analysis)
    assert score < 0.5
