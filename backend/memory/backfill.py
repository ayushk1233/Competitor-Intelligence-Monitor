import time
import uuid
import logging
from typing import Sequence
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import CompetitorAnalysisRecord, ComparisonRecord, Run, User
from backend.models.schemas import CompetitorAnalysis, ComparisonResult as SchemaComparisonResult
from backend.memory.factory import MemoryDocumentFactory
from backend.memory.pipeline import MemoryIngestionPipeline

logger = logging.getLogger(__name__)

class BackfillResult(BaseModel):
    analyses_processed: int = 0
    comparisons_processed: int = 0
    documents_generated: int = 0
    chunks_inserted: int = 0
    duplicates_skipped: int = 0
    failures: int = 0
    runtime_ms: float = 0.0

class HistoricalBackfillService:
    def __init__(self, pipeline: MemoryIngestionPipeline):
        self.pipeline = pipeline
        self.default_org_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    async def backfill(
        self,
        session: AsyncSession,
        *,
        batch_size: int = 50,
        resume: bool = True,
    ) -> BackfillResult:
        start_time = time.time()
        result = BackfillResult()
        
        # 1. Backfill CompetitorAnalysisRecords
        last_id = 0
        while True:
            # Join with Run and User to get the organization_id
            query = select(CompetitorAnalysisRecord, User.organization_id).join(
                Run, CompetitorAnalysisRecord.run_id == Run.id
            ).outerjoin(
                User, Run.user_id == User.id
            ).where(
                CompetitorAnalysisRecord.id > last_id
            ).order_by(CompetitorAnalysisRecord.id).limit(batch_size)
            
            rows = (await session.execute(query)).all()
            if not rows:
                break
                
            documents = []
            for record, org_id in rows:
                last_id = record.id
                try:
                    if not record.full_analysis:
                        continue
                        
                    if resume:
                        from backend.database.models import IntelligenceEmbedding
                        # Check if any embedding exists for this run_id
                        exists_query = select(IntelligenceEmbedding.id).where(IntelligenceEmbedding.run_id == record.run_id).limit(1)
                        exists = (await session.execute(exists_query)).scalar_one_or_none()
                        if exists:
                            result.analyses_processed += 1
                            continue

                    org_uuid = org_id if org_id else self.default_org_id
                    schema_obj = CompetitorAnalysis.model_validate(record.full_analysis)
                    
                    docs = MemoryDocumentFactory.from_competitor_analysis(
                        analysis=schema_obj,
                        organization_id=org_uuid,
                        run_id=record.run_id,
                        analyzed_at=record.created_at
                    )
                    documents.extend(docs)
                    result.analyses_processed += 1
                except Exception as e:
                    logger.error(f"Failed to process CompetitorAnalysisRecord {record.id}: {e}")
                    result.failures += 1
                
            if documents:
                try:
                    ingest_res = await self.pipeline.ingest_many(documents, session)
                    result.documents_generated += len(documents)
                    result.chunks_inserted += ingest_res.inserted_chunks
                    result.duplicates_skipped += ingest_res.skipped_duplicates
                    await session.commit()
                except Exception as e:
                    logger.error(f"Failed to ingest batch of analyses ending at id {last_id}: {e}")
                    await session.rollback()
                    result.failures += 1
                    # Continue despite batch failure to allow partial backfills
                    
        # 2. Backfill ComparisonRecords
        last_id = 0
        while True:
            query = select(ComparisonRecord, User.organization_id).join(
                Run, ComparisonRecord.run_id == Run.id
            ).outerjoin(
                User, Run.user_id == User.id
            ).where(
                ComparisonRecord.id > last_id
            ).order_by(ComparisonRecord.id).limit(batch_size)
            
            rows = (await session.execute(query)).all()
            if not rows:
                break
                
            documents = []
            for record, org_id in rows:
                last_id = record.id
                try:
                    if not record.full_comparison:
                        continue

                    if resume:
                        from backend.database.models import IntelligenceEmbedding
                        # Check if any embedding exists for this run_id
                        exists_query = select(IntelligenceEmbedding.id).where(IntelligenceEmbedding.run_id == record.run_id).limit(1)
                        exists = (await session.execute(exists_query)).scalar_one_or_none()
                        if exists:
                            result.comparisons_processed += 1
                            continue

                    org_uuid = org_id if org_id else self.default_org_id
                    schema_obj = SchemaComparisonResult.model_validate(record.full_comparison)
                    
                    docs = MemoryDocumentFactory.from_comparison_result(
                        comparison=schema_obj,
                        organization_id=org_uuid,
                        run_id=record.run_id,
                        analyzed_at=record.created_at
                    )
                    documents.extend(docs)
                    result.comparisons_processed += 1
                except Exception as e:
                    logger.error(f"Failed to process ComparisonRecord {record.id}: {e}")
                    result.failures += 1
                
            if documents:
                try:
                    ingest_res = await self.pipeline.ingest_many(documents, session)
                    result.documents_generated += len(documents)
                    result.chunks_inserted += ingest_res.inserted_chunks
                    result.duplicates_skipped += ingest_res.skipped_duplicates
                    await session.commit()
                except Exception as e:
                    logger.error(f"Failed to ingest batch of comparisons ending at id {last_id}: {e}")
                    await session.rollback()
                    result.failures += 1
                    
        result.runtime_ms = (time.time() - start_time) * 1000
        return result
