"use client";

import { use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ROUTES, QUERY_KEYS } from "@/constants";
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
  ExternalLink,
} from "lucide-react";
import type { IntelligenceReport, CompetitorAnalysisReport, ComparisonResult } from "@/types/api";

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

function ScoreDisplay({ score }: { score: number }) {
  const color = score >= 7 ? "text-[#22C55E]" : score >= 4 ? "text-[#F59E0B]" : "text-[#EF4444]";
  return <span className={`text-2xl font-bold ${color}`}>{score}</span>;
}

function CompetitorSection({ c }: { c: CompetitorAnalysisReport }) {
  const toneClass = toneColors[c.messaging_tone] ?? "bg-[#2A2A2A] text-[#A0A0A0] border-[rgba(255,255,255,0.1)]";
  return (
    <Card className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <CardTitle className="text-lg font-bold text-white">{c.name}</CardTitle>
          <p className="text-xs text-[#A0A0A0]">{c.domain}</p>
        </div>
        <div className="flex items-center gap-3">
          <ScoreDisplay score={c.momentum_score} />
          <span className="text-[11px] text-[#6B7280]">/ 10</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <Zap className="h-3.5 w-3.5" /> Positioning
            </p>
            <p className="mt-1 text-sm text-white">{c.core_offering}</p>
          </div>
          <div>
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <Target className="h-3.5 w-3.5" /> Target Market
            </p>
            <p className="mt-1 text-sm text-white">{c.icp}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <MessageSquare className="h-3.5 w-3.5" /> Tone
            </p>
            <Badge variant="outline" className={`mt-1 text-xs font-medium capitalize ${toneClass}`}>
              {c.messaging_tone}
            </Badge>
          </div>
          <div>
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <DollarSign className="h-3.5 w-3.5" /> Pricing
            </p>
            <p className="mt-1 text-sm text-white">{c.pricing_signals || "Not detected"}</p>
          </div>
          <div>
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <Users className="h-3.5 w-3.5" /> Hiring
            </p>
            <p className="mt-1 text-sm text-white">{c.hiring_signals || "No signals"}</p>
          </div>
        </div>

        {c.strategic_keywords.length > 0 && (
          <div>
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <Hash className="h-3.5 w-3.5" /> Keywords
            </p>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {c.strategic_keywords.filter(Boolean).map((kw, i) => (
                <Badge key={i} variant="outline" className="border-[rgba(255,255,255,0.1)] bg-[#2A2A2A] text-xs text-white">
                  {kw}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {c.recent_launches.length > 0 && (
          <div>
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <Package className="h-3.5 w-3.5" /> Recent Signals
            </p>
            <ul className="mt-1.5 space-y-1.5">
              {c.recent_launches.map((signal, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-white">
                  <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#BC6C50]" />
                  {signal}
                </li>
              ))}
            </ul>
          </div>
        )}

        {c.analyst_note && (
          <div className="rounded-lg border border-[#F59E0B]/30 bg-[#222222] p-3">
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#F59E0B]">
              <Lightbulb className="h-3.5 w-3.5" /> Analyst Note
            </p>
            <p className="mt-1 text-sm italic text-[#CBD5E1]">{c.analyst_note}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function ComparisonSection({ comparison }: { comparison: ComparisonResult }) {
  return (
    <div className="space-y-4">
      <h2 className="text-sm font-semibold text-white">Cross-Competitor Intelligence</h2>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <Trophy className="h-3.5 w-3.5 text-[#F59E0B]" /> Market Leader
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-white">{comparison.market_leader}</p>
          </CardContent>
        </Card>

        <Card className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <Rocket className="h-3.5 w-3.5 text-[#BC6C50]" /> Fastest Mover
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-white">{comparison.fastest_mover}</p>
          </CardContent>
        </Card>
      </div>

      {comparison.threat_ranking.length > 0 && (
        <Card className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              <Swords className="h-3.5 w-3.5 text-[#EF4444]" /> Strategic Threat Ranking
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {comparison.threat_ranking.map((threat, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="flex h-6 w-6 items-center justify-center rounded-md bg-[#2A2A2A] text-xs font-bold text-[#A0A0A0]">
                    {i + 1}
                  </span>
                  <span className="text-sm text-white">{threat}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {comparison.ai_emphasis_ranking.length > 0 && (
        <Card className="border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#A0A0A0]">
              AI Emphasis Ranking
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1.5">
              {comparison.ai_emphasis_ranking.map((company, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-white">
                  <span className="text-xs text-[#6B7280]">{i + 1}.</span>
                  {company}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {comparison.executive_briefing && (
        <Card className="border-[rgba(255,255,255,0.1)] bg-[#222222]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#F59E0B]">
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
          <Skeleton className="h-8 w-8 rounded-lg bg-[#2A2A2A]" />
          <Skeleton className="h-6 w-48 bg-[#2A2A2A]" />
        </div>
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-48 rounded-lg bg-[#2A2A2A]" />
        ))}
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex flex-col items-center gap-4 p-6 py-24 text-center">
        <AlertTriangle className="h-10 w-10 text-[#A0A0A0]" />
        <p className="text-sm text-[#A0A0A0]">Report not available</p>
        <p className="text-xs text-[#6B7280]">The analysis may still be running or the report was deleted</p>
        <Button
          variant="outline"
          onClick={() => router.push(ROUTES.dashboard)}
          className="border-[rgba(255,255,255,0.1)] text-[#A0A0A0]"
        >
          <ArrowLeft className="mr-1.5 h-4 w-4" />
          Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push(ROUTES.dashboard)}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-[rgba(255,255,255,0.1)] bg-[#1E1E1E] text-[#A0A0A0] hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">Intelligence Report</h1>
            <p className="text-xs text-[#A0A0A0]">
              {report.competitors.length} competitors · {report.total_pages_fetched} pages · {report.run_duration_seconds.toFixed(1)}s
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={() => {
            if (confirm("Delete this analysis and all its data?")) {
              deleteMutation.mutate();
            }
          }}
          disabled={deleteMutation.isPending}
          className="border-[rgba(255,255,255,0.1)] text-[#EF4444] hover:bg-[#EF4444]/10"
        >
          {deleteMutation.isPending ? (
            <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
          ) : (
            <Trash2 className="mr-1.5 h-4 w-4" />
          )}
          Delete
        </Button>
      </div>

      <div className="space-y-6">
        {report.competitors.map((c) => (
          <CompetitorSection key={c.name} c={c} />
        ))}
      </div>

      <ComparisonSection comparison={report.comparison} />
    </div>
  );
}
