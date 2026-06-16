import os
import sys
import asyncio
import uuid
from backend.celery_app import celery_app
from backend.tasks import run_analysis_task

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from backend.database.models import Run

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "cim_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "cim_password")
DB_NAME = os.getenv("POSTGRES_DB", "competitor_intel")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

COMPANIES = ["Notion", "Airtable", "Coda"]

async def main():
    print(f"Creating Run for: {COMPANIES}")
    run_id = str(uuid.uuid4())
    async with async_session() as session:
        new_run = Run(
            id=run_id,
            status="queued",
            competitor_names=COMPANIES,
            user_id=None
        )
        session.add(new_run)
        await session.commit()
        
    print(f"Created run {run_id}. Dispatching celery task...")
    task = run_analysis_task.delay(run_id, COMPANIES, {})
    print(f"Task ID: {task.id}")

if __name__ == "__main__":
    asyncio.run(main())
