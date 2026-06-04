import json
from pathlib import Path

ALERT_RUNS_DIR = Path("alert_runs")


def load_all_alerts():

    alerts = []

    if not ALERT_RUNS_DIR.exists():
        return alerts

    for file in sorted(
        ALERT_RUNS_DIR.glob("*.json")
    ):

        with open(file) as f:
            alerts.append(
                json.load(f)
            )

    return alerts


def load_company_alerts(
    company_name: str
):

    company_name = (
        company_name.lower().strip()
    )

    return [
        alert
        for alert in load_all_alerts()
        if alert["company_name"].lower()
        == company_name
    ]
