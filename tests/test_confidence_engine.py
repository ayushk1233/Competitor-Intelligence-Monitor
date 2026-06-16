from backend.reasoning.confidence_engine import compute_confidence

def test_confidence_scaling():
    # 1 piece of evidence, 1 source
    conf1 = compute_confidence("pricing_signals", ["Enterprise plans available"], ["homepage"])
    # 2 pieces of evidence, 2 sources
    conf2 = compute_confidence("pricing_signals", ["Enterprise plans available", "Contact sales for enterprise"], ["homepage", "pricing_page"])
    
    assert conf2["confidence"] > conf1["confidence"]
    assert conf2["evidence_count"] == 2
    assert conf2["source_count"] == 2
    
def test_confidence_source_diversity():
    # 3 pieces, 1 source
    conf1 = compute_confidence("strategic_keywords", ["A", "B", "C"], ["homepage"])
    # 3 pieces, 3 sources
    conf2 = compute_confidence("strategic_keywords", ["A", "B", "C"], ["homepage", "blog", "news"])
    
    assert conf2["confidence"] > conf1["confidence"]

def test_confidence_deterministic():
    conf1 = compute_confidence("pricing_signals", ["A", "B"], ["homepage", "blog"])
    conf2 = compute_confidence("pricing_signals", ["A", "B"], ["homepage", "blog"])
    assert conf1["confidence"] == conf2["confidence"]
