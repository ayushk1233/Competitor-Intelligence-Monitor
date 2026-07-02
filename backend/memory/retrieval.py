from datetime import datetime
from typing import Sequence, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import IntelligenceEmbedding, EmbeddingSourceType, ChunkType


class RetrievedMemory(BaseModel):
    """
    Canonical retrieval object for memory queries.
    This model maps the domain concepts without leaking ORM details.
    """
    model_config = ConfigDict(from_attributes=True)

    company_name: str
    chunk_text: str
    similarity_score: float
    source_type: EmbeddingSourceType
    chunk_type: ChunkType
    run_id: str
    analyzed_at: datetime
    embedding_model: str


class RetrievalRepository:
    """
    Repository for the read-side of the Memory subsystem (CQRS).
    Handles all retrieval of IntelligenceEmbedding records.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def similarity_search(
        self,
        *,
        query_embedding: list[float],
        limit: int = 10,
    ) -> Sequence[RetrievedMemory]:
        """
        Perform a vector similarity search across all companies.
        """
        stmt = (
            select(
                IntelligenceEmbedding,
                IntelligenceEmbedding.embedding.cosine_distance(query_embedding).label("similarity_score")
            )
            .order_by(IntelligenceEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        
        memories = []
        for row in result.all():
            embedding_model = row[0]
            similarity_score = row[1]
            # Convert to distance score (0 means exactly same, smaller is better)
            # You might want to convert this to similarity score if similarity_score should be higher=better.
            # We'll map the cosine distance directly to similarity_score for now.
            memories.append(
                RetrievedMemory(
                    company_name=embedding_model.company_name,
                    chunk_text=embedding_model.chunk_text,
                    similarity_score=similarity_score,
                    source_type=embedding_model.source_type,
                    chunk_type=embedding_model.chunk_type,
                    run_id=embedding_model.run_id,
                    analyzed_at=embedding_model.analyzed_at,
                    embedding_model=embedding_model.embedding_model,
                )
            )
            
        return memories

    async def similarity_search_company(
        self,
        *,
        company_name: str,
        query_embedding: list[float],
        limit: int = 10,
    ) -> Sequence[RetrievedMemory]:
        """
        Perform a vector similarity search filtered by a specific company.
        """
        stmt = (
            select(
                IntelligenceEmbedding,
                IntelligenceEmbedding.embedding.cosine_distance(query_embedding).label("similarity_score")
            )
            .where(IntelligenceEmbedding.company_name == company_name)
            .order_by(IntelligenceEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        
        memories = []
        for row in result.all():
            embedding_model = row[0]
            similarity_score = row[1]
            memories.append(
                RetrievedMemory(
                    company_name=embedding_model.company_name,
                    chunk_text=embedding_model.chunk_text,
                    similarity_score=similarity_score,
                    source_type=embedding_model.source_type,
                    chunk_type=embedding_model.chunk_type,
                    run_id=embedding_model.run_id,
                    analyzed_at=embedding_model.analyzed_at,
                    embedding_model=embedding_model.embedding_model,
                )
            )
            
        return memories

    async def similarity_search_timerange(
        self,
        *,
        company_name: str,
        start_date: datetime,
        end_date: datetime,
        query_embedding: list[float],
        limit: int = 10,
    ) -> Sequence[RetrievedMemory]:
        """
        Perform a vector similarity search filtered by company and time range.
        """
        stmt = (
            select(
                IntelligenceEmbedding,
                IntelligenceEmbedding.embedding.cosine_distance(query_embedding).label("similarity_score")
            )
            .where(IntelligenceEmbedding.company_name == company_name)
            .where(IntelligenceEmbedding.analyzed_at.between(start_date, end_date))
            .order_by(IntelligenceEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        
        memories = []
        for row in result.all():
            embedding_model = row[0]
            similarity_score = row[1]
            memories.append(
                RetrievedMemory(
                    company_name=embedding_model.company_name,
                    chunk_text=embedding_model.chunk_text,
                    similarity_score=similarity_score,
                    source_type=embedding_model.source_type,
                    chunk_type=embedding_model.chunk_type,
                    run_id=embedding_model.run_id,
                    analyzed_at=embedding_model.analyzed_at,
                    embedding_model=embedding_model.embedding_model,
                )
            )
            
        return memories

    async def company_history(
        self,
        company_name: str,
    ) -> Sequence[RetrievedMemory]:
        """
        Retrieve all memory chunks for a specific company ordered chronologically.
        """
        stmt = (
            select(IntelligenceEmbedding)
            .where(IntelligenceEmbedding.company_name == company_name)
            .order_by(IntelligenceEmbedding.analyzed_at.asc(), IntelligenceEmbedding.chunk_order.asc())
        )
        
        result = await self.session.execute(stmt)
        
        memories = []
        for embedding_model in result.scalars().all():
            memories.append(
                RetrievedMemory(
                    company_name=embedding_model.company_name,
                    chunk_text=embedding_model.chunk_text,
                    similarity_score=0.0, # Not applicable for chronological retrieval
                    source_type=embedding_model.source_type,
                    chunk_type=embedding_model.chunk_type,
                    run_id=embedding_model.run_id,
                    analyzed_at=embedding_model.analyzed_at,
                    embedding_model=embedding_model.embedding_model,
                )
            )
            
        return memories

    async def latest_memory(
        self,
        company_name: str,
    ) -> Optional[RetrievedMemory]:
        """
        Retrieve the most recent memory chunk for a specific company.
        """
        stmt = (
            select(IntelligenceEmbedding)
            .where(IntelligenceEmbedding.company_name == company_name)
            .order_by(IntelligenceEmbedding.analyzed_at.desc(), IntelligenceEmbedding.chunk_order.asc())
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        embedding_model = result.scalar_one_or_none()
        
        if not embedding_model:
            return None
            
        return RetrievedMemory(
            company_name=embedding_model.company_name,
            chunk_text=embedding_model.chunk_text,
            similarity_score=0.0,
            source_type=embedding_model.source_type,
            chunk_type=embedding_model.chunk_type,
            run_id=embedding_model.run_id,
            analyzed_at=embedding_model.analyzed_at,
            embedding_model=embedding_model.embedding_model,
        )

    async def previous_memory(
        self,
        company_name: str,
    ) -> Optional[RetrievedMemory]:
        """
        Retrieve a memory chunk from the previous historical analysis (distinct run_id/analyzed_at).
        Useful for change detection (comparing latest with previous).
        """
        # First, find the latest analyzed_at
        latest_stmt = (
            select(IntelligenceEmbedding.analyzed_at)
            .where(IntelligenceEmbedding.company_name == company_name)
            .order_by(IntelligenceEmbedding.analyzed_at.desc())
            .limit(1)
        )
        latest_date = (await self.session.execute(latest_stmt)).scalar_one_or_none()
        
        if not latest_date:
            return None
            
        # Then, find the first chunk of the newest analysis before that date
        stmt = (
            select(IntelligenceEmbedding)
            .where(IntelligenceEmbedding.company_name == company_name)
            .where(IntelligenceEmbedding.analyzed_at < latest_date)
            .order_by(IntelligenceEmbedding.analyzed_at.desc(), IntelligenceEmbedding.chunk_order.asc())
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        embedding_model = result.scalar_one_or_none()
        
        if not embedding_model:
            return None
            
        return RetrievedMemory(
            company_name=embedding_model.company_name,
            chunk_text=embedding_model.chunk_text,
            similarity_score=0.0,
            source_type=embedding_model.source_type,
            chunk_type=embedding_model.chunk_type,
            run_id=embedding_model.run_id,
            analyzed_at=embedding_model.analyzed_at,
            embedding_model=embedding_model.embedding_model,
        )
