import pytest
from backend.eval.intelligence_scorer import score_company_understanding
from backend.models.schemas import CompetitorAnalysis

def test_company_understanding_pass():
    expected_concepts = ["foundation models", "enterprise AI", "API ecosystem"]
    
    analysis = CompetitorAnalysis(
        name="Openai",
        domain="openai.com",
        strategic_keywords=["foundation models", "api", "enterprise"],
        core_offering="Building enterprise AI and foundation models",
        analyst_note="OpenAI is establishing an API ecosystem.",
        icp="Enterprises and developers",
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
    
    score = score_company_understanding(expected_concepts, analysis)
    assert score > 0.6

def test_company_understanding_fail():
    expected_concepts = ["foundation models", "enterprise AI", "API ecosystem"]
    
    analysis = CompetitorAnalysis(
        name="Openai",
        domain="openai.com",
        strategic_keywords=["developer tool", "productivity", "chat"],
        core_offering="A chat assistant for productivity",
        analyst_note="Just a generic AI assistant.",
        icp="Consumers",
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
    
    score = score_company_understanding(expected_concepts, analysis)
    assert score < 0.5
