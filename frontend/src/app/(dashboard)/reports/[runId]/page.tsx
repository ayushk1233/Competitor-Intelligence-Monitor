"use client";

import { use, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ROUTES } from "@/constants";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Target,
  Zap,
  Lightbulb,
  Hash,
  Package,
  MessageSquare,
  Building2,
  DollarSign,
  Users,
  AlertTriangle,
  Swords,
  Trophy,
  Rocket,
  Trash2,
  Loader2,
  Activity,
  Shield,
  AlertCircle,
  BarChart3,
  ChevronDown,
  ChevronRight,
  Quote,
  ExternalLink,
  CheckCircle2,
  XCircle,
  AlertOctagon,
  Database,
  FileSpreadsheet,
  Star,
  Info,
} from "lucide-react";
import type { IntelligenceReport, CompetitorAnalysisReport, ComparisonResult, DashboardAlertResponse } from "@/types/api";

interface ReportPageProps {
  params: Promise<{ runId: string }>;
}

const toneColors: Record<string, string> = {
  enterprise: "bg-[#6366F1]/15 text-[#6366F1] border-[#6366F1]/30",
  startup: "bg-[#BC6C50]/15 text-[#BC6C50] border-[#BC6C50]/30",
  technical: "bg-[#3B82F6]/15 text-[#3B82F6] border-[#3B82F6]/30",
  visionary: "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30",
  hybrid: "bg-[#8B5CF6]/15 text-[#8B5CF6] border-[#8B5CF6]/30",
};

const severityColors: Record<string, string> = {
  critical: "bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30",
  high: "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30",
  medium: "bg-[#3B82F6]/15 text-[#3B82F6] border-[#3B82F6]/30",
  low: "bg-[#6B7280]/15 text-[var(--muted-text)] border-[#6B7280]/30",
};

function ConfidenceBadge({ confidence }: { confidence: number }) {
  if (confidence === 0 || (!confidence && confidence !== 0)) return null;
  const color =
    confidence >= 90
      ? "bg-[#22C55E]/15 text-[#22C55E] border-[#22C55E]/30"
      : confidence >= 70
        ? "bg-[#3B82F6]/15 text-[#3B82F6] border-[#3B82F6]/30"
        : confidence >= 40
          ? "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30"
          : "bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30";
  return (
    <Badge variant="outline" className={`text-[10px] font-mono ${color}`}>
      {confidence}%
    </Badge>
  );
}

