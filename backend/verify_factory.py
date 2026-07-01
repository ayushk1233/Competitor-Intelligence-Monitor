from uuid import uuid4
from datetime import datetime, timezone
from backend.models.schemas import CompetitorAnalysis
from backend.memory.factory import MemoryDocumentFactory

def main():
    analysis = CompetitorAnalysis(
        name="Acme Corp",
        domain="acme.com",
        core_offering="AI Memory Infrastructure",
        icp="Enterprise Data Teams",
        messaging_tone="technical",
        pricing_signals="Enterprise tiers only",
        hiring_signals="Hiring AI engineers",
        recent_launches=["Vector Search v2"],
        strategic_keywords=["AI", "Memory", "RAG"],
        growth_signals=["$50M Series B"],
        risk_flags=["High churn on SMB"],
        momentum_score=9,
        analyst_note="Acme is leading the pack in memory tech.",
        strategic_interpretation={"tone": "aggressive", "reason": "recent funding"},
        competitor_dna={"culture": "engineering-first"},
        pages_analyzed=["home", "pricing"]
    )
    
    docs = MemoryDocumentFactory.from_competitor_analysis(
        analysis,
        organization_id=uuid4(),
        run_id="run_123",
        analyzed_at=datetime.now(timezone.utc)
    )
    
    print(f"Number of generated documents: {len(docs)}")
    if len(docs) >= 2:
        print(f"docs[0].chunk_type: {docs[0].chunk_type.name}")
        print("\ndocs[1].text:\n")
        print(docs[1].text)
        
    print("\n\nTesting with missing DNA...")
    analysis.competitor_dna = {}
    docs_no_dna = MemoryDocumentFactory.from_competitor_analysis(
        analysis,
        organization_id=uuid4(),
        run_id="run_123",
        analyzed_at=datetime.now(timezone.utc)
    )
    print(f"Number of generated documents (missing DNA): {len(docs_no_dna)}")

if __name__ == "__main__":
    main()
