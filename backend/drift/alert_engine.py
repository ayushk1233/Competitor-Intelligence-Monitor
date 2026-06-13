from backend.drift.drift_models import DriftReport


def _build_headline(company: str, severity: str, momentum_delta: float, tone_changed: bool) -> str:
    if severity == "HIGH" and abs(momentum_delta) >= 3:
        return f"{company} momentum shifted significantly"
    if tone_changed:
        return f"{company} messaging tone changed"
    if abs(momentum_delta) >= 2:
        return f"{company} momentum score shifted"
    return f"{company} updated"


def generate_alert(
    report: DriftReport,
):

    reasons = []
    evidence = []

    severity = "LOW"

    if abs(report.momentum_delta) >= 2:
        severity = "HIGH"
        reasons.append(
            f"Momentum changed by {report.momentum_delta}"
        )
        evidence.append(f"Momentum delta: {report.momentum_delta}")

    if report.tone_changed:
        if severity != "HIGH":
            severity = "MEDIUM"
        reasons.append("Messaging tone changed")
        evidence.append("Tone shift detected")

    if len(report.added_keywords) >= 2:
        if severity == "LOW":
            severity = "MEDIUM"
        reasons.append(f"{len(report.added_keywords)} new strategic keywords")
        evidence.append(f"Keywords added: {', '.join(report.added_keywords[:5])}")

    headline = _build_headline(report.company_name, severity, report.momentum_delta, report.tone_changed)

    impact = None
    action = None
    if severity == "HIGH":
        impact = "May affect competitive positioning — review and adjust strategy"
        action = "Review latest analysis and determine response"
    elif severity == "MEDIUM":
        impact = "Notable shift detected — monitor closely"
        action = "Review details in next monitoring cycle"

    return {
        "company_name": report.company_name,
        "severity": severity,
        "headline": headline,
        "summary": "; ".join(reasons) if reasons else "Minor changes detected",
        "reasons": reasons,
        "evidence": evidence,
        "confidence": 90,
        "business_impact": impact,
        "recommended_action": action,
    }