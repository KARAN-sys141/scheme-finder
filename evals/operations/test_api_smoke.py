import json

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # runs startup (loads the retriever)
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["chunks"] > 20


def test_index_page_served(client):
    r = client.get("/")
    assert r.status_code == 200 and "SchemeMitra" in r.text


@pytest.mark.parametrize("f", ["style.css", "app.js"])
def test_static_files(client, f):
    assert client.get(f"/static/{f}").status_code == 200


@pytest.mark.parametrize("payload", [{}, {"message": ""}, {"message": "   "}, {"message": "x" * 501}])
def test_chat_rejects_bad_input(client, payload):
    assert client.post("/chat", json=payload).status_code == 422


def test_feedback_validation(client):
    assert client.post("/feedback", json={"session_id": "s", "rating": "maybe"}).status_code == 422


def test_feedback_saved(client, monkeypatch, tmp_path):
    path = tmp_path / "fb.jsonl"
    monkeypatch.setattr("api.main.FEEDBACK_PATH", path)
    r = client.post("/feedback", json={"session_id": "s1", "rating": "up", "message": "q", "reply": "a"})
    assert r.status_code == 200
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1 and rows[0]["rating"] == "up"


def test_chat_keeps_session_between_turns(client):
    r1 = client.post("/chat", json={"message": "क्या मैं किसान योजना के लिए पात्र हूँ?"})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["kind"] == "followup" and d1["session_id"]

    r2 = client.post(
        "/chat",
        json={
            "message": "हाँ, मेरे पास 2 हेक्टेयर ज़मीन है और मैं इनकम टैक्स नहीं भरता",
            "session_id": d1["session_id"],
        },
    )
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["kind"] == "verdict" and d2["verdicts"].get("pmkisan") == "likely_eligible"