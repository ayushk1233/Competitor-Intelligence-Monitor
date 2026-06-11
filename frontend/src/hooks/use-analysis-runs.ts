"use client";

import { useQuery } from "@tanstack/react-query";
import { POLL_INTERVAL } from "@/constants";
import { fetchRecentRuns } from "@/services/analysis.service";

export const QUERY_KEY_RECENT_RUNS = ["recent-analysis-runs"] as const;

export function useRecentAnalysisRuns() {
  return useQuery({
    queryKey: QUERY_KEY_RECENT_RUNS,
    queryFn: fetchRecentRuns,
    refetchInterval: POLL_INTERVAL,
  });
}
