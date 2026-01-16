from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.analytics import AnalyticsSummary, AnalyticsStore
from app.contradiction_store import ContradictionStore
from app.contradictions import ContradictionResponse, detect_contradictions, to_response
from app.embeddings import EmbeddingProviderError, get_embedding_provider
from app.flow import FlowResponse
from app.interrogation import (
    InterrogationFrequency,
    InterrogationResponse,
    InterrogationSubmission,
    InterrogationSubmissionCreate,
    generate_interrogation,
)
from app.interrogation_store import InterrogationStore
from app.models import EmbeddingStatus, ItemType, MemoryItem, MemoryItemCreate
from app.storage import MemoryStore


class HealthResponse(BaseModel):
    status: str
    timestamp: str


class RootResponse(BaseModel):
    name: str
    description: str
    mvp_features: list[str]


app = FastAPI(
    title="Second Brain That Fights You",
    version="0.1.0",
    description="An AI productivity system that challenges, contradicts, and interrogates you.",
)
store = MemoryStore()
contradiction_store = ContradictionStore()
interrogation_store = InterrogationStore()
analytics_store = AnalyticsStore()
embedding_provider = get_embedding_provider()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    timestamp = datetime.now(timezone.utc).isoformat()
    return HealthResponse(status="ok", timestamp=timestamp)


@app.get("/", response_model=RootResponse)
def root() -> RootResponse:
    return RootResponse(
        name="Second Brain That Fights You",
        description="MVP foundation service placeholder.",
        mvp_features=[
            "Memory Engine",
            "Contradiction Detector",
            "Daily / Weekly Interrogation",
        ],
    )


@app.post("/items", response_model=MemoryItem, status_code=201)
def create_item(item: MemoryItemCreate) -> MemoryItem:
    record = store.add(item)
    analytics_store.record_item_created()
    return record.to_public()


@app.get("/items", response_model=list[MemoryItem])
def list_items(
    item_type: ItemType | None = None,
    query: str | None = None,
) -> list[MemoryItem]:
    items = store.list(item_type=item_type, query=query)
    return [item.to_public() for item in items]


@app.get("/items/{item_id}", response_model=MemoryItem)
def get_item(item_id: UUID) -> MemoryItem:
    record = store.get(item_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return record.to_public()


@app.put("/items/{item_id}", response_model=MemoryItem)
def update_item(item_id: UUID, item: MemoryItemCreate) -> MemoryItem:
    record = store.update(item_id, item)
    if record is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return record.to_public()


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: UUID) -> None:
    deleted = store.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    analytics_store.record_item_deleted()


@app.post("/items/{item_id}/embedding", response_model=MemoryItem)
def update_embedding_status(
    item_id: UUID,
    status: EmbeddingStatus = EmbeddingStatus.completed,
) -> MemoryItem:
    record = store.update_embedding_status(item_id, status)
    if record is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return record.to_public()


@app.post("/items/{item_id}/embed", response_model=MemoryItem)
def embed_item(item_id: UUID) -> MemoryItem:
    record = store.get(item_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Item not found")
    try:
        embedding = embedding_provider.embed_text(
            record.content,
            [item.content for item in store.list()],
        )
    except EmbeddingProviderError as exc:
        analytics_store.record_embedding_failure()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    record = store.update_embedding(item_id, embedding)
    if record is None:
        raise HTTPException(status_code=404, detail="Item not found")
    analytics_store.record_embedding_created()
    return record.to_public()


@app.post("/items/embeddings/refresh", response_model=list[MemoryItem])
def refresh_embeddings() -> list[MemoryItem]:
    items = list(store.list())
    if not items:
        return []
    corpus = [item.content for item in items]
    updated_items: list[MemoryItem] = []
    for item in items:
        try:
            embedding = embedding_provider.embed_text(item.content, corpus)
        except EmbeddingProviderError as exc:
            analytics_store.record_embedding_failure()
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        record = store.update_embedding(item.id, embedding)
        if record is None:
            raise HTTPException(status_code=404, detail="Item not found")
        analytics_store.record_embedding_created()
        updated_items.append(record.to_public())
    return updated_items


@app.get("/contradictions", response_model=list[ContradictionResponse])
def list_contradictions() -> list[ContradictionResponse]:
    items = [item.to_public() for item in store.list()]
    contradictions = detect_contradictions(items)
    return [to_response(record) for record in contradictions]


@app.post("/contradictions/run", response_model=list[ContradictionResponse])
def run_contradiction_detection() -> list[ContradictionResponse]:
    items = [item.to_public() for item in store.list()]
    contradictions = detect_contradictions(items)
    saved = contradiction_store.add_many(contradictions)
    analytics_store.record_contradiction_run(len(saved))
    return [to_response(record) for record in saved]


@app.get("/contradictions/history", response_model=list[ContradictionResponse])
def list_contradiction_history() -> list[ContradictionResponse]:
    return [to_response(record) for record in contradiction_store.list()]


@app.post("/interrogations", response_model=InterrogationResponse)
def create_interrogation(
    frequency: InterrogationFrequency = InterrogationFrequency.daily,
) -> InterrogationResponse:
    items = [item.to_public() for item in store.list()]
    prompt = generate_interrogation(items, frequency=frequency)
    interrogation_store.add_session(prompt)
    analytics_store.record_interrogation_created()
    return InterrogationResponse(**prompt.model_dump())


@app.get("/interrogations/history", response_model=list[InterrogationResponse])
def list_interrogations() -> list[InterrogationResponse]:
    return [
        InterrogationResponse(**session.model_dump())
        for session in interrogation_store.list_sessions()
    ]


@app.post(
    "/interrogations/{interrogation_id}/responses",
    response_model=InterrogationSubmission,
)
def create_interrogation_response(
    interrogation_id: UUID,
    payload: InterrogationSubmissionCreate,
) -> InterrogationSubmission:
    session = interrogation_store.get_session(interrogation_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interrogation not found")
    submission = interrogation_store.add_submission(interrogation_id, payload)
    analytics_store.record_interrogation_response()
    return submission


@app.get(
    "/interrogations/{interrogation_id}/responses",
    response_model=list[InterrogationSubmission],
)
def list_interrogation_responses(
    interrogation_id: UUID,
) -> list[InterrogationSubmission]:
    session = interrogation_store.get_session(interrogation_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interrogation not found")
    return interrogation_store.list_submissions(interrogation_id)


@app.post("/flows/run", response_model=FlowResponse)
def run_flow(
    frequency: InterrogationFrequency = InterrogationFrequency.daily,
) -> FlowResponse:
    items = [item.to_public() for item in store.list()]
    contradictions = detect_contradictions(items)
    saved_contradictions = contradiction_store.add_many(contradictions)
    prompt = generate_interrogation(items, frequency=frequency)
    interrogation_store.add_session(prompt)
    analytics_store.record_flow_run(len(saved_contradictions))
    return FlowResponse(
        items=items,
        contradictions=[to_response(record) for record in saved_contradictions],
        interrogation=InterrogationResponse(**prompt.model_dump()),
    )


@app.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary() -> AnalyticsSummary:
    return analytics_store.summary()
