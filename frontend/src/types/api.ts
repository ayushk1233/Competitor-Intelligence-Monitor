// ── Auth ───────────────────────────────────────────────

export interface SignupRequest {
  email: string;
  password: string;
  display_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  display_name?: string;
}

export interface CurrentUserResponse {
  id: string;
  email: string;
  display_name?: string;
}

// ── Dashboard ──────────────────────────────────────────

export interface DashboardCompetitor {
  company_name: string;
  domain?: string;
  logo_url?: string;
  messaging_tone?: string;
  momentum_score?: number;
  last_analyzed_at?: string;
  alert_count: number;
  has_active_alerts: boolean;
  max_severity?: string;
  analyst_note?: string;
  core_offering?: string;
}

export interface DashboardCompetitorsResponse {
  items: DashboardCompetitor[];
}

export interface DashboardSummaryResponse {
  watchlists: number;
  competitors: number;
  monitoring_runs_today: number;
  notification_channels: number;
  critical_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  competitors_requiring_review: number;
  last_run_at?: string;
  total_alerts: number;
  has_active_run: boolean;
  active_run_status?: string;
  active_run_id?: string;
}

export interface MonitoringRunResponse {
  id: string;
  watchlist_id: string;
  trigger_type: string;
  status: string;
  competitors_checked: number;
  alerts_generated: number;
  notifications_sent: number;
  celery_task_id?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface DashboardRecentRunsResponse {
  items: MonitoringRunResponse[];
}

export interface DashboardAlertResponse {
  id: number;
  company_name: string;
  severity: string;
  headline: string;
  summary?: string;
  evidence?: string[];
  confidence?: number;
  business_impact?: string;
  recommended_action?: string;
  status: string;
  created_at: string;
}

export interface DashboardRecentAlertsResponse {
  items: DashboardAlertResponse[];
}

export interface DashboardActivityItem {
  activity_type: string;
  title: string;
  timestamp: string;
}

export interface DashboardActivityResponse {
  items: DashboardActivityItem[];
}

// ── Watchlists ─────────────────────────────────────────

export interface WatchlistCreateRequest {
  name: string;
  description?: string;
  monitoring_frequency?: string;
  monitoring_config?: {
    frequency?: string;
    sources?: string[];
    sensitivity?: string;
  };
  alert_rules?: Record<string, unknown>;
  notification_channels?: string[];
}

export interface WatchlistUpdateRequest {
  name?: string;
  description?: string;
  monitoring_config?: {
    frequency?: string;
    sources?: string[];
    sensitivity?: string;
  };
  alert_rules?: Record<string, unknown>;
  notification_channels?: string[];
  is_active?: boolean;
}

export interface WatchlistResponse {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  is_active: boolean;
  monitoring_frequency: string;
  monitoring_config?: {
    frequency?: string;
    sources?: string[];
    sensitivity?: string;
  };
  alert_rules?: Record<string, unknown>;
  notification_channels?: string[];
  last_monitored_at?: string;
  next_run_at?: string;
  created_at: string;
}

export interface WatchlistListResponse {
  items: WatchlistResponse[];
}

// ── Competitors ────────────────────────────────────────

export interface CompetitorCreateRequest {
  company_name: string;
  domain?: string;
  priority?: string;
  monitoring_enabled?: boolean;
}

export interface CompetitorUpdateRequest {
  company_name?: string;
  domain?: string;
  priority?: string;
  monitoring_enabled?: boolean;
}

export interface CompetitorResponse {
  id: string;
  watchlist_id: string;
  company_name: string;
  domain?: string;
  is_active: boolean;
  priority: string;
  monitoring_enabled: boolean;
  added_at: string;
}

export interface CompetitorListResponse {
  items: CompetitorResponse[];
}

// ── Monitoring Runs ────────────────────────────────────

export interface MonitoringRunCreateRequest {
  trigger_type: string;
}

export interface MonitoringRunListResponse {
  items: MonitoringRunResponse[];
}

// ── Notifications ──────────────────────────────────────

export interface NotificationChannelCreateRequest {
  channel_type: string;
  destination: string;
  label?: string;
}

export interface NotificationChannelUpdateRequest {
  enabled: boolean;
}

export interface NotificationChannelResponse {
  id: string;
  user_id: string;
  channel_type: string;
  destination: string;
  label?: string;
  enabled: boolean;
  verified: boolean;
  created_at: string;
}

export interface NotificationChannelListResponse {
  items: NotificationChannelResponse[];
}

// ── Competitor Analysis ─────────────────────────────────

export interface CompetitorAnalysisResponse {
  name: string;
  domain: string;
  core_offering: string;
  icp: string;
  messaging_tone: string;
  pricing_signals: string;
  hiring_signals: string;
  recent_launches: string[];
  strategic_keywords: string[];
  growth_signals: string[];
  risk_flags: string[];
  momentum_score: number;
  analyst_note: string;
  pages_analyzed: string[];
  analysis_success: boolean;
  error?: string;
}

export interface CompetitorHistoryItem {
  created_at: string;
  momentum_score: number;
  messaging_tone: string;
}

export interface CompetitorHistoryResponse {
  competitor: string;
  history: CompetitorHistoryItem[];
}

export interface DriftReport {
  company_name: string;
  old_momentum: number;
  new_momentum: number;
  momentum_delta: number;
  added_keywords: string[];
  removed_keywords: string[];
  tone_changed: boolean;
}

// ── Intelligence Report ──────────────────────────────────

export interface CompetitorAnalysisReport {
  name: string;
  domain: string;
  logo_url?: string;
  core_offering: string;
  icp: string;
  messaging_tone: string;
  pricing_signals: string;
  hiring_signals: string;
  recent_launches: string[];
  strategic_keywords: string[];
  growth_signals: string[];
  risk_flags: string[];
  momentum_score: number;
  analyst_note: string;
  pages_analyzed: string[];
  analysis_success: boolean;
  error?: string;

