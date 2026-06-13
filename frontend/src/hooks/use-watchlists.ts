"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { QUERY_KEYS } from "@/constants";
import {
  fetchWatchlists,
  createWatchlist,
  updateWatchlist,
  deleteWatchlist,
} from "@/services/watchlist.service";
import type { WatchlistCreateRequest, WatchlistUpdateRequest } from "@/types/api";

export function useWatchlists() {
  return useQuery({
    queryKey: QUERY_KEYS.watchlists,
    queryFn: fetchWatchlists,
  });
}

function invalidateDashboardQueries(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: QUERY_KEYS.watchlists });
  queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
  queryClient.invalidateQueries({ queryKey: ["dashboard-competitors"] });
  queryClient.invalidateQueries({ queryKey: ["recent-alerts"] });
  queryClient.invalidateQueries({ queryKey: ["all-alerts"] });
  queryClient.invalidateQueries({ queryKey: ["recent-analysis-runs"] });
}

export function useCreateWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: WatchlistCreateRequest) => createWatchlist(data),
    onSuccess: () => {
      invalidateDashboardQueries(queryClient);
    },
  });
}

export function useUpdateWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: WatchlistUpdateRequest }) =>
      updateWatchlist(id, data),
    onSuccess: () => {
      invalidateDashboardQueries(queryClient);
    },
  });
}

export function useDeleteWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteWatchlist(id),
    onSuccess: () => {
      invalidateDashboardQueries(queryClient);
    },
  });
}
