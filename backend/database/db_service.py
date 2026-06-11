from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_, func
from backend.database.models import (
    Run, CompetitorAnalysisRecord,
    ComparisonRecord, PageSnapshot, AlertHistory,
    AlertSuppression, NotificationEvent, Watchlist,
    NotificationChannel, User, WatchlistCompetitor,
    MonitoringRun,
)
from backend.models.schemas import IntelligenceReport, CompetitorPages


class DatabaseService:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── User operations ───────────────────────────────────────────────────

    async def get_user_by_email(
        self,
        email: str,
    ):
        result = await self.session.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        user_id: str,
    ):
        result = await self.session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        password_hash: str,
        display_name: str | None = None,
    ):
        user = User(
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            is_active=True,
        )

        self.session.add(user)

        await self.session.flush()

        return user

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

    async def delete_run(self, run_id: str) -> bool:
        """Delete an ad-hoc analysis run and its cascade (analyses, comparison, snapshots)."""
        run = await self.session.get(Run, run_id)
        if not run:
            return False
        await self.session.delete(run)
        await self.session.commit()
        return True

    async def get_last_adhoc_run(self) -> Run | None:
        """Get the most recent ad-hoc analysis run."""
        result = await self.session.execute(
            select(Run).order_by(desc(Run.created_at)).limit(1)
        )
        return result.scalar_one_or_none()


    async def delete_monitoring_run(self, run_id: str) -> bool:
        """Delete a monitoring run."""
        run = await self.session.get(MonitoringRun, run_id)
        if not run:
            return False
        await self.session.delete(run)
        await self.session.commit()
        return True

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

    async def save_alert(
        self,
        company_name: str,
        severity: str,
        headline: str,
        summary: str | None = None,
        reasons: list | None = None,
        evidence: list | None = None,
        confidence: int = 90,
        business_impact: str | None = None,
        recommended_action: str | None = None,
        watchlist_id: str | None = None,
        fingerprint_hash: str | None = None,
    ):
        alert = AlertHistory(
            company_name=company_name,
            severity=severity,
            headline=headline,
            summary=summary,
            reasons=reasons or [],
            evidence=evidence or [],
            confidence=confidence,
            business_impact=business_impact,
            recommended_action=recommended_action,
            watchlist_id=watchlist_id,
            fingerprint_hash=fingerprint_hash,
            status="new",
        )

        self.session.add(alert)
        await self.session.flush()
        return alert

    async def get_alert_by_id(self, alert_id: int) -> AlertHistory | None:
        result = await self.session.execute(
            select(AlertHistory).where(AlertHistory.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def update_alert_status(
        self, alert_id: int, status: str
    ) -> AlertHistory | None:
        alert = await self.get_alert_by_id(alert_id)
        if not alert:
            return None
        alert.status = status
        alert.updated_at = datetime.utcnow()
        await self.session.flush()
        return alert

    async def get_user_competitor_names(self, user_id: str) -> list[str]:
        result = await self.session.execute(
            select(WatchlistCompetitor.company_name)
            .join(Watchlist, Watchlist.id == WatchlistCompetitor.watchlist_id)
            .where(Watchlist.user_id == user_id)
            .distinct()
        )
        return [row[0] for row in result.all()]

    async def get_alert_counts_by_severity(
        self,
        competitor_names: list[str] | None = None,
        watchlist_ids: list[str] | None = None,
    ) -> dict[str, int]:
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for severity in counts:
            query = select(func.count()).select_from(AlertHistory).where(
                AlertHistory.severity == severity,
                AlertHistory.status.in_(["new", "viewed"]),
            )
            if competitor_names is not None:
                query = query.where(AlertHistory.company_name.in_(competitor_names))
            if watchlist_ids is not None:
                query = query.where(AlertHistory.watchlist_id.in_(watchlist_ids))
            result = await self.session.execute(query)
            counts[severity] = result.scalar() or 0
        return counts

    async def get_alert_counts_by_severity_for_user(self, user_id: str) -> dict[str, int]:
        watchlist_ids = await self.get_user_watchlist_ids(user_id)
        if not watchlist_ids:
            return {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        competitor_names = await self.get_user_watchlist_competitor_names(user_id)
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for severity in counts:
            query = (
                select(func.count())
                .select_from(AlertHistory)
                .where(
                    AlertHistory.severity == severity,
                    AlertHistory.status.in_(["new", "viewed"]),
                    or_(
                        AlertHistory.watchlist_id.in_(watchlist_ids),
                        and_(
                            AlertHistory.watchlist_id.is_(None),
                            AlertHistory.company_name.in_(competitor_names),
                        ),
                    ),
                )
            )
            result = await self.session.execute(query)
            counts[severity] = result.scalar() or 0
        return counts

    async def get_alert_count_for_company(self, company_name: str) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(AlertHistory)
            .where(AlertHistory.company_name == company_name)
            .where(AlertHistory.status.in_(["new", "acknowledged"]))
        )
        return result.scalar() or 0

    async def update_run_pages_fetched(self, run_id: str, total_pages: int):
        result = await self.session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one_or_none()
        if run:
            run.total_pages_fetched = total_pages

    async def get_active_run(self) -> Run | None:
        result = await self.session.execute(
            select(Run)
            .where(Run.status.in_(["queued", "scraping", "analyzing", "comparing"]))
            .order_by(Run.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

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

    async def get_user_watchlist_ids(self, user_id: str) -> list[str]:
        result = await self.session.execute(
            select(Watchlist.id).where(Watchlist.user_id == user_id)
        )
        return [row[0] for row in result.all()]

    async def get_alerts(
        self,
        limit: int = 100,
        competitor_names: list[str] | None = None,
        watchlist_ids: list[str] | None = None,
    ):
        query = select(AlertHistory).order_by(desc(AlertHistory.created_at))
        if competitor_names is not None:
            query = query.where(AlertHistory.company_name.in_(competitor_names))
        if watchlist_ids is not None:
            query = query.where(AlertHistory.watchlist_id.in_(watchlist_ids))
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_watchlist_competitor_names(self, user_id: str) -> list[str]:
        """Get all competitor names from all of a user's watchlists."""
        watchlist_ids_sub = select(Watchlist.id).where(Watchlist.user_id == user_id).scalar_subquery()
        result = await self.session.execute(
            select(WatchlistCompetitor.company_name)
            .where(WatchlistCompetitor.watchlist_id.in_(watchlist_ids_sub))
            .distinct()
        )
        return [row[0] for row in result.all()]

    async def get_alerts_for_user(
        self,
        user_id: str,
        limit: int = 100,
    ):
        watchlist_ids = await self.get_user_watchlist_ids(user_id)
        if not watchlist_ids:
            return []
        competitor_names = await self.get_user_watchlist_competitor_names(user_id)
        query = (
            select(AlertHistory)
            .where(
                or_(
                    AlertHistory.watchlist_id.in_(watchlist_ids),
                    and_(
                        AlertHistory.watchlist_id.is_(None),
                        AlertHistory.company_name.in_(competitor_names),
                    ),
                )
            )
            .order_by(desc(AlertHistory.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_alerts_for_company(
        self,
        company_name: str,
        limit: int = 50,
    ):
        result = await self.session.execute(
            select(AlertHistory)
            .where(AlertHistory.company_name == company_name)
            .order_by(desc(AlertHistory.created_at))
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_latest_alerts(
        self,
        limit: int = 10,
    ):
        return await self.get_alerts(limit)

    async def get_latest_analysis(
        self,
        competitor_name: str,
    ):
        history = await self.get_competitor_history(
            competitor_name,
            limit=1,
        )

        if not history:
            return None

        return history[0]

    async def get_latest_two_analyses(
        self,
        competitor_name: str,
    ):
        history = await self.get_competitor_history(
            competitor_name,
            limit=2,
        )

        if len(history) < 2:
            return None

        return history

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

    # ── Suppression operations ────────────────────────────────────────────

    async def get_active_suppression(
        self, company_name: str, alert_type: str
    ) -> AlertSuppression | None:
        result = await self.session.execute(
            select(AlertSuppression)
            .where(AlertSuppression.company_name == company_name)
            .where(AlertSuppression.alert_type == alert_type)
            .where(AlertSuppression.suppressed_until > datetime.utcnow())
        )
        return result.scalar_one_or_none()

    async def create_suppression(
        self, company_name: str, alert_type: str, hours: int = 24
    ) -> AlertSuppression:
        from datetime import timedelta
        suppression = AlertSuppression(
            company_name=company_name,
            alert_type=alert_type,
            suppressed_until=datetime.utcnow() + timedelta(hours=hours)
        )
        self.session.add(suppression)
        await self.session.flush()
        return suppression

    async def get_user_notification_channels(
        self,
        user_id: str,
    ):
        result = await self.session.execute(
            select(NotificationChannel)
            .where(
                NotificationChannel.user_id == user_id,
                NotificationChannel.enabled == True,
            )
        )

        return list(result.scalars().all())

    async def get_notification_events(
        self,
        channel_id: str,
        limit: int = 20,
    ):
        channel = await self.session.execute(
            select(NotificationChannel).where(NotificationChannel.id == channel_id)
        )
        channel = channel.scalar_one_or_none()
        if not channel:
            return []

        result = await self.session.execute(
            select(NotificationEvent)
            .where(
                NotificationEvent.destination == channel.destination,
                NotificationEvent.channel_type == channel.channel_type,
            )
            .order_by(NotificationEvent.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def create_notification_event(
        self,
        company_name: str,
        severity: str,
        destination: str,
        channel_type: str,
        delivery_status: str,
        error_message: str | None = None,
    ):
        event = NotificationEvent(
            company_name=company_name,
            severity=severity,
            destination=destination,
            channel_type=channel_type,
            delivery_status=delivery_status,
            error_message=error_message,
        )

        self.session.add(event)

        await self.session.flush()

        return event

    async def create_notification_channel(
        self,
        user_id: str,
        channel_type: str,
        destination: str,
        label: str | None = None,
    ):
        channel = NotificationChannel(
            user_id=user_id,
            channel_type=channel_type.upper(),
            destination=destination,
            label=label,
            enabled=True,
            verified=False,
        )

        self.session.add(channel)

        await self.session.flush()

        return channel

    async def get_notification_channels(
        self,
        user_id: str,
    ):
        result = await self.session.execute(
            select(NotificationChannel)
            .where(
                NotificationChannel.user_id == user_id
            )
            .order_by(
                NotificationChannel.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_enabled_notification_channels(
        self,
    ):
        result = await self.session.execute(
            select(NotificationChannel)
            .where(
                NotificationChannel.enabled == True
            )
        )

        return list(result.scalars().all())

    async def update_notification_channel(
        self,
        channel_id: str,
        user_id: str,
        enabled: bool,
    ):
        channel = await self.get_notification_channel_for_user(
            channel_id,
            user_id,
        )

        if channel:
            channel.enabled = enabled

        return channel

    async def delete_notification_channel(
        self,
        channel_id: str,
        user_id: str,
    ):
        channel = await self.get_notification_channel_for_user(
            channel_id,
            user_id,
        )

        if channel:
            await self.session.delete(channel)

        return channel

    async def get_watchlist_for_user(
        self,
        watchlist_id: str,
        user_id: str,
    ):
        result = await self.session.execute(
            select(Watchlist).where(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_notification_channel_for_user(
        self,
        channel_id: str,
        user_id: str,
    ):
        result = await self.session.execute(
            select(NotificationChannel).where(
                NotificationChannel.id == channel_id,
                NotificationChannel.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_due_watchlists(
        self,
    ):
        result = await self.session.execute(
            select(Watchlist)
            .where(
                Watchlist.is_active == True,
                Watchlist.next_run_at <= datetime.now(UTC),
            )
        )

        return list(result.scalars().all())

    async def update_watchlist_schedule(
        self,
        watchlist_id: str,
        next_run_at,
    ):
        result = await self.session.execute(
            select(Watchlist)
            .where(
                Watchlist.id == watchlist_id
            )
        )

        watchlist = result.scalar_one_or_none()

        if watchlist:
            watchlist.last_monitored_at = datetime.now(UTC)
            watchlist.next_run_at = next_run_at

    async def get_watchlist_count(
        self,
        user_id: str,
    ):
        result = await self.session.execute(
            select(func.count())
            .select_from(Watchlist)
            .where(
                Watchlist.user_id == user_id
            )
        )

        return result.scalar() or 0

    async def get_competitor_count(
        self,
        user_id: str,
    ):
        result = await self.session.execute(
            select(func.count())
            .select_from(WatchlistCompetitor)
            .join(
                Watchlist,
                Watchlist.id
                == WatchlistCompetitor.watchlist_id
            )
            .where(
                Watchlist.user_id == user_id
            )
        )

        return result.scalar() or 0

    async def get_notification_channel_count(
        self,
        user_id: str,
    ):
        result = await self.session.execute(
            select(func.count())
            .select_from(NotificationChannel)
            .where(
                NotificationChannel.user_id == user_id
            )
        )

        return result.scalar() or 0

    async def get_recent_runs_for_user(
        self,
        user_id: str,
        limit: int = 10,
    ):
        result = await self.session.execute(
            select(MonitoringRun)
            .join(
                Watchlist,
                Watchlist.id
                == MonitoringRun.watchlist_id
            )
            .where(
                Watchlist.user_id == user_id
            )
            .order_by(
                MonitoringRun.created_at.desc()
            )
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    async def get_last_run_for_user(
        self,
        user_id: str,
    ):
        result = await self.session.execute(
            select(MonitoringRun)
            .join(
                Watchlist,
                Watchlist.id == MonitoringRun.watchlist_id,
            )
            .where(Watchlist.user_id == user_id)
            .order_by(MonitoringRun.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_monitoring_runs_today(
        self,
        user_id: str,
    ):
        today = datetime.now(
            UTC
        ).date()

        result = await self.session.execute(
            select(func.count())
            .select_from(MonitoringRun)
            .join(
                Watchlist,
                Watchlist.id
                == MonitoringRun.watchlist_id
            )
            .where(
                Watchlist.user_id == user_id,
                func.date(
                    MonitoringRun.created_at
                ) == today,
            )
        )

        return result.scalar() or 0

    async def get_recent_alerts(
        self,
        limit: int = 10,
    ):
        result = await self.session.execute(
            select(AlertHistory)
            .order_by(
                AlertHistory.created_at.desc()
            )
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    async def get_watchlists(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ):
        result = await self.session.execute(
            select(Watchlist)
            .where(
                Watchlist.user_id == user_id
            )
            .order_by(
                Watchlist.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def create_watchlist(
        self,
        user_id: str,
        name: str,
        description: str | None = None,
        monitoring_config: dict | None = None,
        alert_rules: dict | None = None,
        notification_channels: list | None = None,
    ) -> Watchlist:
        watchlist = Watchlist(
            user_id=user_id,
            name=name,
            description=description,
            monitoring_config=monitoring_config or {
                "frequency": "daily",
                "sources": ["homepage", "pricing", "blog", "careers"],
                "sensitivity": "medium",
            },
            alert_rules=alert_rules or {},
            notification_channels=notification_channels or [],
        )
        self.session.add(watchlist)
        await self.session.flush()
        return watchlist

    async def update_watchlist(
        self,
        watchlist_id: str,
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        monitoring_config: dict | None = None,
        alert_rules: dict | None = None,
        notification_channels: list | None = None,
        is_active: bool | None = None,
    ) -> Watchlist | None:
        watchlist = await self.get_watchlist_for_user(watchlist_id, user_id)
        if not watchlist:
            return None
        if name is not None:
            watchlist.name = name
        if description is not None:
            watchlist.description = description
        if monitoring_config is not None:
            watchlist.monitoring_config = monitoring_config
        if alert_rules is not None:
            watchlist.alert_rules = alert_rules
        if notification_channels is not None:
            watchlist.notification_channels = notification_channels
        if is_active is not None:
            watchlist.is_active = is_active
        watchlist.updated_at = datetime.utcnow()
        await self.session.flush()
        return watchlist

    async def delete_watchlist(
        self, watchlist_id: str, user_id: str
    ) -> bool:
        watchlist = await self.get_watchlist_for_user(watchlist_id, user_id)
        if not watchlist:
            return False
        await self.session.delete(watchlist)
        await self.session.flush()
        return True

    async def get_all_latest_analyses(self) -> list[CompetitorAnalysisRecord]:
        """
        Get the latest analysis for every unique competitor.
        Returns the full CompetitorAnalysisRecord objects.
        """
        latest_per_competitor = (
            select(
                CompetitorAnalysisRecord.competitor_name,
                func.max(CompetitorAnalysisRecord.created_at).label("max_created_at"),
            )
            .group_by(CompetitorAnalysisRecord.competitor_name)
            .subquery()
        )

        result = await self.session.execute(
            select(CompetitorAnalysisRecord)
            .join(
                latest_per_competitor,
                (CompetitorAnalysisRecord.competitor_name == latest_per_competitor.c.competitor_name)
                & (CompetitorAnalysisRecord.created_at == latest_per_competitor.c.max_created_at),
            )
        )
        return list(result.scalars().all())

    async def add_competitor_to_watchlist(
        self,
        watchlist_id: str,
        company_name: str,
        domain: str | None = None,
        priority: str = "medium",
        monitoring_enabled: bool = True,
    ) -> WatchlistCompetitor:
        competitor = WatchlistCompetitor(
            watchlist_id=watchlist_id,
            company_name=company_name,
            domain=domain,
            priority=priority,
            monitoring_enabled=monitoring_enabled,
        )
        self.session.add(competitor)
        await self.session.flush()
        return competitor

    async def update_watchlist_competitor(
        self,
        competitor_id: str,
        company_name: str | None = None,
        domain: str | None = None,
        priority: str | None = None,
        monitoring_enabled: bool | None = None,
    ) -> WatchlistCompetitor | None:
        result = await self.session.execute(
            select(WatchlistCompetitor).where(WatchlistCompetitor.id == competitor_id)
        )
        comp = result.scalar_one_or_none()
        if not comp:
            return None
        if company_name is not None:
            comp.company_name = company_name
        if domain is not None:
            comp.domain = domain
        if priority is not None:
            comp.priority = priority
        if monitoring_enabled is not None:
            comp.monitoring_enabled = monitoring_enabled
        await self.session.flush()
        return comp

    async def delete_watchlist_competitor(self, competitor_id: str) -> bool:
        result = await self.session.execute(
            select(WatchlistCompetitor).where(WatchlistCompetitor.id == competitor_id)
        )
        comp = result.scalar_one_or_none()
        if not comp:
            return False
        await self.session.delete(comp)
        await self.session.flush()
        return True