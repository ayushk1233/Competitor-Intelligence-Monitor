from backend.celery_app import celery_app
from backend.tasks import run_memory_backfill_task
import time

print("Triggering memory backfill task...")
result = run_memory_backfill_task.delay(batch_size=50, resume=True)
print(f"Task ID: {result.id}")
print("Waiting for task to complete...")

while not result.ready():
    time.sleep(1)

print("Task complete!")
print("Result:")
print(result.get())
