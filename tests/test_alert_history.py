from backend.drift.history import (
    load_all_alerts,
)


def test_alert_history_loads():

    alerts = load_all_alerts()

    assert isinstance(
        alerts,
        list,
    )
