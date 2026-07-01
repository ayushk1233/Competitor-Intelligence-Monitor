import asyncio
from backend.tasks import run_memory_backfill_task

result = run_memory_backfill_task(batch_size=50, resume=True)
print(result)
