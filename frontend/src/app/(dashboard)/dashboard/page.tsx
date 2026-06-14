"use client";

import { useState } from "react";
import Link from "next/link";
import {
  useDashboardSummary,
  useRecentAlerts,
  useDashboardCompetitors,
  useRecentRuns,
} from "@/hooks/use-dashboard";
import { useRunStatus } from "@/hooks/use-run-status";
import { useRecentAnalysisRuns } from "@/hooks/use-analysis-runs";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardOverview, MomentumRanking, RecentRunsWidget } from "@/components/dashboard/DashboardOverview";
import { NewAnalysisModal } from "@/components/dashboard/NewAnalysisModal";
import { RecentRunsTable } from "@/components/dashboard/RecentRunsTable";
import { AlertTriangle, TrendingUp, TrendingDown, Minus, Lightbulb, Loader2, XCircle } from "lucide-react";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import type { DashboardAlertResponse, DashboardCompetitor } from "@/types/api";

const toneColors: Record<string, string> = {
  enterprise: "bg-[var(--tone-enterprise-bg)] text-[var(--tone-enterprise-text)]",
  startup: "bg-[var(--tone-startup-bg)] text-[var(--tone-startup-text)]",
  technical: "bg-[var(--tone-technical-bg)] text-[var(--tone-technical-text)]",
  visionary: "bg-[var(--tone-visionary-bg)] text-[var(--tone-visionary-text)]",
  hybrid: "bg-[var(--tone-hybrid-bg)] text-[var(--tone-hybrid-text)]",
};

