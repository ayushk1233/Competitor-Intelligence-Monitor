from backend.models.schemas import CompetitorAnalysis

def score_company_understanding(expected_concepts: list[str], analysis: CompetitorAnalysis) -> float:
    """
    Measures if the core identity of the company is understood.
    Uses semantic similarity to check recall of expected concepts in the analysis outputs.
    """
    if not expected_concepts:
        return 1.0

    actual_texts = set(analysis.strategic_keywords)
    if analysis.core_offering:
        actual_texts.add(analysis.core_offering)
    if analysis.analyst_note:
        actual_texts.add(analysis.analyst_note)
    if analysis.icp:
        actual_texts.add(analysis.icp)
        
    if getattr(analysis, "competitor_dna", None):
        dna = analysis.competitor_dna
        if isinstance(dna, dict):
            if dna.get("archetype"):
                actual_texts.add(dna.get("archetype"))
            if dna.get("growth_model"):
                actual_texts.add(dna.get("growth_model"))
            if dna.get("strategic_risk"):
                actual_texts.add(dna.get("strategic_risk"))
            if dna.get("primary_moat"):
                actual_texts.add(dna.get("primary_moat"))
            if dna.get("expansion_vector"):
                actual_texts.add(dna.get("expansion_vector"))
                
    if getattr(analysis, "strategic_interpretation", None):
        interp = analysis.strategic_interpretation
        if isinstance(interp, dict):
            for v in interp.values():
                if isinstance(v, str) and v:
                    actual_texts.add(v)

    from backend.eval.scorer import semantic_similarity
    return semantic_similarity(set(expected_concepts), actual_texts, is_recall=True)

def score_strategic_accuracy(
    expected_pass: list[str], expected_fail: list[str], analysis: CompetitorAnalysis
) -> float:
    """
    Measures if the generated conclusions are strategically accurate.
    Pass conditions increase the score, fail conditions decrease it.
    """
    if not expected_pass and not expected_fail:
        return 1.0

    actual_texts = set()
    if analysis.core_offering:
        actual_texts.add(analysis.core_offering)
    if analysis.analyst_note:
        actual_texts.add(analysis.analyst_note)

    if not actual_texts:
        return 0.0

    from backend.eval.scorer import semantic_similarity

    pass_score = 1.0
    if expected_pass:
        pass_score = semantic_similarity(set(expected_pass), actual_texts, is_recall=True)

    fail_penalty = 0.0
    if expected_fail:
        # Check if fail concepts are recalled in the actual texts
        fail_recall = semantic_similarity(set(expected_fail), actual_texts, is_recall=True)
        # If fail concepts are found with high similarity, penalty is high
        fail_penalty = fail_recall

    final_score = max(0.0, pass_score - fail_penalty)
    return min(1.0, final_score)
