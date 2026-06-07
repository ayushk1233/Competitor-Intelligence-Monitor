from typing import Any
from datetime import datetime, UTC

from backend.models.schemas import CompetitorAnalysis
from backend.drift.diff_service import compare_analysis
from backend.drift.alert_engine import generate_alert
from backend.drift.alert_models import AlertRecord
from backend.drift.alert_storage import save_alert
from backend.drift.suppression_service import is_suppressed, suppress_alert


class MonitoringService:

    def __init__(
        self,
        db: Any,
    ):
        self.db = db

    async def detect_drift(
        self,
        competitor_name: str,
    ):

        history = await self.db.get_competitor_history(
            competitor_name,
            limit=2,
        )

        if len(history) < 2:
            return None

        newest = CompetitorAnalysis(
            **history[0].full_analysis
        )

        previous = CompetitorAnalysis(
            **history[1].full_analysis
        )

        drift_report = compare_analysis(
            previous,
            newest,
        )

        alert_data = generate_alert(
            drift_report
        )

        suppressed = await is_suppressed(
            self.db,
            alert_data["company_name"],
            alert_data["severity"],
        )

        if suppressed:
            return {
                "drift_report": drift_report,
                "alert_suppressed": True,
            }

        alert_record = AlertRecord(
            company_name=alert_data["company_name"],
            severity=alert_data["severity"],
            reasons=alert_data["reasons"],
            created_at=datetime.now(UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )

        save_alert(
            alert_record
        )

        await self.db.save_alert(
            company_name=alert_record.company_name,
            severity=alert_record.severity,
            reasons=alert_record.reasons,
        )

        await suppress_alert(
            self.db,
            alert_record.company_name,
            alert_record.severity,
            hours=24,
        )

        return {
            "drift_report": drift_report,
            "alert": alert_record,
        }