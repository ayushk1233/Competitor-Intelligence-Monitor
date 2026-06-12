"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Radar } from "lucide-react";
import type { DashboardAlertResponse } from "@/types/api";

interface IntelligenceFeedProps {
  alerts: DashboardAlertResponse[] | undefined;
  isLoading: boolean;
}

const severityConfig = {
  HIGH: { label: "High", border: "border-l-[#EF4444]", bg: "bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30" },
  MEDIUM: { label: "Medium", border: "border-l-[#F59E0B]", bg: "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30" },
  LOW: { label: "Low", border: "border-l-[#22C55E]", bg: "bg-[#22C55E]/15 text-[#22C55E] border-[#22C55E]/30" },
} as const;

function AlertItem({ alert }: { alert: DashboardAlertResponse }) {
  const config = severityConfig[alert.severity as keyof typeof severityConfig] ?? severityConfig.LOW;

  return (
    <div className={`border-l-4 ${config.border} rounded-r-lg border border-[rgba(255,255,255,0.1)] bg-[#1E1E1E] p-4`}>
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-white">{alert.company_name}</span>
            <Badge variant="outline" className={`text-[10px] font-semibold uppercase ${config.bg}`}>
              {config.label}
            </Badge>
          </div>
            <p className="mt-1 text-sm text-white">{alert.headline}</p>
          {alert.summary && (
            <p className="mt-0.5 text-xs text-[#A0A0A0]">{alert.summary}</p>
          )}
        </div>
        <span className="shrink-0 text-xs text-[#A0A0A0]">
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
    </div>
  );
}

const filters = ["All", "High", "Medium", "Low"] as const;

export function IntelligenceFeed({ alerts, isLoading }: IntelligenceFeedProps) {
  const [activeFilter, setActiveFilter] = useState<string>("All");

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-lg bg-[#2A2A2A]" />
        ))}
      </div>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <div className="flex flex-col items-center gap-4 rounded-lg border border-[rgba(255,255,255,0.1)] bg-[#1E1E1E] py-20 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-[#2A2A2A]">
          <Radar className="h-6 w-6 text-[#6B7280]" />
        </div>
        <div>
          <p className="text-base font-medium text-white">No intelligence yet</p>
          <p className="mt-1 text-sm text-[#A0A0A0]">
            Run your first monitoring to see competitor changes here
          </p>
        </div>
      </div>
    );
  }

  const filtered =
    activeFilter === "All"
      ? alerts
      : alerts.filter((a) => a.severity === activeFilter.toUpperCase());

  const counts = {
    All: alerts.length,
    High: alerts.filter((a) => a.severity === "HIGH").length,
    Medium: alerts.filter((a) => a.severity === "MEDIUM").length,
    Low: alerts.filter((a) => a.severity === "LOW").length,
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white font-mono">Alerts</h3>
        <div className="flex gap-1 rounded-lg bg-[#1E1E1E] p-0.5">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                activeFilter === f
                  ? "bg-[#2A2A2A] text-white"
                  : "text-[#A0A0A0] hover:text-white"
              }`}
            >
              {f} ({counts[f]})
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-2">
        {filtered.map((alert, i) => (
          <AlertItem key={`${alert.company_name}-${i}`} alert={alert} />
        ))}
      </div>
    </div>
  );
}
