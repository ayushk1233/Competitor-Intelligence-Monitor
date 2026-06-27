"""
Local sentence-transformers embedding provider.
"""
from typing import Optional

from sentence_transformers import SentenceTransformer

from backend.memory.constants import DEFAULT_EMBEDDING_MODEL, VECTOR_DIMENSION
from backend.memory.exceptions import (
    EmbeddingGenerationError,
    UnsupportedEmbeddingModelError,
)
from backend.memory.interfaces import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._expected_dim = VECTOR_DIMENSION

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def vector_dimension(self) -> int:
        return self._expected_dim

    @property
    def is_initialized(self) -> bool:
        return self._model is not None

    async def initialize(self) -> None:
        """
        Lazy-loads the embedding model into memory and validates it.
        """
        if self._model is not None:
            return

        try:
            # CPU-bound, synchronous load. For now, runs inline.
            self._model = SentenceTransformer(self._model_name)
        except Exception as e:
            raise UnsupportedEmbeddingModelError(
                f"Failed to load model {self._model_name}: {e}"
            ) from e

        # Validate dimension matches system constants
        actual_dim = self._model.get_sentence_embedding_dimension()
        if actual_dim != self._expected_dim:
            self._model = None
            raise UnsupportedEmbeddingModelError(
                f"Model {self._model_name} returns {actual_dim}D vectors, "
                f"but system requires {self._expected_dim}D."
            )

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple documents.
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # We assume self._model is not None here.
            embeddings = self._model.encode(documents, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to embed documents: {e}") from e

    async def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a single query.
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            embedding = self._model.encode(query, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to embed query: {e}") from e

    async def health_check(self) -> bool:
        """
        Simple check to verify the provider is functional.
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            _ = self._model.encode("health check")
            return True
        except Exception:
            return False
