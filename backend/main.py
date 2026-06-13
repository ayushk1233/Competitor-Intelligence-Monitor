# ✅ FIX 1: single clean import block — no duplicates
import glob
import logging
import os
import time

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from backend.api.auth import router as auth_router
from backend.api.dashboard import router as dashboard_router
from backend.api.notifications import (
    router as notification_router,
)
from backend.api.watchlists import router as watchlist_router
from backend.auth.dependencies import get_current_user
from backend.database.connection import create_tables, get_db
from backend.database.db_service import DatabaseService
from backend.database.models import (
    ComparisonRecord,
    CompetitorAnalysisRecord,
    User,
)
from backend.drift.diff_service import compare_analysis
from backend.metrics import active_pipeline_runs
from backend.models.schemas import (
    AnalysisRequest,
    ComparisonResult,
    CompetitorAnalysis,
    IntelligenceReport,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Competitor Intelligence Monitor",
    description="Strategic intelligence extraction powered by OpenRouter LLM.",
    version="2.3.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception: %s",
        str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(watchlist_router)
app.include_router(auth_router)
app.include_router(notification_router)
app.include_router(dashboard_router)
# ── Prometheus instrumentation ────────────────────────────────────────────────
# Auto-instruments all HTTP endpoints with request count and latency metrics
# Exposes them at GET /metrics — this is what Prometheus scrapes
Instrumentator().instrument(app)

@app.get("/metrics")
def metrics():
    from backend.metrics import registry
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s - %(name)s - "
            "%(levelname)s - %(message)s"
        ),
    )
    PROM_DIR = "/tmp/prometheus"

    # ✅ Clean multiprocess metric files (NOT the directory)
    if os.path.exists(PROM_DIR):
        for f in glob.glob(f"{PROM_DIR}/*"):
            try:
                os.remove(f)
            except IsADirectoryError:
                pass
    else:
        os.makedirs(PROM_DIR, exist_ok=True)

    # Existing startup logic
    await create_tables()


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
    current_user: User = Depends(get_current_user),
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
    run_id = await db_service.create_run(request.competitors, user_id=str(current_user.id))
    await db.commit()

    
    # Track active runs
    active_pipeline_runs.inc()
    run_analysis_task.delay(run_id, request.competitors, request.competitor_urls)

    logger.info(
        "Enqueued run %s for %s",
        run_id,
        request.competitors,
    )

    # Return run_id to client — they will poll for status
    return {
        "run_id": run_id,
        "status": "queued",
        "competitors": request.competitors,
        "message": "Analysis started. Poll /api/status/{run_id} for progress."
    }


