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

from backend.auth.dependencies import (
    get_current_user,
)

from backend.database.models import (
    User,
)

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router.post(
    "/channels",
    response_model=NotificationChannelResponse,
    summary="Create notification channel",
    description="Register a new notification destination.",
    responses={
        200: {"description": "Operation successful"},
        401: {"description": "Unauthorized"},
        404: {"description": "Resource not found"},
    },
)
async def create_notification_channel(
    request: NotificationChannelCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = DatabaseService(db)

    channel = await service.create_notification_channel(
        user_id=current_user.id,
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
    summary="List notification channels",
    description="Return notification channels owned by the authenticated user.",
    responses={
        200: {"description": "Operation successful"},
        401: {"description": "Unauthorized"},
        404: {"description": "Resource not found"},
    },
)
async def list_notification_channels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = DatabaseService(db)

    channels = await service.get_notification_channels(
        current_user.id,
    )

    return {
        "items": channels,
    }


@router.put(
    "/channels/{channel_id}",
    response_model=NotificationChannelResponse,
    summary="Update notification channel",
    description="Enable or disable a notification channel.",
    responses={
        200: {"description": "Operation successful"},
        401: {"description": "Unauthorized"},
        404: {"description": "Resource not found"},
    },
)
async def update_notification_channel(
    channel_id: str,
    request: NotificationChannelUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DatabaseService(db)

    owned_channel = await (
        service.get_notification_channel_for_user(
            channel_id,
            current_user.id,
        )
    )

    if owned_channel is None:
        raise HTTPException(
            status_code=404,
            detail="Notification channel not found",
        )

    channel = await service.update_notification_channel(
        channel_id,
        current_user.id,
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
    summary="Delete notification channel",
    description="Remove a notification channel.",
    responses={
        200: {"description": "Operation successful"},
        401: {"description": "Unauthorized"},
        404: {"description": "Resource not found"},
    },
)
async def delete_notification_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DatabaseService(db)

    owned_channel = await (
        service.get_notification_channel_for_user(
            channel_id,
            current_user.id,
        )
    )

    if owned_channel is None:
        raise HTTPException(
            status_code=404,
            detail="Notification channel not found",
        )

    channel = await service.delete_notification_channel(
        channel_id,
        current_user.id,
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
