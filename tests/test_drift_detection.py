from backend.models.schemas import CompetitorAnalysis
from backend.drift.diff_service import compare_analysis


def make_analysis(
    name,
    tone,
    momentum,
    keywords,
):
    return CompetitorAnalysis(
        name=name,
        domain="example.com",

        core_offering="platform",
        icp="enterprise",

        messaging_tone=tone,
        pricing_signals="",
        hiring_signals="",

        recent_launches=[],
        strategic_keywords=keywords,
        growth_signals=[],
        risk_flags=[],

        momentum_score=momentum,
        analyst_note="",

        pages_analyzed=[],
        analysis_success=True,
    )


def test_business_drift_detection():

    old = make_analysis(
        name="Cursor",
        tone="technical",
        momentum=6,
        keywords=[
            "autocomplete",
            "developer tools",
        ],
    )

    new = make_analysis(
        name="Cursor",
        tone="technical",
        momentum=8,
        keywords=[
            "developer tools",
            "agents",
            "reasoning",
        ],
    )

    report = compare_analysis(
        old,
        new,
    )

    assert report.momentum_delta == 2

    assert "agents" in report.added_keywords
    assert "reasoning" in report.added_keywords

    assert "autocomplete" in report.removed_keywords

    assert report.tone_changed is False
