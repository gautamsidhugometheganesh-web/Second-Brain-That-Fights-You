from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.contradictions import ContradictionResponse
from app.interrogation import InterrogationResponse
from app.models import MemoryItem


class FlowResponse(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    items: list[MemoryItem]
    contradictions: list[ContradictionResponse]
    interrogation: InterrogationResponse
