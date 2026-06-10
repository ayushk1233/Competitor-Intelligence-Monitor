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

from backend.models.schemas import (
    DashboardSummaryResponse,
    DashboardRecentRunsResponse,
    DashboardRecentAlertsResponse,
    DashboardActivityResponse,
    DashboardActivityItem,
)

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
        current_user.id
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

    alerts = await service.get_recent_alerts(
        limit=10
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
