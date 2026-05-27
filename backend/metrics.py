from prometheus_client import Counter, Histogram, Gauge
import os
from prometheus_client import CollectorRegistry, multiprocess

if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
else:
    registry = None

# ── Pipeline metrics ──────────────────────────────────────────────────────────

pipeline_duration = Histogram(
    "pipeline_duration_seconds",
    "Total time for a full intelligence pipeline run",
    ["status"],          # completed | failed
    buckets=[10, 20, 30, 45, 60, 90, 120, 180, 300]
)

pipeline_stage_duration = Histogram(
    "pipeline_stage_duration_seconds",
    "Time spent in each pipeline stage",
    ["stage"],           # scraping | analyzing | comparing
    buckets=[5, 10, 15, 20, 30, 45, 60, 90]
)

pipelines_total = Counter(
    "pipelines_total",
    "Total number of pipeline runs",
    ["status"]           # completed | failed
)

# ── LLM API metrics (OpenRouter) ─────────────────────────────────────────────

llm_request_duration = Histogram(
    "llm_api_call_duration_seconds",
    "Time taken for each LLM API call",
    ["call_type", "model"],   # call_type: analysis | comparison
    buckets=[1, 2, 3, 5, 8, 10, 15, 20, 30]
)

llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM API calls made",
    ["call_type", "status"]   # status: success | error | retry
)

llm_tokens_used = Counter(
    "llm_tokens_used_total",
    "Estimated tokens sent to LLM",
    ["call_type"]
)

llm_errors_total = Counter(
    "llm_errors_total",
    "Total LLM API errors",
    ["error_type"]       # rate_limit | parse_error | timeout | unknown
)

llm_momentum_score = Histogram(
    "momentum_score_distribution",
    "Distribution of momentum scores returned by LLM",
    buckets=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
)


# ── Scraper metrics ───────────────────────────────────────────────────────────

scrape_requests_total = Counter(
    "scrape_requests_total",
    "Total scrape attempts",
    ["domain", "page_type", "method"]  # method: jina | beautifulsoup
)

scrape_success_total = Counter(
    "scrape_success_total",
    "Successful page fetches",
    ["domain", "page_type"]
)

scrape_failure_total = Counter(
    "scrape_failure_total",
    "Failed page fetches",
    ["domain", "reason"]    # reason: timeout | ssl | http_error | parse_error
)

scrape_duration = Histogram(
    "scrape_duration_seconds",
    "Time to fetch and clean a single page",
    ["page_type"],
    buckets=[0.5, 1, 2, 3, 5, 8, 10, 15]
)

pages_fetched_per_run = Histogram(
    "pages_fetched_per_run",
    "Number of pages fetched in a single pipeline run",
    buckets=[1, 2, 3, 4, 5, 8, 10, 15, 20]
)

# ── Active run gauge ──────────────────────────────────────────────────────────

active_pipeline_runs = Gauge(
    "active_pipeline_runs",
    "Number of pipeline runs currently in progress"
)