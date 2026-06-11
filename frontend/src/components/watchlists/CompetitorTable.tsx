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
    <TableRow className="border-[rgba(255,255,255,0.1)]">
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
  low: "text-[#A0A0A0] border-[rgba(255,255,255,0.1)] bg-[#2A2A2A]",
};

export function CompetitorTable({ watchlistId, competitors, isLoading }: CompetitorTableProps) {
  return (
    <div className="rounded-lg border border-[rgba(255,255,255,0.1)] bg-[#1E1E1E]">
      {isLoading ? (
        <Table>
          <TableHeader>
            <TableRow className="border-[rgba(255,255,255,0.1)] hover:bg-transparent">
              <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Company Name</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Domain</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Priority</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Monitoring</TableHead>
              <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Status</TableHead>
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
          <p className="text-sm text-[#A0A0A0]">No competitors yet</p>
          <p className="text-xs text-[#6B7280]">
            Add your first competitor to start monitoring
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-[rgba(255,255,255,0.1)] hover:bg-transparent">
                <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Company Name</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Domain</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Priority</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Monitoring</TableHead>
                <TableHead className="text-xs font-medium uppercase text-[#A0A0A0]">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {competitors.map((c) => (
                <TableRow key={c.id} className="border-[rgba(255,255,255,0.1)] hover:bg-[#2A2A2A]/50">
                  <TableCell className="text-sm font-medium">
                    <Link
                      href={ROUTES.competitorDetail(watchlistId, c.company_name)}
                      className="flex items-center gap-1.5 text-[#BC6C50] transition-colors hover:text-[#BC6C50]/80 hover:underline"
                    >
                      {c.company_name}
                      <ExternalLink className="h-3 w-3" />
                    </Link>
                  </TableCell>
                  <TableCell className="text-sm text-[#A0A0A0]">
                    {c.domain || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={`text-[10px] font-semibold capitalize ${priorityColors[c.priority] ?? priorityColors.medium}`}>
                      {c.priority}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-[#A0A0A0]">
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
