from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.database.models import (
    Run, CompetitorAnalysisRecord,
    ComparisonRecord, PageSnapshot
)
from backend.models.schemas import IntelligenceReport, CompetitorPages


class DatabaseService:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Run operations ────────────────────────────────────────────────────

    async def create_run(self, competitor_names: list[str]) -> str:
        """Create a new run record. Returns the run_id."""
        run = Run(competitor_names=competitor_names, status="queued")
        self.session.add(run)
        await self.session.flush()  # Gets the ID without committing
        return run.id

    async def update_run_status(self, run_id: str, status: str):
        """Update run status: queued|scraping|analyzing|comparing|completed|failed"""
        result = await self.session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one_or_none()
        if run:
            run.status = status
            if status == "completed":
                run.completed_at = datetime.utcnow()

    async def get_run(self, run_id: str) -> Run | None:
        """Fetch a single run by ID."""
        result = await self.session.execute(select(Run).where(Run.id == run_id))
        return result.scalar_one_or_none()

    async def get_recent_runs(self, limit: int = 10) -> list[Run]:
        """Get the most recent runs ordered by creation time."""
        result = await self.session.execute(
            select(Run).order_by(desc(Run.created_at)).limit(limit)
        )
        return list(result.scalars().all())

    # ── Analysis operations ───────────────────────────────────────────────

    async def save_competitor_analysis(
        self, run_id: str, analysis
    ) -> CompetitorAnalysisRecord:
        """Save one competitor's analysis result to the database."""
        record = CompetitorAnalysisRecord(
            run_id=run_id,
            competitor_name=analysis.name,
            domain=analysis.domain,
            messaging_tone=analysis.messaging_tone,
            momentum_score=analysis.momentum_score,
            analysis_success=analysis.analysis_success,
            pages_analyzed=analysis.pages_analyzed,
            # Store the full analysis as JSON for complete retrieval
            full_analysis=analysis.model_dump()
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def save_comparison(
        self, run_id: str, comparison
    ) -> ComparisonRecord:
        """Save the cross-competitor comparison to the database."""
        record = ComparisonRecord(
            run_id=run_id,
            market_leader=comparison.market_leader,
            fastest_mover=comparison.fastest_mover,
            executive_briefing=comparison.executive_briefing,
            full_comparison=comparison.model_dump()
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def save_page_snapshots(
        self, run_id: str, competitor_pages: CompetitorPages
    ):
        """Save raw scraped page content — used later for drift detection."""
        for page in competitor_pages.pages:
            if page.fetch_success:
                snapshot = PageSnapshot(
                    run_id=run_id,
                    competitor_name=competitor_pages.name,
                    page_url=page.url,
                    page_type=page.page_type,
                    content_text=page.content,
                    word_count=len(page.content.split()) if page.content else 0,
                    fetch_success=page.fetch_success
                )
                self.session.add(snapshot)

    async def save_full_report(
        self, run_id: str, report: IntelligenceReport
    ):
        """
        Save a complete IntelligenceReport to the database.
        Updates run metadata + saves all analyses + comparison.
        """
        # Update run with final metadata
        result = await self.session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one_or_none()
        if run:
            run.status = "completed"
            run.total_pages_fetched = report.total_pages_fetched
            run.run_duration_seconds = report.run_duration_seconds
            run.completed_at = datetime.utcnow()

        # Save each competitor analysis
        for analysis in report.competitors:
            await self.save_competitor_analysis(run_id, analysis)

        # Save the comparison
        await self.save_comparison(run_id, report.comparison)

    # ── History operations ────────────────────────────────────────────────

    async def get_competitor_history(
        self, competitor_name: str, limit: int = 10
    ) -> list[CompetitorAnalysisRecord]:
        """
        Get historical analyses for one competitor.
        Used in Phase 3 for drift detection.
        """
        result = await self.session.execute(
            select(CompetitorAnalysisRecord)
            .where(CompetitorAnalysisRecord.competitor_name == competitor_name)
            .order_by(desc(CompetitorAnalysisRecord.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_momentum_history(
        self, competitor_name: str, limit: int = 10
    ) -> list[dict]:
        """
        Get just the momentum scores over time for one competitor.
        Used for trend charts in Phase 3.
        """
        records = await self.get_competitor_history(competitor_name, limit)
        return [
            {
                "date": r.created_at.strftime("%Y-%m-%d"),
                "momentum_score": r.momentum_score,
                "tone": r.messaging_tone
            }
            for r in records
        ]