from datetime import UTC, datetime
from typing import Any

from backend.config import get_settings
from backend.drift.alert_engine import generate_alert
from backend.drift.alert_models import AlertRecord
from backend.drift.alert_storage import save_alert
from backend.drift.diff_service import compare_analysis
from backend.drift.suppression_service import is_suppressed, suppress_alert
from backend.models.schemas import CompetitorAnalysis
from backend.notifications.models import NotificationRequest
from backend.notifications.service import NotificationService


class MonitoringService:

    def __init__(
        self,
        db: Any,
    ):
        self.db = db
        self.notification_service = NotificationService()
        self.settings = get_settings()

    async def detect_drift(
        self,
        competitor_name: str,
        watchlist_id: str | None = None,
        skip_suppression: bool = False,
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

        if not skip_suppression:
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
            headline=alert_data.get("headline", f"{alert_data['company_name']} changed"),
            summary=alert_data.get("summary"),
            reasons=alert_data.get("reasons", []),
            evidence=alert_data.get("evidence", []),
            confidence=alert_data.get("confidence", 90),
            business_impact=alert_data.get("business_impact"),
            recommended_action=alert_data.get("recommended_action"),
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
            headline=alert_record.headline,
            summary=alert_record.summary,
            reasons=alert_record.reasons,
            evidence=alert_record.evidence,
            confidence=alert_record.confidence,
            business_impact=alert_record.business_impact,
            recommended_action=alert_record.recommended_action,
            watchlist_id=watchlist_id,
        )

        notifications_sent = 0

        channels = await (
            self.db.get_enabled_notification_channels()
        )

        for channel in channels:

            notification_request = NotificationRequest(
                company_name=alert_record.company_name,
                severity=alert_record.severity,
                message="Competitor drift detected",
                destination=channel.destination,
                channel_type=channel.channel_type,
            )

            notification_result = await (
                self.notification_service.send(
                    notification_request
                )
            )

            await self.db.create_notification_event(
                company_name=alert_record.company_name,
                severity=alert_record.severity,
                destination=channel.destination,
                channel_type=channel.channel_type,
                delivery_status=(
                    "DELIVERED"
                    if notification_result.success
                    else "FAILED"
                ),
                error_message=notification_result.error_message,
            )

            if notification_result.success:
                notifications_sent += 1

        if not skip_suppression:
            await suppress_alert(
                self.db,
                alert_record.company_name,
                alert_record.severity,
                hours=24,
            )

        return {
            "drift_report": drift_report,
            "alert": alert_record,
            "notifications_sent": notifications_sent,
        }