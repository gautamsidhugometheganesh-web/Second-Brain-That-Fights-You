from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from enum import Enum

from pydantic import BaseModel, Field

from app.models import ItemType, MemoryItem


class ContradictionType(str, Enum):
    goal_vs_action = "goal_vs_action"
    repeated_abandonment = "repeated_abandonment"
    content_conflict = "content_conflict"


class ContradictionRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: ContradictionType
    description: str
    item_ids: list[UUID]
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContradictionResponse(BaseModel):
    id: UUID
    type: str
    description: str
    item_ids: list[UUID]
    confidence: float
    created_at: datetime


def to_response(record: ContradictionRecord) -> ContradictionResponse:
    return ContradictionResponse(
        id=record.id,
        type=record.type,
        description=record.description,
        item_ids=list(record.item_ids),
        confidence=record.confidence,
        created_at=record.created_at,
    )


def detect_contradictions(items: list[MemoryItem]) -> list[ContradictionRecord]:
    contradictions: list[ContradictionRecord] = []
    lowered = [(item, item.content.lower()) for item in items]

    for item, content in lowered:
        if item.type == ItemType.goal and ("won't" in content or "will not" in content):
            contradictions.append(
                ContradictionRecord(
                    type=ContradictionType.goal_vs_action,
                    description="Goal conflicts with stated refusal or constraint.",
                    item_ids=[item.id],
                    confidence=0.55,
                )
            )

    for item, content in lowered:
        if "quit" in content or "abandon" in content:
            contradictions.append(
                ContradictionRecord(
                    type=ContradictionType.repeated_abandonment,
                    description="Item references abandoning goals or plans.",
                    item_ids=[item.id],
                    confidence=0.45,
                )
            )

    for index, (item, content) in enumerate(lowered):
        if "not " in content and index + 1 < len(lowered):
            next_item, next_content = lowered[index + 1]
            if item.type == next_item.type and content.replace("not ", "") in next_content:
                contradictions.append(
                    ContradictionRecord(
                        type=ContradictionType.content_conflict,
                        description="Two items of the same type appear to conflict.",
                        item_ids=[item.id, next_item.id],
                        confidence=0.35,
                    )
                )

    return contradictions
