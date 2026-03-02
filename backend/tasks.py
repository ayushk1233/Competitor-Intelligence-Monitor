import asyncio
import time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.celery_app import celery_app
from backend.services.scraper_service import ScraperService
from backend.services.analysis_service import AnalysisService
from backend.services.comparison_service import ComparisonService
from backend.database.db_service import DatabaseService
from backend.config import get_settings

settings = get_settings()


def _make_session_factory():
    """
    Create a brand new engine + session factory for this task.
    Never reuse the global engine across event loops — asyncpg
    connections are bound to the loop they were created in.
    A new engine = new connection pool = no loop conflict.
    """
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=2,
        max_overflow=2,
    )
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    ), engine


@celery_app.task(bind=True, name="run_analysis")
def run_analysis_task(self, run_id: str, competitors: list[str]):
    """
    Background task — creates its own event loop and its own
    database engine to avoid asyncpg cross-loop conflicts.
    """
    print(f"[task] Starting run {run_id} for {competitors}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_run_pipeline(run_id, competitors))
        print(f"[task] Completed run {run_id}")
        return {"status": "completed", "run_id": run_id}

    except Exception as e:
        print(f"[task] Failed run {run_id}: {e}")
        try:
            loop.run_until_complete(_mark_failed(run_id, str(e)))
        except Exception as e2:
            print(f"[task] Could not mark run as failed: {e2}")
        raise

    finally:
        try:
            loop.close()
        except Exception:
            pass


async def _run_pipeline(run_id: str, competitors: list[str]):
    start_time = time.time()

    # Fresh engine and session factory — no shared state from previous tasks
    SessionLocal, engine = _make_session_factory()

    try:
        async with SessionLocal() as session:
            db = DatabaseService(session)
            scraper = ScraperService()
            analyzer = AnalysisService()
            comparator = ComparisonService()

            try:
                # ── Stage 1: Scraping ─────────────────────────────────────
                print(f"[task] Stage 1: Scraping {len(competitors)} competitors...")
                await db.update_run_status(run_id, "scraping")
                await session.commit()

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

                for pages in valid_pages:
                    await db.save_page_snapshots(run_id, pages)
                await session.commit()

                # ── Stage 2: Analyzing ────────────────────────────────────
                print(f"[task] Stage 2: Analyzing {len(valid_pages)} competitors...")
                await db.update_run_status(run_id, "analyzing")
                await session.commit()

                analyses = []
                for pages in valid_pages:
                    analysis = await analyzer.analyze_competitor(pages)
                    analyses.append(analysis)
                    print(
                        f"[task] ✓ {analysis.name} "
                        f"— momentum: {analysis.momentum_score}/10"
                    )

                # ── Stage 3: Comparing ────────────────────────────────────
                print(f"[task] Stage 3: Running comparison synthesis...")
                await db.update_run_status(run_id, "comparing")
                await session.commit()

                report = await comparator.generate_report(analyses, start_time)
                await db.save_full_report(run_id, report)
                await session.commit()

                print(
                    f"[task] ✅ Run {run_id} complete "
                    f"in {report.run_duration_seconds}s"
                )

            finally:
                await scraper.close()

    finally:
        # Dispose engine to cleanly close all connections
        await engine.dispose()


async def _mark_failed(run_id: str, error: str):
    SessionLocal, engine = _make_session_factory()
    try:
        async with SessionLocal() as session:
            db = DatabaseService(session)
            await db.update_run_status(run_id, "failed")

            from sqlalchemy import select
            from backend.database.models import Run
            result = await session.execute(
                select(Run).where(Run.id == run_id)
            )
            run = result.scalar_one_or_none()
            if run:
                run.error_message = error
            await session.commit()
    finally:
        await engine.dispose()