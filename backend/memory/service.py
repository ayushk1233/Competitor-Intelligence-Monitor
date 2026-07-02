import time
from typing import Sequence, Optional
from datetime import datetime

from backend.memory.interfaces import EmbeddingProvider
from backend.memory.retrieval import RetrievalRepository, RetrievedMemory
from backend.memory.models import RetrievedAnalysis, MemorySearchResult, TimelineEvent, CompanyTimeline
from backend.database.models import ChunkType

class MemoryService:
    """
    Public API for the Historical Intelligence Memory.
    Hides embedding generation, vector search, and chunk-level storage behind a clean domain-oriented interface.
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
        repository: RetrievalRepository,
    ):
        self.provider = provider
        self.repository = repository

    def _group_chunks(self, chunks: Sequence[RetrievedMemory]) -> list[RetrievedAnalysis]:
        """
        Groups chunks by run_id, extracting summary fields and finding the strongest similarity score.
        """
        run_map = {}
        for chunk in chunks:
            if chunk.run_id not in run_map:
                run_map[chunk.run_id] = {
                    "run_id": chunk.run_id,
                    "company_name": chunk.company_name,
                    "analyzed_at": chunk.analyzed_at,
                    # Initialize with the chunk's score
                    "similarity_score": chunk.similarity_score,
                    "executive_briefing": None,
                    "structured_summary": None,
                    "supporting_chunks": []
                }
            
            run_data = run_map[chunk.run_id]
            # Since pgvector uses cosine_distance (lower is more similar), we take the minimum distance.
            # "The strongest supporting chunk should determine ranking."
            run_data["similarity_score"] = min(run_data["similarity_score"], chunk.similarity_score)
            run_data["supporting_chunks"].append(chunk)
            
            # Extract main summaries if they exist in the chunk type
            if chunk.chunk_type == ChunkType.EXECUTIVE_BRIEFING:
                if not run_data["executive_briefing"]:
                    run_data["executive_briefing"] = chunk.chunk_text
                else:
                    run_data["executive_briefing"] += "\n\n" + chunk.chunk_text
            elif chunk.chunk_type == ChunkType.STRUCTURED_SUMMARIES:
                if not run_data["structured_summary"]:
                    run_data["structured_summary"] = chunk.chunk_text
                else:
                    run_data["structured_summary"] += "\n\n" + chunk.chunk_text

        # Sort the grouped analyses by their strongest chunk's similarity score
        analyses = [RetrievedAnalysis(**data) for data in run_map.values()]
        analyses.sort(key=lambda x: x.similarity_score)
        return analyses

    async def search(self, query: str, *, limit: int = 5) -> MemorySearchResult:
        start_time = time.perf_counter()
        
        # Embed the search query
        embeddings = await self.provider.embed_documents([query])
        query_embedding = embeddings[0]
        
        # Retrieve chunks (fetch more chunks to group into `limit` analyses)
        # Assuming an analysis has 4-6 chunks on average, fetching limit * 5 gives enough candidates
        chunks = await self.repository.similarity_search(
            query_embedding=query_embedding, 
            limit=max(50, limit * 10)
        )
        
        # Group chunks into analyses
        analyses = self._group_chunks(chunks)
        
        # Limit to requested number of analyses
        analyses = analyses[:limit]
        
        runtime_ms = (time.perf_counter() - start_time) * 1000
        
        return MemorySearchResult(
            query=query,
            analyses=analyses,
            retrieved_chunks=len(chunks),
            runtime_ms=runtime_ms
        )

    async def search_company(self, company_name: str, query: str, *, limit: int = 5) -> MemorySearchResult:
        start_time = time.perf_counter()
        
        embeddings = await self.provider.embed_documents([query])
        query_embedding = embeddings[0]
        
        chunks = await self.repository.similarity_search_company(
            company_name=company_name, 
            query_embedding=query_embedding, 
            limit=max(50, limit * 10)
        )
        
        analyses = self._group_chunks(chunks)
        analyses = analyses[:limit]
        
        runtime_ms = (time.perf_counter() - start_time) * 1000
        
        return MemorySearchResult(
            query=query,
            analyses=analyses,
            retrieved_chunks=len(chunks),
            runtime_ms=runtime_ms
        )

    async def search_timerange(self, company_name: str, start_date: datetime, end_date: datetime, query: str, *, limit: int = 5) -> MemorySearchResult:
        start_time = time.perf_counter()
        
        embeddings = await self.provider.embed_documents([query])
        query_embedding = embeddings[0]
        
        chunks = await self.repository.similarity_search_timerange(
            company_name=company_name, 
            start_date=start_date, 
            end_date=end_date, 
            query_embedding=query_embedding, 
            limit=max(50, limit * 10)
        )
        
        analyses = self._group_chunks(chunks)
        analyses = analyses[:limit]
        
        runtime_ms = (time.perf_counter() - start_time) * 1000
        
        return MemorySearchResult(
            query=query,
            analyses=analyses,
            retrieved_chunks=len(chunks),
            runtime_ms=runtime_ms
        )

    def _group_events(self, chunks: Sequence[RetrievedMemory]) -> list[TimelineEvent]:
        """
        Groups chunks by run_id for chronological timelines.
        """
        run_map = {}
        for chunk in chunks:
            if chunk.run_id not in run_map:
                run_map[chunk.run_id] = {
                    "run_id": chunk.run_id,
                    "company_name": chunk.company_name,
                    "analyzed_at": chunk.analyzed_at,
                    "executive_briefing": None,
                    "structured_summary": None,
                    "supporting_chunks": []
                }
            
            run_data = run_map[chunk.run_id]
            run_data["supporting_chunks"].append(chunk)
            
            if chunk.chunk_type == ChunkType.EXECUTIVE_BRIEFING:
                if not run_data["executive_briefing"]:
                    run_data["executive_briefing"] = chunk.chunk_text
                else:
                    run_data["executive_briefing"] += "\n\n" + chunk.chunk_text
            elif chunk.chunk_type == ChunkType.STRUCTURED_SUMMARIES:
                if not run_data["structured_summary"]:
                    run_data["structured_summary"] = chunk.chunk_text
                else:
                    run_data["structured_summary"] += "\n\n" + chunk.chunk_text

        # Sort the grouped events chronologically
        events = [TimelineEvent(**data) for data in run_map.values()]
        events.sort(key=lambda x: x.analyzed_at)
        return events

    async def timeline(self, company_name: str) -> CompanyTimeline:
        """
        Retrieves the canonical historical timeline for a company.
        """
        chunks = await self.repository.company_history(company_name)
        events = self._group_events(chunks)
        
        if not events:
            return CompanyTimeline(
                company_name=company_name,
                events=[],
                first_seen=datetime.now(),
                latest_seen=datetime.now(),
                total_events=0
            )
            
        return CompanyTimeline(
            company_name=company_name,
            events=events,
            first_seen=events[0].analyzed_at,
            latest_seen=events[-1].analyzed_at,
            total_events=len(events)
        )

    async def latest(self, company_name: str) -> Optional[TimelineEvent]:
        """
        Helper method to retrieve the most recent historical analysis event.
        """
        timeline_obj = await self.timeline(company_name)
        if not timeline_obj.events:
            return None
        return timeline_obj.events[-1]

    async def previous(self, company_name: str) -> Optional[TimelineEvent]:
        """
        Helper method to retrieve the second most recent historical analysis event.
        """
        timeline_obj = await self.timeline(company_name)
        if len(timeline_obj.events) < 2:
            return None
        return timeline_obj.events[-2]
