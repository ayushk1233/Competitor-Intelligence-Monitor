from celery import Celery
from backend.config import get_settings

settings = get_settings()

# Create the Celery app
# broker = Redis (where jobs are sent)
# backend = Redis (where results are stored)
celery_app = Celery(
    "competitor_intel",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Celery configuration
celery_app.conf.update(
    # Task will be acknowledged only after it completes
    # If worker crashes mid-task, job goes back to queue
    task_acks_late=True,

    # Reject tasks if worker is killed — puts job back in queue
    task_reject_on_worker_lost=True,

    # Serialize tasks as JSON (readable, debuggable)
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Tasks expire after 1 hour if not picked up
    task_soft_time_limit=3600,
)

# This is where we will register actual tasks in Milestone 2.3
# For now the worker starts up cleanly and waits for jobs