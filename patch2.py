import re

with open('backend/retrieval/signal_extractor.py', 'r') as f:
    content = f.read()

# Fix split_into_sentences
split_old = """def split_into_sentences(text: str) -> list:
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n', text) if s.strip()]"""
split_new = """def split_into_sentences(text: str) -> list:
    # Split merged feature lists like "Semantic search Published 2025 Reinforcement learning..."
    text = re.sub(r'(Published 20\d\d)\s+(?=[A-Z])', r'\\1. ', text)
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n', text) if s.strip()]"""
content = content.replace(split_old, split_new)


with open('backend/retrieval/signal_extractor.py', 'w') as f:
    f.write(content)

