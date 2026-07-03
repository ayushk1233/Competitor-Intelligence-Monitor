import logging
import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.memory.models import CompanyTimeline, MemorySearchResult, TimelineEvent
from backend.memory.providers.factory import ProviderFactory
from backend.memory.retrieval import RetrievalRepository
from backend.memory.service import MemoryService

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])
logger = logging.getLogger(__name__)

async def get_memory_service(session: AsyncSession = Depends(get_db)) -> MemoryService:
    """Dependency for injecting MemoryService"""
    try:
        provider = ProviderFactory.create()
        repository = RetrievalRepository(session)
        return MemoryService(provider, repository)
    except Exception as e:
        logger.error(f"Failed to initialize MemoryService: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize intelligence service.")

@router.get("/search", response_model=MemorySearchResult)
async def search_memory(
    query: str = Query(..., description="The semantic search query"),
    company: Optional[str] = Query(None, description="Optional company filter"),
    start_date: Optional[datetime] = Query(None, description="Optional start date filter"),
    end_date: Optional[datetime] = Query(None, description="Optional end date filter"),
    limit: int = Query(5, ge=1, le=50, description="Max number of analyses to return"),
    service: MemoryService = Depends(get_memory_service)
):
    try:
        if company and start_date and end_date:
            result = await service.search_timerange(
                company_name=company,
                start_date=start_date,
                end_date=end_date,
                query=query,
                limit=limit
            )
        elif company:
            result = await service.search_company(
                company_name=company,
                query=query,
                limit=limit
            )
        else:
            result = await service.search(
                query=query,
                limit=limit
            )
        
        logger.info(
            "Search request completed",
            extra={
                "query": query,
                "company": company,
                "runtime_ms": result.runtime_ms,
                "retrieved_analyses": len(result.analyses)
            }
        )
        return result
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while searching memory.")

@router.get("/timeline/{company}", response_model=CompanyTimeline)
async def company_timeline(
    company: str,
    service: MemoryService = Depends(get_memory_service)
):
    try:
        start_time = time.perf_counter()
        timeline = await service.timeline(company)
        runtime_ms = (time.perf_counter() - start_time) * 1000
        
        if not timeline.events:
            raise HTTPException(status_code=404, detail=f"No timeline found for company: {company}")
            
        logger.info(
            "Timeline request completed",
            extra={
                "company": company,
                "events": len(timeline.events),
                "runtime_ms": runtime_ms
            }
        )
        return timeline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Timeline generation failed: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the timeline.")

@router.get("/latest/{company}", response_model=TimelineEvent)
async def latest_analysis(
    company: str,
    service: MemoryService = Depends(get_memory_service)
):
    try:
        event = await service.latest(company)
        if not event:
            raise HTTPException(status_code=404, detail=f"No analyses found for company: {company}")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Latest memory failed: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving latest memory.")

@router.get("/previous/{company}", response_model=TimelineEvent)
async def previous_analysis(
    company: str,
    service: MemoryService = Depends(get_memory_service)
):
    try:
        event = await service.previous(company)
        if not event:
            raise HTTPException(status_code=404, detail=f"Previous analysis not found for company: {company}")
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Previous memory failed: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving previous memory.")
