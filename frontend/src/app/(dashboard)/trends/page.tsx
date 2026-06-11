"use client";

import { ComingSoon } from "@/components/shared/ComingSoon";
import { TrendingUp } from "lucide-react";

export default function TrendsPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Trends</h1>
        <p className="mt-0.5 text-sm text-[#A0A0A0]">Competitor momentum and market trends</p>
      </div>
      <ComingSoon
        icon={<TrendingUp className="h-6 w-6" />}
        title="Trends dashboard"
        description="Visualize competitor momentum scores, keyword trends, and market positioning over time. Charts and graphs coming soon."
      />
    </div>
  );
}
