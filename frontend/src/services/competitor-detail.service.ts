import { apiClient } from "@/lib/api-client";
import type {
  CompetitorAnalysisResponse,
  CompetitorHistoryItem,
  DriftReport,
} from "@/types/api";

export async function fetchCompetitorAnalysis(
  companyName: string
): Promise<CompetitorAnalysisResponse> {
  const response = await apiClient.get<CompetitorAnalysisResponse>(
    `/api/competitors/${encodeURIComponent(companyName)}/latest`
  );
  return response.data;
}

export async function fetchCompetitorHistory(
  companyName: string
): Promise<CompetitorHistoryItem[]> {
  const response = await apiClient.get<CompetitorHistoryItem[]>(
    `/api/competitors/${encodeURIComponent(companyName)}/history`
  );
  return response.data;
}

export async function fetchCompetitorDrift(
  companyName: string
): Promise<DriftReport> {
  const response = await apiClient.get<DriftReport>(
    `/api/competitors/${encodeURIComponent(companyName)}/drift`
  );
  return response.data;
}
