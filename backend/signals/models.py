from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from backend.temporal.enums import (
    TemporalChangeCategory,
    TemporalChangeDirection,
    TemporalConfidenceLevel
)
from backend.temporal.models import TemporalEvidence
from backend.signals.enums import SignalSeverity

class StrategicSignal(BaseModel):
    signal_id: UUID
    signal_fingerprint: str
    company_name: str
    category: TemporalChangeCategory
    direction: TemporalChangeDirection
    summary: str
    business_impact: str
    confidence_score: float
    confidence_level: TemporalConfidenceLevel
    severity: SignalSeverity
    evidence: list[TemporalEvidence]
    originating_run_id: str
    signal_source: str
    prompt_version: str
    model_name: str
    analysis_version: str
    detected_at: datetime
    
    model_config = {"protected_namespaces": ()}
