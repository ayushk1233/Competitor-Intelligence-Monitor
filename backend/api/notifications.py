from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database.db_service import DatabaseService

from backend.models.schemas import (
    NotificationChannelCreateRequest,
    NotificationChannelUpdateRequest,
    NotificationChannelResponse,
    NotificationChannelListResponse,
)

from backend.api.watchlists import (
    get_default_user,
)

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router.post(
    "/channels",
    response_model=NotificationChannelResponse,
)
async def create_notification_channel(
    request: NotificationChannelCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await get_default_user(db)

    service = DatabaseService(db)

    channel = await service.create_notification_channel(
        user_id=user.id,
        channel_type=request.channel_type,
        destination=request.destination,
        label=request.label,
    )

    await db.flush()
    await db.refresh(channel)

    return channel


@router.get(
    "/channels",
    response_model=NotificationChannelListResponse,
)
async def list_notification_channels(
    db: AsyncSession = Depends(get_db),
):
    user = await get_default_user(db)

    service = DatabaseService(db)

    channels = await service.get_notification_channels(
        user.id,
    )

    return {
        "items": channels,
    }


@router.put(
    "/channels/{channel_id}",
    response_model=NotificationChannelResponse,
)
async def update_notification_channel(
    channel_id: str,
    request: NotificationChannelUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DatabaseService(db)

    channel = await service.update_notification_channel(
        channel_id,
        request.enabled,
    )

    if channel is None:
        raise HTTPException(
            status_code=404,
            detail="Notification channel not found",
        )

    await db.flush()
    await db.refresh(channel)

    return channel


@router.delete(
    "/channels/{channel_id}",
)
async def delete_notification_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = DatabaseService(db)

    channel = await service.delete_notification_channel(
        channel_id,
    )

    if channel is None:
        raise HTTPException(
            status_code=404,
            detail="Notification channel not found",
        )

    await db.flush()

    return {
        "deleted": True,
        "channel_id": channel_id,
    }
