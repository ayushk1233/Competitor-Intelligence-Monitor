import pytest
import uuid
from datetime import datetime, timezone
from backend.memory.retrieval import RetrievedMemory
from backend.database.models import EmbeddingSourceType, ChunkType
from backend.memory.service import MemoryService
from backend.memory.models import MemorySearchResult

class MockProvider:
    async def embed_documents(self, texts):
        # return a mock embedding for each text
        return [[0.1] * 384 for _ in texts]

class MockRepository:
    def __init__(self, mock_chunks):
        self.mock_chunks = mock_chunks
        
    async def similarity_search(self, query_embedding, limit):
        return self.mock_chunks[:limit]
        
    async def similarity_search_company(self, company_name, query_embedding, limit):
        return [c for c in self.mock_chunks if c.company_name == company_name][:limit]
        
    async def similarity_search_timerange(self, company_name, start_date, end_date, query_embedding, limit):
        return [
            c for c in self.mock_chunks 
            if c.company_name == company_name and start_date <= c.analyzed_at <= end_date
        ][:limit]

@pytest.fixture
def mock_chunks():
    base_time = datetime(2026, 7, 1, tzinfo=timezone.utc)
    return [
        # Run A chunks (Anthropic)
        RetrievedMemory(
            company_name="Anthropic",
            chunk_text="Anthropic exec briefing",
            similarity_score=0.1,
            source_type=EmbeddingSourceType.ANALYSIS,
            chunk_type=ChunkType.EXECUTIVE_BRIEFING,
            run_id="run_a",
            analyzed_at=base_time,
            embedding_model="mock"
        ),
        RetrievedMemory(
            company_name="Anthropic",
            chunk_text="Anthropic structured summary",
            similarity_score=0.2,
            source_type=EmbeddingSourceType.ANALYSIS,
            chunk_type=ChunkType.STRUCTURED_SUMMARIES,
            run_id="run_a",
            analyzed_at=base_time,
            embedding_model="mock"
        ),
        # Run B chunks (OpenAI)
        RetrievedMemory(
            company_name="OpenAI",
            chunk_text="OpenAI exec briefing",
            similarity_score=0.15,
            source_type=EmbeddingSourceType.ANALYSIS,
            chunk_type=ChunkType.EXECUTIVE_BRIEFING,
            run_id="run_b",
            analyzed_at=base_time,
            embedding_model="mock"
        )
    ]

@pytest.mark.asyncio
async def test_search_grouping(mock_chunks):
    service = MemoryService(MockProvider(), MockRepository(mock_chunks))
    
    result = await service.search("AI pricing", limit=2)
    
    assert isinstance(result, MemorySearchResult)
    assert result.query == "AI pricing"
    assert result.retrieved_chunks == 3
    assert len(result.analyses) == 2
    
    # Sort order: run_a has min distance 0.1, run_b has min distance 0.15
    assert result.analyses[0].run_id == "run_a"
    assert result.analyses[1].run_id == "run_b"
    
    assert result.analyses[0].similarity_score == 0.1
    assert result.analyses[0].executive_briefing == "Anthropic exec briefing"
    assert result.analyses[0].structured_summary == "Anthropic structured summary"
    assert len(result.analyses[0].supporting_chunks) == 2
    
    assert result.analyses[1].similarity_score == 0.15
    assert result.analyses[1].executive_briefing == "OpenAI exec briefing"
    assert len(result.analyses[1].supporting_chunks) == 1

@pytest.mark.asyncio
async def test_search_company(mock_chunks):
    service = MemoryService(MockProvider(), MockRepository(mock_chunks))
    
    result = await service.search_company("OpenAI", "AI pricing", limit=5)
    
    assert len(result.analyses) == 1
    assert result.analyses[0].run_id == "run_b"

@pytest.mark.asyncio
async def test_search_limit(mock_chunks):
    service = MemoryService(MockProvider(), MockRepository(mock_chunks))
    
    # Even though chunks cover 2 runs, limit=1 should return 1 analysis
    result = await service.search("AI pricing", limit=1)
    
    assert len(result.analyses) == 1
    assert result.analyses[0].run_id == "run_a"
