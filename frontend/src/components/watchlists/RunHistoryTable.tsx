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
    class: "bg-[var(--muted-bg)] text-[var(--muted-text)] border-[var(--muted-border)]",
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
    <TableRow className="border-[var(--dialog-border)]">
      <TableCell><Skeleton className="h-5 w-20 rounded-full bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-16 bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-8 bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-8 bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-8 bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-24 bg-[#2A2A2A]" /></TableCell>
    </TableRow>
  );
}

export function RunHistoryTable({ runs, isLoading }: RunHistoryTableProps) {
  return (
    <div className="rounded-lg border border-[var(--dialog-border)] bg-[var(--dialog-bg)]">
      {isLoading ? (
        <Table>
          <TableHeader>
            <TableRow className="border-[var(--dialog-border)] hover:bg-transparent">
              <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Status</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Trigger</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Checked</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Alerts</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Sent</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Created</TableHead>
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
          <Activity className="h-8 w-8 text-[#2A2A2A]" />
          <p className="text-sm text-[var(--muted-text)]">No monitoring runs yet</p>
          <p className="text-xs text-[#6B7280]">
            Trigger a monitoring run to see results here
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-[var(--dialog-border)] hover:bg-transparent">
                <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Status</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Trigger</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Checked</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Alerts</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Sent</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--muted-text)]">Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((run) => (
                <TableRow key={run.id} className="border-[var(--dialog-border)] hover:bg-[var(--dialog-surface)]/50">
                  <TableCell>
                    <StatusBadge status={run.status} />
                  </TableCell>
                  <TableCell className="text-sm text-[var(--dialog-text)]">
                    {run.trigger_type}
                  </TableCell>
                  <TableCell className="text-sm text-[var(--dialog-text)]">
                    {run.competitors_checked}
                  </TableCell>
                  <TableCell className="text-sm text-[var(--dialog-text)]">
                    {run.alerts_generated}
                  </TableCell>
                  <TableCell className="text-sm text-[var(--dialog-text)]">
                    {run.notifications_sent}
                  </TableCell>
                  <TableCell className="text-sm text-[var(--muted-text)]">
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
