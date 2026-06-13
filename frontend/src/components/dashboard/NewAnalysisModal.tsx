"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { triggerAnalysis } from "@/services/analysis.service";
import { X, Play, Loader2, ExternalLink, Link } from "lucide-react";

interface NewAnalysisModalProps {
  open: boolean;
  onClose: () => void;
}

export function NewAnalysisModal({ open, onClose }: NewAnalysisModalProps) {
  const [competitors, setCompetitors] = useState(["", "", ""]);
  const [competitorUrls, setCompetitorUrls] = useState(["", "", ""]);
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

    const urls: Record<string, string> = {};
    for (let i = 0; i < competitors.length; i++) {
      const name = competitors[i].trim();
      const url = competitorUrls[i]?.trim();
      if (name && url) {
        urls[name] = url.startsWith("http") ? url : `https://${url}`;
      }
    }

    setLoading(true);
    try {
      await triggerAnalysis({
        competitors: valid,
        competitor_urls: Object.keys(urls).length > 0 ? urls : undefined,
        options: {
          include_careers: includeCareers,
          include_blog: includeBlog,
          max_pages_per_competitor: includePricing ? 4 : 3,
        },
      });
      toast.success("Analysis queued");
      setCompetitors(["", "", ""]);
      setCompetitorUrls(["", "", ""]);
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
      <div className="w-full max-w-md rounded-xl border border-[var(--dialog-border)] bg-[var(--dialog-bg)] shadow-2xl">
        <div className="flex items-center justify-between border-b border-[var(--dialog-border)] px-6 py-4">
          <h2 className="text-base font-semibold text-[var(--dialog-text)]">New analysis</h2>
          <button
            onClick={onClose}
            className="flex h-7 w-7 items-center justify-center rounded-md text-[var(--dialog-muted)] hover:text-[var(--dialog-text)]"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="px-6 py-5">
          <h3 className="text-sm font-semibold text-[var(--dialog-text)]">Add your competitors</h3>
          <p className="mt-0.5 text-xs text-[var(--dialog-muted)]">
            Enter the companies you want to analyze
          </p>

          <div className="mt-5 space-y-4">
            {competitors.map((val, i) => (
              <div key={i} className="rounded-lg border border-[var(--dialog-surface-border)] bg-[var(--dialog-surface)] p-3">
                <label className="text-xs font-medium text-[var(--dialog-muted)]">
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
                  className="mt-1.5 border border-[var(--dialog-border)] bg-[var(--input-bg)] text-[var(--dialog-text)] placeholder:text-[var(--dialog-muted)] focus:border-[var(--accent-color)] focus:ring-0"
                />
                <div className="mt-2 flex items-center gap-1.5">
                  <Link className="h-3 w-3 shrink-0 text-[var(--dialog-placeholder)]" />
                  <input
                    value={competitorUrls[i] || ""}
                    onChange={(e) => {
                      const next = [...competitorUrls];
                      next[i] = e.target.value;
                      setCompetitorUrls(next);
                    }}
                    placeholder="Website URL (optional)"
                    className="w-full border-0 bg-transparent py-1 text-xs text-[var(--dialog-placeholder)] placeholder:text-[var(--dialog-placeholder)] focus:outline-none focus:text-[var(--dialog-muted)]"
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-5 space-y-2 rounded-lg border border-[var(--dialog-border)] bg-[var(--dialog-surface)] p-4">
            <p className="text-xs font-medium text-[var(--dialog-muted)]">Include pages</p>
            {[
              { label: "Careers page", key: "careers", checked: includeCareers, set: setIncludeCareers },
              { label: "Blog posts", key: "blog", checked: includeBlog, set: setIncludeBlog },
              { label: "Pricing page", key: "pricing", checked: includePricing, set: setIncludePricing },
            ].map((item) => (
              <label
                key={item.key}
                className="flex cursor-pointer items-center gap-2.5 rounded-md px-1 py-1 hover:bg-[var(--dialog-surface)]/50"
              >
                <div
                  className={`flex h-4 w-4 items-center justify-center rounded border ${
                    item.checked
                      ? "border-[var(--accent-color)] bg-[var(--accent-color)]"
                      : "border-[var(--dialog-border)] bg-transparent"
                  }`}
                >
                  {item.checked && (
                    <svg className="h-3 w-3 text-[var(--dialog-text)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
                <span className="text-xs text-[var(--dialog-text)]">{item.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="border-t border-[var(--dialog-border)] px-6 py-4">
          <Button
            onClick={handleRun}
            disabled={loading}
             className="w-full border border-[var(--accent-color)] bg-transparent text-[var(--accent-color)] hover:bg-[var(--accent-color)] hover:text-[var(--dialog-text)] transition-colors"
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
