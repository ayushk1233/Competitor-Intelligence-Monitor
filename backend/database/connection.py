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


async def create_tables():
    """
    Create all tables defined in models.py if they don't exist.
    Called once on app startup.
    """
    async with engine.begin() as conn:
        from backend.database import models  # noqa: F401 — registers models
        await conn.run_sync(Base.metadata.create_all)

        # Dev migrations: add columns that may not exist on existing tables
        migrations = [
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS watchlist_id VARCHAR(36) REFERENCES watchlists(id) ON DELETE SET NULL",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS headline VARCHAR(300) NOT NULL DEFAULT ''",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS summary TEXT",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS evidence JSON DEFAULT '[]'::json",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS confidence INTEGER DEFAULT 90",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS business_impact VARCHAR(500)",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS recommended_action VARCHAR(500)",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'new'",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS fingerprint_hash VARCHAR(64)",
            "ALTER TABLE alert_history ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ",
            "ALTER TABLE watchlist_competitors ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium'",
            "ALTER TABLE watchlist_competitors ADD COLUMN IF NOT EXISTS monitoring_enabled BOOLEAN DEFAULT TRUE",
            "ALTER TABLE watchlists ADD COLUMN IF NOT EXISTS monitoring_config JSON DEFAULT '{}'::json",
            "ALTER TABLE watchlists ADD COLUMN IF NOT EXISTS alert_rules JSON DEFAULT '{}'::json",
            "ALTER TABLE watchlists ADD COLUMN IF NOT EXISTS notification_channels JSON DEFAULT '[]'::json",
            "ALTER TABLE runs ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL",
            "CREATE INDEX IF NOT EXISTS ix_runs_user_id ON runs(user_id)",
            "CREATE INDEX IF NOT EXISTS ix_alert_history_company_name ON alert_history(company_name)",
            "CREATE INDEX IF NOT EXISTS ix_alert_history_watchlist_id ON alert_history(watchlist_id)",
            "CREATE INDEX IF NOT EXISTS ix_alert_history_fingerprint_hash ON alert_history(fingerprint_hash)",
        ]
        for migration in migrations:
            try:
                await conn.execute(text(migration))
            except Exception:
                pass  # Skip if column already exists or other non-critical error