"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ComingSoon } from "@/components/shared/ComingSoon";
import { Swords } from "lucide-react";

function BattlecardsContent() {
  const searchParams = useSearchParams();
  const company = searchParams.get("company");

  return (
    <ComingSoon
      icon={<Swords className="h-6 w-6" />}
      title={company ? `Battlecard — ${company}` : "Battlecards"}
      description={
        company
          ? `The battlecard for ${company} is coming soon. Generate one-page competitor battlecards with positioning, strengths, weaknesses, and objection handling. Export-ready for your sales team.`
          : "Generate one-page competitor battlecards with positioning, strengths, weaknesses, and objection handling. Export-ready for your sales team."
      }
    />
  );
}

export default function BattlecardsPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <p className="text-sm text-muted-foreground">Competitor battlecards for sales and positioning</p>
      </div>
      <Suspense fallback={null}>
        <BattlecardsContent />
      </Suspense>
    </div>
  );
}
