import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from backend.config import get_settings
from backend.database.models import Run, CompetitorAnalysisRecord, ComparisonRecord

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine)
    
    async with session_factory() as session:
        # Get latest run
        run_res = await session.execute(select(Run).order_by(Run.created_at.desc()).limit(1))
        latest_run = run_res.scalar_one_or_none()
        if not latest_run:
            print("No runs found")
            return
            
        print("=== LATEST RUN ===")
        print(f"RUN_ID: {latest_run.id}")
        
        # Get comparison for api response
        comp_res = await session.execute(select(ComparisonRecord).where(ComparisonRecord.run_id == latest_run.id))
        comparison = comp_res.scalar_one_or_none()
        
        # Get analyses
        analyses_res = await session.execute(select(CompetitorAnalysisRecord).where(CompetitorAnalysisRecord.run_id == latest_run.id))
        analyses = analyses_res.scalars().all()
        
        api_response = {
            "id": latest_run.id,
            "status": latest_run.status,
            "created_at": str(latest_run.created_at),
            "competitors": latest_run.competitor_names,
            "analyses": [a.full_analysis for a in analyses],
            "comparison": comparison.full_comparison if comparison else None
        }
        
        with open("api_response_sample.json", "w") as f:
            json.dump(api_response, f, indent=2)
        print("Wrote api_response_sample.json")
        
        with open("saved_analyses.json", "w") as f:
            json.dump([a.full_analysis for a in analyses], f, indent=2)
        print("Wrote saved_analyses.json")

asyncio.run(main())
