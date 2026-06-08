from backend.notifications.models import (
    NotificationRequest,
    NotificationResult,
)


async def send_webhook(
    request: NotificationRequest,
) -> NotificationResult:

    return NotificationResult(
        success=True,
        channel_type="WEBHOOK",
        destination=request.destination,
    )