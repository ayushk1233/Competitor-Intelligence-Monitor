from pydantic import BaseModel


class AlertRecord(BaseModel):
    company_name: str
    severity: str
    headline: str
    summary: str | None = None
    reasons: list[str] = []
    evidence: list[str] = []
    confidence: int = 90
    business_impact: str | None = None
    recommended_action: str | None = None
    created_at: str
