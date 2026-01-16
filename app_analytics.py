from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AnalyticsSummary(BaseModel):
    items_created: int = 0
    items_deleted: int = 0
    contradictions_detected: int = 0
    contradiction_runs: int = 0
    interrogations_created: int = 0
    interrogation_responses: int = 0
    flows_run: int = 0
    embeddings_created: int = 0
    embedding_failures: int = 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnalyticsStore:
    def __init__(self) -> None:
        self._summary = AnalyticsSummary()

    def summary(self) -> AnalyticsSummary:
        return self._summary

    def record_item_created(self) -> None:
        self._summary.items_created += 1
        self._touch()

    def record_item_deleted(self) -> None:
        self._summary.items_deleted += 1
        self._touch()

    def record_contradiction_run(self, detected_count: int) -> None:
        self._summary.contradiction_runs += 1
        self._summary.contradictions_detected += detected_count
        self._touch()

    def record_interrogation_created(self) -> None:
        self._summary.interrogations_created += 1
        self._touch()

    def record_interrogation_response(self) -> None:
        self._summary.interrogation_responses += 1
        self._touch()

    def record_flow_run(self, detected_count: int) -> None:
        self._summary.flows_run += 1
        self._summary.contradictions_detected += detected_count
        self._summary.interrogations_created += 1
        self._touch()

    def record_embedding_created(self) -> None:
        self._summary.embeddings_created += 1
        self._touch()

    def record_embedding_failure(self) -> None:
        self._summary.embedding_failures += 1
        self._touch()

    def clear(self) -> None:
        self._summary = AnalyticsSummary()

    def _touch(self) -> None:
        self._summary.last_updated = datetime.now(timezone.utc)
