"""
Abstract interfaces for the memory subsystem.

Concrete implementations should inherit from these rather
than exposing provider-specific APIs throughout the codebase.
"""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Contract for any embedding provider.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...

    @property
    @abstractmethod
    def vector_dimension(self) -> int:
        ...

    @abstractmethod
    async def embed_documents(
        self,
        documents: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple documents.
        """

    @abstractmethod
    async def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate embedding for a single query.
        """
