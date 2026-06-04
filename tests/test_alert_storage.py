from backend.drift.alert_models import AlertRecord
from backend.drift.alert_storage import save_alert


def test_alert_storage():

    alert = AlertRecord(
        company_name="Cursor",
        severity="HIGH",
        reasons=["Momentum changed by 2"],
        created_at="2026-06-04 12:00:00",
    )

    path = save_alert(alert)

    assert path.exists()