function EvidenceBlock({ evidence, source }: { evidence?: string[]; source?: string }) {
  const [open, setOpen] = useState(false);
  if (!evidence || evidence.length === 0) return null;
  return (
    <div className="mt-1.5">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-[11px] text-[#2DD4BF] hover:text-[#2DD4BF]/80 transition-colors"
      >
        {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
        <Quote className="h-3 w-3" />
        Evidence{source ? ` (${source})` : ""}
      </button>
      {open && (
        <div className="mt-1.5 space-y-1 border-l-2 border-[#2DD4BF]/20 pl-3">
          {evidence.map((e, i) => (
            <p key={i} className="text-xs italic text-muted-foreground">
              &ldquo;{e}&rdquo;
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

function SectionHeading({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">
      {icon}
      {label}
    </p>
  );
}

function CollapsibleSection({
  icon,
  label,
  summary,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  summary?: React.ReactNode;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-t border-border pt-4">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-2 text-left group"
      >
        <span className="flex items-center gap-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground font-mono flex items-center gap-1.5">
            {icon}{label}
          </span>
          {!open && summary && (
            <span className="hidden sm:flex items-center gap-1.5 truncate max-w-xs">{summary}</span>
          )}
        </span>
        <span className="text-[var(--muted-text)] group-hover:text-foreground transition-colors">
          {open ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
        </span>
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
}

function StarRating({ score }: { score: number }) {
  const filled = Math.round(score);
  const total = 10;
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex gap-0.5">
        {Array.from({ length: total }).map((_, i) => (
          <Star
            key={i}
            className={`h-3.5 w-3.5 ${i < filled ? "text-[#F59E0B] fill-[#F59E0B]" : "text-[var(--muted-text)]"}`}
          />
        ))}
      </div>
      <span className="ml-1 text-lg font-bold text-foreground">{score}</span>
      <span className="text-xs text-[var(--muted-text)]">/10</span>
    </div>
  );
}

function ScoreMeter({ score }: { score: number }) {
  const segments = 10;
  const filled = Math.round((score / 10) * segments);
  return (
    <div className="flex items-center gap-2">
      <span className={`text-2xl font-bold ${score >= 7 ? "text-[#22C55E]" : score >= 4 ? "text-[#2DD4BF]" : "text-[#EF4444]"}`}>
        {score}
      </span>
      <span className="text-[11px] text-[var(--muted-text)]">/ 10</span>
      <div className="ml-1 flex gap-0.5">
        {Array.from({ length: segments }).map((_, i) => (
          <div
            key={i}
            className={`h-2 w-2 rounded-sm ${
              i < filled
                ? score >= 7
                  ? "bg-[#22C55E]"
                  : score >= 4
                    ? "bg-[#2DD4BF]"
                    : "bg-[#EF4444]"
                : "bg-muted"
            }`}
          />
        ))}
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  status,
  evidence,
  source,
  confidence,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  value?: string | null;
  status?: string | null;
  evidence?: string[];
  source?: string;
  confidence?: number;
  children?: React.ReactNode;
}) {
  const displayValue = value && value !== "Not detected" && value !== "" ? value : null;
  const displayStatus = status && status !== "Not detected" && status !== "" ? status : null;
  return (
    <div className="rounded-lg border border-border bg-muted p-3.5 flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[#2DD4BF]">{icon}</span>
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">{label}</span>
        </div>
        {confidence !== undefined && <ConfidenceBadge confidence={confidence} />}
      </div>
      {displayValue && (
        <p className="text-sm text-foreground leading-relaxed">{displayValue}</p>
      )}
      {!displayValue && displayStatus && (
        <p className="text-sm text-muted-foreground">{displayStatus}</p>
      )}
      {!displayValue && !displayStatus && (
        <p className="text-sm italic text-[var(--muted-text)]">No public evidence found</p>
      )}
      {children}
      {displayValue && <EvidenceBlock evidence={evidence} source={source} />}
    </div>
  );
}

function MomentumHero({ c }: { c: CompetitorAnalysisReport }) {
  const positiveCount = c.momentum_evidence?.length ?? 0;
  const negativeCount = c.momentum_negative_factors?.length ?? 0;
  const score = c.momentum_score;

  const momentumLabel =
    score >= 7
      ? "Strong momentum — gaining market traction"
      : score >= 4
        ? "Moderate momentum — steady but not dominant"
        : "Low momentum — potential vulnerability";

  const hasNoHiring = !c.hiring_signals || c.hiring_signals === "Not detected" || c.hiring_signals === "No public evidence found" || c.hiring_signals === "";

  return (
    <div className="rounded-lg border border-border bg-gradient-to-br from-card to-muted p-5">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="h-4 w-4 text-[#2DD4BF]" />
        <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">Momentum Score</span>
      </div>

      {/* Gauge + Stars */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="flex items-center gap-3">
          <StarRating score={score} />
        </div>
        <div className="flex-1">
          <ScoreMeter score={score} />
        </div>
      </div>

      {/* Score description */}
      <p className="mt-3 text-sm text-foreground">{momentumLabel}</p>

      {/* Hiring alert */}
      {hasNoHiring && (
        <div className="mt-3 flex items-center gap-2 rounded-md bg-[#EF4444]/10 border border-[#EF4444]/20 px-3 py-2">
          <AlertOctagon className="h-3.5 w-3.5 text-[#EF4444] shrink-0" />
          <span className="text-xs text-[#EF4444] font-medium">No hiring activity detected.</span>
        </div>
      )}

      {/* Drivers + Negative Factors */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {positiveCount > 0 && (
          <div>
            <p className="flex items-center gap-1 text-xs font-semibold text-[#10B981] font-mono">
              <TrendingUp className="h-3 w-3" />
              Drivers
            </p>
            <div className="mt-1.5 space-y-1">
              {c.momentum_evidence!.map((ev, i) => (
                <p key={i} className="flex items-start gap-1.5 text-xs text-foreground">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#10B981]" />
                  {ev}
                </p>
              ))}
            </div>
          </div>
        )}
        {negativeCount > 0 && (
          <div>
            <p className="flex items-center gap-1 text-xs font-semibold text-[#EF4444] font-mono">
              <TrendingDown className="h-3 w-3" />
              Negative Factors
            </p>
            <div className="mt-1.5 space-y-1">
              {c.momentum_negative_factors!.map((factor, i) => (
                <p key={i} className="flex items-start gap-1.5 text-xs text-foreground">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#EF4444]" />
                  {factor}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Reasoning */}
      {c.momentum_reasoning && (
        <div className="mt-4 border-t border-border pt-3">
          <p className="text-[11px] text-[var(--muted-text)] font-mono mb-1">Why this score</p>
          <p className="text-xs text-foreground leading-relaxed">{c.momentum_reasoning}</p>
        </div>
      )}
    </div>
  );
}

function CompetitorSection({ c, alerts }: { c: CompetitorAnalysisReport; alerts: DashboardAlertResponse[] }) {
  const competitorAlerts = alerts.filter((a) => a.company_name === c.name);
  const hasDrift = competitorAlerts.length > 0;
  const maxSeverity = hasDrift
    ? competitorAlerts.reduce(
        (max, a) => {
          const order = { critical: 4, high: 3, medium: 2, low: 1 } as Record<string, number>;
          return (order[a.severity] || 0) > (order[max] || 0) ? a.severity : max;
        },
        competitorAlerts[0].severity,
      )
    : null;

  // Key Insight (analyst_note)
  const keyInsight = c.analyst_note?.replace(/^Key Insight:\s*/i, "").trim() || "";

  return (
    <div className="rounded-xl border border-border bg-card shadow-lg overflow-hidden">
      {/* ── HEADER ── */}
      <div className="flex items-start justify-between p-6 pb-4 border-b border-border">
        <div className="flex items-center gap-4">
          {c.logo_url && (
            <img
              src={c.logo_url}
              alt={`${c.name} logo`}
              className="h-12 w-12 rounded-xl bg-muted object-contain shrink-0"
              onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = "none" }}
            />
          )}
          <div>
            <h2 className="text-xl font-bold text-foreground">{c.name}</h2>
            <p className="text-sm text-[var(--muted-text)] mt-0.5">{c.domain}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <StarRating score={c.momentum_score} />
          {hasDrift && (
            <Badge variant="outline" className={`text-[10px] font-medium capitalize ${severityColors[maxSeverity!]}`}>
              <Activity className="mr-1 h-3 w-3" />
              Drift Detected
            </Badge>
          )}
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* ── EXECUTIVE OVERVIEW ── */}
        {(c.validation?.company_description || c.core_offering) && (
          <div className="space-y-3">
            <SectionHeading icon={<Lightbulb className="h-3.5 w-3.5 text-[#2DD4BF]" />} label="Executive Overview" />

            {/* Company metadata line */}
            {c.validation?.company_description && (
              <p className="text-xs text-muted-foreground leading-relaxed">{c.validation.company_description}</p>
            )}
            {c.validation?.category || c.validation?.product_type || c.validation?.primary_use_case ? (
              <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-[var(--muted-text)]">
                {c.validation?.category && (
                  <span><span className="font-semibold text-muted-foreground">Category:</span> {c.validation.category}</span>
                )}
                {c.validation?.product_type && (
                  <span><span className="font-semibold text-muted-foreground">Type:</span> {c.validation.product_type}</span>
                )}
                {c.validation?.primary_use_case && (
                  <span className="w-full"><span className="font-semibold text-muted-foreground">Customers:</span> {c.validation.primary_use_case}</span>
                )}
              </div>
            ) : null}

            {/* Core offering */}
            <p className="text-sm text-foreground leading-relaxed">{c.core_offering}</p>
          </div>
        )}

        {/* ── VALIDATION WARNING CALLOUT ── */}
        {c.validation?.validation_warning && (
          <div className="rounded-lg border border-amber-400/40 bg-[#FEF3C7] px-4 py-3">
            <div className="flex items-start gap-3">
              <AlertOctagon className="h-4 w-4 shrink-0 text-[#D97706] mt-0.5" />
              <div>
                <p className="text-xs font-semibold text-[#92400E] font-mono">Validation Warning</p>
                <p className="text-xs text-[#92400E]/80 mt-0.5">
                  {c.validation?.reason
                    ? `Low confidence in company identification: ${c.validation.reason}`
                    : "Low confidence in company identification. The extracted intelligence may be unreliable."}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ── KEY INSIGHT ── */}
        {keyInsight && (
          <div className="rounded-lg border border-[#2DD4BF]/20 bg-[#2DD4BF]/5 p-3.5">
            <SectionHeading icon={<Lightbulb className="h-3.5 w-3.5 text-[#2DD4BF]" />} label="Key Insight" />
            <p className="mt-1 text-sm text-foreground leading-relaxed">{keyInsight}</p>
          </div>
        )}

        {/* ── KEY SIGNALS GRID ── */}
        {(c.momentum_evidence?.length || c.momentum_negative_factors?.length) && (
          <div className="space-y-3">
            <SectionHeading icon={<Info className="h-3.5 w-3.5 text-[#2DD4BF]" />} label="Key Signals" />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Key Strengths */}
              <div className="rounded-lg border border-[#10B981]/20 bg-[#10B981]/5 p-3.5">
                <p className="flex items-center gap-1.5 text-xs font-semibold text-[#10B981] font-mono">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Key Strengths
                </p>
                <ul className="mt-2 space-y-1.5">
                  {c.momentum_evidence?.map((ev, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-foreground">
                      <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#10B981]" />
                      {ev}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Key Risks */}
              <div className="rounded-lg border border-[#EF4444]/20 bg-[#EF4444]/5 p-3.5">
                <p className="flex items-center gap-1.5 text-xs font-semibold text-[#EF4444] font-mono">
                  <XCircle className="h-3.5 w-3.5" />
                  Key Risks
                </p>
                <ul className="mt-2 space-y-1.5">
                  {c.momentum_negative_factors?.map((factor, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-foreground">
                      <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#EF4444]" />
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* ── DETAILED METRICS GRID ── */}
        <div className="space-y-3">
          <SectionHeading icon={<Activity className="h-3.5 w-3.5 text-[#2DD4BF]" />} label="Detailed Metrics" />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {/* Positioning */}
            <MetricCard
              icon={<Zap className="h-4 w-4" />}
              label="Position"
              value={c.core_offering}
              evidence={c.core_offering_evidence}
              source={c.core_offering_source}
              confidence={c.core_offering_confidence ?? c.confidence_scores?.core_offering}
            />
            {/* Target Market */}
            <MetricCard
              icon={<Target className="h-4 w-4" />}
              label="Target Market"
              value={c.icp}
              evidence={c.icp_evidence}
              confidence={c.confidence_scores?.icp}
            />
            {/* Tone */}
            <MetricCard
              icon={<MessageSquare className="h-4 w-4" />}
              label="Tone"
              status={c.messaging_tone}
              evidence={c.tone_evidence}
              confidence={c.confidence_scores?.tone}
            >
              {c.messaging_tone && (
                <Badge variant="outline" className={`mt-1 text-[11px] font-medium capitalize ${toneColors[c.messaging_tone] ?? "bg-muted text-muted-foreground border-border"}`}>
                  {c.messaging_tone}
                </Badge>
              )}
            </MetricCard>
            {/* Pricing */}
            <MetricCard
              icon={<DollarSign className="h-4 w-4" />}
              label="Pricing"
              value={c.pricing_signals}
              evidence={c.pricing_evidence}
              source={c.pricing_source}
              confidence={c.pricing_confidence ?? c.confidence_scores?.pricing}
            />
            {/* Hiring */}
            <MetricCard
              icon={<Users className="h-4 w-4" />}
              label="Hiring"
              value={c.hiring_signals}
              evidence={c.hiring_evidence}
              source={c.hiring_source}
              confidence={c.hiring_confidence ?? c.confidence_scores?.hiring}
            />
            {/* Risk Flags */}
            {c.risk_flags.length > 0 && (
              <MetricCard
                icon={<AlertCircle className="h-4 w-4" />}
                label="Risk Flags"
                value={c.risk_flags.join(", ")}
                evidence={undefined}
              />
            )}
          </div>
        </div>

        {/* ── STRATEGIC KEYWORDS ── */}
        {c.strategic_keywords.length > 0 && (
          <div className="space-y-2.5">
            <SectionHeading icon={<Hash className="h-3.5 w-3.5 text-[#2DD4BF]" />} label="Strategic Keywords" />
            <div className="flex flex-wrap gap-1.5">
              {c.strategic_keywords.filter(Boolean).map((kw, i) => (
                <Badge
                  key={i}
                  variant="outline"
                  className="border-border bg-muted text-xs text-foreground font-mono"
                >
                  {kw}
                </Badge>
              ))}
            </div>
            <EvidenceBlock evidence={c.keywords_evidence} />
          </div>
        )}

        {/* ── RECENT SIGNALS ── */}
        {(c.recent_launches.length > 0 || c.growth_signals.length > 0) && (
          <div className="space-y-2.5">
            <SectionHeading icon={<Package className="h-3.5 w-3.5 text-[#2DD4BF]" />} label="Recent Signals" />
            <div className="space-y-1.5">
              {c.recent_launches.map((signal, i) => (
                <p key={i} className="flex items-start gap-2 text-sm text-foreground">
                  <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#BC6C50]" />
                  {signal}
                </p>
              ))}
              {c.growth_signals.map((signal, i) => (
                <p key={i} className="flex items-start gap-2 text-sm text-foreground">
                  <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#10B981]" />
                  {signal}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* ── DRIFT ANALYSIS ── */}
        {hasDrift && (
          <div className="space-y-3">
            <SectionHeading icon={<Activity className="h-3.5 w-3.5 text-[#EF4444]" />} label="Drift Analysis" />
            <p className="text-xs text-[#EF4444]/70 mt-1">Changes detected since last analysis run</p>
            <div className="space-y-3">
              {competitorAlerts.map((alert) => (
                <div key={alert.id} className="rounded-lg border border-border bg-muted p-3 space-y-1.5">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={`text-[10px] font-medium capitalize ${severityColors[alert.severity] ?? "bg-[#6B7280]/15 text-[var(--muted-text)]"}`}>
                      {alert.severity}
                    </Badge>
                    <span className="text-sm font-medium text-foreground">{alert.headline}</span>
                  </div>
                  {alert.summary && <p className="text-sm text-foreground">{alert.summary}</p>}
                  {alert.evidence && alert.evidence.length > 0 && (
                    <div className="space-y-0.5 pl-1">
                      {alert.evidence.map((e, i) => (
                        <p key={i} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                          <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-[#6B7280]" />
                          {e}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className={`text-xs font-medium ${severityColors[maxSeverity!]}`}>
                <AlertCircle className="mr-1 h-3 w-3" />
                {competitorAlerts.length} {competitorAlerts.length === 1 ? "Alert" : "Alerts"}
              </Badge>
              <span className="text-xs text-[var(--muted-text)]">
                Last alert: {new Date(competitorAlerts[0].created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        )}
        {!hasDrift && (
          <div className="flex items-center gap-2 text-xs text-[var(--muted-text)]">
            <Shield className="h-3.5 w-3.5 text-[#10B981]" />
            No drift detected — competitor state consistent with previous analysis
          </div>
        )}

        {/* ── MOMENTUM SCORE HERO ── */}
        <MomentumHero c={c} />

        {/* ── COMPETITOR DNA (v1.2.x) — collapsed by default ── */}
        {c.competitor_dna?.archetype && (
          <CollapsibleSection
            icon={<Swords className="h-3.5 w-3.5 text-[#8B5CF6]" />}
            label="Competitor DNA"
            summary={
              <span className="flex items-center gap-2">
                <Badge variant="outline" className="text-[10px] font-mono bg-[#8B5CF6]/10 text-[#8B5CF6] border-[#8B5CF6]/30">
                  {c.competitor_dna.archetype}
                </Badge>
                {c.competitor_dna.confidence !== undefined && (
                  <span className="text-[10px] text-[var(--muted-text)] font-mono">
                    {Math.round(c.competitor_dna.confidence * 100)}% confidence
                  </span>
                )}
              </span>
            }
          >
            <div className="space-y-4 pt-1">
              {/* Archetype + Confidence bar */}
              <div className="flex items-center gap-3 flex-wrap">
                <Badge variant="outline" className="text-xs font-semibold bg-[#8B5CF6]/10 text-[#8B5CF6] border-[#8B5CF6]/30 px-3 py-1">
                  {c.competitor_dna.archetype}
                </Badge>
                {c.competitor_dna.confidence !== undefined && (
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-24 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full rounded-full bg-[#8B5CF6]"
                        style={{ width: `${Math.round(c.competitor_dna.confidence * 100)}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-[var(--muted-text)]">
                      {Math.round(c.competitor_dna.confidence * 100)}%
                    </span>
                  </div>
                )}
              </div>

              {/* Supporting Signals */}
              {c.competitor_dna.supporting_signals && c.competitor_dna.supporting_signals.length > 0 && (
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)] mb-1.5">Supporting Signals</p>
                  <div className="flex flex-wrap gap-1.5">
                    {c.competitor_dna.supporting_signals.map((sig, i) => (
                      <Badge key={i} variant="outline" className="text-[10px] font-mono bg-[#2DD4BF]/10 text-[#2DD4BF] border-[#2DD4BF]/20">
                        {sig}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* DNA Attribute Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                {c.competitor_dna.growth_model && (
                  <div className="rounded-lg bg-muted border border-border p-3">
                    <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)]">Growth Model</p>
                    <p className="text-xs text-foreground mt-0.5">{c.competitor_dna.growth_model}</p>
                  </div>
                )}
                {c.competitor_dna.primary_moat && (
                  <div className="rounded-lg bg-muted border border-border p-3">
                    <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)]">Primary Moat</p>
                    <p className="text-xs text-foreground mt-0.5">{c.competitor_dna.primary_moat}</p>
                  </div>
                )}
                {c.competitor_dna.strategic_risk && (
                  <div className="rounded-lg bg-muted border border-border p-3">
                    <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)]">Strategic Risk</p>
                    <p className="text-xs text-foreground mt-0.5">{c.competitor_dna.strategic_risk}</p>
                  </div>
                )}
              </div>

              {/* Expansion Vector */}
              {c.competitor_dna.expansion_vector && (
                <div className="rounded-lg border border-[#8B5CF6]/20 bg-[#8B5CF6]/5 p-3">
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[#8B5CF6] mb-1">Expansion Vector</p>
                  <p className="text-xs text-foreground leading-relaxed">{c.competitor_dna.expansion_vector}</p>
                </div>
              )}

              {/* Likely Next Moves */}
              {c.competitor_dna.likely_next_moves && c.competitor_dna.likely_next_moves.length > 0 && (
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)] mb-1.5">Likely Next Moves</p>
                  <div className="space-y-1.5">
                    {c.competitor_dna.likely_next_moves.map((move, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs text-foreground">
                        <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#8B5CF6]" />
                        <span className="flex-1">{move.hypothesis}</span>
                        <Badge variant="outline" className="text-[9px] font-mono shrink-0 capitalize">
                          {move.confidence}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Alternative Archetypes */}
              {c.competitor_dna.alternative_archetypes && c.competitor_dna.alternative_archetypes.length > 0 && (
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)] mb-1.5">Alternative Archetypes</p>
                  <div className="flex flex-wrap gap-2">
                    {c.competitor_dna.alternative_archetypes.map((alt, i) => (
                      <div key={i} className="flex items-center gap-1.5">
                        <Badge variant="outline" className="text-[10px] font-mono bg-muted text-muted-foreground border-border">
                          {alt.archetype}
                        </Badge>
                        <span className="text-[10px] text-[var(--muted-text)] font-mono">
                          {Math.round(alt.confidence * 100)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CollapsibleSection>
        )}

        {/* ── STRATEGIC INTERPRETATION (v1.2.x) — collapsed by default ── */}
        {c.strategic_interpretation && Object.keys(c.strategic_interpretation).length > 0 && (
          <CollapsibleSection
            icon={<Lightbulb className="h-3.5 w-3.5 text-[#F59E0B]" />}
            label="Strategic Interpretation"
            summary={
              c.strategic_interpretation.strategic_direction
                ? <span className="text-[10px] text-[var(--muted-text)] font-mono truncate">{c.strategic_interpretation.strategic_direction}</span>
                : undefined
            }
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-1">
              {c.strategic_interpretation.strategic_direction && (
                <div className="rounded-lg bg-muted border border-border p-3 md:col-span-2">
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[#F59E0B]">Strategic Direction</p>
                  <p className="text-xs text-foreground mt-0.5 leading-relaxed">{c.strategic_interpretation.strategic_direction}</p>
                </div>
              )}
              {c.strategic_interpretation.commercial_signal && (
                <div className="rounded-lg bg-muted border border-border p-3">
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)]">Commercial Signal</p>
                  <p className="text-xs text-foreground mt-0.5 leading-relaxed">{c.strategic_interpretation.commercial_signal}</p>
                </div>
              )}
              {c.strategic_interpretation.expansion_signal && (
                <div className="rounded-lg bg-muted border border-border p-3">
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)]">Expansion Signal</p>
                  <p className="text-xs text-foreground mt-0.5 leading-relaxed">{c.strategic_interpretation.expansion_signal}</p>
                </div>
              )}
              {c.strategic_interpretation.defensibility_signal && (
                <div className="rounded-lg bg-muted border border-border p-3">
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)]">Defensibility Signal</p>
                  <p className="text-xs text-foreground mt-0.5 leading-relaxed">{c.strategic_interpretation.defensibility_signal}</p>
                </div>
              )}
              {c.strategic_interpretation.market_position && (
                <div className="rounded-lg bg-muted border border-border p-3">
                  <p className="text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)]">Market Position</p>
                  <p className="text-xs text-foreground mt-0.5 leading-relaxed">{c.strategic_interpretation.market_position}</p>
                </div>
              )}
            </div>
          </CollapsibleSection>
        )}

        {/* ── INTELLIGENCE CONFIDENCE (v1.2.3) — collapsed by default ── */}
        {c.confidence_metrics && Object.keys(c.confidence_metrics).length > 0 && (() => {
          const metricEntries = Object.entries(c.confidence_metrics).filter(([, m]) => m.evidence_count > 0);
          if (metricEntries.length === 0) return null;
          const avgConf = Math.round(
            metricEntries.reduce((sum, [, m]) => sum + m.confidence, 0) / metricEntries.length * 100
          );
          return (
            <CollapsibleSection
              icon={<BarChart3 className="h-3.5 w-3.5 text-[#2DD4BF]" />}
              label="Intelligence Confidence"
              summary={
                <span className="text-[10px] text-[var(--muted-text)] font-mono">
                  avg {avgConf}% · {metricEntries.length} fields with evidence
                </span>
              }
            >
              <div className="pt-1 overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)] pb-2 pr-4">Field</th>
                      <th className="text-right text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)] pb-2 pr-4">Confidence</th>
                      <th className="text-right text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)] pb-2 pr-4">Evidence</th>
                      <th className="text-right text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)] pb-2 pr-4">Sources</th>
                      <th className="text-right text-[10px] font-mono uppercase tracking-wider text-[var(--muted-text)] pb-2">Agreement</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {metricEntries.map(([field, m]) => (
                      <tr key={field} className="hover:bg-muted/50 transition-colors">
                        <td className="py-2 pr-4 font-mono text-foreground capitalize">{field.replace(/_/g, " ")}</td>
                        <td className="py-2 pr-4 text-right">
                          <ConfidenceBadge confidence={Math.round(m.confidence * 100)} />
                        </td>
                        <td className="py-2 pr-4 text-right font-mono text-[var(--muted-text)]">{m.evidence_count}</td>
                        <td className="py-2 pr-4 text-right font-mono text-[var(--muted-text)]">{m.source_count}</td>
                        <td className="py-2 text-right font-mono text-[var(--muted-text)]">{Math.round(m.agreement_score * 100)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CollapsibleSection>
          );
        })()}

        {/* ── DATA QUALITY + SOURCES ── */}
        <div className="border-t border-border pt-4 space-y-4">
          <SectionHeading icon={<Database className="h-3.5 w-3.5 text-[var(--muted-text)]" />} label="Data Quality" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="rounded-lg bg-muted border border-border p-3">
              <p className="text-[10px] text-[var(--muted-text)] font-mono">Understanding</p>
              <p className="text-sm font-semibold text-foreground font-mono mt-0.5">
                {c.confidence_scores ? (
                  <>
                    {Math.round(
                      Object.values(c.confidence_scores).reduce((a, b) => a + b, 0) /
                        Math.max(Object.values(c.confidence_scores).length, 1)
                    )}%
                  </>
                ) : "—"}
              </p>
            </div>
            <div className="rounded-lg bg-muted border border-border p-3">
              <p className="text-[10px] text-[var(--muted-text)] font-mono">Sources</p>
              <p className="text-sm font-semibold text-foreground font-mono mt-0.5">{c.pages_analyzed.length} pages</p>
            </div>
            <div className="rounded-lg bg-muted border border-border p-3">
              <p className="text-[10px] text-[var(--muted-text)] font-mono">Evidence</p>
              <p className="text-sm font-semibold text-foreground font-mono mt-0.5">
                {[
                  c.core_offering_evidence?.length ?? 0,
                  c.icp_evidence?.length ?? 0,
                  c.tone_evidence?.length ?? 0,
                  c.pricing_evidence?.length ?? 0,
                  c.hiring_evidence?.length ?? 0,
                  c.keywords_evidence?.length ?? 0,
                  c.momentum_evidence?.length ?? 0,
                ].reduce((a, b) => a + b, 0)}{" "}
                snippets
              </p>
            </div>
            <div className="rounded-lg bg-muted border border-border p-3">
              <p className="text-[10px] text-[var(--muted-text)] font-mono">Warnings</p>
              <p className="text-sm font-semibold text-foreground font-mono mt-0.5">
                {c.validation?.validation_warning ? (
                  <span className="text-[#F59E0B]">Yes</span>
                ) : (
                  <span className="text-[#10B981]">None</span>
                )}
              </p>
            </div>
          </div>

          {/* Sources Analyzed */}
          {c.pages_analyzed.length > 0 && (
            <div>
              <SectionHeading icon={<FileSpreadsheet className="h-3.5 w-3.5 text-[var(--muted-text)]" />} label="Sources Analyzed" />
              <div className="mt-1.5 flex flex-wrap gap-1">
                {c.pages_analyzed.map((page, i) => (
                  <Badge
                    key={i}
                    variant="outline"
                    className="border-border bg-muted text-[10px] text-[var(--muted-text)] font-mono"
                  >
                    {page}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ComparisonSection({ comparison }: { comparison: ComparisonResult }) {
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-semibold text-foreground font-mono">Cross-Competitor Intelligence</h2>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">
              <Trophy className="h-3.5 w-3.5 text-[#F59E0B]" /> Market Leader
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-foreground">{comparison.market_leader}</p>
            {comparison.market_leader_reason && (
              <p className="mt-1.5 text-[11px] leading-relaxed text-[var(--muted-text)]">
                {comparison.market_leader_reason}
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">
              <Rocket className="h-3.5 w-3.5 text-[#BC6C50]" /> Fastest Mover
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-foreground">{comparison.fastest_mover}</p>
            {comparison.fastest_mover_reason && (
              <p className="mt-1.5 text-[11px] leading-relaxed text-[var(--muted-text)]">
                {comparison.fastest_mover_reason}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {comparison.threat_ranking.length > 0 && (
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">
              <Swords className="h-3.5 w-3.5 text-[#EF4444]" /> Strategic Threat Ranking
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {comparison.threat_ranking.map((threat, i) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-muted text-xs font-bold text-muted-foreground font-mono">
                    {i + 1}
                  </span>
                  <div>
                    <span className="text-sm text-foreground">{threat}</span>
                    {comparison.threat_ranking_reasons?.[i] && (
                      <p className="mt-0.5 text-[11px] leading-relaxed text-[var(--muted-text)]">
                        {comparison.threat_ranking_reasons[i]}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {comparison.ai_emphasis_ranking.length > 0 && (
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground font-mono">
              <Building2 className="h-3.5 w-3.5" /> AI Emphasis Ranking
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1.5">
              {comparison.ai_emphasis_ranking.map((company, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-foreground">
                  <span className="text-xs text-[var(--muted-text)] font-mono">{i + 1}.</span>
                  {company}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {comparison.executive_briefing && (
        <Card className="border-border bg-[var(--dialog-surface)]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#F59E0B] font-mono">
              <Lightbulb className="h-3.5 w-3.5" /> Executive Briefing
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-foreground italic">
              {comparison.executive_briefing}
            </p>
          </CardContent>
        </Card>
      )}

      {comparison.messaging_gap ? (
        <Card className="border-border bg-[var(--dialog-surface)]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#3B82F6] font-mono">
              <Lightbulb className="h-3.5 w-3.5" /> Messaging Gap (Opportunity)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-xs font-semibold text-[#3B82F6] uppercase tracking-wider mb-1">Title</p>
              <p className="text-sm font-bold text-foreground">{comparison.messaging_gap.title}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-[#3B82F6] uppercase tracking-wider mb-1">Description</p>
              <p className="text-sm leading-relaxed text-foreground">{comparison.messaging_gap.description}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-[#3B82F6] uppercase tracking-wider mb-1">Target Persona</p>
              <p className="text-sm text-foreground">{comparison.messaging_gap.target_persona}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-[#3B82F6] uppercase tracking-wider mb-1">Business Value</p>
              <p className="text-sm text-foreground">{comparison.messaging_gap.business_value}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-[#3B82F6] uppercase tracking-wider mb-1">Confidence</p>
              <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                comparison.messaging_gap.confidence === "High"
                  ? "bg-emerald-500/10 text-emerald-400"
                  : comparison.messaging_gap.confidence === "Medium"
                  ? "bg-amber-500/10 text-amber-400"
                  : "bg-neutral-500/10 text-neutral-400"
              }`}>
                {comparison.messaging_gap.confidence}
              </span>
            </div>
          </CardContent>
        </Card>
      ) : comparison.messaging_gaps ? (
        <Card className="border-border bg-[var(--dialog-surface)]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#3B82F6] font-mono">
              <Lightbulb className="h-3.5 w-3.5" /> Messaging Gaps & Opportunities
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-foreground">
              {comparison.messaging_gaps}
            </p>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

export default function ReportPage({ params }: ReportPageProps) {
  const { runId } = use(params);
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: report, isLoading, error } = useQuery({
    queryKey: ["report", runId],
    queryFn: async () => {
      const res = await apiClient.get<IntelligenceReport>(`/api/report/${runId}`);
      return res.data;
    },
  });

  const { data: alerts = [] } = useQuery({
    queryKey: ["report-alerts", runId],
    queryFn: async () => {
      const res = await apiClient.get<DashboardAlertResponse[]>("/api/alerts");
      return res.data;
    },
    enabled: !!report,
  });

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.delete(`/api/runs/${runId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recent-analysis-runs"] });
      toast.success("Analysis deleted");
      router.push(ROUTES.runHistory);
    },
    onError: () => toast.error("Failed to delete analysis"),
  });

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-8 w-8 rounded-lg bg-muted" />
        </div>
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-64 rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex flex-col items-center gap-4 p-6 py-24 text-center">
        <AlertTriangle className="h-10 w-10 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Report not available</p>
        <p className="text-xs text-[var(--muted-text)]">The analysis may still be running or the report was deleted</p>
        <Button
          variant="outline"
          onClick={() => router.push(ROUTES.runHistory)}
          className="border-border text-muted-foreground"
        >
          <ArrowLeft className="mr-1.5 h-4 w-4" />
          Back to Run History
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push(ROUTES.runHistory)}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-[var(--muted-text)] font-mono">
            {report.competitors.length} competitors
          </span>
          <span className="text-xs text-[var(--muted-text)]">·</span>
          <span className="text-xs text-[var(--muted-text)] font-mono">
            {report.run_duration_seconds.toFixed(1)}s
          </span>
          <Button
            variant="outline"
            onClick={() => {
              if (confirm("Delete this analysis and all its data?")) {
                deleteMutation.mutate();
              }
            }}
            disabled={deleteMutation.isPending}
            className="border-border text-[#EF4444] hover:bg-[#EF4444]/10"
          >
            {deleteMutation.isPending ? (
              <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="mr-1.5 h-4 w-4" />
            )}
            Delete
          </Button>
        </div>
      </div>

      {/* Competitor Sections */}
      <div className="space-y-6">
        {report.competitors.map((c) => (
          <CompetitorSection key={c.name} c={c} alerts={alerts} />
        ))}
      </div>

      {/* Cross-Competitor Intelligence */}
      <ComparisonSection comparison={report.comparison} />
    </div>
  );
}
