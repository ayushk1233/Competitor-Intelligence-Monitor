import requests

from backend.config import get_settings

from backend.notifications.models import (
    NotificationRequest,
    NotificationResult,
)


async def send_slack(
    request: NotificationRequest,
) -> NotificationResult:

    settings = get_settings()

    try:

        response = requests.post(
            settings.slack_webhook_url,
            json={
                "text":
                (
                    f"🚨 [{request.severity}] "
                    f"{request.company_name}\n\n"
                    f"{request.message}"
                )
            },
            timeout=10,
        )

        response.raise_for_status()

        return NotificationResult(
            success=True,
            channel_type="SLACK",
            destination=request.destination,
        )

    except Exception as e:

        return NotificationResult(
            success=False,
            channel_type="SLACK",
            destination=request.destination,
            error_message=str(e),
        )