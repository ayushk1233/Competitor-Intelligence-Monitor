import { apiClient } from "@/lib/api-client";
import type {
  AnalysisRequest,
  AnalysisResponse,
  RunListItem,
  RunStatusResponse,
  IntelligenceReport,
} from "@/types/api";

export async function triggerAnalysis(
  data: AnalysisRequest
): Promise<AnalysisResponse> {
  const response = await apiClient.post<AnalysisResponse>(
    "/api/analyze",
    data
  );
  return response.data;
}

export async function fetchRecentRuns(): Promise<RunListItem[]> {
  const response = await apiClient.get<RunListItem[]>("/api/runs");
  return response.data;
}

export async function fetchRunStatus(
  runId: string
): Promise<RunStatusResponse> {
  const response = await apiClient.get<RunStatusResponse>(
    `/api/status/${runId}`
  );
  return response.data;
}

export async function fetchReport(
  runId: string
): Promise<IntelligenceReport> {
  const response = await apiClient.get<IntelligenceReport>(
    `/api/report/${runId}`
  );
  return response.data;
}

export async function deleteRun(runId: string): Promise<void> {
  await apiClient.delete(`/api/runs/${runId}`);
}

export async function deleteMonitoringRun(
  watchlistId: string,
  runId: string
): Promise<void> {
  await apiClient.delete(`/api/watchlists/${watchlistId}/runs/${runId}`);
}
