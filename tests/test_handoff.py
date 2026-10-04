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


def test_handoff_reply_asks_for_contact(client, monkeypatch):
    assert "zostaw e-mail lub telefon" in _start_handoff(client, monkeypatch)["reply"].lower()


def test_english_handoff_reply_asks_for_contact(client, monkeypatch):
    body = _start_handoff(client, monkeypatch, route=_route_llm_handoff, text="get me a person please")
    assert "e-mail or phone" in body["reply"].lower()


def _all_message_text():
    return " ".join(str(value) for row in _rows("SELECT * FROM messages") for value in row.values())


def test_contact_goes_only_to_ticket(client, monkeypatch, caplog):
    first = _start_handoff(client, monkeypatch)
    sid = first["session_id"]
    caplog.set_level("DEBUG")
    client.post("/chat", json={"text": "mój mail jan.kowalski@example.pl, tel 600 700 800", "session_id": sid})
    contact = _rows("SELECT contact FROM tickets WHERE id=?", (first["ticket_id"],))[0]["contact"]
    assert "jan.kowalski@example.pl" in contact
    assert "600 700 800" in contact
    stored = _all_message_text()
    assert "<EMAIL_1>" in stored and "<PHONE_1>" in stored
    assert "jan.kowalski@example.pl" not in stored and "600 700 800" not in stored
    assert "jan.kowalski@example.pl" not in caplog.text


def test_contact_in_the_handoff_request_is_kept(client, monkeypatch):
    first = _start_handoff(client, monkeypatch, text="połączcie mnie z konsultantem, anna@example.pl")
    assert _rows("SELECT contact FROM tickets")[0]["contact"] == "anna@example.pl"
    assert "anna@example.pl" not in _all_message_text()
    assert first["ticket_id"] == 1


def test_message_without_contact_keeps_saved_contact(client, monkeypatch):
    first = _start_handoff(client, monkeypatch)
    sid = first["session_id"]
    client.post("/chat", json={"text": "anna@example.pl", "session_id": sid})
    client.post("/chat", json={"text": "dziękuję", "session_id": sid})
    client.post("/chat", json={"text": "anna@example.pl albo ola@example.pl", "session_id": sid})
    assert _rows("SELECT contact FROM tickets")[0]["contact"] == "anna@example.pl, ola@example.pl"


def test_contact_outside_handoff_is_not_stored(client, monkeypatch):
    import api
    monkeypatch.setattr(api.cascade, "route", lambda text: {
        "turn_id": "t", "raw_text": text, "language": "pl", "timings_ms": {},
        "classification": {"intent": "payment_limits", "scope": "in_scope", "confidence": "high"},
        "decision": {"action": "ticket", "reason": "no_knowledge", "confidence": "high"}})
    client.post("/chat", json={"text": "limit? mój mail jan@example.pl"})
    assert _rows("SELECT contact FROM tickets") == [{"contact": None}]


def test_old_database_gets_ticket_contact_column(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "old.db")
    _old_schema_db(config.DB_PATH)
    import store
    store.set_ticket_contact(1, ["jan@example.pl"])
    assert "contact" in _columns("tickets")
    assert _rows("SELECT reason, contact FROM tickets") == [{"reason": "no_knowledge", "contact": "jan@example.pl"}]
