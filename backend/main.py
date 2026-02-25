import asyncio
import time
from backend.services.scraper_service import ScraperService
from backend.services.analysis_service import AnalysisService
from backend.services.comparison_service import ComparisonService
from backend.models.schemas import IntelligenceReport


async def run_intelligence_pipeline(
    competitors: list[str],
    include_blog: bool = True,
    include_careers: bool = True,
    progress_callback=None
) -> IntelligenceReport:
    """
    Master pipeline. Runs all three stages in order:
    1. Scrape all competitors concurrently
    2. Analyze each competitor with Gemini
    3. Run cross-competitor comparison with Gemini
    Returns a complete IntelligenceReport.
    """
    start_time = time.time()

    scraper = ScraperService()
    analyzer = AnalysisService()
    comparator = ComparisonService()

    try:
        # ── Stage 1: Scrape all competitors concurrently ──────────────────
        if progress_callback:
            progress_callback("scraping", 0, len(competitors))

        print(f"\n[pipeline] Stage 1: Scraping {len(competitors)} competitors...")

        scrape_tasks = [
            scraper.fetch_competitor(name)
            for name in competitors
        ]
        all_pages = await asyncio.gather(*scrape_tasks, return_exceptions=True)

        # Filter out any total scrape failures
        valid_pages = []
        for i, result in enumerate(all_pages):
            if isinstance(result, Exception):
                print(f"[pipeline] Scrape failed for {competitors[i]}: {result}")
            else:
                valid_pages.append(result)

        if not valid_pages:
            raise RuntimeError("All competitor scrapes failed. Check your internet connection.")

        if progress_callback:
            progress_callback("scraping", len(valid_pages), len(competitors))

        # ── Stage 2: Analyze each competitor with Gemini ──────────────────
        print(f"\n[pipeline] Stage 2: Analyzing {len(valid_pages)} competitors...")

        analyses = []
        for i, pages in enumerate(valid_pages):
            if progress_callback:
                progress_callback("analyzing", i, len(valid_pages))

            analysis = await analyzer.analyze_competitor(pages)
            analyses.append(analysis)
            print(f"[pipeline] ✓ {analysis.name} — momentum: {analysis.momentum_score}/10")

        if progress_callback:
            progress_callback("analyzing", len(analyses), len(valid_pages))

        # ── Stage 3: Cross-competitor comparison ──────────────────────────
        print(f"\n[pipeline] Stage 3: Running comparison synthesis...")

        if progress_callback:
            progress_callback("comparing", 0, 1)

        report = await comparator.generate_report(analyses, start_time)

        if progress_callback:
            progress_callback("comparing", 1, 1)

        print(f"\n[pipeline] ✅ Done in {report.run_duration_seconds}s")
        return report

    finally:
        await scraper.close()