from datetime import datetime, timedelta, UTC

from jose import jwt
from passlib.context import CryptContext

from backend.config import get_settings

settings = get_settings()

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_HOURS = (
    settings.jwt_expire_hours
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        password_hash,
    )


def create_access_token(
    user_id: str,
):
    expire = (
        datetime.now(UTC)
        + timedelta(
            hours=ACCESS_TOKEN_EXPIRE_HOURS
        )
    )

    payload = {
        "sub": user_id,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
):
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )
