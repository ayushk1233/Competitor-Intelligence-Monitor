import asyncio
from backend.database.connection import AsyncSessionLocal
from backend.memory.retrieval import RetrievalRepository
from backend.memory.providers.factory import ProviderFactory
from backend.memory.service import MemoryService

async def main():
    async with AsyncSessionLocal() as session:
        repo = RetrievalRepository(session)
        provider = ProviderFactory.create()
        service = MemoryService(provider, repo)
        
        print("\n--- Verification 1: Search Anthropic pricing ---")
        result = await service.search("What changed in Anthropic pricing?", limit=5)
        print(f"Total analyses returned: {len(result.analyses)}")
        print(f"Total chunks retrieved: {result.retrieved_chunks}")
        print(f"Runtime: {result.runtime_ms:.2f}ms")
        
        for i, analysis in enumerate(result.analyses):
            print(f"\n[{i+1}] Run ID: {analysis.run_id} | Company: {analysis.company_name} | Score: {analysis.similarity_score:.4f}")
            print(f"Supporting chunks count: {len(analysis.supporting_chunks)}")
            if analysis.executive_briefing:
                print(f"Exec Briefing length: {len(analysis.executive_briefing)}")
            if analysis.structured_summary:
                print(f"Structured Summary length: {len(analysis.structured_summary)}")
                
        print("\n--- Verification 4: Grouping check ---")
        run_ids = [a.run_id for a in result.analyses]
        if len(run_ids) == len(set(run_ids)):
            print("Grouping SUCCESS: run_id appears only once per analysis.")
        else:
            print("Grouping FAILED: duplicate run_ids found!")

if __name__ == "__main__":
    asyncio.run(main())
