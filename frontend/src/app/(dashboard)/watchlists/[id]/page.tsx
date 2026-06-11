"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ROUTES } from "@/constants";
import { useWatchlists } from "@/hooks/use-watchlists";
import { useCompetitors } from "@/hooks/use-competitors";
import { useMonitoringRuns, useCreateMonitoringRun } from "@/hooks/use-monitoring-runs";
import { CompetitorTable } from "@/components/watchlists/CompetitorTable";
import { AddCompetitorDialog } from "@/components/watchlists/AddCompetitorDialog";
import { RunHistoryTable } from "@/components/watchlists/RunHistoryTable";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ArrowLeft,
  Play,
  Loader2,
  Users,
  Activity,
} from "lucide-react";
import { extractApiError } from "@/lib/utils";

interface WatchlistDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function WatchlistDetailPage({
  params,
}: WatchlistDetailPageProps) {
  const { id } = use(params);
  const router = useRouter();

  const { data: watchlists, isLoading: watchlistLoading } = useWatchlists();
  const { data: competitors, isLoading: competitorsLoading } = useCompetitors(id);
  const { data: runs, isLoading: runsLoading } = useMonitoringRuns(id);
  const createRun = useCreateMonitoringRun(id);

  const watchlist = watchlists?.items.find((wl) => wl.id === id);

  const handleTriggerRun = async () => {
    try {
      await createRun.mutateAsync({ trigger_type: "MANUAL" });
      toast.success("Monitoring run triggered");
    } catch (error) {
      toast.error(extractApiError(error));
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push(ROUTES.watchlists)}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-[rgba(255,255,255,0.1)] bg-[#1E1E1E] text-[#A0A0A0] transition-colors hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            {watchlistLoading ? (
              <div className="space-y-1">
                <Skeleton className="h-5 w-40 bg-[#2A2A2A]" />
                <Skeleton className="h-4 w-60 bg-[#2A2A2A]" />
              </div>
            ) : watchlist ? (
              <>
                <h1 className="text-xl font-semibold text-white">
                  {watchlist.name}
                </h1>
                {watchlist.description && (
                  <p className="text-sm text-[#A0A0A0]">
                    {watchlist.description}
                  </p>
                )}
              </>
            ) : (
              <h1 className="text-xl font-semibold text-white">
                Watchlist
              </h1>
            )}
          </div>
        </div>

        <Button
          onClick={handleTriggerRun}
          disabled={createRun.isPending}
          className="bg-[#BC6C50] text-white hover:bg-[#BC6C50]/90"
        >
          {createRun.isPending ? (
            <>
              <Loader2 className="mr-1 h-4 w-4 animate-spin" />
              Triggering...
            </>
          ) : (
            <>
              <Play className="mr-1 h-4 w-4" />
              Run Monitoring
            </>
          )}
        </Button>
      </div>

      <Tabs defaultValue="competitors">
        <TabsList className="border border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
          <TabsTrigger
            value="competitors"
            className="flex items-center gap-2 text-[#A0A0A0] data-[state=active]:bg-[#2A2A2A] data-[state=active]:text-white"
          >
            <Users className="h-4 w-4" />
            Competitors
          </TabsTrigger>
          <TabsTrigger
            value="runs"
            className="flex items-center gap-2 text-[#A0A0A0] data-[state=active]:bg-[#2A2A2A] data-[state=active]:text-white"
          >
            <Activity className="h-4 w-4" />
            Monitoring Runs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="competitors" className="mt-4 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Competitors</h2>
            <AddCompetitorDialog watchlistId={id} />
          </div>
          <CompetitorTable
            watchlistId={id}
            competitors={competitors?.items}
            isLoading={competitorsLoading}
          />
        </TabsContent>

        <TabsContent value="runs" className="mt-4 space-y-4">
          <h2 className="text-sm font-semibold text-[#F8FAFC]">Run History</h2>
          <RunHistoryTable
            runs={runs?.items}
            isLoading={runsLoading}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
