"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Bell } from "lucide-react";
import type { DashboardAlertResponse } from "@/types/api";

interface AlertFeedProps {
  alerts: DashboardAlertResponse[] | undefined;
  isLoading: boolean;
}

const severityConfig = {
  HIGH: { class: "bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30" as const },
  MEDIUM: { class: "bg-[#D97706]/15 text-[#D97706] border-[#D97706]/30" as const },
  LOW: { class: "bg-[#3B82F6]/15 text-[#3B82F6] border-[#3B82F6]/30" as const },
} as const;

function SeverityBadge({ severity }: { severity: string }) {
  const config = severityConfig[severity as keyof typeof severityConfig] ?? severityConfig.LOW;
  return (
    <Badge variant="outline" className={`border text-xs font-medium ${config.class}`}>
      {severity}
    </Badge>
  );
}

function AlertItem({ alert }: { alert: DashboardAlertResponse }) {
  const date = alert.created_at
    ? new Date(alert.created_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <div className="flex items-start gap-3 rounded-lg border border-[#1A2332] bg-[#0B1020] p-3">
      <SeverityBadge severity={alert.severity} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-[#F8FAFC]">
          {alert.company_name}
        </p>
        <p className="mt-0.5 text-xs text-[var(--muted-text)]">
          {alert.headline || alert.summary || "No details"}
        </p>
      </div>
      <span className="shrink-0 text-xs text-[var(--muted-text)]">{date}</span>
    </div>
  );
}

function SkeletonAlert() {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-[#1A2332] bg-[#0B1020] p-3">
      <Skeleton className="h-5 w-14 rounded-full bg-[#1A2332]" />
      <div className="flex-1 space-y-1">
        <Skeleton className="h-4 w-28 bg-[#1A2332]" />
        <Skeleton className="h-3 w-40 bg-[#1A2332]" />
      </div>
      <Skeleton className="h-3 w-16 bg-[#1A2332]" />
    </div>
  );
}

export function AlertFeed({ alerts, isLoading }: AlertFeedProps) {
  return (
    <Card className="border-[#1A2332] bg-[#121826]">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm font-semibold text-[#F8FAFC]">
          <Bell className="h-4 w-4 text-[#14B8A6]" />
          Recent Alerts
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <>
            <SkeletonAlert />
            <SkeletonAlert />
            <SkeletonAlert />
          </>
        ) : !alerts || alerts.length === 0 ? (
          <div className="flex flex-col items-center gap-1 py-8 text-center">
            <Bell className="h-8 w-8 text-[#1A2332]" />
            <p className="text-sm text-[var(--muted-text)]">No alerts yet</p>
            <p className="text-xs text-[#6B7280]">
              Alerts appear when competitor drift is detected
            </p>
          </div>
        ) : (
          alerts.slice(0, 5).map((alert, i) => <AlertItem key={`${alert.company_name}-${i}`} alert={alert} />)
        )}
      </CardContent>
    </Card>
  );
}
