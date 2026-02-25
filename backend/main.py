import asyncio
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.services.scraper_service import ScraperService
from backend.services.analysis_service import AnalysisService
from backend.services.comparison_service import ComparisonService
from backend.models.schemas import AnalysisRequest, IntelligenceReport

app = FastAPI(
    title="Competitor Intelligence Monitor",
    description="Strategic intelligence extraction powered by Gemini. Not summaries — signals.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "competitor-intelligence-monitor"}


@app.post("/api/analyze", response_model=IntelligenceReport)
async def analyze(request: AnalysisRequest):
    """
    Run the full intelligence pipeline on 2–5 competitors.
    Accepts names or URLs. Returns structured IntelligenceReport.
    """
    if len(request.competitors) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 competitors required")
    if len(request.competitors) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 competitors allowed")

    start_time = time.time()
    scraper = ScraperService()
    analyzer = AnalysisService()
    comparator = ComparisonService()

    try:
        # Stage 1: Scrape
        scrape_tasks = [scraper.fetch_competitor(name) for name in request.competitors]
        all_pages = await asyncio.gather(*scrape_tasks, return_exceptions=True)

        valid_pages = [r for r in all_pages if not isinstance(r, Exception)]
        if not valid_pages:
            raise HTTPException(status_code=502, detail="All competitor scrapes failed")

        # Stage 2: Analyze
        analyses = []
        for pages in valid_pages:
            analysis = await analyzer.analyze_competitor(pages)
            analyses.append(analysis)

        # Stage 3: Compare
        report = await comparator.generate_report(analyses, start_time)
        return report

    finally:
        await scraper.close()


# Keep this so Streamlit can still import the pipeline function directly
async def run_intelligence_pipeline(
    competitors: list[str],
    include_blog: bool = True,
    include_careers: bool = True,
    progress_callback=None
) -> IntelligenceReport:
    start_time = time.time()
    scraper = ScraperService()
    analyzer = AnalysisService()
    comparator = ComparisonService()

    try:
        if progress_callback:
            progress_callback("scraping", 0, len(competitors))

        scrape_tasks = [scraper.fetch_competitor(name) for name in competitors]
        all_pages = await asyncio.gather(*scrape_tasks, return_exceptions=True)

        valid_pages = []
        for i, result in enumerate(all_pages):
            if isinstance(result, Exception):
                print(f"[pipeline] Scrape failed for {competitors[i]}: {result}")
            else:
                valid_pages.append(result)

        if not valid_pages:
            raise RuntimeError("All competitor scrapes failed.")

        if progress_callback:
            progress_callback("scraping", len(valid_pages), len(competitors))

        analyses = []
        for i, pages in enumerate(valid_pages):
            if progress_callback:
                progress_callback("analyzing", i, len(valid_pages))
            analysis = await analyzer.analyze_competitor(pages)
            analyses.append(analysis)
            print(f"[pipeline] ✓ {analysis.name} — momentum: {analysis.momentum_score}/10")

        if progress_callback:
            progress_callback("analyzing", len(analyses), len(valid_pages))
            progress_callback("comparing", 0, 1)

        report = await comparator.generate_report(analyses, start_time)

        if progress_callback:
            progress_callback("comparing", 1, 1)

        print(f"\n[pipeline] ✅ Done in {report.run_duration_seconds}s")
        return report

    finally:
        await scraper.close()