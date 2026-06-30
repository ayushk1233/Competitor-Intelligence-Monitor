import pytest
import uuid
import asyncio
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from backend.memory.repository import EmbeddingRepository
from backend.memory.embedding import EmbeddingRecord
from backend.memory.document import EmbeddingSourceType, ChunkType

class MockResult:
    def __init__(self, items):
        self._items = items
        
    def scalars(self):
        return self
        
    def all(self):
        return self._items

class MockSession:
    def __init__(self, existing_hashes=None, should_fail_flush=False):
        self.existing_hashes = existing_hashes or set()
        self.added = []
        self._should_fail_flush = should_fail_flush
        self.flushed = False

    async def execute(self, stmt):
        # We just extract the hashes the query looks for
        # In a real mock, we might inspect stmt, but for this simple test
        # we just return the intersection of existing_hashes.
        # This is enough to simulate the DB lookup.
        return MockResult(list(self.existing_hashes))

    def add_all(self, instances):
        self.added.extend(instances)

    async def flush(self):
        if self._should_fail_flush:
            raise IntegrityError("Mock rollback", orig=Exception(), params={})
        self.flushed = True


@pytest.fixture
def mock_records():
    return [
        EmbeddingRecord(
            organization_id=uuid.uuid4(),
            run_id="run_1",
            company_name="Acme",
            source_type=EmbeddingSourceType.ANALYSIS,
            source_id="snap_1",
            chunk_type=ChunkType.EXECUTIVE_BRIEFING,
            chunk_order=i,
            chunk_text=f"Text {i}",
            embedding_model="mock-model",
            embedding=[0.1] * 384,
            content_hash=f"hash_{i}",
            analyzed_at=datetime.now(timezone.utc)
        )
        for i in range(3)
    ]

@pytest.mark.asyncio
async def test_empty_batch():
    repo = EmbeddingRepository()
    session = MockSession()
    
    inserted = await repo.save_embeddings(session, [])
    assert inserted == 0
    assert len(session.added) == 0

@pytest.mark.asyncio
async def test_all_new_records(mock_records):
    repo = EmbeddingRepository()
    session = MockSession()
    
    inserted = await repo.save_embeddings(session, mock_records)
    assert inserted == 3
    assert len(session.added) == 3
    assert session.flushed

@pytest.mark.asyncio
async def test_partial_duplicates(mock_records):
    repo = EmbeddingRepository()
    # Simulate that hash_0 already exists in DB
    session = MockSession(existing_hashes={"hash_0"})
    
    inserted = await repo.save_embeddings(session, mock_records)
    assert inserted == 2 # hash_1 and hash_2
    assert len(session.added) == 2
    assert session.flushed
    # Verify the correct ones were added
    added_hashes = {m.content_hash for m in session.added}
    assert "hash_1" in added_hashes
    assert "hash_2" in added_hashes
    assert "hash_0" not in added_hashes

@pytest.mark.asyncio
async def test_all_duplicate_hashes(mock_records):
    repo = EmbeddingRepository()
    session = MockSession(existing_hashes={"hash_0", "hash_1", "hash_2"})
    
    inserted = await repo.save_embeddings(session, mock_records)
    assert inserted == 0
    assert len(session.added) == 0
    assert not session.flushed # No flush needed if nothing added

@pytest.mark.asyncio
async def test_transaction_rollback(mock_records):
    repo = EmbeddingRepository()
    session = MockSession(should_fail_flush=True)
    
    with pytest.raises(IntegrityError):
        await repo.save_embeddings(session, mock_records)
        
    assert not session.flushed
