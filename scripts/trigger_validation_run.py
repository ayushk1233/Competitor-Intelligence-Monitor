import asyncio
import uuid
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from backend.celery_app import celery_app
from backend.database.models import Run
from backend.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def trigger_run():
    async with AsyncSessionLocal() as session:
        # Create a run in the DB
        run_id = str(uuid.uuid4())
        # The schema for Run:
        run = Run(
            id=run_id,
            status="pending",
            competitor_names=["OpenAI", "Anthropic", "Google"]
        )
        session.add(run)
        await session.commit()
        
        # Dispatch celery task
        # competitor_urls defaults to empty dict or we can pass some
        print(f"Created run {run_id}. Dispatching celery task...")
        celery_app.send_task(
            "run_analysis",
            args=[run_id, ["OpenAI", "Anthropic", "Google"]],
            kwargs={"competitor_urls": {
                "OpenAI": "https://openai.com",
                "Anthropic": "https://www.anthropic.com",
                "Google": "https://cloud.google.com/ai"
            }}
        )
        print("Task dispatched! Run ID:", run_id)

if __name__ == "__main__":
    asyncio.run(trigger_run())
