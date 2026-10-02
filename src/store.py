# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import json
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import datetime, timezone

import config

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
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        conn.executescript(SCHEMA)
        with conn:
            yield conn


def create_session(channel: str = "web") -> str:
    sid = str(uuid.uuid4())[:12]
    with _conn() as conn:
        conn.execute("INSERT INTO sessions (id, channel, started_at) VALUES (?,?,?)",
                     (sid, channel, _now()))
    return sid


def add_message(session_id: str, role: str, masked_text: str, turn_state: dict | None = None) -> int:
    with _conn() as conn:
        cursor = conn.execute(
            "INSERT INTO messages (session_id, role, masked_text, turn_state, created_at) "
            "VALUES (?,?,?,?,?)",
            (session_id, role, masked_text,
             json.dumps(turn_state, ensure_ascii=False) if turn_state else None, _now()))
        return cursor.lastrowid


def create_ticket(session_id: str, reason: str, category: str | None = None,
                  intent: str | None = None, priority: str = "normal") -> int:
    with _conn() as conn:
        cursor = conn.execute(
            "INSERT INTO tickets (session_id, reason, category, intent, priority, created_at) "
            "VALUES (?,?,?,?,?,?)", (session_id, reason, category, intent, priority, _now()))
        return cursor.lastrowid


def get_stats() -> dict:
    with _conn() as conn:
        sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        rows = conn.execute(
            "SELECT session_id, masked_text, turn_state, created_at FROM messages "
            "WHERE role='user' AND turn_state IS NOT NULL ORDER BY id DESC LIMIT 50"
        ).fetchall()
        dialogs = []
        actions: dict[str, int] = {}
        for row in rows:
            ts = json.loads(row["turn_state"])
            action = ts.get("decision", {}).get("action", "?")
            actions[action] = actions.get(action, 0) + 1
            cls = ts.get("classification") or {}
            dialogs.append({
                "text": row["masked_text"][:70], "action": action,
                "intent": cls.get("intent"), "confidence": cls.get("confidence"),
                "layer_path": list(ts.get("timings_ms", {}).keys()),
                "total_ms": round(sum(ts.get("timings_ms", {}).values())),
                "reason": ts.get("decision", {}).get("reason"),
                "at": row["created_at"][11:19],
            })
        tickets = conn.execute(
            "SELECT id, reason, intent, status, created_at FROM tickets "
            "ORDER BY id DESC LIMIT 20").fetchall()
        return {"sessions": sessions, "actions": actions, "dialogs": dialogs,
                "tickets": [dict(ticket) for ticket in tickets]}
