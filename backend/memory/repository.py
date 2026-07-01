from typing import Sequence, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import IntelligenceEmbedding
from backend.memory.embedding import EmbeddingRecord


class EmbeddingRepository:
    """
    Repository for persisting Memory embeddings.
    """

    async def get_existing_hashes(
        self, session: AsyncSession, hashes: Sequence[str]
    ) -> Set[str]:
        """
        Return a set of content_hashes that already exist in the database
        from the provided sequence.
        """
        if not hashes:
            return set()

        stmt = select(IntelligenceEmbedding.content_hash).where(
            IntelligenceEmbedding.content_hash.in_(hashes)
        )
        result = await session.execute(stmt)
        return set(result.scalars().all())

    async def save_embeddings(
        self, session: AsyncSession, records: Sequence[EmbeddingRecord]
    ) -> int:
        """
        Save a batch of EmbeddingRecord domain objects to the database.
        Returns the number of rows successfully inserted.
        Skips records that already exist based on content_hash.
        """
        if not records:
            return 0

        hashes = [r.content_hash for r in records]
        existing_hashes = await self.get_existing_hashes(session, hashes)

        new_records = []
        seen_hashes = set(existing_hashes)
        for r in records:
            if r.content_hash not in seen_hashes:
                new_records.append(r)
                seen_hashes.add(r.content_hash)
                
        if not new_records:
            return 0

        # Convert domain objects to ORM models
        db_models = [
            IntelligenceEmbedding(
                organization_id=r.organization_id,
                run_id=r.run_id,
                company_name=r.company_name,
                source_type=r.source_type.value if hasattr(r.source_type, 'value') else r.source_type,
                source_id=r.source_id,
                chunk_type=r.chunk_type.value if hasattr(r.chunk_type, 'value') else r.chunk_type,
                chunk_order=r.chunk_order,
                chunk_text=r.chunk_text,
                embedding_model=r.embedding_model,
                embedding=r.embedding,
                content_hash=r.content_hash,
                analyzed_at=r.analyzed_at,
            )
            for r in new_records
        ]

        # Batch insert
        session.add_all(db_models)
        await session.flush()

        return len(new_records)
