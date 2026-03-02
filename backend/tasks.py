import asyncio
import time
from backend.celery_app import celery_app
from backend.services.scraper_service import ScraperService
from backend.services.analysis_service import AnalysisService
from backend.services.comparison_service import ComparisonService
from backend.database.connection import AsyncSessionLocal
from backend.database.db_service import DatabaseService


@celery_app.task(bind=True, name="run_analysis")
def run_analysis_task(self, run_id: str, competitors: list[str]):
    """
    Background task that runs the full intelligence pipeline.
    Called by FastAPI instantly — executes in background worker.
    bind=True gives us access to self for status updates.
    """
    print(f"[task] Starting run {run_id} for {competitors}")

    # Celery tasks are synchronous — we run async code inside
    # using asyncio.run()
    try:
        asyncio.run(_run_pipeline(run_id, competitors))
        print(f"[task] Completed run {run_id}")
        return {"status": "completed", "run_id": run_id}

    except Exception as e:
        print(f"[task] Failed run {run_id}: {e}")
        # Mark run as failed in database
        asyncio.run(_mark_failed(run_id, str(e)))
        raise


async def _run_pipeline(run_id: str, competitors: list[str]):
    """
    The actual async pipeline — same logic as before
    but now runs inside a Celery worker process.
    """
    start_time = time.time()

    async with AsyncSessionLocal() as session:
        db = DatabaseService(session)

        # ── Stage 1: Scraping ─────────────────────────────────────────────
        await db.update_run_status(run_id, "scraping")
        await session.commit()

        scraper = ScraperService()
        analyzer = AnalysisService()
        comparator = ComparisonService()

        try:
            print(f"[task] Stage 1: Scraping {len(competitors)} competitors...")
            scrape_tasks = [
                scraper.fetch_competitor(name) for name in competitors
            ]
            all_pages = await asyncio.gather(
                *scrape_tasks, return_exceptions=True
            )

            valid_pages = []
            for i, result in enumerate(all_pages):
                if isinstance(result, Exception):
                    print(f"[task] Scrape failed for {competitors[i]}: {result}")
                else:
                    valid_pages.append(result)

            if not valid_pages:
                raise RuntimeError("All competitor scrapes failed")

            # Save raw page snapshots
            for pages in valid_pages:
                await db.save_page_snapshots(run_id, pages)
            await session.commit()

            # ── Stage 2: Analyzing ────────────────────────────────────────
            await db.update_run_status(run_id, "analyzing")
            await session.commit()

            print(f"[task] Stage 2: Analyzing {len(valid_pages)} competitors...")
            analyses = []
            for pages in valid_pages:
                analysis = await analyzer.analyze_competitor(pages)
                analyses.append(analysis)
                print(
                    f"[task] ✓ {analysis.name} "
                    f"— momentum: {analysis.momentum_score}/10"
                )

            # ── Stage 3: Comparing ────────────────────────────────────────
            await db.update_run_status(run_id, "comparing")
            await session.commit()

            print(f"[task] Stage 3: Running comparison synthesis...")
            report = await comparator.generate_report(analyses, start_time)

            # Save everything to database
            await db.save_full_report(run_id, report)
            await session.commit()

            print(f"[task] ✅ Run {run_id} complete in {report.run_duration_seconds}s")

        finally:
            await scraper.close()


async def _mark_failed(run_id: str, error: str):
    """Mark a run as failed in the database."""
    async with AsyncSessionLocal() as session:
        db = DatabaseService(session)
        await db.update_run_status(run_id, "failed")

        from sqlalchemy import select
        from backend.database.models import Run
        result = await session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one_or_none()
        if run:
            run.error_message = error
        await session.commit()