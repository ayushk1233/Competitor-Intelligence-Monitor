from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import (
    get_current_user,
)
from backend.database.connection import (
    get_db,
)
from backend.database.db_service import (
    DatabaseService,
)
from backend.database.models import (
    User,
)
from urllib.parse import urlparse

from backend.models.schemas import (
    DashboardActivityResponse,
    DashboardCompetitorResponse,
    DashboardCompetitorsResponse,
    DashboardRecentAlertsResponse,
    DashboardRecentRunsResponse,
    DashboardSummaryResponse,
)

def _extract_hostname(url: str) -> str:
    if not url:
        return ""
    if not url.startswith("http"):
        url = "https://" + url
    parsed = urlparse(url)
    return parsed.hostname or ""

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard summary",
    description="Return aggregate dashboard metrics for the authenticated user.",
)
async def get_dashboard_summary(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    service = DatabaseService(db)

    alert_counts = await service.get_alert_counts_by_severity_for_user(current_user.id)
    last_monitoring_run = await service.get_last_run_for_user(current_user.id)
    last_adhoc_run = await service.get_last_adhoc_run(user_id=str(current_user.id))
    active_run = await service.get_active_run()

    candidates = []
    if last_monitoring_run:
        candidates.append(last_monitoring_run.created_at)
    if last_adhoc_run:
        candidates.append(last_adhoc_run.created_at)
    last_run_at = max(candidates) if candidates else None

    from backend.database.models import Watchlist
    from sqlalchemy import select, func
    next_run_res = await db.execute(
        select(func.min(Watchlist.next_run_at))
        .where(Watchlist.user_id == str(current_user.id))
        .where(Watchlist.is_active == True)
        .where(Watchlist.next_run_at.is_not(None))
    )
    next_scheduled_analysis = next_run_res.scalar()

    return DashboardSummaryResponse(
        watchlists=await service.get_watchlist_count(
            current_user.id
        ),
        competitors=await service.get_competitor_count(
            current_user.id
        ),
        monitoring_runs_today=await service.get_monitoring_runs_today(
            current_user.id
        ),
        notification_channels=await service.get_notification_channel_count(
            current_user.id
        ),
        critical_alerts=alert_counts.get("CRITICAL", 0),
        high_alerts=alert_counts.get("HIGH", 0),
        medium_alerts=alert_counts.get("MEDIUM", 0),
        low_alerts=alert_counts.get("LOW", 0),
        competitors_requiring_review=alert_counts.get("HIGH", 0) + alert_counts.get("CRITICAL", 0),
        last_run_at=last_run_at,
        total_alerts=sum(alert_counts.values()),
        has_active_run=active_run is not None,
        active_run_status=active_run.status if active_run else None,
        active_run_id=active_run.id if active_run else None,
        next_scheduled_analysis=next_scheduled_analysis,
    )


@router.get(
    "/recent-runs",
    response_model=DashboardRecentRunsResponse,
    summary="Recent monitoring runs",
    description="Return recent monitoring runs for the authenticated user.",
)
async def get_recent_runs(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    service = DatabaseService(db)

    runs = await service.get_recent_runs_for_user(
        current_user.id, limit=5
    )

    return {
        "items": runs
    }


@router.get(
    "/recent-alerts",
    response_model=DashboardRecentAlertsResponse,
    summary="Recent alerts",
    description="Return latest generated alerts.",
)
async def get_recent_alerts(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    service = DatabaseService(db)

    alerts = await service.get_alerts_for_user(
        current_user.id,
        limit=10,
    )

    return {
        "items": alerts
    }


@router.get(
    "/activity",
    response_model=DashboardActivityResponse,
    summary="Recent activity",
    description="Return recent user activity shown on the dashboard.",
)
async def get_activity(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = DatabaseService(db)

    watchlists = await service.get_watchlists(
        current_user.id,
        limit=5,
        offset=0,
    )

    activities = []

    for watchlist in watchlists:
        activities.append(
            {
                "activity_type": "WATCHLIST_CREATED",
                "title": watchlist.name,
                "timestamp": watchlist.created_at,
            }
        )

    activities.sort(
        key=lambda x: x["timestamp"],
        reverse=True,
    )

    return {
        "items": activities[:20]
    }


@router.get(
    "/competitors",
    response_model=DashboardCompetitorsResponse,
    summary="Dashboard competitors",
    description="Return all competitors with their latest analysis data.",
)
async def get_dashboard_competitors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DatabaseService(db)

    names_from_runs = await service.get_run_competitor_names(str(current_user.id))

    user_competitor_names = list(set(names_from_runs))
    if not user_competitor_names:
        return DashboardCompetitorsResponse(items=[])

    records = await service.get_all_latest_analyses(competitor_names=user_competitor_names)

    user_watchlist_ids = await service.get_user_watchlist_ids(current_user.id)

    items = []
    for r in records:
        count = await service.get_alert_count_for_company(r.competitor_name, watchlist_ids=user_watchlist_ids)
        max_severity = await service.get_highest_severity_for_company(r.competitor_name, watchlist_ids=user_watchlist_ids)
        fa = r.full_analysis or {}
        items.append(
            DashboardCompetitorResponse(
                company_name=r.competitor_name,
                domain=r.domain,
                logo_url=f"https://www.google.com/s2/favicons?domain={_extract_hostname(r.domain)}&sz=32" if r.domain else None,
                messaging_tone=r.messaging_tone,
                momentum_score=r.momentum_score,
                last_analyzed_at=r.created_at,
                alert_count=count,
                has_active_alerts=count > 0,
                max_severity=max_severity,
                analyst_note=fa.get("analyst_note"),
                core_offering=fa.get("core_offering"),
            )
        )

    return DashboardCompetitorsResponse(items=items)
