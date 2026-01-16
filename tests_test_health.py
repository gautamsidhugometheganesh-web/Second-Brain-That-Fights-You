from fastapi.testclient import TestClient

from app.main import app, contradiction_store, store


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_item_crud_flow() -> None:
    store.clear()
    contradiction_store.clear()
    client = TestClient(app)
    payload = {
        "type": "goal",
        "content": "Ship MVP in 5 weeks",
        "importance": 5,
        "tags": ["mvp", "timeline"],
    }

    create_response = client.post("/items", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["content"] == payload["content"]
    assert created["importance"] == payload["importance"]
    assert created["embedding_status"] == "pending"

    list_response = client.get("/items")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

    item_id = created["id"]
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == item_id

    update_payload = {
        "type": "goal",
        "content": "Ship MVP in 6 weeks",
        "importance": 4,
        "tags": ["mvp"],
    }
    update_response = client.put(f"/items/{item_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["content"] == update_payload["content"]

    search_response = client.get("/items", params={"query": "6 weeks"})
    assert search_response.status_code == 200
    assert len(search_response.json()) == 1

    embed_response = client.post(f"/items/{item_id}/embedding")
    assert embed_response.status_code == 200
    assert embed_response.json()["embedding_status"] == "completed"

    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 204


def test_contradiction_detection() -> None:
    store.clear()
    contradiction_store.clear()
    client = TestClient(app)

    payloads = [
        {"type": "goal", "content": "I won't exercise this week", "importance": 3, "tags": []},
        {"type": "note", "content": "I plan to quit reading daily", "importance": 2, "tags": []},
        {"type": "note", "content": "Do not launch the beta", "importance": 4, "tags": []},
        {"type": "note", "content": "Launch the beta", "importance": 4, "tags": []},
    ]

    for payload in payloads:
        response = client.post("/items", json=payload)
        assert response.status_code == 201

    contradiction_response = client.get("/contradictions")
    assert contradiction_response.status_code == 200
    types = {item["type"] for item in contradiction_response.json()}

    assert "goal_vs_action" in types
    assert "repeated_abandonment" in types
    assert "content_conflict" in types


def test_contradiction_history() -> None:
    store.clear()
    contradiction_store.clear()
    client = TestClient(app)

    payloads = [
        {"type": "goal", "content": "I won't exercise this week", "importance": 3, "tags": []},
        {"type": "note", "content": "I plan to quit reading daily", "importance": 2, "tags": []},
    ]

    for payload in payloads:
        response = client.post("/items", json=payload)
        assert response.status_code == 201

    run_response = client.post("/contradictions/run")
    assert run_response.status_code == 200
    assert len(run_response.json()) >= 1

    history_response = client.get("/contradictions/history")
    assert history_response.status_code == 200
    assert len(history_response.json()) >= 1

