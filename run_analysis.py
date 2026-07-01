import asyncio
import uuid
from backend.database.connection import AsyncSessionLocal
from backend.database.models import Run, CompetitorAnalysisRecord, Organization, User
from backend.tasks import _run_pipeline
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        # Fetch or create org and user
        org_result = await session.execute(select(Organization).limit(1))
        org = org_result.scalar_one_or_none()
        
        user_result = await session.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                email="test@example.com",
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
        # Check competitor_analyses
        analyses_result = await session.execute(
            select(CompetitorAnalysisRecord).where(CompetitorAnalysisRecord.run_id == run_uuid)
        )
        analyses = analyses_result.scalars().all()
        print(f"Analyses found: {len(analyses)}")
        
        # Check intelligence_embeddings
        from backend.database.models import IntelligenceEmbedding
        embeddings_result = await session.execute(
            select(IntelligenceEmbedding).where(IntelligenceEmbedding.run_id == run_uuid)
        )
        embeddings = embeddings_result.scalars().all()
        print(f"Embeddings found: {len(embeddings)}")
        
    # Run again to test duplication
    print(f"Starting run {run_uuid} AGAIN")
    await _run_pipeline(run_uuid, ["vercel", "netlify"])
    
if __name__ == "__main__":
    asyncio.run(main())
