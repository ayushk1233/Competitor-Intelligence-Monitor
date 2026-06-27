"""
Factory for creating embedding providers.
"""
from backend.memory.constants import DEFAULT_EMBEDDING_MODEL
from backend.memory.interfaces import EmbeddingProvider
from backend.memory.providers.local import LocalEmbeddingProvider


class ProviderFactory:
    """
    Factory to instantiate the appropriate embedding provider.
    """

    @staticmethod
    def create() -> EmbeddingProvider:
        """
        Creates and returns the configured embedding provider.
        Initially, we return the LocalEmbeddingProvider.
        """
        return LocalEmbeddingProvider(model_name=DEFAULT_EMBEDDING_MODEL)
