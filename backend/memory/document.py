from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from backend.database.models import EmbeddingSourceType, ChunkType

class MemoryDocument(BaseModel):
    organization_id: UUID
    run_id: str
    company_name: str
    source_type: EmbeddingSourceType
    source_id: str
    chunk_type: ChunkType
    text: str
    analyzed_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
