import pytest
import uuid
from datetime import datetime, timezone, timedelta
from backend.memory.retrieval import RetrievalRepository, RetrievedMemory
from backend.memory.document import EmbeddingSourceType, ChunkType

class MockResult:
    def __init__(self, items, is_scalar=False):
        self._items = items
        self._is_scalar = is_scalar
        
    def scalars(self):
        self._is_scalar = True
        return self
        
    def all(self):
        if self._is_scalar:
            # When testing chronological queries (company_history), it returns model instances directly
            return self._items
        return self._items
        
    def scalar_one_or_none(self):
        if not self._items:
            return None
        return self._items[0]

class MockSession:
    def __init__(self, expected_results=None):
        # expected_results can be a single list (returned for all queries) 
        # or a list of lists (returned in order)
        self.expected_results = expected_results or []
        self.stmts_executed = []
        self.call_count = 0

    async def execute(self, stmt):
        self.stmts_executed.append(stmt)
        if getattr(self.expected_results, '__iter__', False) and len(self.expected_results) > 0 and isinstance(self.expected_results[0], list):
            res = self.expected_results[self.call_count] if self.call_count < len(self.expected_results) else []
            self.call_count += 1
            return MockResult(res)
        return MockResult(self.expected_results)

class MockIntelligenceEmbedding:
    def __init__(self, company_name, chunk_text, chunk_order=0, analyzed_at=None):
        self.organization_id = uuid.uuid4()
        self.run_id = "run_1"
        self.company_name = company_name
        self.source_type = EmbeddingSourceType.ANALYSIS
        self.source_id = "snap_1"
        self.chunk_type = ChunkType.EXECUTIVE_BRIEFING
        self.chunk_order = chunk_order
        self.chunk_text = chunk_text
        self.embedding_model = "mock-model"
        self.embedding = [0.1] * 384
        self.content_hash = "mock_hash"
        self.analyzed_at = analyzed_at or datetime.now(timezone.utc)

@pytest.mark.asyncio
async def test_empty_db():
    session = MockSession()
    repo = RetrievalRepository(session)
    
    results = await repo.similarity_search(query_embedding=[0.1]*384)
    assert len(results) == 0
    assert len(session.stmts_executed) == 1

@pytest.mark.asyncio
async def test_similarity_search():
    # similarity_search returns tuples of (IntelligenceEmbedding, distance)
    mock_item = MockIntelligenceEmbedding("Acme", "Text 1")
    session = MockSession(expected_results=[(mock_item, 0.05)])
    repo = RetrievalRepository(session)
    
    results = await repo.similarity_search(query_embedding=[0.1]*384)
    
    assert len(results) == 1
    assert isinstance(results[0], RetrievedMemory)
    assert results[0].company_name == "Acme"
    assert results[0].chunk_text == "Text 1"
    assert results[0].similarity_score == 0.05

@pytest.mark.asyncio
async def test_similarity_search_company():
    mock_item = MockIntelligenceEmbedding("Cursor", "Cursor text")
    session = MockSession(expected_results=[(mock_item, 0.12)])
    repo = RetrievalRepository(session)
    
    results = await repo.similarity_search_company(company_name="Cursor", query_embedding=[0.1]*384)
    
    assert len(results) == 1
    assert results[0].company_name == "Cursor"
    assert results[0].chunk_text == "Cursor text"
    
@pytest.mark.asyncio
async def test_similarity_search_timerange():
    dt = datetime(2026, 1, 15, tzinfo=timezone.utc)
    mock_item = MockIntelligenceEmbedding("Cursor", "Cursor timerange", analyzed_at=dt)
    session = MockSession(expected_results=[(mock_item, 0.2)])
    repo = RetrievalRepository(session)
    
    start_date = dt - timedelta(days=1)
    end_date = dt + timedelta(days=1)
    results = await repo.similarity_search_timerange(
        company_name="Cursor",
        start_date=start_date,
        end_date=end_date,
        query_embedding=[0.1]*384
    )
    
    assert len(results) == 1
    assert results[0].analyzed_at == dt

@pytest.mark.asyncio
async def test_ordering_company_history():
    # company_history returns scalars (IntelligenceEmbedding directly)
    mock_items = [
        MockIntelligenceEmbedding("Cursor", "Text 1"),
        MockIntelligenceEmbedding("Cursor", "Text 2")
    ]
    session = MockSession(expected_results=mock_items)
    repo = RetrievalRepository(session)
    
    results = await repo.company_history("Cursor")
    
    assert len(results) == 2
    assert results[0].chunk_text == "Text 1"
    assert results[1].chunk_text == "Text 2"
    assert results[0].similarity_score == 0.0

@pytest.mark.asyncio
async def test_latest_memory():
    # latest_memory returns scalar_one_or_none
    mock_item = MockIntelligenceEmbedding("Cursor", "Latest text")
    session = MockSession(expected_results=[mock_item])
    repo = RetrievalRepository(session)
    
    result = await repo.latest_memory("Cursor")
    
    assert result is not None
    assert result.company_name == "Cursor"
    assert result.chunk_text == "Latest text"

@pytest.mark.asyncio
async def test_previous_memory():
    mock_item = MockIntelligenceEmbedding("Cursor", "Previous text")
    # First query expects a date, second query expects the IntelligenceEmbedding
    session = MockSession(expected_results=[
        [datetime.now(timezone.utc)],
        [mock_item]
    ])
    repo = RetrievalRepository(session)
    
    result = await repo.previous_memory("Cursor")
    
    assert result is not None
    assert result.company_name == "Cursor"
    assert result.chunk_text == "Previous text"

@pytest.mark.asyncio
async def test_latest_memory_none():
    session = MockSession(expected_results=[])
    repo = RetrievalRepository(session)
    
    result = await repo.latest_memory("Cursor")
    assert result is None
