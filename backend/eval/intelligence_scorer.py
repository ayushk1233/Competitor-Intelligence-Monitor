from backend.models.schemas import CompetitorAnalysis

NEGATIVE_PATTERNS = [
    "no public evidence found",
    "not detected",
    "insufficient information available",
    "none",
    "n/a",
    "analysis failed",
]


def _has_real_content(value) -> bool:
    if not value:
        return False
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if not cleaned:
            return False
        if any(p in cleaned for p in NEGATIVE_PATTERNS):
            return False
        return True
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return bool(value)


def _coverage_score(analysis: CompetitorAnalysis) -> float:
    fields = [
        ("core_offering", analysis.core_offering),
        ("icp", analysis.icp),
        ("messaging_tone", analysis.messaging_tone),
        ("pricing_signals", analysis.pricing_signals),
        ("hiring_signals", analysis.hiring_signals),
        ("recent_launches", analysis.recent_launches),
        ("strategic_keywords", analysis.strategic_keywords),
        ("growth_signals", analysis.growth_signals),
        ("risk_flags", analysis.risk_flags),
        ("analyst_note", analysis.analyst_note),
    ]
    filled = sum(1 for _, v in fields if _has_real_content(v))
    return filled / len(fields) if fields else 0.0


def _evidence_quality_score(analysis: CompetitorAnalysis) -> float:
    evidence_fields = [
        getattr(analysis, "core_offering_evidence", []),
        getattr(analysis, "pricing_evidence", []),
        getattr(analysis, "hiring_evidence", []),
        getattr(analysis, "keywords_evidence", []),
        getattr(analysis, "tone_evidence", []),
        getattr(analysis, "icp_evidence", []),
        getattr(analysis, "momentum_evidence", []),
    ]
    with_evidence = sum(1 for ev in evidence_fields if isinstance(ev, list) and len(ev) > 0)
    return with_evidence / len(evidence_fields) if evidence_fields else 0.0


def score_company_understanding(expected_concepts: list[str], analysis: CompetitorAnalysis) -> float:
    """
    Measures if the core identity of the company is understood.
    Combines: semantic recall (40%), field coverage + completeness (40%), evidence quality (20%).
    """
    if not expected_concepts:
        return 1.0

    # Dimension 1: Semantic recall of expected concepts (40%)
    actual_texts = set(analysis.strategic_keywords)
    if _has_real_content(analysis.core_offering):
        actual_texts.add(analysis.core_offering)
    if _has_real_content(analysis.analyst_note):
        actual_texts.add(analysis.analyst_note)
    if _has_real_content(analysis.icp):
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
                if isinstance(v, str) and _has_real_content(v):
                    actual_texts.add(v)

    from backend.eval.scorer import semantic_similarity
    recall_score = semantic_similarity(set(expected_concepts), actual_texts, is_recall=True)

    # Dimension 2: Field coverage and completeness (40%)
    coverage = _coverage_score(analysis)

    # Dimension 3: Evidence quality (20%)
    evidence = _evidence_quality_score(analysis)

    final = recall_score * 0.40 + coverage * 0.40 + evidence * 0.20
    return min(1.0, max(0.0, final))

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
