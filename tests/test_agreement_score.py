from backend.reasoning.agreement_score import compute_agreement_score

def test_agreement_high():
    # Evidence is consistent
    evidence = [
        "Enterprise platform for businesses",
        "Enterprise plans available",
        "Enterprise adoption is growing"
    ]
    score = compute_agreement_score(evidence)
    assert score > 0.6

def test_agreement_low():
    # Evidence conflicts or is disjoint
    evidence = [
        "SMB tool for startups",
        "Enterprise platform",
        "Consumer application"
    ]
    score = compute_agreement_score(evidence)
    # Should be significantly lower than the high agreement case
    assert score < 0.5

def test_agreement_single():
    assert compute_agreement_score(["One piece of evidence"]) == 1.0
