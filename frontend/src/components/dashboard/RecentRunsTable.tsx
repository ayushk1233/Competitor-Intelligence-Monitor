"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Activity } from "lucide-react";
import type { MonitoringRunResponse } from "@/types/api";

interface RecentRunsTableProps {
  runs: MonitoringRunResponse[] | undefined;
  isLoading: boolean;
}

const statusConfig: Record<string, { class: string; label: string }> = {
  COMPLETED: {
    class: "bg-[#22C55E]/15 text-[#22C55E] border-[#22C55E]/30",
    label: "Completed",
  },
  RUNNING: {
    class: "bg-[#8B5CF6]/15 text-[#8B5CF6] border-[#8B5CF6]/30",
    label: "Running",
  },
  QUEUED: {
    class: "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30",
    label: "Queued",
  },
  FAILED: {
    class: "bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30",
    label: "Failed",
  },
};

function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] ?? {
    class: "bg-[#94A3B8]/15 text-[#94A3B8] border-[#94A3B8]/30",
    label: status,
  };
  return (
    <Badge variant="outline" className={`border text-xs font-medium ${config.class}`}>
      {config.label}
    </Badge>
  );
}

function RunRow({ run }: { run: MonitoringRunResponse }) {
  const date = run.created_at
    ? new Date(run.created_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <TableRow className="border-[#2D3540] hover:bg-[#2A313C]/50">
      <TableCell>
        <StatusBadge status={run.status} />
      </TableCell>
      <TableCell className="text-sm text-[#F8FAFC]">{run.trigger_type}</TableCell>
      <TableCell className="text-sm text-[#F8FAFC]">{run.competitors_checked}</TableCell>
      <TableCell className="text-sm text-[#F8FAFC]">{run.alerts_generated}</TableCell>
      <TableCell className="text-sm text-[#CBD5E1]">{date}</TableCell>
    </TableRow>
  );
}

function SkeletonRow() {
  return (
    <TableRow className="border-[#2D3540]">
      <TableCell><Skeleton className="h-5 w-20 rounded-full bg-[#2D3540]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-16 bg-[#2D3540]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-8 bg-[#2D3540]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-8 bg-[#2D3540]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-24 bg-[#2D3540]" /></TableCell>
    </TableRow>
  );
}

export function RecentRunsTable({ runs, isLoading }: RecentRunsTableProps) {
  return (
    <Card className="border-[#2D3540] bg-[#232931]">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm font-semibold text-[#F8FAFC]">
          <Activity className="h-4 w-4 text-[#14B8A6]" />
          Recent Runs
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {isLoading ? (
          <Table>
            <TableHeader>
              <TableRow className="border-[#2D3540] hover:bg-transparent">
                <TableHead className="text-xs font-medium uppercase text-[#E2E8F0]">Status</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#E2E8F0]">Trigger</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#E2E8F0]">Checked</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#E2E8F0]">Alerts</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#E2E8F0]">Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <SkeletonRow />
              <SkeletonRow />
              <SkeletonRow />
            </TableBody>
          </Table>
        ) : !runs || runs.length === 0 ? (
          <div className="flex flex-col items-center gap-1 py-8 text-center">
            <Activity className="h-8 w-8 text-[#2D3540]" />
            <p className="text-sm text-[#E2E8F0]">No runs yet</p>
            <p className="text-xs text-[#CBD5E1]">
              Monitoring runs appear after watchlists are triggered
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-[#1A2332] hover:bg-transparent">
                  <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Status</TableHead>
                  <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Trigger</TableHead>
                  <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Checked</TableHead>
                  <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Alerts</TableHead>
                  <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runs.slice(0, 5).map((run) => (
                  <RunRow key={run.id} run={run} />
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
