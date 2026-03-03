from prometheus_client import Counter, Histogram, Gauge
import time

# ── Pipeline metrics ──────────────────────────────────────────────────────────

# Counts total pipeline runs, labeled by status (completed/failed)
pipeline_runs_total = Counter(
    "cim_pipeline_runs_total",
    "Total number of intelligence pipeline runs",
    ["status"]  # label: completed or failed
)

# Measures how long each pipeline stage takes in seconds
pipeline_stage_duration_seconds = Histogram(
    "cim_pipeline_stage_duration_seconds",
    "Duration of each pipeline stage in seconds",
    ["stage"],  # label: scraping, analyzing, comparing
    buckets=[5, 10, 20, 30, 60, 90, 120, 180]
)

# ── Gemini API metrics ────────────────────────────────────────────────────────

# Counts Gemini API calls, labeled by call type and status
gemini_api_calls_total = Counter(
    "cim_gemini_api_calls_total",
    "Total number of Gemini API calls",
    ["call_type", "status"]  # call_type: analysis/comparison, status: success/error/retry
)

# Measures Gemini response latency
gemini_api_latency_seconds = Histogram(
    "cim_gemini_api_latency_seconds",
    "Gemini API call latency in seconds",
    ["call_type"],
    buckets=[1, 2, 5, 10, 15, 20, 30, 45, 60]
)

# ── Scraping metrics ──────────────────────────────────────────────────────────

# Counts scrape attempts per domain
scrape_attempts_total = Counter(
    "cim_scrape_attempts_total",
    "Total scrape attempts per domain",
    ["domain", "status"]  # status: success/failed/jina_failed
)

# ── Intelligence metrics ──────────────────────────────────────────────────────

# Tracks momentum score distribution — shows what scores Gemini typically gives
momentum_score_distribution = Histogram(
    "cim_momentum_score_distribution",
    "Distribution of momentum scores across analyses",
    buckets=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
)

# Tracks how many competitors are currently being analyzed (active jobs)
active_pipeline_runs = Gauge(
    "cim_active_pipeline_runs",
    "Number of pipeline runs currently in progress"
)


# ── Helper context managers ───────────────────────────────────────────────────

class track_gemini_call:
    """
    Context manager that times a Gemini call and records metrics.

    Usage:
        with track_gemini_call("analysis"):
            result = gemini.generate(...)
    """
    def __init__(self, call_type: str):
        self.call_type = call_type
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        status = "error" if exc_type else "success"

        gemini_api_calls_total.labels(
            call_type=self.call_type,
            status=status
        ).inc()

        gemini_api_latency_seconds.labels(
            call_type=self.call_type
        ).observe(duration)

        # Don't suppress the exception
        return False