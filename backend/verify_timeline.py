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
        
        company = "Anthropic"
        print(f"\n--- Verification: Timeline Builder for {company} ---")
        
        timeline = await service.timeline(company)
        print(f"Total events: {timeline.total_events}")
        if timeline.events:
            print(f"First seen: {timeline.first_seen}")
            print(f"Latest seen: {timeline.latest_seen}")
            
            for i, event in enumerate(timeline.events):
                print(f"\nEvent {i+1} [{event.analyzed_at}]")
                print(f"Run ID: {event.run_id}")
                print(f"Supporting chunks: {len(event.supporting_chunks)}")
                if event.executive_briefing:
                    print(f"Exec Briefing length: {len(event.executive_briefing)}")
                if event.structured_summary:
                    print(f"Structured Summary length: {len(event.structured_summary)}")
        
        print("\n--- Helper methods check ---")
        latest = await service.latest(company)
        previous = await service.previous(company)
        
        if latest:
            print(f"Latest: {latest.analyzed_at} | Run ID: {latest.run_id}")
        if previous:
            print(f"Previous: {previous.analyzed_at} | Run ID: {previous.run_id}")

if __name__ == "__main__":
    asyncio.run(main())
