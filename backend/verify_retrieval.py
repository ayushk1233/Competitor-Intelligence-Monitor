import asyncio
from datetime import datetime, timezone, timedelta
from backend.database.connection import AsyncSessionLocal
from backend.memory.retrieval import RetrievalRepository
from backend.memory.providers.factory import ProviderFactory

async def main():
    async with AsyncSessionLocal() as session:
        repo = RetrievalRepository(session)
        provider = ProviderFactory.create()
        
        # We need an embedding for "What changed in Cursor pricing?"
        # The local provider takes a list of strings and returns a list of embeddings
        print("Generating query embedding...")
        query_text = "What changed in Anthropic pricing?"
        embeddings = await provider.embed_documents([query_text])
        query_emb = embeddings[0]

        print("\n--- Verification 1: similarity_search ---")
        top_memories = await repo.similarity_search(query_embedding=query_emb, limit=5)
        for i, mem in enumerate(top_memories):
            print(f"{i+1}. [{mem.company_name}] Score: {mem.similarity_score:.4f} | {mem.chunk_text[:100]}...")
            
        print("\n--- Verification 2: similarity_search_company ---")
        cursor_memories = await repo.similarity_search_company(company_name="Anthropic", query_embedding=query_emb, limit=3)
        for i, mem in enumerate(cursor_memories):
            assert mem.company_name == "Anthropic", f"Expected Anthropic, got {mem.company_name}"
            print(f"{i+1}. [{mem.company_name}] Score: {mem.similarity_score:.4f} | {mem.chunk_text[:100]}...")
            
        print("\n--- Verification 3: company_history ---")
        history = await repo.company_history("Anthropic")
        print(f"Total historical chunks for Anthropic: {len(history)}")
        if history:
            print(f"Oldest: {history[0].analyzed_at}")
            print(f"Newest: {history[-1].analyzed_at}")

        print("\n--- Verification 4: latest_memory ---")
        latest = await repo.latest_memory("Anthropic")
        if latest:
            print(f"Latest analysis for Anthropic: {latest.analyzed_at}")
        
        print("\n--- Verification 5: previous_memory ---")
        previous = await repo.previous_memory("Anthropic")
        if previous:
            print(f"Previous analysis for Anthropic: {previous.analyzed_at}")
            
        print("\n--- Verification 6: Timerange query ---")
        if history and len(history) > 1:
            end_date = history[-1].analyzed_at
            start_date = history[0].analyzed_at
            # Just take a window
            mid_date = start_date + (end_date - start_date) / 2
            
            timerange_memories = await repo.similarity_search_timerange(
                company_name="Anthropic",
                start_date=start_date,
                end_date=mid_date,
                query_embedding=query_emb,
                limit=3
            )
            print(f"Found {len(timerange_memories)} memories between {start_date} and {mid_date}")
            for mem in timerange_memories:
                assert start_date <= mem.analyzed_at <= mid_date, f"Time range mismatch: {mem.analyzed_at}"
                print(f"[{mem.analyzed_at}] {mem.chunk_text[:50]}...")

if __name__ == "__main__":
    asyncio.run(main())
