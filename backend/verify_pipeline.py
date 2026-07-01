import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select

from backend.database.connection import AsyncSessionLocal
from backend.database.models import Organization, Run
from backend.memory.document import MemoryDocument
from backend.database.models import EmbeddingSourceType, ChunkType
from backend.memory.embedding import EmbeddingService
from backend.memory.repository import EmbeddingRepository
from backend.memory.pipeline import MemoryIngestionPipeline
from backend.memory.providers.factory import ProviderFactory

async def main():
    async with AsyncSessionLocal() as session:
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
        
        doc1 = MemoryDocument(
            organization_id=org.id,
            run_id=run_uuid,
            company_name="PipelineCorp",
            source_type=EmbeddingSourceType.ANALYSIS,
            source_id="analysis_p1",
            chunk_type=ChunkType.EXECUTIVE_BRIEFING,
            text="First document text for pipeline verification." * 10,
            analyzed_at=datetime.now(timezone.utc),
            metadata={}
        )
        
        doc2 = MemoryDocument(
            organization_id=org.id,
            run_id=run_uuid,
            company_name="PipelineCorp",
            source_type=EmbeddingSourceType.ANALYSIS,
            source_id="analysis_p2",
            chunk_type=ChunkType.STRUCTURED_SUMMARIES,
            text="Second document text for pipeline verification." * 10,
            analyzed_at=datetime.now(timezone.utc),
            metadata={}
        )

        provider = ProviderFactory.create()
        await provider.initialize()
        service = EmbeddingService(provider)
        repo = EmbeddingRepository()
        pipeline = MemoryIngestionPipeline(service, repo)

        print("Ingesting two new documents...")
        result1 = await pipeline.ingest_many([doc1, doc2], session)
        await session.commit()
        
        print(f"processed_documents == {result1.processed_documents}")
        print(f"inserted_chunks > 0: {result1.inserted_chunks > 0} ({result1.inserted_chunks})")
        print(f"runtime_ms: {result1.runtime_ms:.2f} ms")
        
        print("\nIngesting the identical documents again...")
        result2 = await pipeline.ingest_many([doc1, doc2], session)
        await session.commit()
        
        print(f"skipped_duplicates > 0: {result2.skipped_duplicates > 0} ({result2.skipped_duplicates})")
        print(f"inserted_chunks == 0: {result2.inserted_chunks == 0}")

if __name__ == "__main__":
    asyncio.run(main())
