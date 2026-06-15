import pytest
from backend.retrieval.evidence_router import route_evidence

def test_route_evidence():
    chunks = [
        "We just launched a new feature today.",
        "Our pricing is $10 per month.",
        "We are hiring engineers.",
        "Our customers are enterprise developers.",
        "We partnered with Google."
    ]
    
    routed = route_evidence(chunks)
    
    # Check that keys exist
    assert "tone" in routed
    assert "icp" in routed
    
    # "Our customers are enterprise developers." -> tone
    assert any("developers" in chunk for chunk in routed["tone"])
    
    # "Our customers are enterprise developers." -> icp
    assert any("developers" in chunk for chunk in routed["icp"])

