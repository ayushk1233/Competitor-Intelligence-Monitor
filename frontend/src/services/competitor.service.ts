import { apiClient } from "@/lib/api-client";
import type {
  CompetitorCreateRequest,
  CompetitorResponse,
  CompetitorListResponse,
} from "@/types/api";

export async function fetchCompetitors(
  watchlistId: string
): Promise<CompetitorListResponse> {
  const response = await apiClient.get<CompetitorListResponse>(
    `/api/watchlists/${watchlistId}/competitors`
  );
  return response.data;
}

export async function addCompetitor(
  watchlistId: string,
  data: CompetitorCreateRequest
): Promise<CompetitorResponse> {
  const response = await apiClient.post<CompetitorResponse>(
    `/api/watchlists/${watchlistId}/competitors`,
    data
  );
  return response.data;
}

export async function deleteCompetitor(
  watchlistId: string,
  competitorId: string
): Promise<void> {
  await apiClient.delete(
    `/api/watchlists/${watchlistId}/competitors/${competitorId}`
  );
}