function matchesRunName(companyName: string, domain: string | undefined, candidates: Set<string> | string[]): boolean {
  if (candidates instanceof Set && candidates.has(companyName)) return true;
  if (Array.isArray(candidates) && candidates.includes(companyName)) return true;
  if (!domain) return false;
  const list = candidates instanceof Set ? [...candidates] : candidates;
  return list.some((n) => {
    const urlDomain = n.replace(/^https?:\/\//, "").replace(/\/.*$/, "").replace(/^www\./, "");
    return urlDomain === domain || urlDomain === `www.${domain}`;
  });
}

function relativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return `${Math.floor(diff / 60000)}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

const severityBorder: Record<string, string> = {
  CRITICAL: "border-red-500/70",
  HIGH: "border-red-500/70",
  MEDIUM: "border-amber-500/70",
  LOW: "border-emerald-500/70",
};

const severityDot: Record<string, string> = {
  CRITICAL: "bg-red-500",
  HIGH: "bg-red-500",
  MEDIUM: "bg-amber-500",
  LOW: "bg-emerald-500",
};

function CompetitorCard({ competitor }: { competitor: DashboardCompetitor }) {
  const hasAlerts = competitor.has_active_alerts;
  const sev = competitor.max_severity || "";
  const borderClass = hasAlerts
    ? `border ${severityBorder[sev] || "border-red-500/70"}`
    : "border border-neutral-800";
  const dotClass = hasAlerts ? severityDot[sev] || "bg-red-500" : "";

  return (
    <div className={`rounded-xl bg-card p-4 flex flex-col gap-4 ${borderClass}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3 min-w-0">
          {competitor.logo_url && (
            <img
              src={competitor.logo_url}
              alt={`${competitor.company_name} logo`}
              className="h-8 w-8 rounded-lg bg-neutral-800 object-contain shrink-0"
              onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = "none" }}
            />
          )}
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-base font-bold text-foreground">{competitor.company_name}</span>
              {hasAlerts && <span className={`h-2 w-2 rounded-full shrink-0 ${dotClass}`} />}
            </div>
            {competitor.domain && (
              <p className="text-xs text-neutral-500 truncate mt-0.5 font-sans">{competitor.domain}</p>
            )}
          </div>
        </div>
        {competitor.momentum_score !== null && competitor.momentum_score !== undefined && (
          <div className="flex items-center gap-1">
            <svg className="h-3.5 w-3.5 text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
            </svg>
            <span className="text-xs text-neutral-500">Momentum</span>
            <span className="text-lg font-bold text-foreground">{competitor.momentum_score}</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        {competitor.messaging_tone ? (
          <span
            className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
              toneColors[competitor.messaging_tone] || "bg-neutral-800 text-neutral-400"
            }`}
          >
            {competitor.messaging_tone}
          </span>
        ) : (
          <span />
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-neutral-500">
        <span>
          {competitor.last_analyzed_at ? relativeTime(competitor.last_analyzed_at) : "—"}
        </span>
        <span>
          {competitor.alert_count} signal{competitor.alert_count !== 1 ? "s" : ""}
          {competitor.alert_count > 0 ? ` • ${competitor.alert_count} alert` : ""}
        </span>
      </div>
    </div>
  );
}

const severityStyles: Record<string, { border: string; pill: string; pillText: string }> = {
  CRITICAL: { border: "bg-red-500", pill: "bg-white", pillText: "text-red-600" },
  HIGH: { border: "bg-red-500", pill: "bg-white", pillText: "text-red-600" },
  MEDIUM: { border: "bg-amber-500", pill: "bg-amber-100", pillText: "text-amber-800" },
  LOW: { border: "bg-emerald-500", pill: "bg-emerald-100", pillText: "text-emerald-800" },
};

function AlertRow({ alert }: { alert: DashboardAlertResponse }) {
  const s = severityStyles[alert.severity] || severityStyles.HIGH;
  const label = alert.severity === "CRITICAL" ? "Critical" : alert.severity.charAt(0) + alert.severity.slice(1).toLowerCase();
  return (
    <div className="relative flex flex-col py-4 pl-6 border-b border-neutral-800 last:border-b-0 hover:bg-neutral-800/20 transition-colors">
      <div className={`absolute left-0 top-0 bottom-0 w-0.5 ${s.border}`} />
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-foreground">{alert.company_name}</span>
          <span className={`${s.pill} ${s.pillText} px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide`}>
            {label}
          </span>
        </div>
        <span className="shrink-0 text-xs text-neutral-500">
          {alert.created_at ? relativeTime(alert.created_at) : ""}
        </span>
      </div>
      <p className="text-sm text-foreground leading-relaxed mt-1.5">{alert.headline}</p>
      {alert.summary && (
        <p className="text-sm text-neutral-400 leading-relaxed mt-1">{alert.summary}</p>
      )}
    </div>
  );
}

function MomentumIcon({ score }: { score: number }) {
  if (score >= 7) return <TrendingUp className="h-4 w-4 text-emerald-500" />;
  if (score >= 4) return <Minus className="h-4 w-4 text-amber-500" />;
  return <TrendingDown className="h-4 w-4 text-red-500" />;
}

export default function DashboardPage() {
  const [analysisOpen, setAnalysisOpen] = useState(false);
  const { data: summary } = useDashboardSummary();
  const { data: alerts, isLoading: alertsLoading } = useRecentAlerts();
  const { data: competitors, isLoading: competitorsLoading } = useDashboardCompetitors();
  const { data: monitoringRuns, isLoading: monitoringLoading } = useRecentRuns();
  const { data: activeRunStatus } = useRunStatus(summary?.active_run_id);
  const { data: recentRuns } = useRecentAnalysisRuns();
  const completedRuns = recentRuns?.filter((r) => r.status === "completed") ?? [];
  const latestCompletedRun = completedRuns[0];
  const latestCompletedRunId = latestCompletedRun?.run_id;

  const queryClient = useQueryClient();
  const cancelMutation = useMutation({
    mutationFn: () => apiClient.post(`/api/runs/${summary?.active_run_id}/cancel`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-recent-alerts"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-competitors"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-recent-runs"] });
      queryClient.invalidateQueries({ queryKey: ["recent-analysis-runs"] });
      queryClient.invalidateQueries({ queryKey: ["run-status", summary?.active_run_id] });
      toast.success("Analysis cancelled");
    },
    onError: () => toast.error("Failed to cancel analysis"),
  });

  const isRunning = summary?.has_active_run;
  const runStatus = activeRunStatus?.status || summary?.active_run_status;

  const stageConfig: Record<string, { label: string; color: string; barColor: string }> = {
    queued:    { label: "Queued",                  color: "#F59E0B", barColor: "#F59E0B" },
    scraping:  { label: "Scraping pages...",       color: "#3B82F6", barColor: "#3B82F6" },
    analyzing: { label: "Analyzing competitors...", color: "#8B5CF6", barColor: "#8B5CF6" },
    comparing: { label: "Generating comparison...", color: "#14B8A6", barColor: "#14B8A6" },
  };
  const stageLabels: Record<string, string> = Object.fromEntries(
    Object.entries(stageConfig).map(([k, v]) => [k, v.label])
  );

  const lastRunTimestamp = latestCompletedRun?.created_at ?? summary?.last_run_at;
  const hasLastRun = !!lastRunTimestamp;
  const lastRunLabel = lastRunTimestamp
    ? `Last run ${relativeTime(lastRunTimestamp)}`
    : "No runs yet";

  const latestCompetitorNames = new Set(latestCompletedRun?.competitors ?? []);
  const topCompetitors = competitors?.items
    ? competitors.items
        .filter((c) => matchesRunName(c.company_name, c.domain, latestCompetitorNames))
        .sort((a, b) => (b.momentum_score ?? 0) - (a.momentum_score ?? 0))
        .slice(0, 3)
    : [];

  const gridCompetitors = competitors?.items
    ? [...competitors.items]
        .sort((a, b) => new Date(b.last_analyzed_at ?? 0).getTime() - new Date(a.last_analyzed_at ?? 0).getTime())
    : [];

  return (
    <div className="p-8">
      <NewAnalysisModal open={analysisOpen} onClose={() => setAnalysisOpen(false)} />

      {/* Dashboard Overview — KPI Cards + Intelligence Widgets */}
      <div className="mb-10">
        <DashboardOverview
          summary={summary}
          competitors={competitors}
          alerts={alerts}
          monitoringRuns={monitoringRuns}
          isLoading={competitorsLoading || alertsLoading || monitoringLoading}
          lastRunLabel={lastRunLabel}
          hasLastRun={hasLastRun}
          isRunning={!!isRunning}
          onRunAnalysis={() => setAnalysisOpen(true)}
        />
      </div>

      {isRunning && (
        <div className="mb-6 rounded-xl border border-[var(--progress-border)] bg-[var(--progress-bg)] px-5 py-4"
          style={{
            borderColor: `${(stageConfig[runStatus || ""]?.color || "#22C55E")}40`,
            backgroundColor: `color-mix(in srgb, ${(stageConfig[runStatus || ""]?.color || "#22C55E")} 10%, var(--card))`,
          }}
        >
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin"
              style={{ color: stageConfig[runStatus || ""]?.color || "#22C55E" }}
            />
            <div>
              <p className="text-sm font-medium text-foreground">Analysis in progress</p>
              <p className="text-xs mt-0.5"
                style={{ color: `${stageConfig[runStatus || ""]?.color || "#22C55E"}CC` }}
              >
                {stageLabels[runStatus || ""] || "Working..."}
              </p>
            </div>
            <div className="ml-auto flex items-center gap-2">
              {activeRunStatus && (
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">
                    {activeRunStatus.pages_fetched} page{activeRunStatus.pages_fetched !== 1 ? "s" : ""} fetched
                  </span>
                  <span className="text-xs font-semibold mr-1"
                    style={{ color: stageConfig[runStatus || ""]?.color || "#22C55E" }}
                  >
                    {activeRunStatus.progress_percent}%
                  </span>
                </div>
              )}
              <button
                onClick={() => {
                  if (confirm("Cancel this analysis?")) {
                    cancelMutation.mutate();
                  }
                }}
                disabled={cancelMutation.isPending}
                className="flex h-8 px-3 items-center justify-center rounded-md border border-[var(--progress-border)] bg-transparent text-xs font-semibold text-foreground hover:bg-card hover:text-[#EF4444] transition-colors"
              >
                {cancelMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <XCircle className="h-3.5 w-3.5 mr-1.5" />
                    Cancel
                  </>
                )}
              </button>
            </div>
          </div>
          <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-[var(--muted)]">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${activeRunStatus?.progress_percent || 5}%`,
                backgroundColor: stageConfig[runStatus || ""]?.barColor || "#22C55E",
              }}
            />
          </div>
        </div>
      )}

      {/* Latest Intelligence Peek */}
      {topCompetitors.length > 0 && (
        <div className="mb-8">
          <div className="mb-4 flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-emerald-500" />
            <h2 className="text-lg font-bold text-foreground font-mono">Latest Intelligence</h2>
            {latestCompletedRunId && (
              <Link
                href={`/reports/${latestCompletedRunId}`}
                className="ml-auto text-sm text-[var(--link-accent)] hover:text-[var(--link-accent-hover)] transition-colors font-mono"
              >
                View Full Report &rarr;
              </Link>
            )}
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {topCompetitors.map((comp) => {
              const s = comp.max_severity || "";
              const topBorder = comp.has_active_alerts
                ? `border ${severityBorder[s] || "border-red-500/70"}`
                : "border border-neutral-800";
              return (
              <div key={comp.company_name} className={`rounded-xl bg-card p-4 ${topBorder}`}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {comp.logo_url && (
                      <img
                        src={comp.logo_url}
                        alt={`${comp.company_name} logo`}
                        className="h-8 w-8 rounded-lg bg-neutral-800 object-contain shrink-0"
                        onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = "none" }}
                      />
                    )}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-foreground">{comp.company_name}</span>
                        <MomentumIcon score={comp.momentum_score ?? 0} />
                      </div>
                      <span className="text-xs text-neutral-500">Score: {comp.momentum_score ?? "—"}/10</span>
                    </div>
                  </div>
                </div>
                {comp.core_offering && (
                  <p className="text-xs text-neutral-400 leading-relaxed line-clamp-2 mb-2 font-sans">
                    {comp.core_offering}
                  </p>
                )}
                {comp.analyst_note && (
                  <p className="text-xs text-neutral-500 leading-relaxed line-clamp-3 italic font-sans">
                    &ldquo;{comp.analyst_note}&rdquo;
                  </p>
                )}
              </div>
            );
          })}
          </div>
        </div>
      )}

      {/* Intelligence Widgets */}
      <div className="mb-8 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <MomentumRanking competitors={competitors?.items} isLoading={competitorsLoading} />
        <RecentRunsWidget runs={monitoringRuns?.items} isLoading={monitoringLoading} />
      </div>

      {/* Competitors Grid Section */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground font-mono">Competitors</h2>
          <Link href="/run-history" className="text-sm text-[var(--link-accent)] hover:text-[var(--link-accent-hover)] transition-colors font-mono">
            View all &rarr;
          </Link>
        </div>
        {competitorsLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-40 rounded-xl bg-neutral-900" />
            ))}
          </div>
        ) : gridCompetitors.length === 0 ? (
          <div className="flex flex-col items-center gap-3 rounded-xl border border-neutral-800 bg-card py-12 text-center">
            <AlertTriangle className="h-8 w-8 text-neutral-500" />
            <p className="text-sm text-neutral-400">No competitors yet</p>
            <p className="text-xs text-neutral-500">Run your first analysis to start tracking competitors</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {gridCompetitors.map((comp) => (
              <CompetitorCard key={comp.company_name} competitor={comp} />
            ))}
          </div>
        )}
      </div>

      {/* Recent Alerts Section */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground font-mono">Recent alerts</h2>
          <Link href="/alerts" className="text-sm text-[var(--link-accent)] hover:text-[var(--link-accent-hover)] transition-colors font-mono">
            View all &rarr;
          </Link>
        </div>
        {alertsLoading ? (
          <div className="space-y-4 rounded-xl border border-neutral-800 bg-card p-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-16 rounded-lg bg-neutral-800" />
            ))}
          </div>
        ) : !alerts?.items || alerts.items.length === 0 ? (
          <div className="flex flex-col items-center gap-3 rounded-xl border border-neutral-800 bg-card py-12 text-center">
            <AlertTriangle className="h-8 w-8 text-neutral-500" />
            <p className="text-sm text-neutral-400">No alerts yet</p>
            <p className="text-xs text-neutral-500">Alerts will appear here when intelligence signals are detected</p>
          </div>
        ) : (
          <div className="rounded-xl border border-neutral-800 bg-card px-4">
            {alerts.items.slice(0, 2).map((alert, i) => (
              <AlertRow key={alert.id || i} alert={alert} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
