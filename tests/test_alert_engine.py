from backend.drift.alert_engine import generate_alert
from backend.drift.drift_models import DriftReport


def test_high_severity_alert():

    report = DriftReport(
        company_name="Cursor",

        old_momentum=6,
        new_momentum=8,

        momentum_delta=2,

        added_keywords=[
            "agents",
            "reasoning",
        ],

        removed_keywords=[],

        tone_changed=False,
    )

    alert = generate_alert(report)

    assert alert["severity"] == "HIGH"