import sys
sys.path.append('.')
from backend.retrieval.signal_extractor import calculate_quality_score

items = [
    "It's exceptional at debugging issues and attributing them to precise historical code changes, has st",
    "Semantic search Published 2025",
    "Secure codebase indexing Published 2026",
    "Multi-agent collaboration Published 2023"
]

for item in items:
    print(f"[{calculate_quality_score(item)}] {item}")

