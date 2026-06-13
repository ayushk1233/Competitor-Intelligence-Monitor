import { apiClient } from "@/lib/api-client";
import type {
  MonitoringRunCreateRequest,
  MonitoringRunResponse,
  MonitoringRunListResponse,
} from "@/types/api";

export async function fetchMonitoringRuns(
  watchlistId: string
): Promise<MonitoringRunListResponse> {
  const response = await apiClient.get<MonitoringRunListResponse>(
    `/api/watchlists/${watchlistId}/runs`
  );
  return response.data;
}

export async function createMonitoringRun(
  watchlistId: string,
  data: MonitoringRunCreateRequest
): Promise<MonitoringRunResponse> {
  const response = await apiClient.post<MonitoringRunResponse>(
    `/api/watchlists/${watchlistId}/runs`,
    data
  );
  return response.data;
}
