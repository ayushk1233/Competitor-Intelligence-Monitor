import asyncio
import time
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.scraper_service import ScraperService
from backend.services.analysis_service import AnalysisService
from backend.services.comparison_service import ComparisonService
from backend.models.schemas import AnalysisRequest, IntelligenceReport
from backend.database.connection import get_db, create_tables
from backend.database.db_service import DatabaseService

app = FastAPI(
    title="Competitor Intelligence Monitor",
    description="Strategic intelligence extraction powered by Gemini.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup: create tables if they don't exist ────────────────────────────────
@app.on_event("startup")
async def startup():
    await create_tables()
    print("[startup] Database tables ready")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "competitor-intelligence-monitor", "version": "2.0.0"}


# ── Main analysis endpoint ────────────────────────────────────────────────────
@app.post("/api/analyze", response_model=IntelligenceReport)
async def analyze(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    if len(request.competitors) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 competitors required")
    if len(request.competitors) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 competitors allowed")

    db_service = DatabaseService(db)

    # Create run record in database
    run_id = await db_service.create_run(request.competitors)

    start_time = time.time()
    scraper = ScraperService()
    analyzer = AnalysisService()
    comparator = ComparisonService()

    try:
        await db_service.update_run_status(run_id, "scraping")

        scrape_tasks = [scraper.fetch_competitor(name) for name in request.competitors]
        all_pages = await asyncio.gather(*scrape_tasks, return_exceptions=True)

        valid_pages = [r for r in all_pages if not isinstance(r, Exception)]
        if not valid_pages:
            await db_service.update_run_status(run_id, "failed")
            raise HTTPException(status_code=502, detail="All competitor scrapes failed")

        # Save raw page snapshots
        for pages in valid_pages:
            await db_service.save_page_snapshots(run_id, pages)

        await db_service.update_run_status(run_id, "analyzing")

        analyses = []
        for pages in valid_pages:
            analysis = await analyzer.analyze_competitor(pages)
            analyses.append(analysis)

        await db_service.update_run_status(run_id, "comparing")

        report = await comparator.generate_report(analyses, start_time)

        # Save full report to database
        await db_service.save_full_report(run_id, report)

        return report

    except HTTPException:
        raise
    except Exception as e:
        await db_service.update_run_status(run_id, "failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# ── History endpoints ─────────────────────────────────────────────────────────
@app.get("/api/runs")
async def get_recent_runs(db: AsyncSession = Depends(get_db)):
    """Get the 10 most recent analysis runs."""
    db_service = DatabaseService(db)
    runs = await db_service.get_recent_runs(limit=10)
    return [
        {
            "run_id": r.id,
            "status": r.status,
            "competitors": r.competitor_names,
            "pages_fetched": r.total_pages_fetched,
            "duration_seconds": r.run_duration_seconds,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]


@app.get("/api/history/{competitor_name}")
async def get_competitor_history(
    competitor_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get momentum history for a specific competitor."""
    db_service = DatabaseService(db)
    history = await db_service.get_momentum_history(competitor_name)
    return {"competitor": competitor_name, "history": history}


# ── Streamlit pipeline function (unchanged) ───────────────────────────────────
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