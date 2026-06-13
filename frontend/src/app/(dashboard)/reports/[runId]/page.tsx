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
  low: "bg-[#6B7280]/15 text-[#6B7280] border-[#6B7280]/30",
};

function ConfidenceBadge({ confidence }: { confidence: number }) {
  if (!confidence && confidence !== 0) return null;
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
        className="flex items-center gap-1 text-[11px] text-[#6B7280] hover:text-muted-foreground transition-colors"
      >
        {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
        <Quote className="h-3 w-3" />
        Evidence{source ? ` (${source})` : ""}
      </button>
      {open && (
        <div className="mt-1.5 space-y-1 border-l-2 border-[rgba(255,255,255,0.06)] pl-3">
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

function ScoreMeter({ score }: { score: number }) {
  const segments = 10;
  const filled = Math.round((score / 10) * segments);
  return (
    <div className="flex items-center gap-2">
      <span className={`text-2xl font-bold ${score >= 7 ? "text-[#22C55E]" : score >= 4 ? "text-[#F59E0B]" : "text-[#EF4444]"}`}>
        {score}
      </span>
      <span className="text-[11px] text-[#6B7280]">/ 10</span>
      <div className="ml-1 flex gap-0.5">
        {Array.from({ length: segments }).map((_, i) => (
          <div
            key={i}
            className={`h-2 w-2 rounded-sm ${
              i < filled
                ? score >= 7
                  ? "bg-[#22C55E]"
                  : score >= 4
                    ? "bg-[#F59E0B]"
                    : "bg-[#EF4444]"
                : "bg-muted"
            }`}
          />
        ))}
      </div>
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

function SectionWithEvidence({
  icon,
  label,
  value,
  evidence,
  source,
  confidence,
  emptyMessage = "No public evidence found",
}: {
  icon: React.ReactNode;
  label: string;
  value?: string | null;
  evidence?: string[];
  source?: string;
  confidence?: number;
  emptyMessage?: string;
}) {
  const displayValue = value && value !== "Not detected" && value !== "" ? value : null;
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <SectionHeading icon={icon} label={label} />
        {confidence !== undefined && <ConfidenceBadge confidence={confidence} />}
      </div>
      <p className="text-sm text-foreground">{displayValue || emptyMessage}</p>
      {displayValue && <EvidenceBlock evidence={evidence} source={source} />}
    </div>
  );
}

function MomentumCard({ c }: { c: CompetitorAnalysisReport }) {
  const positiveCount = c.momentum_evidence?.length ?? 0;
  const negativeCount = c.momentum_negative_factors?.length ?? 0;
  return (
    <div className="rounded-lg border border-[rgba(255,255,255,0.06)] bg-[#222222] p-3">
      <div className="flex items-center gap-2">
        <SectionHeading icon={<BarChart3 className="h-3.5 w-3.5 text-[#22C55E]" />} label="Momentum Score" />
      </div>
      <div className="mt-2 flex items-center gap-3">
        <ScoreMeter score={c.momentum_score} />
        <span className="text-xs text-[#6B7280]">
          {c.momentum_score >= 7
            ? "Strong momentum — gaining market traction"
            : c.momentum_score >= 4
              ? "Moderate momentum — steady but not dominant"
              : "Low momentum — potential vulnerability"}
        </span>
      </div>

      {/* Positive Drivers */}
      {positiveCount > 0 && (
        <div className="mt-3">
          <p className="flex items-center gap-1 text-xs font-semibold text-[#22C55E] font-mono">
            <TrendingUp className="h-3 w-3" />
            Drivers
          </p>
          <div className="mt-1 space-y-1">
            {c.momentum_evidence!.map((ev, i) => (
              <p key={i} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#22C55E]" />
                {ev}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Negative Factors */}
      {negativeCount > 0 && (
        <div className="mt-2">
          <p className="flex items-center gap-1 text-xs font-semibold text-[#EF4444] font-mono">
            <TrendingDown className="h-3 w-3" />
          </p>
          <div className="mt-1 space-y-1">
            {c.momentum_negative_factors!.map((factor, i) => (
              <p key={i} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#EF4444]" />
                {factor}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Reasoning */}
      {c.momentum_reasoning && (
        <div className="mt-3 border-t border-[rgba(255,255,255,0.06)] pt-2">
          <p className="text-xs text-[#6B7280] font-mono">Why this score</p>
          <p className="mt-0.5 text-xs text-muted-foreground">{c.momentum_reasoning}</p>
        </div>
      )}
    </div>
  );
}

function ValidationBanner({ validation }: { validation: CompetitorAnalysisReport["validation"] }) {
  if (!validation?.validation_warning) return null;
  return (
    <div className="flex items-start gap-3 rounded-lg border border-[#F59E0B]/30 bg-[#1C1508] p-3">
      <AlertOctagon className="mt-0.5 h-4 w-4 shrink-0 text-[#F59E0B]" />
      <div>
        <p className="text-xs font-semibold text-[#F59E0B] font-mono">Validation Warning</p>
        <p className="text-xs text-muted-foreground">
          {validation.reason
            ? `Low confidence in company identification: ${validation.reason}`
            : "Low confidence in company identification. The extracted intelligence may be unreliable."}
        </p>
      </div>
    </div>
  );
}

function AnalystNoteBlock({ note }: { note: string }) {
  if (!note) return null;

  const summaryMatch = note.match(/Summary:\s*(.+?)(?:\n|$)/);
  const strengthMatch = note.match(/Strength:\s*(.+?)(?:\n|$)/);
  const riskMatch = note.match(/Risk:\s*(.+?)(?:\n|$)/);
  const outlookMatch = note.match(/Outlook:\s*([\s\S]+)$/);

  const summary = summaryMatch?.[1]?.trim();
  const strength = strengthMatch?.[1]?.trim();
  const risk = riskMatch?.[1]?.trim();
  const outlook = outlookMatch?.[1]?.trim();

  if (summary || strength || risk || outlook) {
    return (
      <div className="space-y-3 rounded-lg border border-[rgba(255,255,255,0.06)] bg-[#1A1A2E] p-3">
        <SectionHeading icon={<Lightbulb className="h-3.5 w-3.5 text-[#F59E0B]" />} label="Analyst Note" />
        {summary && (
          <div>
            <p className="text-[11px] font-semibold text-[#F59E0B] font-mono">Summary</p>
            <p className="mt-0.5 text-sm text-[#CBD5E1]">{summary}</p>
          </div>
        )}
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {strength && (
            <div className="rounded-lg border border-[#22C55E]/20 bg-[#0A1A0A] p-2.5">
              <p className="flex items-center gap-1 text-[11px] font-semibold text-[#22C55E] font-mono">
                <CheckCircle2 className="h-3 w-3" />
                Strength
              </p>
              <p className="mt-1 text-sm text-[#CBD5E1]">{strength}</p>
            </div>
          )}
          {risk && (
            <div className="rounded-lg border border-[#EF4444]/20 bg-[#1A0A0A] p-2.5">
              <p className="flex items-center gap-1 text-[11px] font-semibold text-[#EF4444] font-mono">
                <XCircle className="h-3 w-3" />
                Risk
              </p>
              <p className="mt-1 text-sm text-[#CBD5E1]">{risk}</p>
            </div>
          )}
        </div>
        {outlook && (
          <div>
            <p className="text-[11px] font-semibold text-[#8B5CF6] font-mono">Outlook</p>
            <p className="mt-0.5 text-sm italic text-[#CBD5E1]">{outlook}</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-[#F59E0B]/30 bg-[#222222] p-3">
      <SectionHeading icon={<Lightbulb className="h-3.5 w-3.5 text-[#F59E0B]" />} label="Analyst Note" />
      <p className="mt-1 text-sm italic text-[#CBD5E1]">{note}</p>
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

  return (
    <Card className="border-border bg-card">
      <CardHeader className="flex flex-row items-center justify-between border-b border-[rgba(255,255,255,0.05)] pb-4">
        <div className="flex items-center gap-3">
          {c.logo_url && (
            <img
              src={c.logo_url}
              alt={`${c.name} logo`}
              className="h-9 w-9 rounded-lg bg-neutral-800 object-contain shrink-0"
              onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = "none" }}
            />
          )}
          <div>
            <CardTitle className="text-lg font-bold text-foreground font-mono">{c.name}</CardTitle>
            <div className="mt-0.5 flex items-center gap-2">
              <span className="text-sm text-[#6B7280]">{c.domain}</span>
              {hasDrift && (
                <Badge
                  variant="outline"
                  className={`text-xs font-medium capitalize ${severityColors[maxSeverity!]}`}
                >
                  <Activity className="mr-1 h-3 w-3" />
                  Drift
                </Badge>
              )}
            </div>
          </div>
        </div>
        <ScoreMeter score={c.momentum_score} />
      </CardHeader>
      <CardContent className="space-y-5 pt-4">
        {/* Validation Warning Banner */}
        <ValidationBanner validation={c.validation} />

        {/* AI Summary / Analyst Note */}
        <AnalystNoteBlock note={c.analyst_note} />

        {/* Company Overview */}
        {c.validation?.company_description && (
          <SectionHeading icon={<Building2 className="h-3.5 w-3.5 text-[#8B5CF6]" />} label="Company Overview" />
        )}
        {c.validation?.company_description && (
          <div className="-mt-4 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
            {c.validation?.category && (
              <div>
                <span className="font-semibold text-foreground font-mono">Category: </span>
                {c.validation.category}
              </div>
            )}
            {c.validation?.product_type && (
              <div>
                <span className="font-semibold text-foreground font-mono">Type: </span>
                {c.validation.product_type}
              </div>
            )}
            {c.validation?.primary_use_case && (
              <div className="col-span-2">
                <span className="font-semibold text-foreground font-mono">Customers: </span>
                {c.validation.primary_use_case}
              </div>
            )}
          </div>
        )}

        {/* Positioning */}
        <SectionWithEvidence
          icon={<Zap className="h-3.5 w-3.5 text-[#3B82F6]" />}
          label="Positioning"
          value={c.core_offering}
          evidence={c.core_offering_evidence}
          source={c.core_offering_source}
          confidence={c.core_offering_confidence ?? c.confidence_scores?.core_offering}
        />

        {/* Target Market / ICP */}
        <SectionWithEvidence
          icon={<Target className="h-3.5 w-3.5 text-[#F59E0B]" />}
          label="Target Market"
          value={c.icp}
          evidence={c.icp_evidence}
          confidence={c.confidence_scores?.icp}
        />

        {/* Tone */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <SectionHeading icon={<MessageSquare className="h-3.5 w-3.5 text-[#6366F1]" />} label="Tone" />
            {c.confidence_scores?.tone !== undefined && <ConfidenceBadge confidence={c.confidence_scores.tone} />}
          </div>
          <Badge
            variant="outline"
            className={`text-xs font-medium capitalize ${toneColors[c.messaging_tone] ?? "bg-muted text-muted-foreground border-border"}`}
          >
            {c.messaging_tone}
          </Badge>
          <EvidenceBlock evidence={c.tone_evidence} />
        </div>

        {/* Pricing */}
        <SectionWithEvidence
          icon={<DollarSign className="h-3.5 w-3.5 text-[#22C55E]" />}
          label="Pricing"
          value={c.pricing_signals}
          evidence={c.pricing_evidence}
          source={c.pricing_source}
          confidence={c.pricing_confidence ?? c.confidence_scores?.pricing}
        />

        {/* Hiring */}
        <SectionWithEvidence
          icon={<Users className="h-3.5 w-3.5 text-[#10B981]" />}
          label="Hiring Signals"
          value={c.hiring_signals}
          evidence={c.hiring_evidence}
          source={c.hiring_source}
          confidence={c.hiring_confidence ?? c.confidence_scores?.hiring}
        />

        {/* Strategic Keywords */}
        {c.strategic_keywords.length > 0 && (
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <SectionHeading icon={<Hash className="h-3.5 w-3.5 text-[#8B5CF6]" />} label="Strategic Keywords" />
              {(c.keywords_confidence ?? c.confidence_scores?.keywords) !== undefined && (
                <ConfidenceBadge confidence={c.keywords_confidence ?? c.confidence_scores?.keywords ?? 0} />
              )}
            </div>
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

        {/* Recent Signals */}
        {(c.recent_launches.length > 0 || c.growth_signals.length > 0) && (
          <SectionHeading icon={<Package className="h-3.5 w-3.5 text-[#BC6C50]" />} label="Recent Signals" />
        )}
        {c.recent_launches.length > 0 && (
          <div className="-mt-3 space-y-1.5">
            {c.recent_launches.map((signal, i) => (
              <p key={i} className="flex items-start gap-2 text-sm text-foreground">
                <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#BC6C50]" />
                {signal}
              </p>
            ))}
          </div>
        )}
        {c.growth_signals.length > 0 && (
          <div className="-mt-1 space-y-1.5">
            {c.growth_signals.map((signal, i) => (
              <p key={i} className="flex items-start gap-2 text-sm text-foreground">
                <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#22C55E]" />
                {signal}
              </p>
            ))}
          </div>
        )}

        {/* Momentum Card */}
        <MomentumCard c={c} />

        {/* Drift Section */}
        {hasDrift && (
          <div className="rounded-lg border border-[rgba(239,68,68,0.15)] bg-[#1C1010] p-3">
            <SectionHeading icon={<Activity className="h-3.5 w-3.5 text-[#EF4444]" />} label="Drift Analysis" />
            <p className="mt-1 text-xs text-[#EF4444]/70">
              Changes detected since last analysis run
            </p>
            <div className="mt-3 space-y-3">
              {competitorAlerts.map((alert) => (
                <div key={alert.id} className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className={`text-[10px] font-medium capitalize ${severityColors[alert.severity] ?? "bg-[#6B7280]/15 text-[#6B7280]"}`}
                    >
                      {alert.severity}
                    </Badge>
                    <span className="text-sm font-medium text-foreground">
                      {alert.headline}
                    </span>
                  </div>
                  {alert.summary && (
                    <p className="pl-1 text-sm text-[#CBD5E1]">{alert.summary}</p>
                  )}
                  {alert.evidence && alert.evidence.length > 0 && (
                    <div className="pl-1 space-y-0.5">
                      {alert.evidence.map((e, i) => (
                        <p key={i} className="flex items-start gap-1.5 text-xs text-[#6B7280]">
                          <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-[#6B7280]" />
                          {e}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Alert Status */}
        {hasDrift && (
          <div className="flex items-center gap-3">
            <Badge variant="outline" className={`text-xs font-medium ${severityColors[maxSeverity!]}`}>
              <AlertCircle className="mr-1 h-3 w-3" />
              {competitorAlerts.length} {competitorAlerts.length === 1 ? "Alert" : "Alerts"}
            </Badge>
            <span className="text-xs text-[#6B7280]">
              Last alert: {new Date(competitorAlerts[0].created_at).toLocaleDateString()}
            </span>
          </div>
        )}
        {!hasDrift && (
          <div className="flex items-center gap-2 text-xs text-[#6B7280]">
            <Shield className="h-3.5 w-3.5 text-[#22C55E]" />
            No drift detected — competitor state consistent with previous analysis
          </div>
        )}

        {/* Data Quality */}
        <div className="border-t border-[rgba(255,255,255,0.06)] pt-3 space-y-3">
          <SectionHeading icon={<Database className="h-3.5 w-3.5 text-[#6B7280]" />} label="Data Quality" />
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <div className="rounded-lg bg-[#222222] p-2.5">
              <p className="text-[10px] text-[#6B7280] font-mono">Understanding</p>
              <p className="text-sm font-semibold text-foreground font-mono">
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
            <div className="rounded-lg bg-[#222222] p-2.5">
              <p className="text-[10px] text-[#6B7280] font-mono">Sources</p>
              <p className="text-sm font-semibold text-foreground font-mono">{c.pages_analyzed.length} pages</p>
            </div>
            <div className="rounded-lg bg-[#222222] p-2.5">
              <p className="text-[10px] text-[#6B7280] font-mono">Evidence</p>
              <p className="text-sm font-semibold text-foreground font-mono">
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
            <div className="rounded-lg bg-[#222222] p-2.5">
              <p className="text-[10px] text-[#6B7280] font-mono">Warnings</p>
              <p className="text-sm font-semibold text-foreground font-mono">
                {c.validation?.validation_warning ? (
                  <span className="text-[#F59E0B]">Yes</span>
                ) : (
                  <span className="text-[#22C55E]">None</span>
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Sources Used */}
        {c.pages_analyzed.length > 0 && (
          <div>
            <SectionHeading icon={<FileSpreadsheet className="h-3.5 w-3.5 text-[#6B7280]" />} label="Sources Analyzed" />
            <div className="mt-1 flex flex-wrap gap-1">
              {c.pages_analyzed.map((page, i) => (
                <Badge
                  key={i}
                  variant="outline"
                  className="border-[rgba(255,255,255,0.06)] bg-muted text-[10px] text-[#6B7280] font-mono"
                >
                  {page}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
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
              <p className="mt-1.5 text-[11px] leading-relaxed text-[#6B7280]">
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
              <p className="mt-1.5 text-[11px] leading-relaxed text-[#6B7280]">
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
                      <p className="mt-0.5 text-[11px] leading-relaxed text-[#6B7280]">
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
                  <span className="text-xs text-[#6B7280] font-mono">{i + 1}.</span>
                  {company}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {comparison.executive_briefing && (
        <Card className="border-border bg-[#222222]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#F59E0B] font-mono">
              <Lightbulb className="h-3.5 w-3.5" /> Executive Briefing
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-[#CBD5E1] italic">
              {comparison.executive_briefing}
            </p>
          </CardContent>
        </Card>
      )}

      {comparison.messaging_gap && (
        <Card className="border-border bg-[#222222]">
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
              <p className="text-sm leading-relaxed text-[#CBD5E1]">{comparison.messaging_gap.description}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-[#3B82F6] uppercase tracking-wider mb-1">Target Persona</p>
              <p className="text-sm text-[#CBD5E1]">{comparison.messaging_gap.target_persona}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-[#3B82F6] uppercase tracking-wider mb-1">Business Value</p>
              <p className="text-sm text-[#CBD5E1]">{comparison.messaging_gap.business_value}</p>
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
      )}
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
      router.push(ROUTES.dashboard);
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
        <p className="text-xs text-[#6B7280]">The analysis may still be running or the report was deleted</p>
        <Button
          variant="outline"
          onClick={() => router.push(ROUTES.dashboard)}
          className="border-border text-muted-foreground"
        >
          <ArrowLeft className="mr-1.5 h-4 w-4" />
          Back to Dashboard
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
            onClick={() => router.push(ROUTES.dashboard)}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-[#6B7280] font-mono">
            {report.competitors.length} competitors
          </span>
          <span className="text-xs text-[#6B7280]">·</span>
          <span className="text-xs text-[#6B7280] font-mono">
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
