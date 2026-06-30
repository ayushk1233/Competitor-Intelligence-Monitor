import pytest
import uuid
import asyncio
from datetime import datetime, timezone
from typing import List

from backend.memory.document import MemoryDocument, EmbeddingSourceType, ChunkType
from backend.memory.embedding import EmbeddingService, EmbeddingRecord
from backend.memory.interfaces import EmbeddingProvider
from backend.memory.exceptions import EmbeddingGenerationError
from backend.memory.constants import MAX_CHUNK_SIZE

class MockProvider(EmbeddingProvider):
    def __init__(self, should_fail=False):
        self._should_fail = should_fail
        
    @property
    def model_name(self) -> str:
        return "mock-model"
        
    @property
    def vector_dimension(self) -> int:
        return 384
        
    async def initialize(self) -> None:
        pass
        
    @property
    def is_initialized(self) -> bool:
        return True
        
    async def embed_query(self, text: str) -> List[float]:
        if self._should_fail:
            raise EmbeddingGenerationError("Mock failure")
        return [0.1] * 384
        
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self._should_fail:
            raise EmbeddingGenerationError("Mock failure")
        return [[0.1] * 384 for _ in texts]
        
    async def health_check(self) -> bool:
        return True


@pytest.fixture
def base_doc():
    return MemoryDocument(
        organization_id=uuid.uuid4(),
        run_id="run_1",
        company_name="TestCorp",
        source_type=EmbeddingSourceType.ANALYSIS,
        source_id="snap_1",
        chunk_type=ChunkType.EXECUTIVE_BRIEFING,
        text="This is a test document.",
        analyzed_at=datetime.now(timezone.utc),
        metadata={}
    )

@pytest.mark.asyncio
async def test_single_document_embedding(base_doc):
    service = EmbeddingService(MockProvider())
    records = await service.generate_embeddings(base_doc)
    
    assert len(records) == 1
    assert records[0].chunk_text == "This is a test document."
    assert records[0].embedding_model == "mock-model"
    assert len(records[0].embedding) == 384
    assert records[0].chunk_order == 0

@pytest.mark.asyncio
async def test_multi_chunk_document_embedding(base_doc):
    sentence = "This is a single sentence that is relatively short. "
    num_sentences = (MAX_CHUNK_SIZE // len(sentence)) + 5
    base_doc.text = sentence * num_sentences
    
    service = EmbeddingService(MockProvider())
    records = await service.generate_embeddings(base_doc)
    
    assert len(records) > 1
    assert all(len(r.embedding) == 384 for r in records)
    assert records[0].chunk_order == 0
    assert records[-1].chunk_order == len(records) - 1

@pytest.mark.asyncio
async def test_deterministic_content_hash(base_doc):
    service = EmbeddingService(MockProvider())
    records1 = await service.generate_embeddings(base_doc)
    records2 = await service.generate_embeddings(base_doc)
    
    assert records1[0].content_hash == records2[0].content_hash

@pytest.mark.asyncio
async def test_propagation_of_provider_errors(base_doc):
    service = EmbeddingService(MockProvider(should_fail=True))
    with pytest.raises(EmbeddingGenerationError):
        await service.generate_embeddings(base_doc)
