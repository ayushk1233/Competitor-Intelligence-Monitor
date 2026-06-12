"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { triggerAnalysis } from "@/services/analysis.service";
import { X, Play, Loader2, ExternalLink } from "lucide-react";

interface NewAnalysisModalProps {
  open: boolean;
  onClose: () => void;
}

export function NewAnalysisModal({ open, onClose }: NewAnalysisModalProps) {
  const [competitors, setCompetitors] = useState(["", "", ""]);
  const [includeCareers, setIncludeCareers] = useState(true);
  const [includeBlog, setIncludeBlog] = useState(true);
  const [includePricing, setIncludePricing] = useState(true);
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const handleRun = async () => {
    const valid = competitors
      .map((c) => c.trim())
      .filter((c) => c.length > 0);
    if (valid.length < 2) {
      toast.error("Enter at least 2 competitors");
      return;
    }

    setLoading(true);
    try {
      await triggerAnalysis({
        competitors: valid,
        options: {
          include_careers: includeCareers,
          include_blog: includeBlog,
          max_pages_per_competitor: includePricing ? 4 : 3,
        },
      });
      toast.success("Analysis queued");
      setCompetitors(["", "", ""]);
      onClose();
    } catch (err) {
      toast.error("Failed to start analysis. Check the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-md rounded-xl border border-[rgba(255,255,255,0.1)] bg-[#1E1E1E] shadow-2xl">
        <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.1)] px-6 py-4">
          <h2 className="text-base font-semibold text-white">New analysis</h2>
          <button
            onClick={onClose}
            className="flex h-7 w-7 items-center justify-center rounded-md text-[#A0A0A0] hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="px-6 py-5">
          <h3 className="text-sm font-semibold text-white">Add your competitors</h3>
          <p className="mt-0.5 text-xs text-[#A0A0A0]">
            Enter the companies you want to analyze
          </p>

          <div className="mt-5 space-y-3">
            {competitors.map((val, i) => (
              <div key={i} className="space-y-1">
                <label className="text-xs font-medium text-[#A0A0A0]">
                  Competitor {i + 1}
                </label>
                <Input
                  value={val}
                  onChange={(e) => {
                    const next = [...competitors];
                    next[i] = e.target.value;
                    setCompetitors(next);
                  }}
                  placeholder={["e.g. Anthropic", "e.g. Vercel", "e.g. Databricks"][i]}
                  className="border border-[rgba(255,255,255,0.1)] bg-[#222222] text-white placeholder:text-[#A0A0A0] focus:border-[#BC6C50] focus:ring-0"
                />
              </div>
            ))}
          </div>

          <div className="mt-5 space-y-2 rounded-lg border border-[rgba(255,255,255,0.1)] bg-[#222222] p-4">
            <p className="text-xs font-medium text-[#A0A0A0]">Include pages</p>
            {[
              { label: "Careers page", key: "careers", checked: includeCareers, set: setIncludeCareers },
              { label: "Blog posts", key: "blog", checked: includeBlog, set: setIncludeBlog },
              { label: "Pricing page", key: "pricing", checked: includePricing, set: setIncludePricing },
            ].map((item) => (
              <label
                key={item.key}
                className="flex cursor-pointer items-center gap-2.5 rounded-md px-1 py-1 hover:bg-[#2A2A2A]/50"
              >
                <div
                  className={`flex h-4 w-4 items-center justify-center rounded border ${
                    item.checked
                      ? "border-[#BC6C50] bg-[#BC6C50]"
                      : "border-[rgba(255,255,255,0.2)] bg-transparent"
                  }`}
                >
                  {item.checked && (
                    <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
                <span className="text-xs text-white">{item.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="border-t border-[rgba(255,255,255,0.1)] px-6 py-4">
          <Button
            onClick={handleRun}
            disabled={loading}
            className="w-full border border-[#BC6C50] bg-transparent text-[#BC6C50] hover:bg-[#BC6C50] hover:text-white transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="mr-1.5 h-4 w-4" />
                Run analysis
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
