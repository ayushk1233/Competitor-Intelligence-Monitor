"use client";

import { useQuery } from "@tanstack/react-query";
import { QUERY_KEYS } from "@/constants";
import {
  fetchCompetitorAnalysis,
  fetchCompetitorHistory,
  fetchCompetitorDrift,
} from "@/services/competitor-detail.service";

export function useCompetitorAnalysis(companyName: string) {
  return useQuery({
    queryKey: QUERY_KEYS.competitorAnalysis(companyName),
    queryFn: () => fetchCompetitorAnalysis(companyName),
    enabled: !!companyName,
  });
}

export function useCompetitorHistory(companyName: string) {
  return useQuery({
    queryKey: QUERY_KEYS.competitorHistory(companyName),
    queryFn: () => fetchCompetitorHistory(companyName),
    enabled: !!companyName,
  });
}

export function useCompetitorDrift(companyName: string) {
  return useQuery({
    queryKey: QUERY_KEYS.competitorDrift(companyName),
    queryFn: () => fetchCompetitorDrift(companyName),
    enabled: !!companyName,
  });
}
