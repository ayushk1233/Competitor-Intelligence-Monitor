import { apiClient } from "@/lib/api-client";
import type {
  NotificationChannelCreateRequest,
  NotificationChannelUpdateRequest,
  NotificationChannelResponse,
  NotificationChannelListResponse,
} from "@/types/api";

export async function fetchNotificationChannels(): Promise<NotificationChannelListResponse> {
  const response = await apiClient.get<NotificationChannelListResponse>(
    "/api/notifications/channels"
  );
  return response.data;
}

export async function createNotificationChannel(
  data: NotificationChannelCreateRequest
): Promise<NotificationChannelResponse> {
  const response = await apiClient.post<NotificationChannelResponse>(
    "/api/notifications/channels",
    data
  );
  return response.data;
}

export async function updateNotificationChannel(
  id: string,
  data: NotificationChannelUpdateRequest
): Promise<NotificationChannelResponse> {
  const response = await apiClient.put<NotificationChannelResponse>(
    `/api/notifications/channels/${id}`,
    data
  );
  return response.data;
}

export async function deleteNotificationChannel(
  id: string
): Promise<void> {
  await apiClient.delete(`/api/notifications/channels/${id}`);
}
