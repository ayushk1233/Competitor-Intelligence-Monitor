"use client";

import { useQuery } from "@tanstack/react-query";
import { QUERY_KEYS, POLL_INTERVAL } from "@/constants";
import {
  fetchDashboardSummary,
  fetchRecentRuns,
  fetchRecentAlerts,
  fetchActivity,
  fetchDashboardCompetitors,
} from "@/services/dashboard.service";

export function useDashboardSummary() {
  return useQuery({
    queryKey: QUERY_KEYS.dashboardSummary,
    queryFn: fetchDashboardSummary,
    refetchInterval: POLL_INTERVAL,
  });
}

export function useRecentRuns() {
  return useQuery({
    queryKey: QUERY_KEYS.recentRuns,
    queryFn: fetchRecentRuns,
    refetchInterval: POLL_INTERVAL,
  });
}

export function useRecentAlerts() {
  return useQuery({
    queryKey: QUERY_KEYS.recentAlerts,
    queryFn: fetchRecentAlerts,
    refetchInterval: POLL_INTERVAL,
  });
}

export function useDashboardActivity() {
  return useQuery({
    queryKey: QUERY_KEYS.activity,
    queryFn: fetchActivity,
  });
}

export function useDashboardCompetitors() {
  return useQuery({
    queryKey: ["dashboard-competitors"],
    queryFn: fetchDashboardCompetitors,
    refetchInterval: POLL_INTERVAL,
  });
}
