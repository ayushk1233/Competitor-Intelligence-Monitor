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
import { NewAnalysisModal } from "@/components/dashboard/NewAnalysisModal";
import { RecentRunsTable } from "@/components/dashboard/RecentRunsTable";
import { Clock, Play, AlertTriangle, TrendingUp, TrendingDown, Minus, Lightbulb, Loader2 } from "lucide-react";
import type { DashboardAlertResponse, DashboardCompetitor } from "@/types/api";

const toneColors: Record<string, string> = {
  enterprise: "bg-emerald-950 text-emerald-400",
  startup: "bg-emerald-950 text-emerald-400",
  technical: "bg-emerald-950 text-emerald-400",
  visionary: "bg-amber-950 text-amber-400",
  hybrid: "bg-purple-950 text-purple-400",
};

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
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-base font-bold text-white">{competitor.company_name}</span>
            {hasAlerts && <span className={`h-2 w-2 rounded-full shrink-0 ${dotClass}`} />}
          </div>
          {competitor.domain && (
            <p className="text-xs text-neutral-500 truncate mt-0.5">{competitor.domain}</p>
          )}
        </div>
        {competitor.momentum_score !== null && competitor.momentum_score !== undefined && (
          <div className="flex items-center gap-1">
            <svg className="h-3.5 w-3.5 text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
            </svg>
            <span className="text-xs text-neutral-500">Momentum</span>
            <span className="text-lg font-bold text-white">{competitor.momentum_score}</span>
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
          <span className="text-sm font-bold text-white">{alert.company_name}</span>
          <span className={`${s.pill} ${s.pillText} px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide`}>
            {label}
          </span>
        </div>
        <span className="shrink-0 text-xs text-neutral-500">
          {alert.created_at ? relativeTime(alert.created_at) : ""}
        </span>
      </div>
      <p className="text-sm text-white leading-relaxed mt-1.5">{alert.headline}</p>
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

  const isRunning = summary?.has_active_run;
  const runStatus = activeRunStatus?.status || summary?.active_run_status;

  const stageLabels: Record<string, string> = {
    queued: "Queued",
    scraping: "Scraping pages...",
    analyzing: "Analyzing competitors...",
    comparing: "Generating comparison...",
  };

  const lastRunTimestamp = latestCompletedRun?.created_at ?? summary?.last_run_at;
  const lastRunLabel = lastRunTimestamp
    ? `Last run ${relativeTime(lastRunTimestamp)}`
    : "No runs yet";

  const latestCompetitorNames = new Set(latestCompletedRun?.competitors ?? []);
  const topCompetitors = competitors?.items
    ? competitors.items
        .filter((c) => latestCompetitorNames.has(c.company_name))
        .sort((a, b) => (b.momentum_score ?? 0) - (a.momentum_score ?? 0))
        .slice(0, 3)
    : [];

  const distinctFromRuns = new Set<string>();
  for (const run of completedRuns) {
    for (const name of run.competitors ?? []) {
      distinctFromRuns.add(name);
    }
    if (distinctFromRuns.size >= 6) break;
  }
  const gridCompetitors = competitors?.items
    ? competitors.items
        .filter((c) => distinctFromRuns.has(c.company_name))
        .sort((a, b) => (b.momentum_score ?? 0) - (a.momentum_score ?? 0))
    : [];

  return (
    <div className="p-8">
      {/* Top Action Bar */}
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button className="inline-flex items-center gap-2 rounded-lg border border-[#BC6C50]/40 bg-transparent px-4 py-2 text-sm text-terracotta transition-colors hover:bg-[#140A07]/30">
            <Clock className="h-4 w-4" />
            {lastRunLabel}
          </button>
          <button
            onClick={() => setAnalysisOpen(true)}
            disabled={isRunning}
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isRunning ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Analyzing...</>
            ) : (
              <><Play className="h-4 w-4" /> Run Analysis</>
            )}
          </button>
        </div>
      </div>

      <NewAnalysisModal open={analysisOpen} onClose={() => setAnalysisOpen(false)} />

      {isRunning && (
        <div className="mb-6 rounded-xl border border-emerald-500/30 bg-emerald-950/20 px-5 py-4">
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-emerald-400" />
            <div>
              <p className="text-sm font-medium text-white">Analysis in progress</p>
              <p className="text-xs text-emerald-400/80 mt-0.5">
                {stageLabels[runStatus || ""] || "Working..."}
              </p>
            </div>
            <div className="ml-auto flex items-center gap-2">
              {activeRunStatus && (
                <span className="text-xs text-neutral-500">
                  {activeRunStatus.pages_fetched} page{activeRunStatus.pages_fetched !== 1 ? "s" : ""} fetched
                </span>
              )}
            </div>
          </div>
          <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-neutral-800">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-500"
              style={{ width: `${activeRunStatus?.progress_percent || 5}%` }}
            />
          </div>
        </div>
      )}

      {/* Latest Intelligence Peek */}
      {topCompetitors.length > 0 && (
        <div className="mb-8">
          <div className="mb-4 flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-emerald-500" />
            <h2 className="text-lg font-bold text-white">Latest Intelligence</h2>
            {latestCompletedRunId && (
              <Link
                href={`/reports/${latestCompletedRunId}`}
                className="ml-auto text-sm text-emerald-500 hover:text-emerald-400 transition-colors"
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
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white">{comp.company_name}</span>
                      <MomentumIcon score={comp.momentum_score ?? 0} />
                    </div>
                    <span className="text-xs text-neutral-500">Score: {comp.momentum_score ?? "—"}/10</span>
                  </div>
                </div>
                {comp.core_offering && (
                  <p className="text-xs text-neutral-400 leading-relaxed line-clamp-2 mb-2">
                    {comp.core_offering}
                  </p>
                )}
                {comp.analyst_note && (
                  <p className="text-xs text-neutral-500 leading-relaxed line-clamp-3 italic">
                    &ldquo;{comp.analyst_note}&rdquo;
                  </p>
                )}
              </div>
            );
          })}
          </div>
        </div>
      )}

      {/* Competitors Grid Section */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">Competitors</h2>
          <Link href="/run-history" className="text-sm text-emerald-500 hover:text-emerald-400 transition-colors">
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

      {/* Monitoring Runs */}
      <div className="mb-8">
        <RecentRunsTable runs={monitoringRuns?.items?.slice(0, 2)} isLoading={monitoringLoading} />
        {monitoringRuns && monitoringRuns.items.length > 2 && (
          <div className="mt-2 text-right">
            <Link href="/watchlists" className="text-sm text-emerald-500 hover:text-emerald-400 transition-colors">
              View all &rarr;
            </Link>
          </div>
        )}
      </div>

      {/* Recent Alerts Section */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">Recent alerts</h2>
          <Link href="/alerts" className="text-sm text-emerald-500 hover:text-emerald-400 transition-colors">
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
