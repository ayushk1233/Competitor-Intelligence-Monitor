from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database.db_service import DatabaseService
from backend.database.models import User
from backend.models.schemas import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    CurrentUserResponse,
)
from backend.auth.service import (
    hash_password,
    verify_password,
    create_access_token,
)
from backend.auth.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=AuthResponse,
)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    db_service = DatabaseService(db)

    existing = await db_service.get_user_by_email(
        request.email
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user = await db_service.create_user(
        email=request.email,
        password_hash=hash_password(
            request.password
        ),
        display_name=request.display_name,
    )

    token = create_access_token(
        str(user.id)
    )

    return AuthResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    db_service = DatabaseService(db)

    user = await db_service.get_user_by_email(
        request.email
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    user.last_login_at = datetime.now(
        UTC
    )

    token = create_access_token(
        str(user.id)
    )

    return AuthResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
async def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
    )
