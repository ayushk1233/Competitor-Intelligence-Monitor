from celery import Celery
from backend.config import get_settings

settings = get_settings()

# ── Create Celery app ─────────────────────────────────────────────────────────
celery_app = Celery(
    "competitor_intel",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["backend.tasks"]   # Where our task functions live
)

# ── Configuration ─────────────────────────────────────────────────────────────
celery_app.conf.update(
    # Acknowledge task only after it completes successfully
    # If worker crashes mid-task, job goes back to queue automatically
    task_acks_late=True,

    # If worker is killed, reject task so it goes back to queue
    task_reject_on_worker_lost=True,

    # JSON serialization — human readable, debuggable
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Task time limits
    task_soft_time_limit=600,   # Warn after 10 minutes
    task_time_limit=900,        # Hard kill after 15 minutes

    # Results expire after 24 hours — cleans up Redis automatically
    result_expires=86400,

    # One task at a time per worker process
    # Prevents memory issues with large scraping jobs
    worker_prefetch_multiplier=1,
)