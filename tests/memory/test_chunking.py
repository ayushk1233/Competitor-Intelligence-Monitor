import pytest
import uuid
from datetime import datetime, timezone

from backend.memory.document import MemoryDocument, EmbeddingSourceType, ChunkType
from backend.memory.chunking import ChunkingService
from backend.memory.constants import MAX_CHUNK_SIZE, CHUNK_OVERLAP
from backend.memory.exceptions import ChunkingError

@pytest.fixture
def base_doc():
    return MemoryDocument(
        organization_id=uuid.uuid4(),
        run_id="run_1",
        company_name="TestCorp",
        source_type=EmbeddingSourceType.PAGE_SNAPSHOT,
        source_id="snap_1",
        chunk_type=ChunkType.TEXT,
        text="",
        analyzed_at=datetime.now(timezone.utc),
        metadata={}
    )

def test_empty_input(base_doc):
    base_doc.text = ""
    with pytest.raises(ChunkingError):
        ChunkingService.chunk_document(base_doc)

    base_doc.text = "   \n  \t "
    with pytest.raises(ChunkingError):
        ChunkingService.chunk_document(base_doc)

def test_single_short_document(base_doc):
    base_doc.text = "This is a short test document. It only has a few sentences."
    chunks = ChunkingService.chunk_document(base_doc)
    assert len(chunks) == 1
    assert chunks[0].chunk_text == "This is a short test document. It only has a few sentences."
    assert chunks[0].chunk_order == 0

def test_multi_paragraph_document(base_doc):
    # Generate a long text exceeding MAX_CHUNK_SIZE
    sentence = "This is a single sentence that is relatively short. "
    num_sentences = (MAX_CHUNK_SIZE // len(sentence)) + 5
    base_doc.text = sentence * num_sentences
    
    chunks = ChunkingService.chunk_document(base_doc)
    assert len(chunks) > 1
    
    # Check max size constraint
    for chunk in chunks:
        assert len(chunk.chunk_text) <= MAX_CHUNK_SIZE
        
    # Check sequential ordering
    orders = [c.chunk_order for c in chunks]
    assert orders == list(range(len(chunks)))

def test_overlap_preservation(base_doc):
    # Create sentences of exact length to test overlap logic
    sentences = [
        "A" * 500 + ".", 
        "B" * 50 + ".", 
        "B2" * 25 + ".", # B + B2 = 51 + 51 = 102 <= 120 overlap
        "C" * 200 + ".", 
        "D" * 200 + "."
    ]
    base_doc.text = " ".join(sentences)
    chunks = ChunkingService.chunk_document(base_doc)
    
    assert len(chunks) == 2
    assert "B" * 50 + "." in chunks[0].chunk_text
    assert "B" * 50 + "." in chunks[1].chunk_text # Overlap preservation
    
def test_oversized_sentence(base_doc):
    base_doc.text = "A" * (MAX_CHUNK_SIZE + 200) + "."
    chunks = ChunkingService.chunk_document(base_doc)
    assert len(chunks) == 2
    assert len(chunks[0].chunk_text) == MAX_CHUNK_SIZE
    
def test_deterministic_output(base_doc):
    sentence = "This is a test sentence for deterministic output checking. "
    base_doc.text = sentence * 50
    chunks1 = ChunkingService.chunk_document(base_doc)
    chunks2 = ChunkingService.chunk_document(base_doc)
    
    for c1, c2 in zip(chunks1, chunks2):
        assert c1.chunk_text == c2.chunk_text
        assert c1.chunk_order == c2.chunk_order