  // Company Validation
  validation?: {
    company_name?: string;
    company_description?: string;
    category?: string;
    product_type?: string;
    primary_use_case?: string;
    validation_warning?: boolean;
    reason?: string;
  };

  // Per-section Evidence
  core_offering_evidence?: string[];
  core_offering_source?: string;
  core_offering_confidence?: number;
  pricing_evidence?: string[];
  pricing_source?: string;
  pricing_confidence?: number;
  hiring_evidence?: string[];
  hiring_source?: string;
  hiring_confidence?: number;
  keywords_evidence?: string[];
  keywords_confidence?: number;

  // Per-section Confidence
  confidence_scores?: Record<string, number>;

  // Momentum Drivers
  momentum_negative_factors?: string[];
  momentum_reasoning?: string;

  // Preserved Evidence
  icp_keywords?: string[];
  icp_evidence?: string[];
  tone_evidence?: string[];
  momentum_evidence?: string[];
  agent_outputs?: Record<string, unknown>;
}

export interface ComparisonResult {
  market_leader: string;
  market_leader_reason?: string;
  fastest_mover: string;
  fastest_mover_reason?: string;
  pivot_detected?: string;
  smb_to_enterprise_shift: string[];
  ai_emphasis_ranking: string[];
  messaging_gaps: string;
  messaging_gap?: {
    title: string;
    description: string;
    target_persona: string;
    business_value: string;
    confidence: string;
  };
  threat_ranking: string[];
  threat_ranking_reasons?: string[];
  executive_briefing: string;
}

export interface IntelligenceReport {
  competitors: CompetitorAnalysisReport[];
  comparison: ComparisonResult;
  generated_at: string;
  total_pages_fetched: number;
  run_duration_seconds: number;
}

// ── Analysis / Scraping ──────────────────────────────────

export interface AnalysisRequest {
  competitors: string[];
  competitor_urls?: Record<string, string>;
  options?: {
    include_careers?: boolean;
    include_blog?: boolean;
    max_pages_per_competitor?: number;
  };
}

export interface AnalysisResponse {
  run_id: string;
  status: string;
  competitors: string[];
  message: string;
}

export interface RunListItem {
  run_id: string;
  status: string;
  competitors: string[];
  pages_fetched: number;
  duration_seconds: number | null;
  created_at: string;
}

export interface RunStatusResponse {
  run_id: string;
  status: string;
  progress_percent: number;
  competitors: string[];
  pages_fetched: number;
  duration_seconds: number | null;
  error: string | null;
  created_at: string | null;
  completed_at: string | null;
}

// ── API Error ──────────────────────────────────────────

export interface ApiError {
  detail: string;
}
