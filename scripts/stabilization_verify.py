"""Stabilization verification: runs benchmark for OpenAI, Anthropic, Google, captures before/after."""

import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.models.schemas import CompetitorPages, PageData
from backend.services.analysis_service import AnalysisService

# Track all data
class BenchmarkTracker:
    def __init__(self, company_name):
        self.company_name = company_name
        self.artifacts_dir = f"artifacts/{company_name.lower()}"
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.pipeline_metrics = {
            "raw_chars": 0, "cleaned_chars": 0, "ranked_chars": 0,
            "signals_extracted": 0, "signals_preserved": 0, "signals_dropped": 0,
            "noise_removed_count": 0, "runtime_seconds": 0
        }

    def save_json(self, filename, data):
        with open(os.path.join(self.artifacts_dir, filename), "w") as f:
            json.dump(data, f, indent=2)

async def run_benchmark_for_company(company_name, snapshots):
    tracker = BenchmarkTracker(company_name)
    start_time = time.time()
    pages = []
    raw_chars = 0
    for snap in snapshots:
        pages.append(PageData(
            url=snap["source_url"],
            content=snap["content_text"],
            page_type=snap["page_type"],
            fetch_success=True
        ))
        raw_chars += len(snap.get("content_text") or "")
    tracker.pipeline_metrics["raw_chars"] = raw_chars

    analyzer = AnalysisService()
    competitor_pages = CompetitorPages(
        name=company_name,
        domain=f"{company_name.lower().replace(' ', '')}.com",
        pages=pages
    )
    analysis = await analyzer.analyze_competitor(competitor_pages)

    tracker.pipeline_metrics["runtime_seconds"] = round(time.time() - start_time, 2)
    tracker.save_json("pipeline_metrics.json", tracker.pipeline_metrics)

    if analysis:
        tracker.save_json("final_competitor_analysis.json", analysis.model_dump())
        report = {
            "company": company_name,
            "momentum_score": analysis.momentum_score,
            "messaging_tone": analysis.messaging_tone,
            "pricing_signals": analysis.pricing_signals,
            "icp": analysis.icp,
            "strategic_keywords": analysis.strategic_keywords,
            "growth_signals": analysis.growth_signals,
            "recent_launches": analysis.recent_launches,
            "risk_flags": analysis.risk_flags,
            "analyst_note": analysis.analyst_note,
            "validation_warning": analysis.validation.get("validation_warning", None) if analysis.validation else None,
        }
        tracker.save_json("benchmark_report.json", report)
        return analysis.model_dump(), tracker.pipeline_metrics
    return None, tracker.pipeline_metrics

def main():
    snapshots_path = os.path.join(os.path.dirname(__file__), "..", "tests", "mock_snapshots.json")
    with open(snapshots_path, "r") as f:
        snapshots_data = json.load(f)

    companies = ["Openai", "Anthropic", "Google"]

    # BEFORE snapshot (from last known artifacts)
    before = {
        "Openai": {
            "pricing": "No public evidence found",
            "momentum": 7,
            "validation_warning": True,
        },
        "Anthropic": {
            "pricing": "No public evidence found",
            "momentum": 7,
            "validation_warning": True,
        },
        "Google": {
            "pricing": "No public evidence found",
            "momentum": 6,
            "validation_warning": True,
        },
    }

    for company in companies:
        print(f"\n========================================")
        print(f"BENCHMARKING: {company}")
        print(f"========================================\n")
        snaps = snapshots_data.get(company, [])
        if not snaps:
            print(f"No snapshot data for {company}")
            continue
        new_analysis, metrics = asyncio.run(run_benchmark_for_company(company, snaps))
        if not new_analysis:
            print(f"Failed to generate analysis for {company}")
            continue
        print(f"✓ {company} complete — momentum: {new_analysis.get('momentum_score')}/10")
        print(f"  pricing: {new_analysis.get('pricing_signals', 'N/A')[:80]}")
        vw = new_analysis.get("validation", {}).get("validation_warning", "N/A")
        print(f"  validation_warning: {vw}")

    # AFTER snapshot (from newly generated artifacts)
    stabilization_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts", "stabilization")
    os.makedirs(stabilization_dir, exist_ok=True)

    after = {}
    for company in companies:
        artifact_path = os.path.join(
            os.path.dirname(__file__), "..", "artifacts",
            company.lower(), "final_competitor_analysis.json"
        )
        if os.path.exists(artifact_path):
            with open(artifact_path, "r") as f:
                data = json.load(f)
            after[company] = {
                "pricing": data.get("pricing_signals", "N/A"),
                "momentum": data.get("momentum_score"),
                "validation_warning": data.get("validation", {}).get("validation_warning", None),
            }

    verification = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "before": before,
        "after": after,
        "changes": {}
    }

    for company in companies:
        b = before.get(company, {})
        a = after.get(company, {})
        verification["changes"][company] = {}
        for key in ["pricing", "momentum", "validation_warning"]:
            bv = b.get(key)
            av = a.get(key)
            if bv != av:
                verification["changes"][company][key] = {"before": bv, "after": av}

    with open(os.path.join(stabilization_dir, "stabilization_verification.json"), "w") as f:
        json.dump(verification, f, indent=2)

    print(f"\n\n========================================")
    print(f"VERIFICATION COMPLETE")
    print(f"========================================")
    print(json.dumps(verification["changes"], indent=2))

if __name__ == "__main__":
    main()
