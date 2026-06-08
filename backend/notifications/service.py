from backend.notifications.models import (
    NotificationRequest,
    NotificationResult,
)

from backend.notifications.channels.email import (
    send_email,
)

from backend.notifications.channels.slack import (
    send_slack,
)

from backend.notifications.channels.webhook import (
    send_webhook,
)


class NotificationService:

    async def send(
        self,
        request: NotificationRequest,
    ) -> NotificationResult:

        channel = request.channel_type.upper()

        if channel == "EMAIL":
            return await send_email(request)

        if channel == "SLACK":
            return await send_slack(request)

        if channel == "WEBHOOK":
            return await send_webhook(request)

        return NotificationResult(
            success=False,
            channel_type=channel,
            destination=request.destination,
            error_message="Unsupported channel",
        )