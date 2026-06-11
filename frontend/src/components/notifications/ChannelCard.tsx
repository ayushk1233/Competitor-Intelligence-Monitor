"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { useQuery } from "@tanstack/react-query";
import {
  Mail,
  MessageSquare,
  Link,
  Trash2,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
} from "lucide-react";
import { useUpdateNotificationChannel, useDeleteNotificationChannel } from "@/hooks/use-notifications";
import { apiClient } from "@/lib/api-client";
import { extractApiError } from "@/lib/utils";
import type { NotificationChannelResponse } from "@/types/api";

interface ChannelCardProps {
  channel: NotificationChannelResponse;
}

const channelIcons: Record<string, React.ReactNode> = {
  EMAIL: <Mail className="h-4 w-4" />,
  SLACK: <MessageSquare className="h-4 w-4" />,
  WEBHOOK: <Link className="h-4 w-4" />,
};

const channelLabels: Record<string, string> = {
  EMAIL: "Email",
  SLACK: "Slack",
  WEBHOOK: "Webhook",
};

export function ChannelCard({ channel }: ChannelCardProps) {
  const [deleteOpen, setDeleteOpen] = useState(false);
  const updateChannel = useUpdateNotificationChannel();
  const deleteChannel = useDeleteNotificationChannel();

  const { data: events = [] } = useQuery({
    queryKey: ["delivery-events", channel.id],
    queryFn: async () => {
      const res = await apiClient.get("/api/notification-events", {
        params: { channel_id: channel.id },
      });
      return res.data ?? [];
    },
    refetchInterval: 30_000,
  });

  const lastEvent = events[0] ?? null;
  const deliveryCount = events.length;
  const failedCount = events.filter((e: { delivery_status: string }) => e.delivery_status === "FAILED").length;

  const handleToggle = async (enabled: boolean) => {
    try {
      await updateChannel.mutateAsync({ id: channel.id, data: { enabled } });
      toast.success(enabled ? "Channel enabled" : "Channel disabled");
    } catch (error) {
      toast.error(extractApiError(error));
    }
  };

  const handleDelete = async () => {
    try {
      await deleteChannel.mutateAsync(channel.id);
      toast.success("Channel deleted");
      setDeleteOpen(false);
    } catch (error) {
      toast.error(extractApiError(error));
    }
  };

  return (
    <>
      <Card className="border-[#262626] bg-[#161616]">
        <CardContent className="flex flex-col gap-4 p-5">
          <div className="flex items-center justify-between">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#BC6C50]/10 text-[#BC6C50]">
              {channelIcons[channel.channel_type] ?? <Mail className="h-4 w-4" />}
            </div>
            <Switch
              checked={channel.enabled}
              onCheckedChange={handleToggle}
              disabled={updateChannel.isPending}
              className="data-[state=checked]:bg-[#BC6C50]"
            />
          </div>

          <div className="space-y-1">
            <h3 className="text-sm font-semibold text-white">
              {channel.label || channelLabels[channel.channel_type] || channel.channel_type}
            </h3>
            <p className="break-all text-xs text-[#A3A3A3]">
              {channel.channel_type === "EMAIL" ? channel.destination : (
                <span className="font-mono text-[#A3A3A3]">{channel.destination}</span>
              )}
            </p>
          </div>

          <div className="flex items-center gap-3 border-t border-[#262626] pt-3 text-xs text-[#666666]">
            {channel.verified ? (
              <span className="flex items-center gap-1 text-[#BC6C50]">
                <CheckCircle2 className="h-3 w-3" />
                Verified
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[#F59E0B]">
                <Clock className="h-3 w-3" />
                Pending
              </span>
            )}
            {lastEvent && (
              <span className="flex items-center gap-1">
                {lastEvent.delivery_status === "DELIVERED" ? (
                  <CheckCircle2 className="h-3 w-3 text-[#BC6C50]" />
                ) : lastEvent.delivery_status === "FAILED" ? (
                  <XCircle className="h-3 w-3 text-[#EF4444]" />
                ) : (
                  <Clock className="h-3 w-3 text-[#F59E0B]" />
                )}
                {deliveryCount} sent
                {failedCount > 0 && (
                  <span className="text-[#EF4444]">({failedCount} failed)</span>
                )}
              </span>
            )}
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-[#666666]">
              {channelLabels[channel.channel_type] || channel.channel_type}
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setDeleteOpen(true)}
              className="h-8 w-8 text-[#666666] hover:text-[#EF4444] hover:bg-transparent"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent className="border-[#262626] bg-[#0A0A0A] sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="text-white">Delete Channel</DialogTitle>
            <DialogDescription className="text-[#666666]">
              Are you sure you want to delete this notification channel? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setDeleteOpen(false)}
              className="text-[#666666] hover:text-white hover:bg-[#161616]"
            >
              Cancel
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteChannel.isPending}
              className="bg-[#EF4444] text-white hover:bg-[#EF4444]/90"
            >
              {deleteChannel.isPending ? (
                <>
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

export function ChannelCardSkeleton() {
  return (
    <Card className="border-[#262626] bg-[#161616]">
      <CardContent className="flex flex-col gap-4 p-5">
        <div className="flex items-center justify-between">
          <Skeleton className="h-9 w-9 rounded-lg bg-[#262626]" />
          <Skeleton className="h-5 w-8 rounded-full bg-[#262626]" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-4 w-3/4 bg-[#262626]" />
          <Skeleton className="h-3 w-full bg-[#262626]" />
        </div>
        <div className="flex items-center justify-between border-t border-[#262626] pt-3">
          <Skeleton className="h-3 w-20 bg-[#262626]" />
          <Skeleton className="h-4 w-4 rounded bg-[#262626]" />
        </div>
      </CardContent>
    </Card>
  );
}
