import { apiClient } from "@/lib/api-client";
import type {
  DashboardSummaryResponse,
  DashboardRecentRunsResponse,
  DashboardRecentAlertsResponse,
  DashboardActivityResponse,
  DashboardCompetitorsResponse,
} from "@/types/api";

export async function fetchDashboardSummary(): Promise<DashboardSummaryResponse> {
  const response = await apiClient.get<DashboardSummaryResponse>(
    "/api/dashboard/summary"
  );
  return response.data;
}

export async function fetchRecentRuns(): Promise<DashboardRecentRunsResponse> {
  const response = await apiClient.get<DashboardRecentRunsResponse>(
    "/api/dashboard/recent-runs"
  );
  return response.data;
}

export async function fetchRecentAlerts(): Promise<DashboardRecentAlertsResponse> {
  const response = await apiClient.get<DashboardRecentAlertsResponse>(
    "/api/dashboard/recent-alerts"
  );
  return response.data;
}

export async function fetchActivity(): Promise<DashboardActivityResponse> {
  const response = await apiClient.get<DashboardActivityResponse>(
    "/api/dashboard/activity"
  );
  return response.data;
}

export async function fetchDashboardCompetitors(): Promise<DashboardCompetitorsResponse> {
  const response = await apiClient.get<DashboardCompetitorsResponse>(
    "/api/dashboard/competitors"
  );
  return response.data;
}
