"""
Central configuration constants for the memory subsystem.

Only immutable configuration belongs here.
"""

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

VECTOR_DIMENSION = 384

MAX_CHUNK_SIZE = 800

CHUNK_OVERLAP = 120

MAX_BATCH_SIZE = 64

CONTENT_HASH_ALGORITHM = "sha256"
