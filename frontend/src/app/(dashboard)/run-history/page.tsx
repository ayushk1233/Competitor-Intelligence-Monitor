"use client";

import Link from "next/link";
import { useRecentAnalysisRuns } from "@/hooks/use-analysis-runs";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/constants";
import {
  Play, Loader2, CheckCircle2, XCircle, Clock, Trash2, FileText,
} from "lucide-react";
import type { RunListItem } from "@/types/api";

const statusConfig: Record<string, { label: string; icon: typeof Loader2; class: string }> = {
  queued:     { label: "Queued",     icon: Clock,        class: "text-[#F59E0B] border-[#F59E0B]/30 bg-[#F59E0B]/15" },
  scraping:   { label: "Scraping",   icon: Loader2,      class: "text-[#3B82F6] border-[#3B82F6]/30 bg-[#3B82F6]/15" },
  analyzing:  { label: "Analyzing",  icon: Loader2,      class: "text-[#8B5CF6] border-[#8B5CF6]/30 bg-[#8B5CF6]/15" },
  comparing:  { label: "Comparing",  icon: Loader2,      class: "text-[#8B5CF6] border-[#8B5CF6]/30 bg-[#8B5CF6]/15" },
  completed:  { label: "Completed",  icon: CheckCircle2, class: "text-[var(--status-completed)] border-[var(--status-completed)]/30 bg-[var(--status-completed)]/15" },
  failed:     { label: "Failed",     icon: XCircle,      class: "text-[#DC2626] border-[#DC2626]/40 bg-[#DC2626]/25" },
};

function StatusBadge({ status }: { status: string }) {
  const c = statusConfig[status] ?? { label: status, icon: Loader2, class: "text-muted-foreground border-border bg-muted" };
  const Icon = c.icon;
  return (
    <Badge variant="outline" className={`flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold ${c.class}`}>
      <Icon className={`h-3.5 w-3.5 ${["scraping","analyzing","comparing"].includes(status) ? "animate-spin" : ""}`} />
      {c.label}
    </Badge>
  );
}

function RunRow({ run }: { run: RunListItem }) {
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.delete(`/api/runs/${run.run_id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recent-analysis-runs"] });
      toast.success("Analysis deleted");
    },
    onError: () => toast.error("Failed to delete analysis"),
  });

  return (
    <div className="flex items-center justify-between rounded-lg border border-border bg-card p-4">
      <div className="flex items-center gap-4">
        <StatusBadge status={run.status} />
        <div>
          <p className="text-sm font-medium text-foreground">{run.competitors.join(", ")}</p>
          <p className="text-xs text-muted-foreground">{run.pages_fetched} pages fetched</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {run.duration_seconds && <span className="text-xs text-[#6B7280]">{run.duration_seconds.toFixed(1)}s</span>}
        <span className="text-xs text-[#6B7280]">
          {new Date(run.created_at).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
        {run.status === "completed" && (
          <Link
            href={ROUTES.reportDetail(run.run_id)}
            className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-muted text-muted-foreground hover:text-foreground"
          >
            <FileText className="h-4 w-4" />
          </Link>
        )}
        <button
          onClick={() => {
            if (confirm("Delete this analysis?")) {
              deleteMutation.mutate();
            }
          }}
          disabled={deleteMutation.isPending}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-muted text-muted-foreground hover:text-[#EF4444]"
        >
          {deleteMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Trash2 className="h-4 w-4" />
          )}
        </button>
      </div>
    </div>
  );
}

export default function RunHistoryPage() {
  const { data: runs, isLoading } = useRecentAnalysisRuns();

  return (
    <div className="space-y-6 p-6">
      <div>
        <p className="text-sm text-muted-foreground">Full history of all analysis runs</p>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-lg bg-muted" />
          ))}
        </div>
      ) : !runs || runs.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-border bg-card py-16 text-center">
          <Play className="h-8 w-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">No runs yet</p>
          <p className="text-xs text-[#6B7280]">Run an analysis from the dashboard to see history here</p>
        </div>
      ) : (
        <div className="space-y-2">
          {runs.map((run) => (
            <RunRow key={run.run_id} run={run} />
          ))}
        </div>
      )}
    </div>
  );
}
