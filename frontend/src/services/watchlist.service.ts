import { apiClient } from "@/lib/api-client";
import type {
  WatchlistCreateRequest,
  WatchlistUpdateRequest,
  WatchlistResponse,
  WatchlistListResponse,
} from "@/types/api";

export async function fetchWatchlists(): Promise<WatchlistListResponse> {
  const response = await apiClient.get<WatchlistListResponse>("/api/watchlists");
  return response.data;
}

export async function createWatchlist(
  data: WatchlistCreateRequest
): Promise<WatchlistResponse> {
  const response = await apiClient.post<WatchlistResponse>(
    "/api/watchlists",
    data
  );
  return response.data;
}

export async function updateWatchlist(
  id: string,
  data: WatchlistUpdateRequest
): Promise<WatchlistResponse> {
  const response = await apiClient.put<WatchlistResponse>(
    `/api/watchlists/${id}`,
    data
  );
  return response.data;
}

export async function deleteWatchlist(id: string): Promise<void> {
  await apiClient.delete(`/api/watchlists/${id}`);
}
