from prometheus_client import Counter, Histogram

temporal_reasoning_duration_seconds = Histogram(
    "temporal_reasoning_duration_seconds",
    "Time spent analyzing a company's timeline (in seconds)",
    ["company"]
)

temporal_reasoning_total = Counter(
    "temporal_reasoning_total",
    "Total number of temporal reasoning executions",
    ["company"]
)

temporal_reasoning_failures_total = Counter(
    "temporal_reasoning_failures_total",
    "Total number of temporal reasoning failures",
    ["company", "error_type"]
)
