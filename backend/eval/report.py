from typing import List

from backend.eval.models import EvalResult


def generate_report(
    results: List[EvalResult],
    status: str,
    llm_model: str,
    temperature: float,
    analysis_prompt_version: str,
    comparison_prompt_version: str,
    runtime_seconds: float
) -> str:

    lines = []

    lines.append("=" * 60)
    lines.append("EVALUATION REPORT")
    lines.append("=" * 60)
    lines.append("")

    lines.append(f"Model: {llm_model}")
    lines.append(f"Evaluation Status: {status}")
    lines.append(f"Temperature: {temperature}")
    lines.append(
        f"Analysis Prompt: "
        f"{analysis_prompt_version}"
    )
    lines.append(
        f"Comparison Prompt: "
        f"{comparison_prompt_version}"
    )
    lines.append(
        f"Runtime: "
        f"{runtime_seconds}s"
    )
    lines.append("")

    total_score = 0.0
    total_extraction = 0.0
    total_intelligence = 0.0

    for result in results:

        total_score += result.overall_score
        
        tone_score = 1.0 if result.tone_match else 0.0
        momentum_score = 1.0 if result.momentum_in_range else 0.0
        
        extr = (tone_score * 0.10) + (momentum_score * 0.10) + (result.keyword_overlap_score * 0.15) + (result.icp_recall_score * 0.10)
        # Normalize to 1.0
        extr_normalized = extr / 0.45
        total_extraction += extr_normalized
        
        intel = (result.company_understanding_score * 0.20) + (result.strategic_accuracy_score * 0.20) + (result.confidence_calibration_score * 0.05) + (result.false_negative_score * 0.05) + (result.evidence_quality_score * 0.05)
        # Normalize to 1.0
        intel_normalized = intel / 0.55
        total_intelligence += intel_normalized

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
            f"Extraction Quality: "
            f"{round(extr_normalized * 100, 1)}%"
        )
        
        lines.append(
            f"Intelligence Quality: "
            f"{round(intel_normalized * 100, 1)}%"
        )

        lines.append(
            f"Overall Score: "
            f"{round(result.overall_score * 100, 1)}%"
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

    count = len(results) if results else 1
    average_score = total_score / count
    avg_extr = total_extraction / count
    avg_intel = total_intelligence / count

    lines.append("")
    lines.append("=" * 60)
    if not results:
        lines.append("OVERALL SUITE SCORE: N/A")
        lines.append("(No successful evaluations)")
    else:
        lines.append(f"EXTRACTION QUALITY SCORE: {round(avg_extr * 100, 1)}%")
        lines.append(f"INTELLIGENCE QUALITY SCORE: {round(avg_intel * 100, 1)}%")
        lines.append(f"OVERALL SUITE SCORE: {round(average_score * 100, 1)}%")
    lines.append("=" * 60)

    return "\n".join(lines)