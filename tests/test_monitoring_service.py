import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.drift.monitoring_service import MonitoringService
from backend.drift.drift_models import DriftReport


@pytest.mark.asyncio
async def test_detect_drift_returns_report():
    mock_db = AsyncMock()
    
    mock_db.get_active_suppression.return_value = None

    mock_history_0 = MagicMock()
    mock_history_0.full_analysis = {
        "name": "Cursor",
        "domain": "cursor.com",
        "core_offering": "editor",
        "icp": "devs",
        "messaging_tone": "technical",
        "pricing_signals": "",
        "hiring_signals": "",
        "recent_launches": [],
        "strategic_keywords": ["ai", "editor"],
        "growth_signals": [],
        "risk_flags": [],
        "momentum_score": 8,
        "analyst_note": "",
        "pages_analyzed": ["cursor.com"],
        "analysis_success": True
    }

    mock_history_1 = MagicMock()
    mock_history_1.full_analysis = {
        "name": "Cursor",
        "domain": "cursor.com",
        "core_offering": "editor",
        "icp": "devs",
        "messaging_tone": "technical",
        "pricing_signals": "",
        "hiring_signals": "",
        "recent_launches": [],
        "strategic_keywords": ["editor"],
        "growth_signals": [],
        "risk_flags": [],
        "momentum_score": 5,
        "analyst_note": "",
        "pages_analyzed": ["cursor.com"],
        "analysis_success": True
    }

    mock_db.get_competitor_history.return_value = [mock_history_0, mock_history_1]

    monitoring = MonitoringService(mock_db)
    
    result = await monitoring.detect_drift("Cursor")

    assert "drift_report" in result
    assert "alert" in result

    assert (
        result["drift_report"]
        .momentum_delta
        == 3
    )

    assert (
        result["alert"]
        .severity
        == "HIGH"
    )

@pytest.mark.asyncio
async def test_detect_drift_suppressed():

    mock_db = AsyncMock()

    mock_db.get_active_suppression.return_value = object()

    mock_history_0 = MagicMock()
    mock_history_0.full_analysis = {
        "name": "Cursor",
        "domain": "cursor.com",
        "core_offering": "editor",
        "icp": "devs",
        "messaging_tone": "technical",
        "pricing_signals": "",
        "hiring_signals": "",
        "recent_launches": [],
        "strategic_keywords": ["ai", "editor"],
        "growth_signals": [],
        "risk_flags": [],
        "momentum_score": 8,
        "analyst_note": "",
        "pages_analyzed": ["cursor.com"],
        "analysis_success": True
    }

    mock_history_1 = MagicMock()
    mock_history_1.full_analysis = {
        "name": "Cursor",
        "domain": "cursor.com",
        "core_offering": "editor",
        "icp": "devs",
        "messaging_tone": "technical",
        "pricing_signals": "",
        "hiring_signals": "",
        "recent_launches": [],
        "strategic_keywords": ["editor"],
        "growth_signals": [],
        "risk_flags": [],
        "momentum_score": 5,
        "analyst_note": "",
        "pages_analyzed": ["cursor.com"],
        "analysis_success": True
    }

    mock_db.get_competitor_history.return_value = [
        mock_history_0,
        mock_history_1,
    ]

    monitoring = MonitoringService(mock_db)

    result = await monitoring.detect_drift("Cursor")

    assert result.get("alert_suppressed") is True
    assert "drift_report" in result