# ── GET /api/status/{run_id} — poll this for progress ────────────────────────
@app.get("/api/status/{run_id}")
async def get_status(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns current status of an analysis run.
    Status values: queued | scraping | analyzing | comparing | completed | failed
    """
    db_service = DatabaseService(db)
    run = await db_service.get_run_for_user(run_id, str(current_user.id))

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
async def get_report(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full intelligence report for a completed run.
    Only works when status = completed.
    """
    db_service = DatabaseService(db)
    run = await db_service.get_run_for_user(run_id, str(current_user.id))

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
    competitors = []
    for r in analysis_records:
        ca = CompetitorAnalysis(**r.full_analysis)
        if ca.domain and not ca.logo_url:
            ca.logo_url = f"https://icons.duckduckgo.com/ip3/{ca.domain}.ico"
        competitors.append(ca)
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
async def get_recent_runs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the 10 most recent analysis runs for the authenticated user."""
    db_service = DatabaseService(db)
    runs = await db_service.get_recent_runs(limit=10, user_id=str(current_user.id))
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


@app.delete("/api/runs/{run_id}")
async def delete_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an ad-hoc analysis run and its cascade."""
    db_service = DatabaseService(db)
    deleted = await db_service.delete_run(run_id, user_id=str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"deleted": True, "run_id": run_id}


@app.get("/api/runs/{run_id}")
async def get_run_details(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_service = DatabaseService(db)
    run = await db_service.get_monitoring_run_for_user(run_id, str(current_user.id))

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Monitoring run not found",
        )

    return run


# ── GET /api/history/{competitor_name} ───────────────────────────────────────
@app.get("/api/history/{competitor_name}")
async def get_competitor_history(
    competitor_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get momentum score history for a specific competitor."""
    db_service = DatabaseService(db)
    user_competitor_names = await db_service.get_user_competitor_names(str(current_user.id))
    if competitor_name not in user_competitor_names:
        raise HTTPException(status_code=404, detail="Competitor not found")
    history = await db_service.get_momentum_history(competitor_name)
    return {"competitor": competitor_name, "history": history}


@app.get("/api/alerts")
async def get_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_service = DatabaseService(db)

    alerts = await db_service.get_alerts_for_user(current_user.id)

    return [
        {
            "id": a.id,
            "company_name": a.company_name,
            "severity": a.severity,
            "headline": a.headline,
            "summary": a.summary,
            "evidence": a.evidence,
            "confidence": a.confidence,
            "business_impact": a.business_impact,
            "recommended_action": a.recommended_action,
            "status": a.status,
            "created_at": (
                a.created_at.isoformat()
                if a.created_at else None
            ),
        }
        for a in alerts
    ]


@app.get("/api/alerts/latest")
async def get_latest_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_service = DatabaseService(db)

    alerts = await db_service.get_alerts_for_user(current_user.id, limit=10)

    return [
        {
            "id": a.id,
            "company_name": a.company_name,
            "severity": a.severity,
            "headline": a.headline,
            "summary": a.summary,
            "evidence": a.evidence,
            "confidence": a.confidence,
            "business_impact": a.business_impact,
            "recommended_action": a.recommended_action,
            "status": a.status,
            "created_at": (
                a.created_at.isoformat()
                if a.created_at else None
            ),
        }
        for a in alerts
    ]


@app.get("/api/alerts/{company_name}")
async def get_company_alerts(
    company_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    user_watchlist_ids = await db_service.get_user_watchlist_ids(str(current_user.id))
    if not user_watchlist_ids:
        return []
    alerts = await db_service.get_alerts_for_company(company_name)
    alerts = [a for a in alerts if a.watchlist_id in user_watchlist_ids]
    return [
        {
            "id": a.id,
            "company_name": a.company_name,
            "severity": a.severity,
            "headline": a.headline,
            "summary": a.summary,
            "evidence": a.evidence,
            "confidence": a.confidence,
            "business_impact": a.business_impact,
            "recommended_action": a.recommended_action,
            "status": a.status,
            "created_at": (
                a.created_at.isoformat()
                if a.created_at else None
            ),
        }
        for a in alerts
    ]


@app.get("/api/alerts/counts")
async def get_alert_counts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    return await db_service.get_alert_counts_by_severity_for_user(str(current_user.id))


@app.get("/api/alerts/detail/{alert_id}")
async def get_alert_detail(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    alert = await db_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    user_watchlist_ids = await db_service.get_user_watchlist_ids(str(current_user.id))
    if alert.watchlist_id not in user_watchlist_ids:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {
        "id": alert.id,
        "company_name": alert.company_name,
        "severity": alert.severity,
        "headline": alert.headline,
        "summary": alert.summary,
        "evidence": alert.evidence,
        "confidence": alert.confidence,
        "business_impact": alert.business_impact,
        "recommended_action": alert.recommended_action,
        "status": alert.status,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
    }


@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    alert = await db_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    user_watchlist_ids = await db_service.get_user_watchlist_ids(str(current_user.id))
    if alert.watchlist_id not in user_watchlist_ids:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert = await db_service.update_alert_status(alert_id, "acknowledged")
    return {"status": "acknowledged"}


@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    alert = await db_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    user_watchlist_ids = await db_service.get_user_watchlist_ids(str(current_user.id))
    if alert.watchlist_id not in user_watchlist_ids:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert = await db_service.update_alert_status(alert_id, "resolved")
    return {"status": "resolved"}


@app.post("/api/suppress/{company_name}/{severity}")
async def suppress_alert(
    company_name: str,
    severity: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from backend.drift.suppression_service import suppress_alert as do_suppress
    db_service = DatabaseService(db)
    user_watchlist_ids = await db_service.get_user_watchlist_ids(str(current_user.id))
    if not user_watchlist_ids:
        raise HTTPException(status_code=404, detail="No watchlists found")
    await do_suppress(db_service, company_name, severity, hours=24)
    return {"status": "suppressed", "company_name": company_name, "severity": severity}


@app.get("/api/notification-events")
async def get_notification_events(
    channel_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    channel = await db_service.get_notification_channel_for_user(channel_id, str(current_user.id))
    if not channel:
        raise HTTPException(status_code=404, detail="Notification channel not found")
    events = await db_service.get_notification_events(channel_id)
    return [
        {
            "id": e.id,
            "company_name": e.company_name,
            "severity": e.severity,
            "delivery_status": e.delivery_status,
            "error_message": e.error_message,
            "delivered_at": e.delivered_at.isoformat() if e.delivered_at else None,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]


@app.get("/api/competitors/{competitor_name}/latest")
async def get_competitor_latest(
    competitor_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    user_competitor_names = await db_service.get_user_competitor_names(str(current_user.id))
    if competitor_name not in user_competitor_names:
        raise HTTPException(status_code=404, detail="Competitor not found")
    record = await db_service.get_latest_analysis(competitor_name)
    if not record:
        raise HTTPException(
            status_code=404,
            detail="Competitor not found"
        )
    return record.full_analysis


@app.get("/api/competitors/{competitor_name}/history")
async def get_competitor_analysis_history(
    competitor_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    user_competitor_names = await db_service.get_user_competitor_names(str(current_user.id))
    if competitor_name not in user_competitor_names:
        raise HTTPException(status_code=404, detail="Competitor not found")
    history = await db_service.get_competitor_history(competitor_name, limit=50)
    return [
        {
            "created_at": (
                h.created_at.isoformat()
                if h.created_at else None
            ),
            "momentum_score": h.momentum_score,
            "messaging_tone": h.messaging_tone,
        }
        for h in history
    ]


@app.get("/api/competitors/{competitor_name}/drift")
async def get_competitor_drift(
    competitor_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_service = DatabaseService(db)
    user_competitor_names = await db_service.get_user_competitor_names(str(current_user.id))
    if competitor_name not in user_competitor_names:
        raise HTTPException(status_code=404, detail="Competitor not found")
    history = await db_service.get_latest_two_analyses(competitor_name)
    if not history:
        raise HTTPException(
            status_code=404,
            detail="Not enough history for drift detection"
        )
    newest = CompetitorAnalysis(**history[0].full_analysis)
    previous = CompetitorAnalysis(**history[1].full_analysis)
    drift = compare_analysis(previous, newest)
    return drift.model_dump()


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

    from backend.services.analysis_service import AnalysisService
    from backend.services.comparison_service import ComparisonService
    from backend.services.scraper_service import ScraperService

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