import json
from pathlib import Path

from backend.drift.alert_models import AlertRecord


ALERT_RUNS_DIR = Path("alert_runs")

ALERT_RUNS_DIR.mkdir(exist_ok=True)


def save_alert(
    alert: AlertRecord,
):

    filename = (
        f"{alert.company_name.lower()}_"
        f"{alert.created_at.replace(':', '-')}.json"
    )

    filepath = ALERT_RUNS_DIR / filename

    with open(filepath, "w") as f:
        json.dump(
            alert.model_dump(),
            f,
            indent=2,
        )

    return filepath
