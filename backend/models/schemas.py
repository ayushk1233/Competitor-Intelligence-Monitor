from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnalysisOptions(BaseModel):
    include_careers: bool = True
    include_blog: bool = True
    max_pages_per_competitor: int = 4


class AnalysisRequest(BaseModel):
    competitors: list[str]          # names, 2–5
    competitor_urls: dict[str, str] = {}  # optional: name → URL override
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

    # Company Validation (Problem 1)
    validation: dict = {}           # {company_name, company_description, category, product_type, primary_use_case, validation_warning}

    # Strategy & Differentiation (v1.2 Upgrade)
    strategic_interpretation: dict = {}
    competitor_dna: dict = {}

    # Per-section Evidence (Problem 2)
    core_offering_evidence: list[str] = []
    core_offering_source: str = ""
    core_offering_source_url: str = ""
    core_offering_confidence: int = 0
    pricing_evidence: list[str] = []
    pricing_source: str = ""
    pricing_source_url: str = ""
    pricing_confidence: int = 0
    hiring_evidence: list[str] = []
    hiring_source: str = ""
    hiring_source_url: str = ""
    hiring_confidence: int = 0
    keywords_evidence: list[str] = []
    keywords_source_url: str = ""
    keywords_confidence: int = 0

    # Per-section Confidence (Problem 5) — legacy format kept for backward compatibility
    confidence_scores: dict = {}    # {core_offering: 92, icp: 88, tone: 85, pricing: 40, hiring: 70, keywords: 75}

    # Evidence-Based Confidence (v1.2.3) — additive; pre-v1.2.3 reports default to {}
    confidence_metrics: dict = {}   # {field: {confidence, evidence_count, source_count, source_types, agreement_score}}

    # Momentum Driver Explanation (Problem 3)
    momentum_negative_factors: list[str] = []
    momentum_reasoning: str = ""

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
    logo_url: str = ""


class MessagingGap(BaseModel):
    title: str
    description: str
    target_persona: str
    business_value: str
    confidence: str


class ComparisonResult(BaseModel):
    market_leader: str
    market_leader_reason: str = ""
    fastest_mover: str
    fastest_mover_reason: str = ""
    pivot_detected: Optional[str]
    smb_to_enterprise_shift: list[str]
    ai_emphasis_ranking: list[str]
    messaging_gaps: str
    messaging_gap: MessagingGap | None = None
    threat_ranking: list[str]
    threat_ranking_reasons: list[str] = []
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
    monitoring_config: Optional[dict] = None
    alert_rules: Optional[dict] = None
    notification_channels: Optional[list] = None


class WatchlistUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    monitoring_config: Optional[dict] = None
    alert_rules: Optional[dict] = None
    notification_channels: Optional[list] = None
    is_active: Optional[bool] = None


class WatchlistResponse(BaseModel):
    id: str
    user_id: str

    name: str
    description: Optional[str]

    is_active: bool
    monitoring_frequency: str
    monitoring_config: Optional[dict] = None
    alert_rules: Optional[dict] = None
    notification_channels: Optional[list] = None
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
    priority: str = "medium"
    monitoring_enabled: bool = True


class CompetitorUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    domain: Optional[str] = None
    priority: Optional[str] = None
    monitoring_enabled: Optional[bool] = None


class CompetitorResponse(BaseModel):
    id: str
    watchlist_id: str

    company_name: str
    domain: Optional[str]

    is_active: bool
    priority: str = "medium"
    monitoring_enabled: bool = True

    added_at: datetime

    class Config:
        from_attributes = True


class CompetitorListResponse(BaseModel):
    items: list[CompetitorResponse]

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
    critical_alerts: int = 0
    high_alerts: int = 0
    medium_alerts: int = 0
    low_alerts: int = 0
    competitors_requiring_review: int = 0
    last_run_at: datetime | None = None
    total_alerts: int = 0
    has_active_run: bool = False
    active_run_status: str | None = None
    active_run_id: str | None = None
    next_scheduled_analysis: datetime | None = None


class DashboardRecentRunsResponse(BaseModel):
    items: list[MonitoringRunResponse]


class DashboardAlertResponse(BaseModel):
    company_name: str
    severity: str
    headline: str
    summary: str | None = None
    evidence: list = []
    confidence: int = 90
    business_impact: str | None = None
    recommended_action: str | None = None
    status: str = "new"
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class DashboardRecentAlertsResponse(BaseModel):
    items: list[DashboardAlertResponse]

    class Config:
        from_attributes = True


class DashboardActivityItem(BaseModel):
    activity_type: str
    title: str
    timestamp: datetime


class DashboardCompetitorResponse(BaseModel):
    company_name: str
    domain: str | None = None
    logo_url: str | None = None
    messaging_tone: str | None = None
    momentum_score: int | None = None
    last_analyzed_at: datetime | None = None
    alert_count: int = 0
    has_active_alerts: bool = False
    max_severity: str | None = None
    analyst_note: str | None = None
    core_offering: str | None = None

    class Config:
        from_attributes = True


class DashboardCompetitorsResponse(BaseModel):
    items: list[DashboardCompetitorResponse]


class DashboardIntelligenceResponse(BaseModel):
    run_id: str | None = None
    generated_at: datetime | None = None
    market_leader: str | None = None
    fastest_mover: str | None = None
    executive_briefing: str | None = None
    threat_ranking: list[str] = []
    total_competitors_analyzed: int = 0


class DashboardLastRunResponse(BaseModel):
    run_id: str
    status: str
    created_at: datetime | None = None
    completed_at: datetime | None = None
    competitors_analyzed: list[str] = []
    intelligence: DashboardIntelligenceResponse | None = None


class DashboardActivityResponse(BaseModel):
    items: list[DashboardActivityItem]