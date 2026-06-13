"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { QUERY_KEYS } from "@/constants";
import {
  fetchNotificationChannels,
  createNotificationChannel,
  updateNotificationChannel,
  deleteNotificationChannel,
} from "@/services/notification.service";
import type {
  NotificationChannelCreateRequest,
  NotificationChannelUpdateRequest,
} from "@/types/api";

export function useNotificationChannels() {
  return useQuery({
    queryKey: QUERY_KEYS.notificationChannels,
    queryFn: fetchNotificationChannels,
  });
}

export function useCreateNotificationChannel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: NotificationChannelCreateRequest) =>
      createNotificationChannel(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.notificationChannels,
      });
    },
  });
}

export function useUpdateNotificationChannel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: NotificationChannelUpdateRequest;
    }) => updateNotificationChannel(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.notificationChannels,
      });
    },
  });
}

export function useDeleteNotificationChannel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteNotificationChannel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.notificationChannels,
      });
    },
  });
}
