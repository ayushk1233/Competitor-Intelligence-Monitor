from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.config import get_settings

settings = get_settings()

# Create async engine — manages the connection pool to PostgreSQL
engine = create_async_engine(
    settings.database_url,
    # Print all SQL queries to terminal (useful for debugging)
    echo=False,
    # Keep up to 10 connections open in the pool
    pool_size=10,
    # Allow 20 extra connections when pool is full
    max_overflow=20,
)

# Session factory — creates database sessions for each request
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class that all database models inherit from
class Base(DeclarativeBase):
    pass


async def get_db():
    """
    FastAPI dependency — provides a database session per request.
    Automatically closes the session when the request finishes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def verify_database():
    """
    Verify that the database schema has already been created by Alembic.

    This function intentionally does NOT create tables or modify schema.
    Database structure must always be managed through Alembic migrations.
    """
    async with engine.begin() as conn:
        # Import models so SQLAlchemy metadata is registered.
        from backend.database import models  # noqa: F401

        # Simple connectivity check.
        await conn.execute(text("SELECT 1"))

        # Verify Alembic has initialized the database.
        await conn.execute(
            text(
                """
                SELECT 1
                FROM alembic_version
                LIMIT 1
                """
            )
        )