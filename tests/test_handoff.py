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


def _no_bot(*_a, **_k):
    raise AssertionError("cascade or model called for a session in handoff")


def _start_handoff(client, monkeypatch, route=_route_rules_handoff, text="chcę rozmawiać z człowiekiem"):
    import api
    monkeypatch.setattr(api.cascade, "route", route)
    body = client.post("/chat", json={"text": text}).json()
    monkeypatch.setattr(api.cascade, "route", _no_bot)
    monkeypatch.setattr(api.answer_gen, "generate", _no_bot)
    monkeypatch.setattr(api.judge, "grounded", _no_bot)
    return body


def test_handoff_marks_session(client, monkeypatch):
    body = _start_handoff(client, monkeypatch)
    assert _rows("SELECT status FROM sessions WHERE id=?", (body["session_id"],)) == [{"status": "handoff"}]


def test_message_in_handoff_session_skips_bot_and_joins_ticket(client, monkeypatch):
    first = _start_handoff(client, monkeypatch)
    sid = first["session_id"]
    second = client.post("/chat", json={"text": "dalej czekam na odpowiedź", "session_id": sid}).json()
    assert second["action"] == "handoff"
    assert second["ticket_id"] == first["ticket_id"]
    assert second["reply"] == f"Twoja wiadomość została dodana do zgłoszenia #{first['ticket_id']}."
    assert len(_rows("SELECT id FROM tickets")) == 1
    user_rows = _rows("SELECT masked_text, ticket_id FROM messages WHERE session_id=? AND role='user'", (sid,))
    assert user_rows[-1] == {"masked_text": "dalej czekam na odpowiedź", "ticket_id": first["ticket_id"]}


def test_message_in_english_handoff_session(client, monkeypatch):
    first = _start_handoff(client, monkeypatch, route=_route_llm_handoff, text="get me a person please")
    second = client.post("/chat", json={"text": "still waiting", "session_id": first["session_id"]}).json()
    assert second["reply"] == f"Your message has been added to ticket #{first['ticket_id']}."


def test_other_sessions_still_reach_the_bot(client, monkeypatch):
    import api
    _start_handoff(client, monkeypatch)
    monkeypatch.setattr(api.cascade, "route", _route_rules_handoff)
    other = client.post("/chat", json={"text": "chcę rozmawiać z człowiekiem"}).json()
    assert other["ticket_id"] == 2


def _old_schema_db(path):
    with sqlite3.connect(path) as conn:
        conn.executescript(
            "CREATE TABLE sessions (id TEXT PRIMARY KEY, channel TEXT NOT NULL, started_at TEXT NOT NULL,"
            " status TEXT NOT NULL DEFAULT 'active');"
            "CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,"
            " role TEXT NOT NULL, masked_text TEXT NOT NULL, turn_state TEXT, created_at TEXT NOT NULL);"
            "CREATE TABLE tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,"
            " reason TEXT NOT NULL, category TEXT, intent TEXT, priority TEXT NOT NULL DEFAULT 'normal',"
            " status TEXT NOT NULL DEFAULT 'new', created_at TEXT NOT NULL, resolution TEXT);"
            "INSERT INTO sessions VALUES ('old', 'web', '2026-10-01', 'active');"
            "INSERT INTO messages (session_id, role, masked_text, created_at) VALUES ('old', 'user', 'stare', '2026-10-01');"
            "INSERT INTO tickets (session_id, reason, created_at) VALUES ('old', 'no_knowledge', '2026-10-01');")


def _columns(table):
    with sqlite3.connect(config.DB_PATH) as conn:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def test_old_database_gets_message_ticket_column(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "old.db")
    _old_schema_db(config.DB_PATH)
    import store
    sid = store.create_session("web")
    store.add_message(sid, "user", "nowe", ticket_id=1)
    assert "ticket_id" in _columns("messages")
    assert _rows("SELECT masked_text, ticket_id FROM messages ORDER BY id") == [
        {"masked_text": "stare", "ticket_id": None}, {"masked_text": "nowe", "ticket_id": 1}]
