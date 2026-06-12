from backend.drift.drift_models import DriftReport
from backend.models.schemas import CompetitorAnalysis


def compare_scores(
    old_score: float,
    new_score: float
):
    delta = round(
        new_score - old_score,
        3
    )

    return {
        "old_score": old_score,
        "new_score": new_score,
        "delta": delta,
        "improved": delta > 0,
        "regressed": delta < 0,
    }


def compare_analysis(
    old_analysis: CompetitorAnalysis,
    new_analysis: CompetitorAnalysis,
) -> DriftReport:

    old_keywords = {
        k.lower().strip()
        for k in old_analysis.strategic_keywords
    }

    new_keywords = {
        k.lower().strip()
        for k in new_analysis.strategic_keywords
    }

    added_keywords = sorted(
        list(new_keywords - old_keywords)
    )

    removed_keywords = sorted(
        list(old_keywords - new_keywords)
    )

    return DriftReport(
        company_name=new_analysis.name,

        old_momentum=old_analysis.momentum_score,
        new_momentum=new_analysis.momentum_score,

        momentum_delta=(
            new_analysis.momentum_score
            - old_analysis.momentum_score
        ),

        added_keywords=added_keywords,
        removed_keywords=removed_keywords,

        tone_changed=(
            old_analysis.messaging_tone.lower().strip()
            !=
            new_analysis.messaging_tone.lower().strip()
        ),
    )