"use client";

import Link from "next/link";
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
import { ROUTES } from "@/constants";
import { Users, ExternalLink } from "lucide-react";
import type { CompetitorResponse } from "@/types/api";

interface CompetitorTableProps {
  watchlistId: string;
  competitors: CompetitorResponse[] | undefined;
  isLoading: boolean;
}

function SkeletonRow() {
  return (
    <TableRow className="border-[var(--dialog-border)]">
      <TableCell><Skeleton className="h-4 w-32 bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-28 bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-20 bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-4 w-24 bg-[#2A2A2A]" /></TableCell>
      <TableCell><Skeleton className="h-5 w-16 rounded-full bg-[#2A2A2A]" /></TableCell>
    </TableRow>
  );
}

const priorityColors: Record<string, string> = {
  high: "text-[#EF4444] border-[#EF4444]/30 bg-[#EF4444]/15",
  medium: "text-[#F59E0B] border-[#F59E0B]/30 bg-[#F59E0B]/15",
  low: "text-[var(--dialog-muted)] border-[var(--dialog-border)] bg-[var(--dialog-surface)]",
};

export function CompetitorTable({ watchlistId, competitors, isLoading }: CompetitorTableProps) {
  return (
    <div className="rounded-lg border border-[var(--dialog-border)] bg-[var(--dialog-bg)]">
      {isLoading ? (
        <Table>
          <TableHeader>
            <TableRow className="border-[var(--dialog-border)] hover:bg-transparent">
              <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Company Name</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Domain</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Priority</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Monitoring</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Status</TableHead>
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
      ) : !competitors || competitors.length === 0 ? (
        <div className="flex flex-col items-center gap-1 py-12 text-center">
          <Users className="h-8 w-8 text-[#2A2A2A]" />
          <p className="text-sm text-[var(--dialog-muted)]">No competitors yet</p>
          <p className="text-xs text-[#6B7280]">
            Add your first competitor to start monitoring
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-[var(--dialog-border)] hover:bg-transparent">
                <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Company Name</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Domain</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Priority</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Monitoring</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[var(--dialog-muted)]">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {competitors.map((c) => (
                <TableRow key={c.id} className="border-[var(--dialog-border)] hover:bg-[var(--dialog-surface)]/50">
                  <TableCell className="text-sm font-medium">
                    <Link
                      href={ROUTES.battlecards}
                      className="flex items-center gap-1.5 text-[var(--accent-color)] transition-colors hover:text-[var(--accent-color-80)] hover:underline"
                    >
                      {c.company_name}
                      <ExternalLink className="h-3 w-3" />
                    </Link>
                  </TableCell>
                  <TableCell className="text-sm text-[var(--dialog-muted)]">
                    {c.domain || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={`text-[10px] font-semibold capitalize ${priorityColors[c.priority] ?? priorityColors.medium}`}>
                      {c.priority}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-[var(--dialog-muted)]">
                    {c.monitoring_enabled ? (
                      <span className="text-[#22C55E]">Enabled</span>
                    ) : (
                      <span className="text-[#6B7280]">Disabled</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {c.is_active ? (
                      <Badge
                        variant="outline"
                        className="border-[#22C55E]/30 bg-[#22C55E]/15 text-[#22C55E] text-[10px] font-medium"
                      >
                        Active
                      </Badge>
                    ) : (
                      <Badge
                        variant="outline"
                        className="border-[#6B7280]/30 bg-[#6B7280]/15 text-[#6B7280] text-[10px] font-medium"
                      >
                        Inactive
                      </Badge>
                    )}
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
