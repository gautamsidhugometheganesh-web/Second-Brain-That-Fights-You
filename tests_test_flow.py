from fastapi.testclient import TestClient

from app.main import app, contradiction_store, interrogation_store, store


def test_run_flow_creates_contradictions_and_interrogation() -> None:
    store.clear()
    contradiction_store.clear()
    interrogation_store.clear()
    client = TestClient(app)

    payloads = [
        {
            "type": "goal",
            "content": "I won't exercise this week",
            "importance": 3,
            "tags": [],
        },
        {
            "type": "note",
            "content": "I plan to quit reading daily",
            "importance": 2,
            "tags": [],
        },
    ]

    for payload in payloads:
        response = client.post("/items", json=payload)
        assert response.status_code == 201

    flow_response = client.post("/flows/run", params={"frequency": "daily"})
    assert flow_response.status_code == 200
    data = flow_response.json()
    assert data["items"]
    assert data["contradictions"]
    assert data["interrogation"]["frequency"] == "daily"

    history_response = client.get("/interrogations/history")
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1
