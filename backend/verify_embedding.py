import uuid
import asyncio
from datetime import datetime, timezone

from backend.memory.document import MemoryDocument, EmbeddingSourceType, ChunkType
from backend.memory.embedding import EmbeddingService
from backend.memory.providers.factory import ProviderFactory

async def main():
    text = (
        "This is the first sentence of the document. "
        "It contains some general introduction. "
        "The ChunkingService should be able to split this text into multiple chunks when it gets long enough. "
        "Let's add some more text to ensure we hit the chunk limit. "
        "Competitor Intel is building a new AI memory layer. "
        "The architecture is modular and uses pgvector. "
        "By enforcing deterministic chunking, we ensure consistent retrieval. "
        "We also preserve sentence boundaries for better semantic meaning. "
        "Overlap prevents context from being lost between chunks. "
        "This is essential for high-quality RAG applications. "
    ) * 10
    
    doc = MemoryDocument(
        organization_id=uuid.uuid4(),
        run_id="run_2026",
        company_name="Acme Corp",
        source_type=EmbeddingSourceType.ANALYSIS_RECORD,
        source_id="analysis_1",
        chunk_type=ChunkType.TEXT,
        text=text,
        analyzed_at=datetime.now(timezone.utc),
        metadata={"version": 1}
    )
    
    provider = ProviderFactory.create()
    await provider.initialize()
    service = EmbeddingService(provider)
    
    records1 = await service.generate_embeddings(doc)
    
    print("len(records):", len(records1))
    if len(records1) > 0:
        print("records[0].embedding_model:", records1[0].embedding_model)
        print("len(records[0].embedding):", len(records1[0].embedding))
    
    records2 = await service.generate_embeddings(doc)
    
    print("records1[0].content_hash:", records1[0].content_hash)
    print("records2[0].content_hash:", records2[0].content_hash)
    print("Hashes match:", records1[0].content_hash == records2[0].content_hash)

if __name__ == "__main__":
    asyncio.run(main())
