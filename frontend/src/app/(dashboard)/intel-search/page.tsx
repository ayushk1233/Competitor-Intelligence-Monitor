"use client";

import { ComingSoon } from "@/components/shared/ComingSoon";
import { Search } from "lucide-react";

export default function IntelSearchPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Intel Search</h1>
        <p className="mt-0.5 text-sm text-[#A0A0A0]">Search across all competitor intelligence data</p>
      </div>
      <ComingSoon
        icon={<Search className="h-6 w-6" />}
        title="Intel Search"
        description="Search across competitor profiles, analysis reports, alerts, and historical data. Natural language queries supported."
      />
    </div>
  );
}
