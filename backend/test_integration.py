import asyncio
import uuid
import sys
from sqlalchemy import select

from backend.database.connection import AsyncSessionLocal
from backend.database.models import Run, CompetitorAnalysisRecord, Organization, User, IntelligenceEmbedding
from backend.tasks import _run_pipeline

async def main():
    async with AsyncSessionLocal() as session:
        org_result = await session.execute(select(Organization).limit(1))
        org = org_result.scalar_one_or_none()
        if not org:
            print("No organization found. Creating one...")
            org = Organization(name="Integration Test Org")
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
        user_result = await session.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        if not user:
            print("No user found. Creating one...")
            user = User(
                email="integration_tester@example.com",
                hashed_password="...",
                organization_id=org.id
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        run_uuid = str(uuid.uuid4())
        new_run = Run(id=run_uuid, status="queued", competitor_names=["vercel", "netlify"], user_id=user.id)
        session.add(new_run)
        await session.commit()
    
    print(f"Starting run {run_uuid}")
    await _run_pipeline(run_uuid, ["vercel", "netlify"])
    
    async with AsyncSessionLocal() as session:
        analyses_result = await session.execute(
            select(CompetitorAnalysisRecord).where(CompetitorAnalysisRecord.run_id == run_uuid)
        )
        analyses = analyses_result.scalars().all()
        print(f"Analyses found: {len(analyses)}")
        
        embeddings_result = await session.execute(
            select(IntelligenceEmbedding).where(IntelligenceEmbedding.run_id == run_uuid)
        )
        embeddings = embeddings_result.scalars().all()
        print(f"Embeddings found: {len(embeddings)}")
        
    print(f"\nStarting second run to verify deduplication")
    async with AsyncSessionLocal() as session:
        run_uuid2 = str(uuid.uuid4())
        new_run2 = Run(id=run_uuid2, status="queued", competitor_names=["vercel", "netlify"], user_id=user.id)
        session.add(new_run2)
        await session.commit()
    await _run_pipeline(run_uuid2, ["vercel", "netlify"])
    
    async with AsyncSessionLocal() as session:
        embeddings_result2 = await session.execute(
            select(IntelligenceEmbedding).where(IntelligenceEmbedding.run_id == run_uuid2)
        )
        embeddings2 = embeddings_result2.scalars().all()
        print(f"Embeddings found for run 2: {len(embeddings2)}")


if __name__ == "__main__":
    asyncio.run(main())
