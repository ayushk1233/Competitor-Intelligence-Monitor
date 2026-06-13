"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { QUERY_KEYS } from "@/constants";
import {
  fetchMonitoringRuns,
  createMonitoringRun,
} from "@/services/monitoring-run.service";
import type { MonitoringRunCreateRequest } from "@/types/api";

export function useMonitoringRuns(watchlistId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.runs(watchlistId),
    queryFn: () => fetchMonitoringRuns(watchlistId),
  });
}

export function useCreateMonitoringRun(watchlistId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: MonitoringRunCreateRequest) =>
      createMonitoringRun(watchlistId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.runs(watchlistId),
      });
    },
  });
}
