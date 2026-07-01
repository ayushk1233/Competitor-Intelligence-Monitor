import asyncio
import uuid
import sys
from sqlalchemy import select

from backend.database.connection import AsyncSessionLocal
from backend.database.models import Run, CompetitorAnalysisRecord, Organization, User, IntelligenceEmbedding
from backend.tasks import _run_pipeline

from unittest.mock import patch

async def main():
    async with AsyncSessionLocal() as session:
        org_result = await session.execute(select(Organization).limit(1))
        org = org_result.scalar_one_or_none()
            
        user_result = await session.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        
        run_uuid = str(uuid.uuid4())
        new_run = Run(id=run_uuid, status="queued", competitor_names=["vercel", "netlify"], user_id=user.id)
        session.add(new_run)
        await session.commit()
    
    print(f"Starting run {run_uuid} with forced failure in EmbeddingRepository")
    
    try:
        with patch('backend.memory.repository.EmbeddingRepository.save_embeddings', side_effect=Exception("Forced Repository Failure")):
            await _run_pipeline(run_uuid, ["vercel", "netlify"])
    except Exception as e:
        print(f"Caught exception: {e}")
        
    async with AsyncSessionLocal() as session:
        analyses_result = await session.execute(
            select(CompetitorAnalysisRecord).where(CompetitorAnalysisRecord.run_id == run_uuid)
        )
        analyses = analyses_result.scalars().all()
        print(f"Analyses found after rollback: {len(analyses)} (Expected: 0)")
        
        embeddings_result = await session.execute(
            select(IntelligenceEmbedding).where(IntelligenceEmbedding.run_id == run_uuid)
        )
        embeddings = embeddings_result.scalars().all()
        print(f"Embeddings found after rollback: {len(embeddings)} (Expected: 0)")
        
        from backend.database.models import ComparisonRecord
        comparison_result = await session.execute(
            select(ComparisonRecord).where(ComparisonRecord.run_id == run_uuid)
        )
        comparisons = comparison_result.scalars().all()
        print(f"Comparisons found after rollback: {len(comparisons)} (Expected: 0)")

if __name__ == "__main__":
    asyncio.run(main())
