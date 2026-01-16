from fastapi.testclient import TestClient

from app.main import app, contradiction_store, interrogation_store, store


def test_interrogation_prompt_includes_context_and_schedule() -> None:
    store.clear()
    contradiction_store.clear()
    interrogation_store.clear()
    client = TestClient(app)

    payload = {
        "type": "plan",
        "content": "Publish the week 4 interrogation workflow",
        "importance": 5,
        "tags": ["weekly"],
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 201

    prompt_response = client.post("/interrogations", params={"frequency": "weekly"})
    assert prompt_response.status_code == 200
    prompt = prompt_response.json()
    assert prompt["frequency"] == "weekly"
    assert len(prompt["questions"]) >= 1
    assert prompt["context_items"]
    assert "scheduled_for" in prompt


def test_interrogation_submission_flow() -> None:
    store.clear()
    contradiction_store.clear()
    interrogation_store.clear()
    client = TestClient(app)

    payload = {
        "type": "goal",
        "content": "Ship week 4 feature",
        "importance": 4,
        "tags": ["weekly"],
    }
    create_response = client.post("/items", json=payload)
    assert create_response.status_code == 201

    prompt_response = client.post("/interrogations")
    assert prompt_response.status_code == 200
    prompt = prompt_response.json()

    submission_payload = {
        "answers": [
            {
                "question": prompt["questions"][0],
                "response": "Stop deferring the setup work.",
            }
        ],
        "forced_choice": "Ship week 4 feature",
        "finish_or_delete": "Delete a stale task",
        "notes": "Need accountability.",
    }
    submission_response = client.post(
        f"/interrogations/{prompt['id']}/responses",
        json=submission_payload,
    )
    assert submission_response.status_code == 200

    list_response = client.get(f"/interrogations/{prompt['id']}/responses")
    assert list_response.status_code == 200
    responses = list_response.json()
    assert len(responses) == 1
    assert responses[0]["forced_choice"] == submission_payload["forced_choice"]
