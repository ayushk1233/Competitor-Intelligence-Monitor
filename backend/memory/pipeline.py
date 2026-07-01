import time
from typing import Sequence
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.memory.document import MemoryDocument
from backend.memory.embedding import EmbeddingService
from backend.memory.repository import EmbeddingRepository


class IngestionResult(BaseModel):
    processed_documents: int
    processed_chunks: int
    inserted_chunks: int
    skipped_duplicates: int
    embedding_model: str
    runtime_ms: float


class MemoryIngestionPipeline:
    """
    Orchestrates the ingestion of MemoryDocuments into the database.
    Coordinates between EmbeddingService and EmbeddingRepository.
    """

    def __init__(self, embedding_service: EmbeddingService, repository: EmbeddingRepository):
        self.embedding_service = embedding_service
        self.repository = repository

    async def ingest_many(
        self,
        documents: Sequence[MemoryDocument],
        session: AsyncSession,
    ) -> IngestionResult:
        if not documents:
            return IngestionResult(
                processed_documents=0,
                processed_chunks=0,
                inserted_chunks=0,
                skipped_duplicates=0,
                embedding_model="none",
                runtime_ms=0.0
            )

        start_time = time.monotonic()
        all_records = []
        
        # We can determine the model from the service's provider
        embedding_model = self.embedding_service.provider.model_name
        
        for doc in documents:
            records = await self.embedding_service.generate_embeddings(doc)
            all_records.extend(records)
            
        inserted_chunks = 0
        if all_records:
            inserted_chunks = await self.repository.save_embeddings(session, all_records)
            
        end_time = time.monotonic()
        runtime_ms = (end_time - start_time) * 1000.0
        
        return IngestionResult(
            processed_documents=len(documents),
            processed_chunks=len(all_records),
            inserted_chunks=inserted_chunks,
            skipped_duplicates=len(all_records) - inserted_chunks,
            embedding_model=embedding_model,
            runtime_ms=runtime_ms
        )

    async def ingest(
        self,
        document: MemoryDocument,
        session: AsyncSession,
    ) -> IngestionResult:
        return await self.ingest_many([document], session)
