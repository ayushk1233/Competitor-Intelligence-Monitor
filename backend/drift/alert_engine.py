from backend.drift.drift_models import DriftReport


def generate_alert(
    report: DriftReport,
):

    reasons = []

    severity = "LOW"

    if abs(report.momentum_delta) >= 2:
        severity = "HIGH"

        reasons.append(
            f"Momentum changed by "
            f"{report.momentum_delta}"
        )

    if report.tone_changed:

        if severity != "HIGH":
            severity = "MEDIUM"

        reasons.append(
            "Messaging tone changed"
        )

    if len(report.added_keywords) >= 2:

        if severity == "LOW":
            severity = "MEDIUM"

        reasons.append(
            f"{len(report.added_keywords)} "
            f"new strategic keywords added"
        )

    return {
        "company_name": report.company_name,
        "severity": severity,
        "reasons": reasons,
    }