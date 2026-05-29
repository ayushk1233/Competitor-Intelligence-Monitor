from backend.eval.scorer import semantic_similarity

def test_semantic_similarity_overlap():
    expected = {"developer platform", "artificial intelligence", "engineering tools"}
    actual = {"developer infrastructure", "AI", "tools for engineers"}
    
    score = semantic_similarity(expected, actual, is_recall=False)
    
    # Should be high due to semantic similarity despite literal mismatch
    assert score > 0.45

def test_semantic_similarity_recall():
    expected = {"large organizations", "global scale"}
    actual = {"enterprise", "worldwide operations", "startups"}
    
    score = semantic_similarity(expected, actual, is_recall=True)
    
    # Should be high since all expected have a match in actual
    assert score > 0.45
