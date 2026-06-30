import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func

from backend.database.connection import AsyncSessionLocal
from backend.database.models import IntelligenceEmbedding
from backend.memory.embedding import EmbeddingRecord
from backend.memory.document import EmbeddingSourceType, ChunkType
from backend.memory.repository import EmbeddingRepository

async def main():
    repo = EmbeddingRepository()
    
    # We need a valid organization_id and run_id if the DB enforces foreign keys.
    # To test locally without complex setup, if we just want to verify insertion
    # and deduplication, we might need to grab an existing org/run or use a mock session.
    # But since this is a real integration verify script, let's try grabbing the default org
    # and creating a dummy run.
    
    async with AsyncSessionLocal() as session:
        # Get an org ID
        from backend.database.models import Organization, Run
        org = (await session.execute(select(Organization).limit(1))).scalars().first()
        if not org:
            org = Organization(name="Test Org")
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
        run_uuid = str(uuid.uuid4())
        run = Run(id=run_uuid, status="queued", competitor_names=[])
        session.add(run)
        await session.commit()
        
        org_id = org.id
        
        # Create a batch
        records = [
            EmbeddingRecord(
                organization_id=org_id,
                run_id=run_uuid,
                company_name="Acme",
                source_type=EmbeddingSourceType.ANALYSIS,
                source_id="snap_1",
                chunk_type=ChunkType.EXECUTIVE_BRIEFING,
                chunk_order=1,
                chunk_text="Test Chunk 1",
                embedding_model="test-model",
                embedding=[0.1] * 384,
                content_hash="verify_hash_1",
                analyzed_at=datetime.now(timezone.utc)
            ),
            EmbeddingRecord(
                organization_id=org_id,
                run_id=run_uuid,
                company_name="Acme",
                source_type=EmbeddingSourceType.ANALYSIS,
                source_id="snap_1",
                chunk_type=ChunkType.EXECUTIVE_BRIEFING,
                chunk_order=2,
                chunk_text="Test Chunk 2",
                embedding_model="test-model",
                embedding=[0.2] * 384,
                content_hash="verify_hash_2",
                analyzed_at=datetime.now(timezone.utc)
            )
        ]
        
        print("Inserting first batch...")
        inserted = await repo.save_embeddings(session, records)
        await session.commit()
        print(f"Inserted rows: {inserted}")
        
        print("Inserting identical batch...")
        inserted_dup = await repo.save_embeddings(session, records)
        await session.commit()
        print(f"Inserted rows (duplicate): {inserted_dup}")
        
        # Count total rows
        count = (await session.execute(select(func.count(IntelligenceEmbedding.id)))).scalar()
        print(f"Total embeddings in DB: {count}")
        
        print("Inserting second document (1 record)...")
        records2 = [
            EmbeddingRecord(
                organization_id=org_id,
                run_id=run_uuid,
                company_name="Acme",
                source_type=EmbeddingSourceType.ANALYSIS,
                source_id="snap_1",
                chunk_type=ChunkType.EXECUTIVE_BRIEFING,
                chunk_order=3,
                chunk_text="Test Chunk 3",
                embedding_model="test-model",
                embedding=[0.3] * 384,
                content_hash="verify_hash_3",
                analyzed_at=datetime.now(timezone.utc)
            )
        ]
        inserted2 = await repo.save_embeddings(session, records2)
        await session.commit()
        print(f"Inserted rows (new): {inserted2}")
        
        count_after = (await session.execute(select(func.count(IntelligenceEmbedding.id)))).scalar()
        print(f"Total embeddings in DB after new record: {count_after}")

if __name__ == "__main__":
    asyncio.run(main())
