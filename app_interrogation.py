from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.models import ItemType, MemoryItem


class InterrogationFrequency(str, Enum):
    daily = "daily"
    weekly = "weekly"


class InterrogationContextItem(BaseModel):
    id: UUID
    type: ItemType
    summary: str
    importance: int
    tags: list[str]


class InterrogationPrompt(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    frequency: InterrogationFrequency
    questions: list[str]
    forced_choice: str
    finish_or_delete: str
    context_items: list[InterrogationContextItem]
    scheduled_for: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterrogationResponse(BaseModel):
    id: UUID
    frequency: InterrogationFrequency
    questions: list[str]
    forced_choice: str
    finish_or_delete: str
    context_items: list[InterrogationContextItem]
    scheduled_for: datetime
    created_at: datetime


class InterrogationAnswer(BaseModel):
    question: str
    response: str


class InterrogationSubmissionCreate(BaseModel):
    answers: list[InterrogationAnswer]
    forced_choice: str
    finish_or_delete: str
    notes: str | None = None


class InterrogationSubmission(BaseModel):
    id: UUID
    interrogation_id: UUID
    answers: list[InterrogationAnswer]
    forced_choice: str
    finish_or_delete: str
    notes: str | None
    created_at: datetime


def _top_items(items: list[MemoryItem], limit: int) -> list[MemoryItem]:
    return sorted(items, key=lambda item: item.importance, reverse=True)[:limit]


def _build_context(items: list[MemoryItem]) -> list[InterrogationContextItem]:
    context_items: list[InterrogationContextItem] = []
    for item in items:
        summary = item.content
        if len(summary) > 120:
            summary = f"{summary[:117].rstrip()}..."
        context_items.append(
            InterrogationContextItem(
                id=item.id,
                type=item.type,
                summary=summary,
                importance=item.importance,
                tags=list(item.tags),
            )
        )
    return context_items


def _question_for_item(item: MemoryItem) -> str:
    if item.type == ItemType.goal:
        return f"What hard move are you dodging for this goal: {item.content}?"
    if item.type == ItemType.plan:
        return f"Which part of this plan are you stalling on: {item.content}?"
    return f"What are you not saying out loud about: {item.content}?"


def _forced_choice(top_items: list[MemoryItem]) -> str:
    if len(top_items) >= 2:
        first, second = top_items[0], top_items[1]
        return (
            "Pick one to make real in the next 48 hours: "
            f"{first.content} or {second.content}?"
        )
    if top_items:
        return f"What would you drop so you can finish: {top_items[0].content}?"
    return "Which matters more right now: shipping something imperfect or waiting for clarity?"


def _next_scheduled_at(
    frequency: InterrogationFrequency,
    now: datetime,
) -> datetime:
    if frequency == InterrogationFrequency.weekly:
        return now + timedelta(days=7)
    return now + timedelta(days=1)


def generate_interrogation(
    items: list[MemoryItem],
    frequency: InterrogationFrequency,
) -> InterrogationPrompt:
    top_items = _top_items(items, limit=3)
    questions = [_question_for_item(item) for item in top_items]

    if not questions:
        questions = [
            "What are you avoiding that keeps repeating?",
            "Which promise to yourself did you ignore most recently?",
            "What is the smallest uncomfortable action you can take today?",
        ]

    now = datetime.now(timezone.utc)
    forced_choice = _forced_choice(top_items)
    finish_or_delete = "Which lingering commitment will you finish or delete today?"
    context_items = _build_context(top_items)
    scheduled_for = _next_scheduled_at(frequency, now)

    return InterrogationPrompt(
        frequency=frequency,
        questions=questions,
        forced_choice=forced_choice,
        finish_or_delete=finish_or_delete,
        context_items=context_items,
        scheduled_for=scheduled_for,
    )
