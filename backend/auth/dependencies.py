from fastapi import (
    Depends,
    HTTPException,
)
from fastapi.security import (
    OAuth2PasswordBearer,
)
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.service import (
    decode_access_token,
)
from backend.database.connection import (
    get_db,
)
from backend.database.db_service import (
    DatabaseService,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


async def get_current_user(
    token: str = Depends(
        oauth2_scheme
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    try:
        payload = decode_access_token(
            token
        )

        user_id = payload.get(
            "sub"
        )

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    db_service = DatabaseService(
        db
    )

    user = await db_service.get_user_by_id(
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user
