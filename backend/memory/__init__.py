"""
Historical Intelligence Memory subsystem.

This package owns all functionality related to:

- Document chunking
- Embedding generation
- Vector persistence
- Semantic retrieval
- Historical memory

Business logic should remain isolated from the rest of the
application so future memory implementations (hybrid search,
reranking, temporal retrieval) can evolve independently.
"""

from .constants import DEFAULT_EMBEDDING_MODEL, VECTOR_DIMENSION

__all__ = [
    "DEFAULT_EMBEDDING_MODEL",
    "VECTOR_DIMENSION",
]
