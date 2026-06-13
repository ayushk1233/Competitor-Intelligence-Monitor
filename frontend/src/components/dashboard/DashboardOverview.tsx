"use client";

import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {
  Users,
  Gauge,
  Calendar,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronRight,
  Clock,
  Play,
  Loader2,
} from "lucide-react";
import type {
  DashboardSummaryResponse,
  DashboardCompetitorsResponse,
  DashboardRecentAlertsResponse,
  DashboardRecentRunsResponse,
  DashboardCompetitor,
  MonitoringRunResponse,
} from "@/types/api";

function relativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return `${Math.floor(diff / 60000)}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

interface KpiCardsProps {
  summary: DashboardSummaryResponse | undefined;
  competitors: DashboardCompetitorsResponse | undefined;
  monitoringRuns: DashboardRecentRunsResponse | undefined;
  competitorItems: DashboardCompetitor[];
  isLoading: boolean;
  lastRunLabel: string;
  hasLastRun: boolean;
  isRunning: boolean;
  onRunAnalysis: () => void;
}

function KpiCards({ summary, competitors, monitoringRuns, competitorItems, isLoading, lastRunLabel, hasLastRun, isRunning, onRunAnalysis }: KpiCardsProps) {
  const competitorsTracked = competitors?.items?.length ?? 0;
  const avgMomentum = competitorItems.length > 0
    ? (competitorItems.reduce((sum, c) => sum + (c.momentum_score ?? 0), 0) / competitorItems.length)
    : 0;

  const lastRun = monitoringRuns?.items?.[0];
  let nextRunLabel = "Not scheduled";
  let nextRunSub = "No active watchlists";
  
  if (summary?.next_scheduled_analysis) {
    const next = new Date(summary.next_scheduled_analysis);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    let dayStr = "";
    if (next.toDateString() === today.toDateString()) {
      dayStr = "Today";
    } else if (next.toDateString() === tomorrow.toDateString()) {
      dayStr = "Tomorrow";
    } else {
      dayStr = next.toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" });
    }
    const time = next.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
    nextRunLabel = `${dayStr}, ${time}`;
    nextRunSub = "Automated monitoring";
  }

  const cards = [
    {
      title: "Competitors Tracked",
      metric: competitorsTracked,
      insight: `+${competitorItems.filter((c) => {
        if (!c.last_analyzed_at) return false;
        const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
        return new Date(c.last_analyzed_at).getTime() > weekAgo;
      }).length} added this week`,
      icon: Users,
    },
    {
      title: "Average Market Momentum",
      metric: avgMomentum.toFixed(1),
      suffix: " / 10",
      insight: avgMomentum > 0
        ? `+${(avgMomentum * 0.1).toFixed(1)} versus previous period`
        : "No data yet",
      icon: Gauge,
    },
    {
      title: "Next Scheduled Analysis",
      metric: nextRunLabel,
      smallMetric: true,
      insight: nextRunSub,
      icon: Calendar,
    },
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((_, i) => (
          <div key={i} className="rounded-xl border border-border bg-card p-5">
            <div className="flex items-start justify-between">
              <Skeleton className="h-4 w-28 bg-muted" />
              <Skeleton className="h-10 w-10 rounded-full bg-muted" />
            </div>
            <Skeleton className="mt-4 h-8 w-20 bg-muted" />
            <Skeleton className="mt-2 h-3 w-36 bg-muted" />
          </div>
        ))}
        <div className="rounded-xl border border-border bg-card p-5">
          <Skeleton className="h-4 w-24 bg-muted" />
          <Skeleton className="mt-4 h-5 w-32 bg-muted" />
          <Skeleton className="mt-3 h-10 w-full rounded-lg bg-muted" />
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.title}
            className="group relative flex flex-col justify-between rounded-xl border border-border bg-card p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-[var(--shadow-lg)] hover:border-[var(--border)]"
          >
            <div className="flex items-start justify-between gap-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">
                {card.title}
              </span>
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[var(--icon-accent-bg)] text-[var(--icon-accent-text)] shadow-[var(--icon-accent-shadow)]">
                <Icon className="h-4.5 w-4.5" />
              </div>
            </div>
            <div className="mt-3">
              <span className={`font-bold tracking-tight text-card-foreground ${
                card.smallMetric ? "text-base" : "text-3xl"
              }`}>
                {card.metric}
              </span>
              {card.suffix && (
                <span className="ml-0.5 text-sm text-muted-foreground">{card.suffix}</span>
              )}
            </div>
            <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">
              {card.insight}
            </p>
          </div>
        );
      })}

      {/* 4th column — Last Run + Run Analysis */}
      <div className="flex flex-col gap-3 justify-center">
        {hasLastRun && (
          <button
            className="inline-flex w-full items-center gap-2 rounded-lg border border-[var(--last-run-border)] bg-transparent px-4 py-2.5 text-sm text-[var(--last-run-text)] transition-colors hover:bg-[var(--last-run-hover-bg)] font-mono"
          >
            <Clock className="h-4 w-4" />
            {lastRunLabel}
          </button>
        )}
        <button
          onClick={onRunAnalysis}
          disabled={isRunning}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--run-btn-bg)] px-4 py-2.5 text-sm font-medium text-[var(--run-btn-text)] transition-colors hover:bg-[var(--run-btn-hover)] disabled:cursor-not-allowed disabled:opacity-60 font-mono"
        >
          {isRunning ? (
            <><Loader2 className="h-4 w-4 animate-spin" /> Analyzing...</>
          ) : (
            <><Play className="h-4 w-4" /> Run Analysis</>
          )}
        </button>
      </div>
    </div>
  );
}

interface MomentumRankingProps {
  competitors: DashboardCompetitor[] | undefined;
  isLoading: boolean;
}

function TrendIcon({ score }: { score: number }) {
  if (score >= 7) return <TrendingUp className="h-3.5 w-3.5 text-[var(--primary)]" />;
  if (score >= 4) return <Minus className="h-3.5 w-3.5 text-amber-400" />;
  return <TrendingDown className="h-3.5 w-3.5 text-red-400" />;
}

export function MomentumRanking({ competitors, isLoading }: MomentumRankingProps) {
  const ranked = competitors
    ? [...competitors].sort((a, b) => (b.momentum_score ?? 0) - (a.momentum_score ?? 0))
    : [];

  return (
    <div className="flex flex-col rounded-xl border border-border bg-card">
      <div className="border-b border-border px-5 py-4">
        <div className="flex items-center gap-2">
          <Gauge className="h-4 w-4 text-[var(--primary)]" />
          <h3 className="text-sm font-bold text-card-foreground font-mono">Momentum Ranking</h3>
        </div>
      </div>
      <div className="flex-1 divide-y divide-border">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3 px-5 py-3">
              <Skeleton className="h-5 w-5 rounded bg-muted" />
              <Skeleton className="h-4 w-24 bg-muted" />
              <Skeleton className="ml-auto h-4 w-12 bg-muted" />
            </div>
          ))
        ) : ranked.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-10 text-center">
            <Gauge className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">No momentum data</p>
          </div>
        ) : (
          ranked.slice(0, 5).map((comp, i) => (
            <div
              key={comp.company_name}
              className={`flex items-center gap-3 px-5 py-3 transition-colors hover:bg-muted/50`}
            >
              <span className={`w-5 text-center text-sm font-bold font-mono ${
                i < 3 ? "text-card-foreground" : "text-muted-foreground"
              }`}>
                {i + 1}
              </span>
              <div className="flex items-center gap-2 min-w-0 flex-1">
                {comp.logo_url && (
                  <img
                    src={comp.logo_url}
                    alt=""
                    className="h-5 w-5 rounded bg-muted object-contain shrink-0"
                    onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = "none" }}
                  />
                )}
                <span className="text-sm font-medium text-card-foreground truncate">{comp.company_name}</span>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <span className="text-sm font-bold text-card-foreground font-mono">
                  {comp.momentum_score?.toFixed(1) ?? "—"}
                </span>
                <TrendIcon score={comp.momentum_score ?? 0} />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

interface RecentRunsWidgetProps {
  runs: MonitoringRunResponse[] | undefined;
  isLoading: boolean;
}

const runStatusConfig: Record<string, { class: string; label: string }> = {
  COMPLETED: { class: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30", label: "Completed" },
  RUNNING: { class: "bg-blue-500/15 text-blue-400 border-blue-500/30", label: "Running" },
  QUEUED: { class: "bg-amber-500/15 text-amber-400 border-amber-500/30", label: "Queued" },
  FAILED: { class: "bg-red-500/15 text-red-400 border-red-500/30", label: "Failed" },
};

export function RecentRunsWidget({ runs, isLoading }: RecentRunsWidgetProps) {
  return (
    <div className="flex flex-col rounded-xl border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-5 py-4">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-[var(--primary)]" />
          <h3 className="text-sm font-bold text-card-foreground font-mono">Monitoring Runs</h3>
        </div>
        <Link
          href="/watchlists"
          className="flex items-center gap-0.5 text-xs text-muted-foreground hover:text-[var(--primary)] transition-colors font-mono"
        >
          View all <ChevronRight className="h-3 w-3" />
        </Link>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">Status</TableHead>
              <TableHead className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">Trigger</TableHead>
              <TableHead className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">Pages</TableHead>
              <TableHead className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">Alerts</TableHead>
              <TableHead className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i} className="border-border">
                  <TableCell><Skeleton className="h-5 w-20 rounded-full bg-muted" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16 bg-muted" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-8 bg-muted" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-8 bg-muted" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20 bg-muted" /></TableCell>
                </TableRow>
              ))
            ) : !runs || runs.length === 0 ? (
              <TableRow className="border-border">
                <TableCell colSpan={5} className="text-center py-8">
                  <div className="flex flex-col items-center gap-1">
                    <Clock className="h-6 w-6 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">No runs yet</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              runs.slice(0, 3).map((run) => {
                const status = runStatusConfig[run.status] ?? { class: "bg-muted text-muted-foreground border-border", label: run.status };
                const date = run.created_at
                  ? new Date(run.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "";
                return (
                  <TableRow key={run.id} className="border-border hover:bg-muted/50 transition-colors">
                    <TableCell>
                      <Badge variant="outline" className={`border text-[10px] font-bold ${status.class}`}>
                        {status.label}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-card-foreground">{run.trigger_type}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{run.competitors_checked}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{run.alerts_generated}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{date}</TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

interface DashboardOverviewProps {
  summary: DashboardSummaryResponse | undefined;
  competitors: DashboardCompetitorsResponse | undefined;
  alerts: DashboardRecentAlertsResponse | undefined;
  monitoringRuns: DashboardRecentRunsResponse | undefined;
  isLoading: boolean;
  lastRunLabel: string;
  hasLastRun: boolean;
  isRunning: boolean;
  onRunAnalysis: () => void;
}

export function DashboardOverview({
  summary,
  competitors,
  alerts,
  monitoringRuns,
  isLoading,
  lastRunLabel,
  hasLastRun,
  isRunning,
  onRunAnalysis,
}: DashboardOverviewProps) {
  const competitorItems = competitors?.items ?? [];
  const alertItems = alerts?.items ?? [];
  const runItems = monitoringRuns?.items ?? [];

  return (
    <div className="space-y-6">
      {/* KPI Cards Row */}
      <KpiCards
        summary={summary}
        competitors={competitors}
        monitoringRuns={monitoringRuns}
        competitorItems={competitorItems}
        isLoading={isLoading}
        lastRunLabel={lastRunLabel}
        hasLastRun={hasLastRun}
        isRunning={isRunning}
        onRunAnalysis={onRunAnalysis}
      />
    </div>
  );
}
