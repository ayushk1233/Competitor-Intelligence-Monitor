from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from backend.main import app
from backend.auth.dependencies import get_current_user

client = TestClient(app)


class MockAlert:
    def __init__(self):
        self.id = 1
        self.company_name = "Cursor"
        self.severity = "LOW"
        self.headline = "Keyword change detected"
        self.summary = None
        self.evidence = []
        self.confidence = 90
        self.business_impact = None
        self.recommended_action = None
        self.status = "new"
        self.reasons = ["keyword change"]
        self.created_at = None


mock_user = MagicMock()
mock_user.id = "test-user-id"


def override_get_current_user():
    return mock_user


@patch("backend.main.DatabaseService")
def test_get_alerts(mock_db_service):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_instance = mock_db_service.return_value

    mock_instance.get_alerts_for_user = AsyncMock(
        return_value=[MockAlert()]
    )

    response = client.get("/api/alerts")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert data[0]["company_name"] == "Cursor"

    app.dependency_overrides.pop(get_current_user, None)


@patch("backend.main.DatabaseService")
def test_get_latest_alerts(mock_db_service):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_instance = mock_db_service.return_value

    alert = MockAlert()
    alert.created_at = datetime.utcnow()

    mock_instance.get_alerts_for_user = AsyncMock(
        return_value=[alert]
    )

    response = client.get("/api/alerts/latest")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert data[0]["company_name"] == "Cursor"

    assert data[0]["severity"] == "LOW"

    app.dependency_overrides.pop(get_current_user, None)


@patch("backend.main.DatabaseService")
def test_get_company_alerts(mock_db_service):
    mock_instance = mock_db_service.return_value

    alert = MockAlert()
    alert.created_at = datetime.utcnow()

    mock_instance.get_alerts_for_company = AsyncMock(
        return_value=[alert]
    )

    response = client.get("/api/alerts/Cursor")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert data[0]["company_name"] == "Cursor"
