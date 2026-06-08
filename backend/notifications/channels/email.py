import smtplib

from email.message import EmailMessage

from backend.config import get_settings

from backend.notifications.models import (
    NotificationRequest,
    NotificationResult,
)


async def send_email(
    request: NotificationRequest,
) -> NotificationResult:

    settings = get_settings()

    try:

        message = EmailMessage()

        message["Subject"] = (
            f"[{request.severity}] "
            f"Competitor Alert - "
            f"{request.company_name}"
        )

        message["From"] = (
            settings.smtp_from_email
        )

        message["To"] = (
            request.destination
        )

        message.set_content(
            request.message
        )

        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
        ) as smtp:

            smtp.starttls()

            smtp.login(
                settings.smtp_username,
                settings.smtp_password,
            )

            smtp.send_message(
                message
            )

        return NotificationResult(
            success=True,
            channel_type="EMAIL",
            destination=request.destination,
        )

    except Exception as e:

        return NotificationResult(
            success=False,
            channel_type="EMAIL",
            destination=request.destination,
            error_message=str(e),
        )