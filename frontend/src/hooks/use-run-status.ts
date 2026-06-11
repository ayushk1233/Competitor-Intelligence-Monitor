"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchRunStatus } from "@/services/analysis.service";

export function useRunStatus(runId: string | undefined) {
  return useQuery({
    queryKey: ["run-status", runId],
    queryFn: () => fetchRunStatus(runId!),
    enabled: !!runId,
    refetchInterval: 5000,
  });
}
