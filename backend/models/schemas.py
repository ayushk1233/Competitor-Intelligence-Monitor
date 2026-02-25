from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnalysisOptions(BaseModel):
    include_careers: bool = True
    include_blog: bool = True
    max_pages_per_competitor: int = 4


class AnalysisRequest(BaseModel):
    competitors: list[str]          # names or URLs, 2–5
    options: AnalysisOptions = AnalysisOptions()


class PageData(BaseModel):
    url: str
    page_type: str                  # homepage | pricing | about | blog | careers
    content: str                    # cleaned text
    fetch_success: bool


class CompetitorPages(BaseModel):
    name: str
    domain: str
    pages: list[PageData]
    fetch_errors: list[str] = []




class CompetitorAnalysis(BaseModel):
    name: str
    domain: str

    # Claude-extracted fields
    core_offering: str
    icp: str
    messaging_tone: str             # enterprise | startup | technical | visionary | hybrid
    pricing_signals: str
    hiring_signals: str
    recent_launches: list[str]
    strategic_keywords: list[str]
    growth_signals: list[str]
    risk_flags: list[str]
    momentum_score: int             # 1–10
    analyst_note: str

    # Metadata
    pages_analyzed: list[str]
    analysis_success: bool = True
    error: Optional[str] = None


class ComparisonResult(BaseModel):
    market_leader: str
    fastest_mover: str
    pivot_detected: Optional[str]
    smb_to_enterprise_shift: list[str]
    ai_emphasis_ranking: list[str]
    messaging_gaps: str
    threat_ranking: list[str]
    executive_briefing: str




class IntelligenceReport(BaseModel):
    competitors: list[CompetitorAnalysis]
    comparison: ComparisonResult
    generated_at: datetime
    total_pages_fetched: int
    run_duration_seconds: float