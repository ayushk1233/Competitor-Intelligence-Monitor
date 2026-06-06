from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from backend.database.connection import get_db
from backend.database.models import User, Watchlist
from backend.models.schemas import (
    WatchlistCreateRequest,
    WatchlistResponse,
)

router = APIRouter(
    prefix="/api/watchlists",
    tags=["Watchlists"],
)

DEFAULT_USER_EMAIL = "local@cim.dev"


@router.post(
    "",
    response_model=WatchlistResponse,
)
async def create_watchlist(
    request: WatchlistCreateRequest,
    db: AsyncSession = Depends(get_db),
):
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

    watchlist = Watchlist(
        user_id=user.id,
        name=request.name,
        description=request.description,
    )

    db.add(watchlist)

    await db.flush()
    await db.refresh(watchlist)

    return watchlist
