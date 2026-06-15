import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from backend.config import get_settings
from backend.database.models import Run, CompetitorAnalysisRecord, PageSnapshot

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine)
    
    async with session_factory() as session:
        # Get one recent analysis record
        result = await session.execute(select(CompetitorAnalysisRecord).order_by(CompetitorAnalysisRecord.id.desc()).limit(1))
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            print("No analysis found")
            return
            
        print("COMPANY:", analysis.competitor_name)
        print("RUN_ID:", analysis.run_id)
        
        # Get snapshots
        snap_result = await session.execute(select(PageSnapshot).where(PageSnapshot.run_id == analysis.run_id, PageSnapshot.competitor_name == analysis.competitor_name).limit(1))
        snapshot = snap_result.scalar_one_or_none()
        
        if snapshot:
            print("\n--- RAW PAGE TEXT ---")
            print(snapshot.content_text[:1000] + "...")
            
        print("\n--- FULL ANALYSIS JSON ---")
        import json
        print(json.dumps(analysis.full_analysis, indent=2))

asyncio.run(main())
