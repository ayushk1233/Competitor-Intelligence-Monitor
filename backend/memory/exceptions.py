"""
Memory subsystem exceptions.
"""


class MemoryError(Exception):
    """Base memory exception."""


class UnsupportedEmbeddingModelError(MemoryError):
    """Raised when an embedding model is not supported."""


class EmbeddingGenerationError(MemoryError):
    """Raised when embedding generation fails."""


class ChunkingError(MemoryError):
    """Raised when document chunking fails."""


class RetrievalError(MemoryError):
    """Raised when semantic retrieval fails."""
