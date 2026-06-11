"use client";

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

interface RunHistoryTableProps {
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

function SkeletonRow() {
  return (
    <TableRow className="border-[#1A2332]">
      <TableCell><Skeleton className="h-5 w-20 rounded-full bg-[#1A2332]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-16 bg-[#1A2332]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-8 bg-[#1A2332]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-8 bg-[#1A2332]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-8 bg-[#1A2332]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-24 bg-[#1A2332]" /></TableCell>
    </TableRow>
  );
}

export function RunHistoryTable({ runs, isLoading }: RunHistoryTableProps) {
  return (
    <div className="rounded-lg border border-[#1A2332] bg-[#121826]">
      {isLoading ? (
        <Table>
          <TableHeader>
            <TableRow className="border-[#1A2332] hover:bg-transparent">
              <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Status</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Trigger</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Checked</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Alerts</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Sent</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Created</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <SkeletonRow />
            <SkeletonRow />
            <SkeletonRow />
            <SkeletonRow />
            <SkeletonRow />
          </TableBody>
        </Table>
      ) : !runs || runs.length === 0 ? (
        <div className="flex flex-col items-center gap-1 py-12 text-center">
          <Activity className="h-8 w-8 text-[#1A2332]" />
          <p className="text-sm text-[#94A3B8]">No monitoring runs yet</p>
          <p className="text-xs text-[#6B7280]">
            Trigger a monitoring run to see results here
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
                <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Sent</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#94A3B8]">Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((run) => (
                <TableRow key={run.id} className="border-[#1A2332] hover:bg-[#1A2332]/50">
                  <TableCell>
                    <StatusBadge status={run.status} />
                  </TableCell>
                  <TableCell className="text-sm text-[#CBD5E1]">
                    {run.trigger_type}
                  </TableCell>
                  <TableCell className="text-sm text-[#CBD5E1]">
                    {run.competitors_checked}
                  </TableCell>
                  <TableCell className="text-sm text-[#CBD5E1]">
                    {run.alerts_generated}
                  </TableCell>
                  <TableCell className="text-sm text-[#CBD5E1]">
                    {run.notifications_sent}
                  </TableCell>
                  <TableCell className="text-sm text-[#94A3B8]">
                    {new Date(run.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
