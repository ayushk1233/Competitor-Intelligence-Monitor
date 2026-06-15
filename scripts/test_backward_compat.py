import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from backend.database.models import Run, CompetitorAnalysisRecord
from backend.config import get_settings
from backend.models.schemas import CompetitorAnalysis as SchemaAnalysis

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def check_historical_reports():
    async with AsyncSessionLocal() as session:
        # Get oldest run
        result = await session.execute(select(Run).order_by(Run.created_at.asc()).limit(1))
        oldest_run = result.scalar_one_or_none()
        
        if oldest_run:
            print(f"Oldest run ID: {oldest_run.id}")
            # Get analyses for this run
            res = await session.execute(select(CompetitorAnalysisRecord).where(CompetitorAnalysisRecord.run_id == oldest_run.id))
            analyses = res.scalars().all()
            for analysis in analyses:
                print(f"Checking analysis for competitor: {analysis.competitor_name}")
                # Try to parse with Pydantic model
                try:
                    parsed = SchemaAnalysis(**analysis.full_analysis)
                    print(f"Successfully deserialized. competitor_dna present? {bool(parsed.competitor_dna)}")
                except Exception as e:
                    print(f"Deserialization failed: {e}")
        else:
            print("No historical runs found.")

if __name__ == "__main__":
    asyncio.run(check_historical_reports())
