"use client";

import { ComingSoon } from "@/components/shared/ComingSoon";
import { Swords } from "lucide-react";

export default function BattlecardsPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <p className="text-sm text-[#A0A0A0]">Competitor battlecards for sales and positioning</p>
      </div>
      <ComingSoon
        icon={<Swords className="h-6 w-6" />}
        title="Battlecards"
        description="Generate one-page competitor battlecards with positioning, strengths, weaknesses, and objection handling. Export-ready for your sales team."
      />
    </div>
  );
}
