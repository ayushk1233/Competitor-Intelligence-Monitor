from backend.models.schemas import CompetitorAnalysis

from backend.eval.models import (
    EvalExpectation,
    EvalResult
)


def jaccard_similarity(expected: set, actual: set) -> float:
    if not expected or not actual:
        return 0.0

    intersection = len(expected & actual)
    union = len(expected | actual)

    return intersection / union


def keyword_recall(expected: set, actual: set) -> float:
    if not expected:
        return 0.0

    intersection = len(expected & actual)

    return intersection / len(expected)


def normalize_keywords(items):

    normalized = set()

    for item in items:

        item = item.lower().strip()

        item = item.replace("-", " ")

        if item.endswith("s"):
            item = item[:-1]

        normalized.add(item)

    return normalized


def score_analysis(
    analysis: CompetitorAnalysis,
    expectation: EvalExpectation
) -> EvalResult:

    errors = []

    # ---------------------------------------
    # Tone Match
    # ---------------------------------------

    actual_tone = analysis.messaging_tone.lower().strip()
    expected_tone = expectation.expected_tone.lower().strip()

    tone_match = actual_tone == expected_tone

    # ---------------------------------------
    # Momentum Match
    # ---------------------------------------

    actual_momentum = analysis.momentum_score

    momentum_in_range = (
        expectation.momentum_min
        <= actual_momentum
        <= expectation.momentum_max
    )

    # ---------------------------------------
    # Keyword Overlap
    # ---------------------------------------

    expected_keywords = normalize_keywords(
        expectation.expected_keywords
    )

    actual_keywords = normalize_keywords(
        analysis.strategic_keywords
    )

    keyword_overlap_score = jaccard_similarity(
        expected_keywords,
        actual_keywords
    )

    # ---------------------------------------
    # ICP Recall
    # ---------------------------------------

    expected_icp = normalize_keywords(
        expectation.expected_icp_keywords
    )

    actual_icp_text = analysis.icp.lower()

    actual_icp_keywords = set(actual_icp_text.split())

    icp_recall_score = keyword_recall(
        expected_icp,
        actual_icp_keywords
    )

    # ---------------------------------------
    # Weighted Final Score
    # ---------------------------------------

    tone_score = 1.0 if tone_match else 0.0
    momentum_score = 1.0 if momentum_in_range else 0.0

    overall_score = (
        (tone_score * 0.25)
        + (momentum_score * 0.25)
        + (keyword_overlap_score * 0.30)
        + (icp_recall_score * 0.20)
    )

    # ---------------------------------------
    # Validation
    # ---------------------------------------

    if not analysis.analysis_success:
        errors.append(
            analysis.error or "Analysis failed"
        )

    return EvalResult(
        company_name=analysis.name,

        tone_match=tone_match,
        momentum_in_range=momentum_in_range,

        keyword_overlap_score=round(
            keyword_overlap_score,
            3
        ),

        icp_recall_score=round(
            icp_recall_score,
            3
        ),

        overall_score=round(
            overall_score,
            3
        ),

        actual_tone=analysis.messaging_tone,
        actual_momentum=analysis.momentum_score,

        errors=errors if errors else None
    )