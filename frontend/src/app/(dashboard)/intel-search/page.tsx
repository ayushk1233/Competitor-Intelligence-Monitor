"use client";

import { ComingSoon } from "@/components/shared/ComingSoon";
import { Search } from "lucide-react";

export default function IntelSearchPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <p className="text-sm text-muted-foreground">Search across all competitor intelligence data</p>
      </div>
      <ComingSoon
        icon={<Search className="h-6 w-6" />}
        title="Intel Search"
        description="Search across competitor profiles, analysis reports, alerts, and historical data. Natural language queries supported."
      />
    </div>
  );
}
