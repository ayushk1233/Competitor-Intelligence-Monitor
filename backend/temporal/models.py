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
    business_impact: str
    reasoning: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: TemporalConfidenceLevel
    evidence: list[TemporalEvidence]

class ComparisonMetadata(BaseModel):
    total_events: int
    historical_depth: int
    days_between_latest_and_previous: int
    timeline_span_days: int

class TimelineComparison(BaseModel):
    company_name: str
    latest_event: TimelineEvent
    previous_event: TimelineEvent
    historical_context: list[TimelineEvent]
    metadata: ComparisonMetadata

class ReasoningContext(BaseModel):
    comparison: TimelineComparison
    prompt_version: str
    model_name: str
    
    model_config = {"protected_namespaces": ()}

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
