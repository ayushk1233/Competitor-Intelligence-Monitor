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

    # Preserved Reasoning Evidence
    icp_keywords: list[str] = []
    icp_evidence: list[str] = []
    tone_evidence: list[str] = []
    momentum_evidence: list[str] = []
    agent_outputs: dict = {}

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


# ============================================================
# Watchlist Schemas
# ============================================================

class WatchlistCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    monitoring_frequency: str = "DAILY"


class WatchlistResponse(BaseModel):
    id: str
    user_id: str

    name: str
    description: Optional[str]

    is_active: bool
    monitoring_frequency: str
    last_monitored_at: datetime | None = None
    next_run_at: datetime | None = None

    created_at: datetime

    class Config:
        from_attributes = True


class WatchlistListResponse(BaseModel):
    items: list[WatchlistResponse]

    class Config:
        from_attributes = True


# ============================================================
# Watchlist Competitor Schemas
# ============================================================

class CompetitorCreateRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None


class CompetitorResponse(BaseModel):
    id: str
    watchlist_id: str

    company_name: str
    domain: Optional[str]

    is_active: bool

    added_at: datetime

    class Config:
        from_attributes = True


class CompetitorListResponse(BaseModel):
    items: list[CompetitorResponse]

    class Config:
        from_attributes = True


# ============================================================
# Monitoring Run Schemas
# ============================================================

class MonitoringRunCreateRequest(BaseModel):
    trigger_type: str = "MANUAL"


class MonitoringRunResponse(BaseModel):
    id: str

    watchlist_id: str

    trigger_type: str
    status: str

    competitors_checked: int
    alerts_generated: int
    notifications_sent: int

    celery_task_id: Optional[str]

    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    created_at: datetime

    class Config:
        from_attributes = True


class MonitoringRunListResponse(BaseModel):
    items: list[MonitoringRunResponse]

    class Config:
        from_attributes = True


# ============================================================
# Notification Channel Schemas
# ============================================================

class NotificationChannelCreateRequest(BaseModel):
    channel_type: str
    destination: str
    label: str | None = None


class NotificationChannelUpdateRequest(BaseModel):
    enabled: bool


class NotificationChannelResponse(BaseModel):
    id: str
    user_id: str

    channel_type: str
    destination: str

    label: str | None

    enabled: bool
    verified: bool

    created_at: datetime

    class Config:
        from_attributes = True


class NotificationChannelListResponse(BaseModel):
    items: list[NotificationChannelResponse]

    class Config:
        from_attributes = True


class SignupRequest(BaseModel):
    email: str
    password: str
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    user_id: str
    email: str
    display_name: str | None = None


class CurrentUserResponse(BaseModel):
    id: str
    email: str
    display_name: str | None = None

    class Config:
        from_attributes = True


# ============================================================
# Dashboard
# ============================================================

class DashboardSummaryResponse(BaseModel):
    watchlists: int
    competitors: int
    monitoring_runs_today: int
    notification_channels: int


class DashboardRecentRunsResponse(BaseModel):
    items: list[MonitoringRunResponse]