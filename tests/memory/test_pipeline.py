import pytest
import uuid
import asyncio
from datetime import datetime, timezone

from backend.memory.pipeline import MemoryIngestionPipeline
from backend.memory.document import MemoryDocument
from backend.database.models import EmbeddingSourceType, ChunkType
from backend.memory.embedding import EmbeddingRecord

class MockProvider:
    @property
    def model_name(self):
        return "mock-model"

class MockEmbeddingService:
    def __init__(self, fail=False):
        self.provider = MockProvider()
        self.fail = fail

    async def generate_embeddings(self, doc):
        if self.fail:
            raise Exception("Provider failure")
        return [
            EmbeddingRecord(
                organization_id=doc.organization_id,
                run_id=doc.run_id,
                company_name=doc.company_name,
                source_type=doc.source_type,
                source_id=doc.source_id,
                chunk_type=doc.chunk_type,
                chunk_order=i,
                chunk_text=f"Chunk {i} of {doc.source_id}",
                embedding_model="mock-model",
                embedding=[0.1] * 384,
                content_hash=f"hash_{doc.source_id}_{i}",
                analyzed_at=doc.analyzed_at
            )
            for i in range(2)  # Generates 2 chunks per doc
        ]

class MockEmbeddingRepository:
    def __init__(self, duplicates=0, fail=False):
        self.duplicates = duplicates
        self.fail = fail

    async def save_embeddings(self, session, records):
        if self.fail:
            raise Exception("Repository failure")
        return len(records) - self.duplicates

class MockSession:
    pass

@pytest.fixture
def sample_doc():
    return MemoryDocument(
        organization_id=uuid.uuid4(),
        run_id="run_1",
        company_name="Acme",
        source_type=EmbeddingSourceType.ANALYSIS,
        source_id="snap_1",
        chunk_type=ChunkType.EXECUTIVE_BRIEFING,
        text="A valid text.",
        analyzed_at=datetime.now(timezone.utc),
        metadata={}
    )

@pytest.mark.asyncio
async def test_single_document(sample_doc):
    pipeline = MemoryIngestionPipeline(
        MockEmbeddingService(),
        MockEmbeddingRepository()
    )
    result = await pipeline.ingest(sample_doc, MockSession())
    
    assert result.processed_documents == 1
    assert result.processed_chunks == 2
    assert result.inserted_chunks == 2
    assert result.skipped_duplicates == 0
    assert result.embedding_model == "mock-model"
    assert result.runtime_ms > 0

@pytest.mark.asyncio
async def test_multiple_documents(sample_doc):
    pipeline = MemoryIngestionPipeline(
        MockEmbeddingService(),
        MockEmbeddingRepository()
    )
    doc2 = sample_doc.model_copy(update={"source_id": "snap_2"})
    result = await pipeline.ingest_many([sample_doc, doc2], MockSession())
    
    assert result.processed_documents == 2
    assert result.processed_chunks == 4
    assert result.inserted_chunks == 4
    assert result.skipped_duplicates == 0

@pytest.mark.asyncio
async def test_duplicate_chunks(sample_doc):
    # Repository reports that 1 chunk was a duplicate
    pipeline = MemoryIngestionPipeline(
        MockEmbeddingService(),
        MockEmbeddingRepository(duplicates=1)
    )
    result = await pipeline.ingest(sample_doc, MockSession())
    
    assert result.processed_chunks == 2
    assert result.inserted_chunks == 1
    assert result.skipped_duplicates == 1

@pytest.mark.asyncio
async def test_repository_failure(sample_doc):
    pipeline = MemoryIngestionPipeline(
        MockEmbeddingService(),
        MockEmbeddingRepository(fail=True)
    )
    with pytest.raises(Exception, match="Repository failure"):
        await pipeline.ingest(sample_doc, MockSession())

@pytest.mark.asyncio
async def test_provider_failure(sample_doc):
    pipeline = MemoryIngestionPipeline(
        MockEmbeddingService(fail=True),
        MockEmbeddingRepository()
    )
    with pytest.raises(Exception, match="Provider failure"):
        await pipeline.ingest(sample_doc, MockSession())

@pytest.mark.asyncio
async def test_empty_input():
    pipeline = MemoryIngestionPipeline(
        MockEmbeddingService(),
        MockEmbeddingRepository()
    )
    result = await pipeline.ingest_many([], MockSession())
    
    assert result.processed_documents == 0
    assert result.processed_chunks == 0
    assert result.inserted_chunks == 0
    assert result.runtime_ms == 0.0
