from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from backend.main import app
from backend.auth.dependencies import get_current_user

client = TestClient(app)


mock_user = MagicMock()
mock_user.id = "test-user-id"


def override_get_current_user():
    return mock_user


class MockHistoryRecord:

    def __init__(self):
        self.created_at = datetime.utcnow()
        self.momentum_score = 7
        self.messaging_tone = "technical"


class MockRecord:

    def __init__(self, keywords):

        self.full_analysis = {
            "name": "Cursor",
            "domain": "cursor.com",

            "core_offering": "AI coding",
            "icp": "developers",
            "messaging_tone": "technical",
            "pricing_signals": "",
            "hiring_signals": "",

            "recent_launches": [],
            "strategic_keywords": keywords,
            "growth_signals": [],
            "risk_flags": [],

            "momentum_score": 7,
            "analyst_note": "",

            "icp_keywords": [],
            "icp_evidence": [],
            "tone_evidence": [],
            "momentum_evidence": [],
            "agent_outputs": {},

            "pages_analyzed": [],
            "analysis_success": True,
            "error": None,
        }


@patch("backend.main.DatabaseService")
def test_get_latest_competitor(mock_db_service):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_instance = mock_db_service.return_value

    mock_instance.get_user_competitor_names = AsyncMock(return_value=["Cursor"])
    mock_instance.get_latest_analysis = AsyncMock(
        return_value=MockRecord([])
    )

    response = client.get(
        "/api/competitors/Cursor/latest"
    )

    assert response.status_code == 200

    app.dependency_overrides.pop(get_current_user, None)

    data = response.json()

    assert data["name"] == "Cursor"

    assert data["momentum_score"] == 7


@patch("backend.main.DatabaseService")
def test_get_history(mock_db_service):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_instance = mock_db_service.return_value

    mock_instance.get_user_competitor_names = AsyncMock(return_value=["Cursor"])
    mock_instance.get_competitor_history = AsyncMock(
        return_value=[MockHistoryRecord()]
    )

    response = client.get(
        "/api/competitors/Cursor/history"
    )

    assert response.status_code == 200

    app.dependency_overrides.pop(get_current_user, None)

    data = response.json()

    assert isinstance(data, list)

    assert data[0]["momentum_score"] == 7

    assert data[0]["messaging_tone"] == "technical"


@patch("backend.main.DatabaseService")
def test_get_drift(mock_db_service):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock_instance = mock_db_service.return_value

    old_record = MockRecord(
        ["enterprise"]
    )

    new_record = MockRecord(
        ["enterprise", "ai"]
    )

    mock_instance.get_user_competitor_names = AsyncMock(return_value=["Cursor"])
    mock_instance.get_latest_two_analyses = AsyncMock(
        return_value=[
            new_record,
            old_record,
        ]
    )

    response = client.get(
        "/api/competitors/Cursor/drift"
    )

    assert response.status_code == 200

    app.dependency_overrides.pop(get_current_user, None)

    data = response.json()

    assert "old_momentum" in data

    assert "new_momentum" in data

    assert "momentum_delta" in data

    assert "added_keywords" in data
