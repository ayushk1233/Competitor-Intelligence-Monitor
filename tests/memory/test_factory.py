import pytest
from uuid import uuid4
from datetime import datetime, timezone

from backend.models.schemas import CompetitorAnalysis, ComparisonResult
from backend.memory.factory import MemoryDocumentFactory
from backend.database.models import ChunkType

@pytest.fixture
def base_analysis():
    return CompetitorAnalysis(
        name="Acme",
        domain="acme.com",
        core_offering="AI memory",
        icp="Enterprise",
        messaging_tone="visionary",
        pricing_signals="Expensive",
        hiring_signals="Growing engineering",
        recent_launches=["v2.0"],
        strategic_keywords=["memory", "AI"],
        growth_signals=["Series B"],
        risk_flags=["High churn"],
        momentum_score=8,
        analyst_note="Acme is doing well.",
        strategic_interpretation={"tone": "aggressive", "reason": "market push"},
        competitor_dna={"culture": "engineering-led"},
        pages_analyzed=["home", "pricing"]
    )

def test_full_analysis_conversion(base_analysis):
    docs = MemoryDocumentFactory.from_competitor_analysis(
        base_analysis,
        organization_id=uuid4(),
        run_id="run_1",
        analyzed_at=datetime.now(timezone.utc)
    )
    # 1 executive briefing, 1 structured summaries, 1 strategic, 1 dna = 4
    assert len(docs) == 4
    assert docs[0].chunk_type == ChunkType.EXECUTIVE_BRIEFING
    assert docs[0].text == "Acme is doing well."
    
    assert docs[1].chunk_type == ChunkType.STRUCTURED_SUMMARIES
    assert "Core Offering:\nAI memory" in docs[1].text
    
    assert docs[2].chunk_type == ChunkType.STRUCTURED_SUMMARIES
    assert "Tone:\naggressive" in docs[2].text
    
    assert docs[3].chunk_type == ChunkType.STRUCTURED_SUMMARIES
    assert "Culture:\nengineering-led" in docs[3].text

def test_missing_dna_and_interpretation(base_analysis):
    base_analysis.strategic_interpretation = {}
    base_analysis.competitor_dna = {}
    
    docs = MemoryDocumentFactory.from_competitor_analysis(
        base_analysis,
        organization_id=uuid4(),
        run_id="run_1",
        analyzed_at=datetime.now(timezone.utc)
    )
    
    assert len(docs) == 2 # Only executive briefing and structured summaries

def test_empty_strings(base_analysis):
    base_analysis.analyst_note = "   "
    docs = MemoryDocumentFactory.from_competitor_analysis(
        base_analysis,
        organization_id=uuid4(),
        run_id="run_1",
        analyzed_at=datetime.now(timezone.utc)
    )
    
    # Executive briefing should be skipped
    assert len(docs) == 3
    assert all(d.chunk_type != ChunkType.EXECUTIVE_BRIEFING for d in docs)

def test_comparison_result_conversion():
    comp = ComparisonResult(
        market_leader="Acme",
        market_leader_reason="They are the biggest.",
        fastest_mover="StartupX",
        fastest_mover_reason="Growing fast.",
        pivot_detected=None,
        smb_to_enterprise_shift=[],
        ai_emphasis_ranking=[],
        messaging_gaps="No one talks about security.",
        threat_ranking=["Acme", "StartupX"],
        threat_ranking_reasons=["Big", "Fast"],
        executive_briefing="This is a summary."
    )
    
    docs = MemoryDocumentFactory.from_comparison_result(
        comp,
        organization_id=uuid4(),
        run_id="run_1",
        analyzed_at=datetime.now(timezone.utc)
    )
    
    # 1 exec, 1 gaps, 1 threat, 1 leader, 1 fastest mover = 5
    assert len(docs) == 5
    
    assert docs[0].chunk_type == ChunkType.EXECUTIVE_BRIEFING
    assert docs[1].chunk_type == ChunkType.COMPARISON_SUMMARY
    assert "Messaging Gaps" in docs[1].text

def test_deterministic_output(base_analysis):
    docs1 = MemoryDocumentFactory.from_competitor_analysis(
        base_analysis,
        organization_id=uuid4(),
        run_id="run_1",
        analyzed_at=datetime.now(timezone.utc)
    )
    docs2 = MemoryDocumentFactory.from_competitor_analysis(
        base_analysis,
        organization_id=uuid4(),
        run_id="run_1",
        analyzed_at=datetime.now(timezone.utc)
    )
    
    for d1, d2 in zip(docs1, docs2):
        assert d1.text == d2.text
