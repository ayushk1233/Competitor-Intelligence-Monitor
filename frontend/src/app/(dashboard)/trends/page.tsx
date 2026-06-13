"use client";

import { ComingSoon } from "@/components/shared/ComingSoon";
import { TrendingUp } from "lucide-react";

export default function TrendsPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <p className="text-sm text-muted-foreground">Competitor momentum and market trends</p>
      </div>
      <ComingSoon
        icon={<TrendingUp className="h-6 w-6" />}
        title="Trends dashboard"
        description="Visualize competitor momentum scores, keyword trends, and market positioning over time. Charts and graphs coming soon."
      />
    </div>
  );
}
