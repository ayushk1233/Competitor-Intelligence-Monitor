import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: number | string;
  icon: ReactNode;
  isLoading?: boolean;
}

export function MetricCard({ title, value, icon, isLoading }: MetricCardProps) {
  return (
    <Card className="border-[var(--dialog-border)] bg-[var(--dialog-bg)]">
      <CardContent className="flex items-center gap-4 p-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--accent-color-10)] text-[var(--accent-color)]">
          {icon}
        </div>
        <div className="flex flex-col">
          <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground font-mono">
            {title}
          </span>
          {isLoading ? (
            <Skeleton className="mt-1 h-7 w-16 bg-[#2A2A2A]" />
          ) : (
            <span className="text-2xl font-bold text-foreground">{value}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
