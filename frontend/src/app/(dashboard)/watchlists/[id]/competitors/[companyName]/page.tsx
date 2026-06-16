"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/constants";
import { useWatchlists } from "@/hooks/use-watchlists";
import {
  useCompetitorAnalysis,
  useCompetitorDrift,
} from "@/hooks/use-competitor-detail";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Minus,
  MessageSquare,
  Lightbulb,
  Hash,
  Zap,
  Target,
  Swords,
  Bell,
  Building2,
} from "lucide-react";

interface CompetitorDetailPageProps {
  params: Promise<{ id: string; companyName: string }>;
}

import { getToneColorHex, getInlineStyle } from "@/lib/color-utils";

const severityColor: Record<string, string> = {
  HIGH: "bg-[#EF4444]",
  MEDIUM: "bg-[#F59E0B]",
  LOW: "bg-[#22C55E]",
};

function ScoreLabel({ delta }: { delta: number }) {
  if (delta > 0) {
    return (
      <span className="flex items-center gap-1 text-sm text-[#22C55E]">
        <TrendingUp className="h-4 w-4" />+{delta}
      </span>
    );
  }
  if (delta < 0) {
    return (
      <span className="flex items-center gap-1 text-sm text-[#EF4444]">
        <TrendingDown className="h-4 w-4" />{delta}
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1 text-sm text-muted-foreground">
      <Minus className="h-4 w-4" />0
    </span>
  );
}

export default function CompetitorDetailPage({ params }: CompetitorDetailPageProps) {
  const { id, companyName } = use(params);
  const decodedName = decodeURIComponent(companyName);
  const router = useRouter();

  const { data: watchlists } = useWatchlists();
  const { data: analysis, isLoading: analysisLoading, error: analysisError } =
    useCompetitorAnalysis(decodedName);
  const { data: drift, isLoading: driftLoading } =
    useCompetitorDrift(decodedName);

  if (analysisLoading || driftLoading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-8 w-8 rounded-lg bg-muted" />
          <div className="space-y-1">
            <Skeleton className="h-6 w-48 bg-muted" />
            <div className="flex gap-3">
              <Skeleton className="h-4 w-20 bg-muted" />
              <Skeleton className="h-4 w-20 bg-muted" />
            </div>
          </div>
        </div>
        <Skeleton className="h-48 rounded-lg bg-muted" />
        <Skeleton className="h-32 rounded-lg bg-muted" />
      </div>
    );
  }

  if (analysisError || !analysis) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Building2 className="h-6 w-6" />}
          title="No analysis found"
          description="Run monitoring for this competitor to generate intelligence data"
          cta={
            <button
              onClick={() => router.push(ROUTES.watchlistDetail(id))}
              className="mt-2 flex items-center gap-1 text-sm text-[#BC6C50] hover:underline"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to watchlist
            </button>
          }
        />
      </div>
    );
  }



  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <button
          onClick={() => router.push(ROUTES.watchlistDetail(id))}
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-card text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="border-border text-muted-foreground hover:text-foreground">
            <Swords className="mr-1.5 h-4 w-4" />
            Battlecard
          </Button>
          <Button variant="outline" className="border-border text-muted-foreground hover:text-foreground">
            <Bell className="mr-1.5 h-4 w-4" />
            Watch
          </Button>
        </div>
      </div>

      <div>
        <h1 className="text-2xl font-bold text-foreground">{analysis.name}</h1>
        <div className="mt-2 flex items-center gap-4">
          <ScoreLabel delta={drift?.momentum_delta ?? 0} />
          <div className="flex items-center gap-1 text-sm text-muted-foreground flex-wrap">
            <MessageSquare className="h-4 w-4" />
            {analysis.messaging_tone ? (
              <div className="flex flex-wrap gap-1">
                {analysis.messaging_tone.split(',').map((t, idx) => {
                  const cleanT = t.trim();
                  if (!cleanT) return null;
                  return (
                    <Badge key={idx} variant="outline" className="text-xs font-medium capitalize" style={getInlineStyle(getToneColorHex(cleanT))}>
                      {cleanT}
                    </Badge>
                  );
                })}
              </div>
            ) : (
              "No tone data"
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {analysis.core_offering && (
          <Card className="border-border bg-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                <Zap className="mr-1.5 inline h-3.5 w-3.5" />
                Core offering
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-foreground">{analysis.core_offering}</p>
            </CardContent>
          </Card>
        )}
        {analysis.icp && (
          <Card className="border-border bg-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                <Target className="mr-1.5 inline h-3.5 w-3.5" />
                Ideal customer
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-foreground">{analysis.icp}</p>
            </CardContent>
          </Card>
        )}
      </div>

      {analysis.analyst_note && (
        <Card className="border-border bg-[var(--dialog-surface)]">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#F59E0B]">
              <Lightbulb className="h-3.5 w-3.5" />
              Analyst note
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-foreground italic">{analysis.analyst_note}</p>
          </CardContent>
        </Card>
      )}

      {analysis.recent_launches && analysis.recent_launches.length > 0 && (
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Recent Signals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {analysis.recent_launches.map((signal, i) => {
                const dotColor = severityColor[i < 3 ? ["HIGH", "MEDIUM", "LOW"][i] : "LOW"];
                return (
                  <li key={i} className="flex items-start gap-3 text-sm text-foreground">
                    <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${dotColor}`} />
                    {signal}
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>
      )}

      {analysis.strategic_keywords && analysis.strategic_keywords.length > 0 && (
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              <Hash className="mr-1.5 inline h-3.5 w-3.5" />
              Strategic Keywords
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {analysis.strategic_keywords.filter(Boolean).map((keyword, i) => (
                <Badge
                  key={i}
                  variant="outline"
                  className={`border-border text-xs font-medium ${
                    i < 3
                      ? "bg-white text-[#121212]"
                      : "bg-muted text-foreground"
                  }`}
                >
                  {i < 3 ? `+ ${keyword}` : keyword}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {drift && (drift.added_keywords.length > 0 || drift.removed_keywords.length > 0 || drift.tone_changed) && (
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Recent Changes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {drift.added_keywords.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {drift.added_keywords.map((kw, i) => (
                    <Badge key={i} className="bg-[#22C55E]/15 text-[#22C55E] border-[#22C55E]/30 text-[11px] font-medium">
                      + {kw}
                    </Badge>
                  ))}
                </div>
              )}
              {drift.removed_keywords.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {drift.removed_keywords.map((kw, i) => (
                    <Badge key={i} className="bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30 text-[11px] font-medium">
                      - {kw}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
