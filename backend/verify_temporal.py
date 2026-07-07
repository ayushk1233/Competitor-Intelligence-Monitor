import asyncio
import json

from backend.database.connection import get_db
from backend.memory.retrieval import RetrievalRepository
from backend.memory.providers.factory import ProviderFactory
from backend.memory.service import MemoryService
from backend.temporal.comparator import TimelineComparator
from backend.temporal.llm import TemporalLLM, OpenRouterLLMProvider
from backend.temporal.engine import TemporalEngine

async def verify():
    # Setup Memory
    session_generator = get_db()
    session = await anext(session_generator)
    
    embedding_provider = ProviderFactory.create()
    await embedding_provider.initialize()
    
    retrieval_repo = RetrievalRepository(session)
    memory_service = MemoryService(provider=embedding_provider, repository=retrieval_repo)
    
    # Setup Temporal Engine
    comparator = TimelineComparator()
    llm_provider = OpenRouterLLMProvider()
    temporal_llm = TemporalLLM(llm_provider=llm_provider)
    
    # We will use haiku since it's faster, or gemini-2.5-flash
    engine = TemporalEngine(
        comparator=comparator,
        llm=temporal_llm,
        model_name="anthropic/claude-3-haiku"
    )
    
    print("1. Fetching Company Timeline...")
    timeline = await memory_service.timeline("Anthropic")
    print(f"Timeline retrieved. Found {timeline.total_events} events.")
    
    if timeline.total_events < 2:
        print("Not enough events to perform temporal analysis. Need at least 2.")
        return
        
    print(f"Latest event run_id: {timeline.events[-1].run_id}")
    print(f"Previous event run_id: {timeline.events[-2].run_id}")
    
    print("\n2. Executing Temporal Analysis...")
    try:
        result = await engine.analyze_timeline(timeline)
    except Exception as e:
        print(f"Analysis failed: {e}")
        return
        
    print("\n3. Inspecting Results...")
    
    print(f"\n[Overall Summary] (Confidence: {result.analysis.confidence_score})")
    print(result.analysis.overall_summary)
    
    print(f"\n[Detected Changes: {len(result.analysis.changes)}]")
    for change in result.analysis.changes:
        print(f"\n- Category: {change.category.value.upper()}")
        print(f"  Direction: {change.direction.value.upper()}")
        print(f"  Summary: {change.summary}")
        print(f"  Reasoning: {change.reasoning}")
        print(f"  Confidence: {change.confidence_score} ({change.confidence_level.value})")
        print(f"  Evidence items: {len(change.evidence)}")
        for ev in change.evidence:
            print(f"    -> {ev.description} [Run: {ev.source_run_id}]")

if __name__ == "__main__":
    asyncio.run(verify())
