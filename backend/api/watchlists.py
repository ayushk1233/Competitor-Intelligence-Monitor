from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from backend.database.connection import get_db
from backend.database.models import (
    User,
    Watchlist,
    WatchlistCompetitor,
    MonitoringRun,
)
from backend.models.schemas import (
    WatchlistCreateRequest,
    WatchlistResponse,
    CompetitorCreateRequest,
    CompetitorResponse,
    MonitoringRunCreateRequest,
    MonitoringRunResponse,
)

router = APIRouter(
    prefix="/api/watchlists",
    tags=["Watchlists"],
)

DEFAULT_USER_EMAIL = "local@cim.dev"

async def get_default_user(
    db: AsyncSession,
) -> User:
    result = await db.execute(
        select(User).where(
            User.email == DEFAULT_USER_EMAIL
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=DEFAULT_USER_EMAIL,
            display_name="Local User",
        )

        db.add(user)
        await db.flush()

    return user


@router.post(
    "",
    response_model=WatchlistResponse,
)
async def create_watchlist(
    request: WatchlistCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await get_default_user(db)

    watchlist = Watchlist(
        user_id=user.id,
        name=request.name,
        description=request.description,
    )

    db.add(watchlist)

    await db.flush()
    await db.refresh(watchlist)

    return watchlist


@router.post(
    "/{watchlist_id}/competitors",
    response_model=CompetitorResponse,
)
async def add_competitor(
    watchlist_id: str,
    request: CompetitorCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    watchlist = await db.get(
        Watchlist,
        watchlist_id,
    )

    if watchlist is None:
        raise HTTPException(
            status_code=404,
            detail="Watchlist not found",
        )

    normalized_name = request.company_name.strip()

    existing = await db.execute(
        select(WatchlistCompetitor).where(
            WatchlistCompetitor.watchlist_id == watchlist_id,
            WatchlistCompetitor.company_name == normalized_name,
        )
    )

    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Competitor already exists in watchlist",
        )

    competitor = WatchlistCompetitor(
        watchlist_id=watchlist_id,
        company_name=normalized_name,
        domain=request.domain,
    )

    db.add(competitor)

    await db.flush()
    await db.refresh(competitor)

    return competitor


@router.post(
    "/{watchlist_id}/runs",
    response_model=MonitoringRunResponse,
)
async def create_monitoring_run(
    watchlist_id: str,
    request: MonitoringRunCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    watchlist = await db.get(
        Watchlist,
        watchlist_id,
    )

    if watchlist is None:
        raise HTTPException(
            status_code=404,
            detail="Watchlist not found",
        )

    run = MonitoringRun(
        watchlist_id=watchlist_id,
        trigger_type=request.trigger_type,
        status="QUEUED",
        competitors_checked=0,
        alerts_generated=0,
        notifications_sent=0,
    )

    db.add(run)

    await db.flush()
    await db.refresh(run)

    return run
