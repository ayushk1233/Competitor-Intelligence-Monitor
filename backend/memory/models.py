from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from backend.memory.retrieval import RetrievedMemory


class RetrievedAnalysis(BaseModel):
    """
    Groups multiple RetrievedMemory chunks into a single historical analysis object.
    The LLM works best with grouped analyses rather than disconnected chunks.
    """
    run_id: str
    company_name: str
    analyzed_at: datetime
    similarity_score: float
    executive_briefing: Optional[str] = None
    structured_summary: Optional[str] = None
    supporting_chunks: list[RetrievedMemory]


class MemorySearchResult(BaseModel):
    """
    Return type for all memory searches.
    """
    query: str
    analyses: list[RetrievedAnalysis]
    retrieved_chunks: int
    runtime_ms: float


class TimelineEvent(BaseModel):
    """
    Chronological event representing a historical analysis.
    Unlike RetrievedAnalysis, this has no similarity score.
    """
    run_id: str
    company_name: str
    analyzed_at: datetime
    executive_briefing: Optional[str] = None
    structured_summary: Optional[str] = None
    supporting_chunks: list[RetrievedMemory]


class CompanyTimeline(BaseModel):
    """
    Canonical historical object for temporal comparisons and tracking company evolution.
    """
    company_name: str
    events: list[TimelineEvent]
    first_seen: datetime
    latest_seen: datetime
    total_events: int
