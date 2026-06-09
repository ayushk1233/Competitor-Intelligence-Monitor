from backend.models.schemas import CompetitorAnalysis

from backend.eval.models import (
    EvalExpectation,
    EvalResult
)

from unittest.mock import MagicMock

try:
    from sentence_transformers import SentenceTransformer, util
    _model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Warning: Could not load sentence-transformers: {e}")

    _model = None
    util = MagicMock()

def semantic_similarity(expected: set, actual: set, is_recall: bool = False) -> float:
    if not expected or not actual:
        return 0.0

    if _model is None or util is None:
        if is_recall:
            return len(expected & actual) / len(expected)
        else:
            return len(expected & actual) / len(expected | actual)

    expected_list = list(expected)
    actual_list = list(actual)
    
    emb_expected = _model.encode(expected_list, convert_to_tensor=True)
    emb_actual = _model.encode(actual_list, convert_to_tensor=True)
    
    cosine_scores = util.cos_sim(emb_expected, emb_actual)
    
    max_scores_expected, _ = cosine_scores.max(dim=1)
    recall_score = max_scores_expected.mean().item()
    
    if is_recall:
        return max(0.0, recall_score)
        
    max_scores_actual, _ = cosine_scores.max(dim=0)
    precision_score = max_scores_actual.mean().item()
    
    if recall_score + precision_score == 0:
        return 0.0
        
    overlap = 2 * (precision_score * recall_score) / (precision_score + recall_score)
    return max(0.0, overlap)


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

    keyword_overlap_score = semantic_similarity(
        expected_keywords,
        actual_keywords,
        is_recall=False
    )

    # ---------------------------------------
    # ICP Recall
    # ---------------------------------------

    expected_icp = normalize_keywords(
        expectation.expected_icp_keywords
    )

    actual_icp_keywords = normalize_keywords(
        analysis.icp_keywords
    )

    icp_recall_score = semantic_similarity(
        expected_icp,
        actual_icp_keywords,
        is_recall=True
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