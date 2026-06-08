from pydantic import BaseModel


class NotificationRequest(BaseModel):
    company_name: str
    severity: str
    message: str
    destination: str
    channel_type: str


class NotificationResult(BaseModel):
    success: bool
    channel_type: str
    destination: str
    error_message: str | None = None