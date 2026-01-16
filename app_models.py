from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ItemType(str, Enum):
    goal = "goal"
    note = "note"
    plan = "plan"


class EmbeddingStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class MemoryItemCreate(BaseModel):
    type: ItemType
    content: str = Field(min_length=1)
    importance: int = Field(ge=1, le=5)
    tags: list[str] = Field(default_factory=list)


class MemoryItem(BaseModel):
    id: UUID
    type: ItemType
    content: str
    importance: int
    tags: list[str]
    created_at: datetime
    embedding_status: EmbeddingStatus


class MemoryItemRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: ItemType
    content: str
    importance: int
    tags: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    embedding_status: EmbeddingStatus = EmbeddingStatus.pending
    embedding: list[float] | None = None

    def to_public(self) -> MemoryItem:
        return MemoryItem(
            id=self.id,
            type=self.type,
            content=self.content,
            importance=self.importance,
            tags=list(self.tags),
            created_at=self.created_at,
            embedding_status=self.embedding_status,
        )
