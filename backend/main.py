# ✅ FIX 1: single clean import block — no duplicates
import time
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.responses import Response

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from backend.models.schemas import AnalysisRequest, IntelligenceReport
from backend.database.connection import get_db, create_tables
from backend.database.db_service import DatabaseService
from backend.database.models import Run, CompetitorAnalysisRecord, ComparisonRecord
from backend.models.schemas import CompetitorAnalysis, ComparisonResult
from backend.metrics import active_pipeline_runs

app = FastAPI(
    title="Competitor Intelligence Monitor",
    description="Strategic intelligence extraction powered by Gemini.",
    version="2.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── Prometheus instrumentation ────────────────────────────────────────────────
# Auto-instruments all HTTP endpoints with request count and latency metrics
# Exposes them at GET /metrics — this is what Prometheus scrapes
Instrumentator().instrument(app).expose(app)



# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await create_tables()
    print("[startup] Database tables ready")


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "competitor-intelligence-monitor",
        "version": "2.3.0"
    }


@app.get("/metrics-raw")
async def metrics_raw():
    """
    Raw Prometheus metrics endpoint.
    Prometheus scrapes this every 15 seconds.
    The Instrumentator already adds /metrics — this is a backup
    for custom metrics that need raw exposition format.
    """
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )



# ── POST /api/analyze — returns instantly with run_id ─────────────────────────
@app.post("/api/analyze")
async def analyze(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Enqueues the intelligence pipeline as a background job.
    Returns run_id immediately — poll /api/status/{run_id} for progress.
    """
    if len(request.competitors) < 2:
        raise HTTPException(
            status_code=400, detail="Minimum 2 competitors required"
        )
    if len(request.competitors) > 5:
        raise HTTPException(
            status_code=400, detail="Maximum 5 competitors allowed"
        )

    # Import here to avoid circular imports
    from backend.tasks import run_analysis_task

    db_service = DatabaseService(db)

    # Create run record in database with status = queued
    run_id = await db_service.create_run(request.competitors)
    await db.commit()

    
    # Track active runs
    active_pipeline_runs.inc()
    run_analysis_task.delay(run_id, request.competitors)

    print(f"[api] Enqueued run {run_id} for {request.competitors}")

    # Return run_id to client — they will poll for status
    return {
        "run_id": run_id,
        "status": "queued",
        "competitors": request.competitors,
        "message": "Analysis started. Poll /api/status/{run_id} for progress."
    }


# ── GET /api/status/{run_id} — poll this for progress ────────────────────────
@app.get("/api/status/{run_id}")
async def get_status(run_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns current status of an analysis run.
    Status values: queued | scraping | analyzing | comparing | completed | failed
    """
    db_service = DatabaseService(db)
    run = await db_service.get_run(run_id)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Map status to a progress percentage for the frontend
    progress_map = {
        "queued":    5,
        "scraping":  25,
        "analyzing": 60,
        "comparing": 85,
        "completed": 100,
        "failed":    0,
    }

    return {
        "run_id": run.id,
        "status": run.status,
        "progress_percent": progress_map.get(run.status, 0),
        "competitors": run.competitor_names,
        "pages_fetched": run.total_pages_fetched,
        "duration_seconds": run.run_duration_seconds,
        "error": run.error_message,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }


# ── GET /api/report/{run_id} — fetch completed report ────────────────────────
@app.get("/api/report/{run_id}")
async def get_report(run_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns the full intelligence report for a completed run.
    Only works when status = completed.
    """
    db_service = DatabaseService(db)
    run = await db_service.get_run(run_id)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Run is not completed yet. Current status: {run.status}"
        )

    # Fetch analyses from database
    analyses_result = await db.execute(
        select(CompetitorAnalysisRecord)
        .where(CompetitorAnalysisRecord.run_id == run_id)
    )
    analysis_records = analyses_result.scalars().all()

    # Fetch comparison from database
    comparison_result = await db.execute(
        select(ComparisonRecord).where(ComparisonRecord.run_id == run_id)
    )
    comparison_record = comparison_result.scalar_one_or_none()

    if not comparison_record:
        raise HTTPException(
            status_code=500, detail="Comparison data missing for this run"
        )

    # Reconstruct IntelligenceReport from stored JSON
    from datetime import datetime
    competitors = [
        CompetitorAnalysis(**r.full_analysis) for r in analysis_records
    ]
    comparison = ComparisonResult(**comparison_record.full_comparison)

    return IntelligenceReport(
        competitors=competitors,
        comparison=comparison,
        generated_at=run.completed_at or datetime.utcnow(),
        total_pages_fetched=run.total_pages_fetched or 0,
        run_duration_seconds=run.run_duration_seconds or 0.0
    )


# ── GET /api/runs — recent run history ───────────────────────────────────────
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


# ── GET /api/history/{competitor_name} ───────────────────────────────────────
@app.get("/api/history/{competitor_name}")
async def get_competitor_history(
    competitor_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get momentum score history for a specific competitor."""
    db_service = DatabaseService(db)
    history = await db_service.get_momentum_history(competitor_name)
    return {"competitor": competitor_name, "history": history}


# ── Streamlit still uses this directly ───────────────────────────────────────
async def run_intelligence_pipeline(
    competitors: list[str],
    include_blog: bool = True,
    include_careers: bool = True,
    progress_callback=None
) -> IntelligenceReport:
    """
    Direct pipeline call for Streamlit frontend.
    Streamlit bypasses the queue and calls this directly
    since it manages its own progress display.
    """
    import asyncio
    from backend.services.scraper_service import ScraperService
    from backend.services.analysis_service import AnalysisService
    from backend.services.comparison_service import ComparisonService

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
            print(
                f"[pipeline] ✓ {analysis.name} "
                f"— momentum: {analysis.momentum_score}/10"
            )

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