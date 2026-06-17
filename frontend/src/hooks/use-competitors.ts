"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { QUERY_KEYS } from "@/constants";
import {
  fetchCompetitors,
  addCompetitor,
  deleteCompetitor,
} from "@/services/competitor.service";
import type { CompetitorCreateRequest } from "@/types/api";

export function useCompetitors(watchlistId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.competitors(watchlistId),
    queryFn: () => fetchCompetitors(watchlistId),
  });
}

export function useAddCompetitor(watchlistId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CompetitorCreateRequest) =>
      addCompetitor(watchlistId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.competitors(watchlistId),
      });
    },
  });
}

export function useDeleteCompetitor(watchlistId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (competitorId: string) =>
      deleteCompetitor(watchlistId, competitorId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.competitors(watchlistId),
      });
      queryClient.invalidateQueries({
        queryKey: ["dashboard-summary"],
      });
      queryClient.invalidateQueries({
        queryKey: ["dashboard-competitors"],
      });
    },
  });
}
