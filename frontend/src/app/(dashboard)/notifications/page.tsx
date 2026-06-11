"use client";

import { useNotificationChannels } from "@/hooks/use-notifications";
import { ChannelCard, ChannelCardSkeleton } from "@/components/notifications/ChannelCard";
import { CreateChannelDialog } from "@/components/notifications/CreateChannelDialog";
import { EmptyState } from "@/components/shared/EmptyState";
import { Bell, AlertCircle } from "lucide-react";

export default function NotificationsPage() {
  const { data, isLoading, isError, error } = useNotificationChannels();

  if (isError) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white">Notifications</h1>
            <p className="text-sm text-[#A0A0A0]">Manage your notification channels</p>
          </div>
        </div>
        <div className="flex flex-col items-center gap-3 py-20 text-center">
          <AlertCircle className="h-10 w-10 text-[#EF4444]" />
          <p className="text-sm text-[#A3A3A3]">Failed to load notification channels</p>
          <p className="text-xs text-[#666666]">{(error as Error)?.message || "An error occurred"}</p>
        </div>
      </div>
    );
  }

  const channels = data?.items ?? [];

  return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white">Notifications</h1>
            <p className="text-sm text-[#A3A3A3]">Manage your notification channels</p>
        </div>
        {!isLoading && channels.length > 0 && <CreateChannelDialog />}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <ChannelCardSkeleton />
          <ChannelCardSkeleton />
          <ChannelCardSkeleton />
          <ChannelCardSkeleton />
          <ChannelCardSkeleton />
          <ChannelCardSkeleton />
        </div>
      ) : channels.length === 0 ? (
        <EmptyState
          icon={<Bell className="h-7 w-7" />}
          title="No notification channels configured"
          description="Create your first channel to receive alerts and notifications"
          cta={<CreateChannelDialog />}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {channels.map((ch) => (
            <ChannelCard key={ch.id} channel={ch} />
          ))}
        </div>
      )}
    </div>
  );
}
