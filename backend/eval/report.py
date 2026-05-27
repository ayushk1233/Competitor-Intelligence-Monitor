from typing import List

from backend.eval.models import EvalResult


def generate_report(results: List[EvalResult]) -> str:

    lines = []

    lines.append("=" * 60)
    lines.append("EVALUATION REPORT")
    lines.append("=" * 60)
    lines.append("")

    total_score = 0.0

    for result in results:

        total_score += result.overall_score

        lines.append(f"Company: {result.company_name}")

        lines.append(
            f"Tone Match: "
            f"{'PASS' if result.tone_match else 'FAIL'}"
        )

        lines.append(
            f"Momentum Range: "
            f"{'PASS' if result.momentum_in_range else 'FAIL'}"
        )

        lines.append(
            f"Keyword Overlap: "
            f"{result.keyword_overlap_score}"
        )

        lines.append(
            f"ICP Recall: "
            f"{result.icp_recall_score}"
        )

        lines.append(
            f"Overall Score: "
            f"{result.overall_score}"
        )

        lines.append(
            f"Actual Tone: "
            f"{result.actual_tone}"
        )

        lines.append(
            f"Actual Momentum: "
            f"{result.actual_momentum}"
        )

        if result.errors:
            lines.append(
                f"Errors: {', '.join(result.errors)}"
            )

        lines.append("-" * 60)

    average_score = (
        total_score / len(results)
        if results
        else 0.0
    )

    lines.append("")
    lines.append("=" * 60)
    lines.append(
        f"OVERALL SUITE SCORE: "
        f"{round(average_score, 3)}"
    )
    lines.append("=" * 60)

    return "\n".join(lines)