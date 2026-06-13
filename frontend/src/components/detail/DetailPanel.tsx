"use client";

import { useDetailPanel, type DetailPanelData } from "./DetailPanelContext";
import { Badge } from "@/components/ui/badge";
import { X, TrendingUp, MessageSquare, Lightbulb, Target, Zap } from "lucide-react";

const severityConfig: Record<string, { label: string; dot: string }> = {
  high: { label: "High", dot: "bg-[#EF4444]" },
  medium: { label: "Medium", dot: "bg-[#D97706]" },
  low: { label: "Low", dot: "bg-[#3B82F6]" },
};

const sevBg: Record<string, string> = {
  CRITICAL: "bg-[#2D1A1A] text-[#EF4444]",
  HIGH: "bg-[#2D1A1A] text-[#EF4444]",
  MEDIUM: "bg-[#2D2214] text-[#D97706]",
  LOW: "bg-[#142D20] text-[#3B82F6]",
};

function CompetitorView({ data, onBack }: { data: DetailPanelData; onBack: () => void }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-[#262626] px-6 py-4">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-xs text-[#666666] hover:text-white"
        >
          <X className="h-3 w-3" /> Back
        </button>
        <div className="flex items-center gap-2">
          <button className="rounded-lg border border-[#262626] px-3 py-1.5 text-xs text-[#A3A3A3] hover:bg-[#161616]">
            Battlecard
          </button>
          <button className="rounded-lg border border-[#262626] px-3 py-1.5 text-xs text-[#A3A3A3] hover:bg-[#161616]">
            Watch
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5">
        <h2 className="text-2xl font-bold tracking-tight text-white">{data.companyName}</h2>
        <div className="mt-2 flex items-center gap-3 text-xs">
          {data.momentumScore !== undefined && (
            <span className="flex items-center gap-1 text-[#A3A3A3]">
              <TrendingUp className="h-3.5 w-3.5 text-[#BC6C50]" />
              {data.momentumScore} Momentum
            </span>
          )}
          {data.tone && (
            <span className="flex items-center gap-1 text-[#A3A3A3]">
              <MessageSquare className="h-3.5 w-3.5" />
              {data.tone}
            </span>
          )}
        </div>

        <div className="my-6 grid grid-cols-2 gap-4 border-y border-[#262626] py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[#666666]">Core Offering</p>
            <p className="mt-1 text-sm leading-relaxed text-[#D4D4D4]">
              {data.coreOffering || "Not available"}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[#666666]">Ideal Customer</p>
            <p className="mt-1 text-sm leading-relaxed text-[#D4D4D4]">
              {data.icp || "Not available"}
            </p>
          </div>
        </div>

        {data.analystNote && (
          <div className="my-4 rounded-xl border border-[#262626] bg-[#161616] p-4">
            <div className="flex items-center gap-2">
              <Lightbulb className="h-3.5 w-3.5 text-[#BC6C50]" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#BC6C50]">Analyst Note</span>
            </div>
            <p className="mt-2 text-sm italic leading-relaxed text-[#A3A3A3]">
              {data.analystNote}
            </p>
          </div>
        )}

        {data.signals && data.signals.length > 0 && (
          <div className="mb-5">
            <p className="mb-3 text-sm font-semibold text-[#A3A3A3]">Recent signals</p>
            <div className="space-y-3">
              {data.signals.map((s, i) => {
                const cfg = severityConfig[s.severity] ?? severityConfig.low;
                return (
                  <div key={i} className="flex items-start gap-3">
                    <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${cfg.dot}`} />
                    <p className="text-sm text-[#D4D4D4]">{s.text}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {data.keywords && data.keywords.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-semibold text-[#666666]">Strategic keywords</p>
            <div className="flex flex-wrap gap-2">
              {data.keywords.map((kw, i) => (
                <span
                  key={i}
                  className="rounded-full border border-[#262626] bg-[#161616] px-2.5 py-1 text-xs font-medium text-[#A3A3A3]"
                >
                  {kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function AlertView({ data, onBack }: { data: DetailPanelData; onBack: () => void }) {
  const severityLabel = data.severity || "MEDIUM";
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-[#262626] px-6 py-4">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-xs text-[#666666] hover:text-white"
        >
          <X className="h-3 w-3" /> Back
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5">
        <Badge className={`mb-3 px-2 py-0.5 text-[10px] font-semibold uppercase ${sevBg[severityLabel] || sevBg.MEDIUM}`}>
          {severityLabel}
        </Badge>
        <h2 className="text-2xl font-bold tracking-tight text-white">{data.headline || data.companyName}</h2>
        {data.summary && (
          <p className="mt-2 text-sm text-[#A3A3A3]">{data.summary}</p>
        )}
        <div className="my-6 space-y-3 border-y border-[#262626] py-4">
          {data.businessImpact && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-[#666666]">Business Impact</p>
              <p className="mt-1 text-sm text-[#D4D4D4]">{data.businessImpact}</p>
            </div>
          )}
          {data.recommendedAction && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-[#666666]">Recommended Action</p>
              <p className="mt-1 text-sm text-[#D4D4D4]">{data.recommendedAction}</p>
            </div>
          )}
          {data.confidence !== undefined && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-[#666666]">Confidence</p>
              <p className="mt-1 text-sm text-[#D4D4D4]">{data.confidence}%</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function DetailPanel() {
  const { selected, clear } = useDetailPanel();

  if (!selected) return null;

  return (
    <aside className="hidden h-full w-[400px] shrink-0 border-l border-[#262626] bg-[#0A0A0A] lg:block">
      {selected.type === "competitor" ? (
        <CompetitorView data={selected} onBack={clear} />
      ) : (
        <AlertView data={selected} onBack={clear} />
      )}
    </aside>
  );
}
