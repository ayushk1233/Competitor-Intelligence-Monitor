export const QUERY_KEYS = {
  me: ["me"] as const,
  dashboardSummary: ["dashboard-summary"] as const,
  recentAlerts: ["recent-alerts"] as const,
  recentRuns: ["recent-runs"] as const,
  activity: ["activity"] as const,
  watchlists: ["watchlists"] as const,
  competitors: (watchlistId: string) => ["competitors", watchlistId] as const,
  runs: (watchlistId: string) => ["runs", watchlistId] as const,
  notificationChannels: ["notification-channels"] as const,
  competitorAnalysis: (name: string) => ["competitor-analysis", name] as const,
  competitorHistory: (name: string) => ["competitor-history", name] as const,
  competitorDrift: (name: string) => ["competitor-drift", name] as const,
};

export const ROUTES = {
  login: "/login",
  signup: "/signup",
  dashboard: "/dashboard",
  watchlists: "/watchlists",
  watchlistDetail: (id: string) => `/watchlists/${id}`,
  competitorDetail: (watchlistId: string, companyName: string) =>
    `/watchlists/${watchlistId}/competitors/${encodeURIComponent(companyName)}`,
  reportDetail: (runId: string) => `/reports/${runId}`,
  notifications: "/notifications",
  settings: "/settings",
} as const;

export const POLL_INTERVAL = 10_000;
