import requests

from backend.config import get_settings

from backend.notifications.models import (
    NotificationRequest,
    NotificationResult,
)

settings = get_settings()


async def send_slack(
    request: NotificationRequest,
) -> NotificationResult:

    try:

        payload = {
            "text": (
                f"🚨 CIM Alert\n\n"
                f"Company: {request.company_name}\n"
                f"Severity: {request.severity}\n"
                f"Message: {request.message}"
            )
        }

        response = requests.post(
            settings.slack_webhook_url,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        return NotificationResult(
            success=True,
            channel_type="SLACK",
            destination="slack",
        )

    except Exception as e:

        return NotificationResult(
            success=False,
            channel_type="SLACK",
            destination="slack",
            error_message=str(e),
        )