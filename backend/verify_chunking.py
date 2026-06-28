import uuid
from datetime import datetime, timezone

from backend.memory.document import MemoryDocument, EmbeddingSourceType, ChunkType
from backend.memory.chunking import ChunkingService

def main():
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
    
    chunks = ChunkingService.chunk_document(doc)
    
    print("len(chunks):", len(chunks))
    print("chunks[0].chunk_order:", chunks[0].chunk_order)
    print("chunks[-1].chunk_order:", chunks[-1].chunk_order)
    
    # Verify overlap visually or programmatically
    print("\nVerifying overlap:")
    if len(chunks) > 1:
        print("End of chunk 0:", repr(chunks[0].chunk_text[-120:]))
        print("Start of chunk 1:", repr(chunks[1].chunk_text[:120]))
        
if __name__ == "__main__":
    main()
