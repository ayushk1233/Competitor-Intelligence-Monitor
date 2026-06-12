import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.config import get_settings
from backend.notifications.models import (
    NotificationRequest,
    NotificationResult,
)

settings = get_settings()


async def send_email(
    request: NotificationRequest,
) -> NotificationResult:

    try:

        msg = MIMEMultipart()

        msg["From"] = settings.smtp_from_email
        msg["To"] = request.destination

        msg["Subject"] = (
            f"[CIM] {request.severity} Alert - "
            f"{request.company_name}"
        )

        body = f"""
Company: {request.company_name}

Severity: {request.severity}

Message:
{request.message}
"""

        msg.attach(
            MIMEText(
                body,
                "plain",
            )
        )

        server = smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
        )

        server.starttls()

        server.login(
            settings.smtp_username,
            settings.smtp_password,
        )

        server.send_message(msg)

        server.quit()

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