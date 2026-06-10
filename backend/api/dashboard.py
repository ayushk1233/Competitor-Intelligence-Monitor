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
)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
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
