from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from app.models import EmbeddingStatus, ItemType, MemoryItemCreate, MemoryItemRecord


class MemoryStore:
    def __init__(self) -> None:
        self._items: list[MemoryItemRecord] = []

    def add(self, item: MemoryItemCreate) -> MemoryItemRecord:
        record = MemoryItemRecord(
            type=item.type,
            content=item.content,
            importance=item.importance,
            tags=list(item.tags),
        )
        self._items.append(record)
        return record

    def list(
        self,
        item_type: ItemType | None = None,
        query: str | None = None,
    ) -> Iterable[MemoryItemRecord]:
        items = self._items
        if item_type:
            items = [item for item in items if item.type == item_type]
        if query:
            normalized = query.lower()
            items = [item for item in items if normalized in item.content.lower()]
        return list(items)

    def get(self, item_id: UUID) -> MemoryItemRecord | None:
        return next((item for item in self._items if item.id == item_id), None)

    def update(self, item_id: UUID, item: MemoryItemCreate) -> MemoryItemRecord | None:
        record = self.get(item_id)
        if record is None:
            return None
        record.type = item.type
        record.content = item.content
        record.importance = item.importance
        record.tags = list(item.tags)
        return record

    def delete(self, item_id: UUID) -> bool:
        for index, item in enumerate(self._items):
            if item.id == item_id:
                self._items.pop(index)
                return True
        return False

    def update_embedding_status(
        self,
        item_id: UUID,
        status: EmbeddingStatus,
    ) -> MemoryItemRecord | None:
        record = self.get(item_id)
        if record is None:
            return None
        record.embedding_status = status
        return record

    def update_embedding(
        self,
        item_id: UUID,
        embedding: list[float],
        status: EmbeddingStatus = EmbeddingStatus.completed,
    ) -> MemoryItemRecord | None:
        record = self.get(item_id)
        if record is None:
            return None
        record.embedding = list(embedding)
        record.embedding_status = status
        return record

    def clear(self) -> None:
        self._items.clear()
