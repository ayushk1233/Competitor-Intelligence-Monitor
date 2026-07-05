from datetime import datetime
from pydantic import BaseModel, Field
from backend.memory.models import TimelineEvent
from backend.temporal.enums import (
    TemporalChangeCategory,
    TemporalChangeDirection,
    TemporalConfidenceLevel
)

class TemporalEvidence(BaseModel):
    category: TemporalChangeCategory
    description: str
    evidence: str
    source_run_id: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: TemporalConfidenceLevel

class TemporalChange(BaseModel):
    category: TemporalChangeCategory
    direction: TemporalChangeDirection
    summary: str
    reasoning: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: TemporalConfidenceLevel
    evidence: list[TemporalEvidence]

class TimelineComparison(BaseModel):
    company_name: str
    latest_event: TimelineEvent
    previous_event: TimelineEvent
    historical_context: list[TimelineEvent]

class TemporalAnalysis(BaseModel):
    company_name: str
    analysis_timestamp: datetime
    changes: list[TemporalChange]
    overall_summary: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: TemporalConfidenceLevel
    timeline_version: str

class TemporalComparisonResult(BaseModel):
    comparison: TimelineComparison
    analysis: TemporalAnalysis
