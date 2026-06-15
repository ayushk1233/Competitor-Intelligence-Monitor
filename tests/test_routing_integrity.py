import pytest
from backend.retrieval.evidence_router import route_evidence

def test_routing_integrity():
    chunks = [
        "Our pricing is meant for startups and businesses.",
        "We have scalable infrastructure and APIs.",
        "We launched a new product today."
    ]
    
    routed = route_evidence(chunks)
    
    # Ensure visibility arrays exist
    assert "tone" in routed
    assert "icp" in routed
    
    # Ensure they received the correct data
    # "startups and businesses" -> ICP
    assert any("startups" in c for c in routed["icp"])
    
    # "infrastructure and APIs" -> Tone
    assert any("infrastructure" in c for c in routed["tone"])
