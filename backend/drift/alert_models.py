from pydantic import BaseModel


class AlertRecord(BaseModel):
    company_name: str
    severity: str
    reasons: list[str]
    created_at: str
