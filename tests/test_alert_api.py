from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from backend.main import app

client = TestClient(app)


class MockAlert:
    def __init__(self):
        self.company_name = "Cursor"
        self.severity = "LOW"
        self.reasons = ["keyword change"]
        self.created_at = None


@patch("backend.main.DatabaseService")
def test_get_alerts(mock_db_service):

    mock_instance = mock_db_service.return_value

    mock_instance.get_alerts = AsyncMock(
        return_value=[MockAlert()]
    )

    response = client.get("/api/alerts")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert data[0]["company_name"] == "Cursor"


@patch("backend.main.DatabaseService")
def test_get_latest_alerts(mock_db_service):

    mock_instance = mock_db_service.return_value

    alert = MockAlert()
    alert.created_at = datetime.utcnow()

    mock_instance.get_latest_alerts = AsyncMock(
        return_value=[alert]
    )

    response = client.get("/api/alerts/latest")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert data[0]["company_name"] == "Cursor"

    assert data[0]["severity"] == "LOW"


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
