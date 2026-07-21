"""Этап 8: хранилище (SQLite) — сессии, сообщения+TurnState, тикеты, actions_log, оценки."""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "data/kremzapay.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY, channel TEXT NOT NULL,
    started_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active');
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL REFERENCES sessions(id),
    role TEXT NOT NULL, masked_text TEXT NOT NULL,
    turn_state TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,
    reason TEXT NOT NULL, category TEXT, intent TEXT,
    priority TEXT NOT NULL DEFAULT 'normal', status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL, resolution TEXT);
CREATE TABLE IF NOT EXISTS actions_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,
    action TEXT NOT NULL, params TEXT, result TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,
    rating TEXT, reopen INTEGER DEFAULT 0, created_at TEXT NOT NULL);
"""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def create_session(channel="web"):
    sid = str(uuid.uuid4())[:12]
    with _conn() as c:
        c.execute("INSERT INTO sessions (id, channel, started_at) VALUES (?,?,?)",
                  (sid, channel, _now()))
    return sid


def add_message(session_id, role, masked_text, turn_state=None):
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO messages (session_id, role, masked_text, turn_state, created_at) "
            "VALUES (?,?,?,?,?)",
            (session_id, role, masked_text,
             json.dumps(turn_state, ensure_ascii=False) if turn_state else None, _now()))
        return cur.lastrowid


def create_ticket(session_id, reason, category=None, intent=None, priority="normal"):
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO tickets (session_id, reason, category, intent, priority, created_at) "
            "VALUES (?,?,?,?,?,?)", (session_id, reason, category, intent, priority, _now()))
        return cur.lastrowid


def list_tickets(status=None):
    with _conn() as c:
        q = "SELECT * FROM tickets" + (" WHERE status=?" if status else "") + " ORDER BY id DESC"
        rows = c.execute(q, (status,) if status else ()).fetchall()
        return [dict(r) for r in rows]


def log_action(session_id, action, params=None, result=None):
    with _conn() as c:
        c.execute("INSERT INTO actions_log (session_id, action, params, result, created_at) "
                  "VALUES (?,?,?,?,?)",
                  (session_id, action, json.dumps(params, ensure_ascii=False), result, _now()))


def add_feedback(session_id, rating, reopen=False):
    with _conn() as c:
        c.execute("INSERT INTO feedback (session_id, rating, reopen, created_at) VALUES (?,?,?,?)",
                  (session_id, rating, int(reopen), _now()))


if __name__ == "__main__":
    sid = create_session("web")
    add_message(sid, "user", "jak zrobic zwrot <CARD_1>?",
                turn_state={"decision": {"action": "answer"}, "classification": {"intent": "refund_how"}})
    tid = create_ticket(sid, "no_knowledge", category="payments", intent="payment_limits")
    log_action(sid, "get_payment_status", {"session_id": "s-123"}, "completed")
    add_feedback(sid, "up")
    print(f"сессия {sid}, тикет #{tid}")
    print("тикеты:", list_tickets("new"))
