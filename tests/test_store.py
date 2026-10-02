import sqlite3

import pytest

import config
import store


@pytest.fixture
def opened(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    connections = []
    real_connect = sqlite3.connect

    def tracking(*args, **kwargs):
        connection = real_connect(*args, **kwargs)
        connections.append(connection)
        return connection
    monkeypatch.setattr(store.sqlite3, "connect", tracking)
    return connections


def _assert_all_closed(connections):
    assert connections
    for connection in connections:
        with pytest.raises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")


def test_every_store_function_closes_its_connection(opened):
    sid = store.create_session("web")
    store.add_message(sid, "user", "pytanie", turn_state={"decision": {"action": "ticket"}, "timings_ms": {}})
    store.create_ticket(sid, "no_knowledge")
    store.get_stats()
    assert len(opened) == 4
    _assert_all_closed(opened)


def test_writes_are_committed_before_close(opened):
    sid = store.create_session("web")
    ticket_id = store.create_ticket(sid, "overloaded")
    stats = store.get_stats()
    assert stats["sessions"] == 1
    assert stats["tickets"][0]["id"] == ticket_id
    assert stats["tickets"][0]["reason"] == "overloaded"


def test_connection_closed_when_query_fails(opened):
    with pytest.raises(sqlite3.Error):
        with store._conn() as connection:
            connection.execute("SELECT * FROM missing_table")
    _assert_all_closed(opened)
