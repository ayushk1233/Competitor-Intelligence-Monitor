import hashlib
from typing import List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from backend.memory.document import MemoryDocument, EmbeddingSourceType, ChunkType
from backend.memory.chunking import ChunkingService
from backend.memory.interfaces import EmbeddingProvider
from backend.memory.constants import CONTENT_HASH_ALGORITHM, MAX_BATCH_SIZE

class EmbeddingRecord(BaseModel):
    organization_id: UUID
    run_id: str
    company_name: str
    source_type: EmbeddingSourceType
    source_id: str
    chunk_type: ChunkType
    chunk_order: int
    chunk_text: str
    embedding_model: str
    embedding: List[float]
    content_hash: str
    analyzed_at: datetime


class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider
        
    @staticmethod
    def _generate_hash(text: str) -> str:
        h = hashlib.new(CONTENT_HASH_ALGORITHM)
        h.update(text.encode('utf-8'))
        return h.hexdigest()

    async def generate_embeddings(self, doc: MemoryDocument) -> List[EmbeddingRecord]:
        chunks = ChunkingService.chunk_document(doc)
        
        records = []
        for i in range(0, len(chunks), MAX_BATCH_SIZE):
            batch_chunks = chunks[i:i + MAX_BATCH_SIZE]
            texts = [c.chunk_text for c in batch_chunks]
            
            # The provider is expected to raise EmbeddingGenerationError on failure
            embeddings = await self.provider.embed_documents(texts)
            
            for chunk, emb in zip(batch_chunks, embeddings):
                content_hash = self._generate_hash(chunk.chunk_text)
                
                record = EmbeddingRecord(
                    organization_id=doc.organization_id,
                    run_id=doc.run_id,
                    company_name=doc.company_name,
                    source_type=doc.source_type,
                    source_id=doc.source_id,
                    chunk_type=chunk.chunk_type,
                    chunk_order=chunk.chunk_order,
                    chunk_text=chunk.chunk_text,
                    embedding_model=self.provider.model_name,
                    embedding=emb,
                    content_hash=content_hash,
                    analyzed_at=doc.analyzed_at
                )
                records.append(record)
                
        return records
