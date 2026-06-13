"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { History, Plus } from "lucide-react";
import type { DashboardActivityItem } from "@/types/api";

interface ActivityTimelineProps {
  activities: DashboardActivityItem[] | undefined;
  isLoading: boolean;
}

const activityIcons: Record<string, React.ReactNode> = {
  WATCHLIST_CREATED: <Plus className="h-3.5 w-3.5" />,
};

const activityBg: Record<string, string> = {
  WATCHLIST_CREATED: "bg-[#14B8A6]/10 text-[#14B8A6]",
};

function ActivityDot({ type }: { type: string }) {
  return (
    <div
      className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
        activityBg[type] ?? "bg-[#1A2332] text-[var(--muted-text)]"
      }`}
    >
      {activityIcons[type] ?? <History className="h-3.5 w-3.5" />}
    </div>
  );
}

function ActivityItem({ item }: { item: DashboardActivityItem }) {
  const date = item.timestamp
    ? new Date(item.timestamp).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  const label: Record<string, string> = {
    WATCHLIST_CREATED: "Watchlist created",
  };

  return (
    <div className="flex items-start gap-3">
      <ActivityDot type={item.activity_type} />
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-[#F8FAFC]">
          {label[item.activity_type] ?? item.activity_type}
        </p>
        <p className="truncate text-xs text-[var(--muted-text)]">{item.title}</p>
      </div>
      <span className="shrink-0 text-xs text-[#6B7280]">{date}</span>
    </div>
  );
}

function SkeletonActivity() {
  return (
    <div className="flex items-start gap-3">
      <Skeleton className="h-7 w-7 rounded-full bg-[#1A2332]" />
      <div className="flex-1 space-y-1">
        <Skeleton className="h-4 w-32 bg-[#1A2332]" />
        <Skeleton className="h-3 w-24 bg-[#1A2332]" />
      </div>
      <Skeleton className="h-3 w-16 bg-[#1A2332]" />
    </div>
  );
}

export function ActivityTimeline({ activities, isLoading }: ActivityTimelineProps) {
  return (
    <Card className="border-[#1A2332] bg-[#121826]">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm font-semibold text-[#F8FAFC]">
          <History className="h-4 w-4 text-[#14B8A6]" />
          Activity
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <>
            <SkeletonActivity />
            <SkeletonActivity />
            <SkeletonActivity />
          </>
        ) : !activities || activities.length === 0 ? (
          <div className="flex flex-col items-center gap-1 py-8 text-center">
            <History className="h-8 w-8 text-[#1A2332]" />
            <p className="text-sm text-[var(--muted-text)]">No activity yet</p>
            <p className="text-xs text-[#6B7280]">
              Activity appears when you create watchlists
            </p>
          </div>
        ) : (
          activities.slice(0, 10).map((item, i) => (
            <ActivityItem key={`${item.activity_type}-${item.timestamp}-${i}`} item={item} />
          ))
        )}
      </CardContent>
    </Card>
  );
}
