"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle } from "lucide-react";
import type { DashboardAlertResponse } from "@/types/api";

type SeverityLevel = "all" | "high" | "medium" | "low";

type SeverityStyle = {
  border: string;
  pill: string;
  pillText: string;
};

const severityStyles: Record<SeverityLevel, SeverityStyle> = {
  all: {
    border: "bg-neutral-500",
    pill: "bg-neutral-100",
    pillText: "text-neutral-800",
  },
  high: {
    border: "bg-red-500",
    pill: "bg-white",
    pillText: "text-red-600",
  },
  medium: {
    border: "bg-amber-500",
    pill: "bg-amber-100",
    pillText: "text-amber-800",
  },
  low: {
    border: "bg-emerald-500",
    pill: "bg-emerald-100",
    pillText: "text-emerald-800",
  },
};

function toSeverityLevel(severity: string): SeverityLevel {
  if (severity === "HIGH" || severity === "CRITICAL") return "high";
  if (severity === "MEDIUM") return "medium";
  return "low";
}

function toLabel(severity: string): string {
  if (severity === "CRITICAL") return "Critical";
  return severity.charAt(0) + severity.slice(1).toLowerCase();
}

function SingleAlertRow({ alert }: { alert: DashboardAlertResponse }) {
  const level = toSeverityLevel(alert.severity);
  const style = severityStyles[level];

  return (
    <div className="relative flex flex-col p-6 border-b border-border bg-transparent hover:bg-neutral-800/30 transition-colors last:border-b-0">
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${style.border}`} />
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-base font-bold text-foreground">{alert.company_name}</span>
          <span className={`${style.pill} ${style.pillText} px-2 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wide`}>
            {toLabel(alert.severity)}
          </span>
        </div>
        <span className="text-xs text-neutral-500 font-medium">
          {alert.created_at
            ? new Date(alert.created_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })
            : ""}
        </span>
      </div>
      <p className="text-sm text-foreground leading-relaxed mt-2">{alert.headline}</p>
      {alert.summary && (
        <p className="text-sm text-neutral-400 leading-relaxed mt-1.5">{alert.summary}</p>
      )}
    </div>
  );
}

const filterTabs: { label: string; value: SeverityLevel }[] = [
  { label: "All", value: "all" },
  { label: "High", value: "high" },
  { label: "Medium", value: "medium" },
  { label: "Low", value: "low" },
];

export default function AlertsPage() {
  const [activeFilter, setActiveFilter] = useState<SeverityLevel>("all");
  const { data, isLoading } = useQuery({
    queryKey: ["all-alerts"],
    queryFn: async () => {
      const res = await apiClient.get<DashboardAlertResponse[]>("/api/alerts");
      return res.data;
    },
    refetchInterval: 10_000,
  });

  const filtered = data?.filter((a) => {
    if (activeFilter === "all") return true;
    if (activeFilter === "high") return a.severity === "HIGH" || a.severity === "CRITICAL";
    if (activeFilter === "medium") return a.severity === "MEDIUM";
    return a.severity === "LOW";
  });

  return (
    <div className="p-8">
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        {/* Header */}
        <div className="flex justify-end items-center px-6 py-4 border-b border-border">
          <div className="flex gap-2 items-center">
            {filterTabs.map((tab) => {
              const isActive = activeFilter === tab.value;
              return (
                <button
                  key={tab.value}
                  onClick={() => setActiveFilter(tab.value)}
                  className={
                    isActive
                      ? "bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium"
                      : "bg-transparent border border-neutral-700 text-neutral-300 px-3 py-1 rounded-full text-sm hover:bg-neutral-800 transition-colors"
                  }
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Alerts List */}
        {isLoading ? (
          <div>
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-24 rounded-none bg-neutral-900" />
            ))}
          </div>
        ) : !filtered || filtered.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-16 text-center">
            <AlertTriangle className="h-8 w-8 text-neutral-500" />
            <p className="text-sm text-neutral-400">{activeFilter === "all" ? "No alerts" : `No ${activeFilter} alerts`}</p>
            <p className="text-xs text-neutral-500">All clear{activeFilter === "all" ? "" : " for this severity level"}</p>
          </div>
        ) : (
          filtered.map((alert, i) => (
            <SingleAlertRow key={alert.id || i} alert={alert} />
          ))
        )}
      </div>
    </div>
  );
}
