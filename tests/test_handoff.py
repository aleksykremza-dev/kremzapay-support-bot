import sqlite3

import pytest
from fastapi.testclient import TestClient

import config


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    import api
    return TestClient(api.app)


def _rows(sql, params=()):
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def _route_rules_handoff(text):
    return {"turn_id": "h1", "raw_text": text, "language": "pl", "timings_ms": {"rules": 0.1},
            "rules": {"action": "handoff", "reason": "explicit_human_request", "layer": 0},
            "decision": {"action": "handoff", "reason": "explicit_human_request", "confidence": "high"}}


def _route_llm_handoff(text):
    return {"turn_id": "h2", "raw_text": text, "language": "en", "timings_ms": {"rules": 0.1, "knn": 1.0},
            "classification": {"intent": "payout_missing", "scope": "in_scope", "confidence": "high"},
            "decision": {"action": "handoff", "reason": "wants_human", "confidence": "high"}}


def test_rules_handoff_creates_high_priority_ticket(client, monkeypatch):
    import api
    monkeypatch.setattr(api.cascade, "route", _route_rules_handoff)
    body = client.post("/chat", json={"text": "chcę rozmawiać z człowiekiem"}).json()
    assert body["action"] == "handoff"
    assert body["ticket_id"] == 1
    assert "#1" in body["reply"]
    ticket = _rows("SELECT * FROM tickets")[0]
    assert (ticket["reason"], ticket["priority"], ticket["intent"]) == ("handoff", "high", None)
    assert ticket["session_id"] == body["session_id"]


def test_classifier_handoff_keeps_intent_and_english_reply(client, monkeypatch):
    import api
    monkeypatch.setattr(api.cascade, "route", _route_llm_handoff)
    body = client.post("/chat", json={"text": "my payout is missing, get me a person"}).json()
    assert body["action"] == "handoff"
    assert "#1" in body["reply"]
    assert "ticket" in body["reply"].lower()
    ticket = _rows("SELECT * FROM tickets")[0]
    assert (ticket["reason"], ticket["priority"], ticket["intent"]) == ("handoff", "high", "payout_missing")
