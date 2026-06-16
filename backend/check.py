import asyncio, os
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from backend.database.models import PageSnapshot, Run, CompetitorAnalysisRecord

engine = create_async_engine("postgresql+asyncpg://cim_user:cim_password@postgres:5432/competitor_intel", echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def check():
    async with async_session() as session:
        result = await session.execute(select(Run).order_by(Run.created_at.desc()))
        run = result.scalars().first()
        records = await session.execute(select(CompetitorAnalysisRecord).filter(CompetitorAnalysisRecord.run_id == run.id))
        for r in records.scalars():
            val = r.full_analysis.get("validation", {})
            print(f"{r.competitor_name} - validation: {val}")

asyncio.run(check())
