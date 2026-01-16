from fastapi.testclient import TestClient

from app.main import analytics_store, app, store


def test_embed_item_creates_embedding() -> None:
    store.clear()
    analytics_store.clear()
    client = TestClient(app)

    payload = {
        "type": "goal",
        "content": "Ship the embedding integration",
        "importance": 4,
        "tags": [],
    }
    create_response = client.post("/items", json=payload)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    embed_response = client.post(f"/items/{item_id}/embed")
    assert embed_response.status_code == 200
    data = embed_response.json()
    assert data["embedding_status"] == "completed"
    assert analytics_store.summary().embeddings_created == 1


def test_refresh_embeddings_updates_all_items() -> None:
    store.clear()
    analytics_store.clear()
    client = TestClient(app)

    payloads = [
        {
            "type": "note",
            "content": "Capture ML context for embeddings",
            "importance": 2,
            "tags": [],
        },
        {
            "type": "plan",
            "content": "Use tf-idf vectors locally",
            "importance": 3,
            "tags": [],
        },
    ]
    for payload in payloads:
        response = client.post("/items", json=payload)
        assert response.status_code == 201

    refresh_response = client.post("/items/embeddings/refresh")
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert len(data) == 2
    assert analytics_store.summary().embeddings_created == 2
