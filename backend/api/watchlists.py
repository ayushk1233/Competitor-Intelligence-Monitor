from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from backend.auth.dependencies import (
    get_current_user,
)

from backend.tasks import monitor_watchlist_task
from backend.database.connection import get_db
from backend.database.db_service import (
    DatabaseService,
)
from backend.database.models import (
    User,
    Watchlist,
    WatchlistCompetitor,
    MonitoringRun,
)
from backend.models.schemas import (
    WatchlistCreateRequest,
    WatchlistResponse,
    WatchlistListResponse,
    CompetitorListResponse,
    CompetitorCreateRequest,
    CompetitorResponse,
    MonitoringRunCreateRequest,
    MonitoringRunResponse,
    MonitoringRunListResponse,
)

router = APIRouter(
    prefix="/api/watchlists",
    tags=["Watchlists"],
)




@router.post(
    "",
    response_model=WatchlistResponse,
    summary="Create watchlist",
    description="Create a new competitor monitoring watchlist.",
    responses={
        200: {"description": "Watchlist created"},
        401: {"description": "Unauthorized"},
    },
)
async def create_watchlist(
    request: WatchlistCreateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    watchlist = Watchlist(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
    )

    db.add(watchlist)

    await db.flush()
    await db.refresh(watchlist)

    return watchlist


@router.get(
    "",
    response_model=WatchlistListResponse,
    summary="List watchlists",
    description="Return paginated watchlists belonging to the authenticated user.",
    responses={
        200: {"description": "Watchlists returned"},
        401: {"description": "Unauthorized"},
    },
)
async def list_watchlists(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Watchlist)
        .where(
            Watchlist.user_id == current_user.id
        )
        .order_by(
            Watchlist.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
    )

    watchlists = result.scalars().all()

    return {
        "items": watchlists,
    }


@router.post(
    "/{watchlist_id}/competitors",
    response_model=CompetitorResponse,
    summary="Add competitor",
    description="Add a competitor to a watchlist.",
    responses={
        200: {"description": "Competitor added"},
        404: {"description": "Watchlist not found"},
        409: {"description": "Competitor already exists"},
    },
)
async def add_competitor(
    watchlist_id: str,
    request: CompetitorCreateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = DatabaseService(db)

    watchlist = await service.get_watchlist_for_user(
        watchlist_id,
        current_user.id,
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


@router.get(
    "/{watchlist_id}/competitors",
    response_model=CompetitorListResponse,
    summary="List competitors",
    description="Return competitors belonging to a watchlist.",
    responses={
        200: {"description": "Competitors returned"},
        404: {"description": "Watchlist not found"},
    },
)
async def list_competitors(
    watchlist_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = DatabaseService(db)

    watchlist = await service.get_watchlist_for_user(
        watchlist_id,
        current_user.id,
    )

    if watchlist is None:
        raise HTTPException(
            status_code=404,
            detail="Watchlist not found",
        )

    result = await db.execute(
        select(WatchlistCompetitor)
        .where(
            WatchlistCompetitor.watchlist_id == watchlist_id
        )
        .order_by(
            WatchlistCompetitor.company_name.asc()
        )
        .offset(offset)
        .limit(limit)
    )

    competitors = result.scalars().all()

    return {
        "items": competitors,
    }


@router.post(
    "/{watchlist_id}/runs",
    response_model=MonitoringRunResponse,
    summary="Start monitoring run",
    description="Queue a monitoring run for the selected watchlist.",
    responses={
        200: {"description": "Monitoring run queued"},
        404: {"description": "Watchlist not found"},
    },
)
async def create_monitoring_run(
    watchlist_id: str,
    request: MonitoringRunCreateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = DatabaseService(db)

    watchlist = await service.get_watchlist_for_user(
        watchlist_id,
        current_user.id,
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

    task = monitor_watchlist_task.delay(
        run.id,
    )

    run.celery_task_id = task.id

    await db.flush()
    await db.refresh(run)

    return run


@router.get(
    "/{watchlist_id}/runs",
    response_model=MonitoringRunListResponse,
    summary="List monitoring runs",
    description="Return monitoring run history for a watchlist.",
    responses={
        200: {"description": "Runs returned"},
        404: {"description": "Watchlist not found"},
    },
)
async def list_monitoring_runs(
    watchlist_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = DatabaseService(db)

    watchlist = await service.get_watchlist_for_user(
        watchlist_id,
        current_user.id,
    )

    if watchlist is None:
        raise HTTPException(
            status_code=404,
            detail="Watchlist not found",
        )

    result = await db.execute(
        select(MonitoringRun)
        .where(
            MonitoringRun.watchlist_id == watchlist_id
        )
        .order_by(
            MonitoringRun.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
    )

    runs = result.scalars().all()

    return {
        "items": runs,
    }
