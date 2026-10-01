import httpx
import pytest

import config
import llm


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=None, response=None)

    def json(self):
        return self._payload


def test_generate_returns_text(monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse({"response": " hello "}))
    assert llm.generate("q", num_predict=5) == "hello"


def test_generate_sends_seed_in_options(monkeypatch):
    sent = {}

    def capture(*_a, **k):
        sent.update(k["json"])
        return FakeResponse({"response": "ok"})
    monkeypatch.setattr(httpx, "post", capture)
    llm.generate("q", num_predict=5)
    assert sent["options"]["seed"] == 42


def test_generate_sends_think_flag(monkeypatch):
    sent = {}

    def capture(*_a, **k):
        sent.update(k["json"])
        return FakeResponse({"response": "ok"})
    monkeypatch.setattr(httpx, "post", capture)
    llm.generate("q", num_predict=5)
    assert sent["think"] is False
    monkeypatch.setattr(config, "LLM_THINK", True)
    llm.generate("q", num_predict=5)
    assert sent["think"] is True


def test_generate_raises_unavailable_on_timeout(monkeypatch):
    monkeypatch.setattr(config, "LLM_RETRIES", 0)

    def timeout(*_a, **_k):
        raise httpx.ReadTimeout("slow")
    monkeypatch.setattr(httpx, "post", timeout)
    with pytest.raises(llm.LLMUnavailable):
        llm.generate("q", num_predict=5)


def test_generate_raises_unavailable_on_http_error(monkeypatch):
    monkeypatch.setattr(config, "LLM_RETRIES", 0)
    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse({}, status=500))
    with pytest.raises(llm.LLMUnavailable):
        llm.generate("q", num_predict=5)


def test_generate_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr(config, "LLM_RETRIES", 1)
    calls = []

    def flaky(*_a, **_k):
        calls.append(1)
        if len(calls) == 1:
            raise httpx.ConnectError("down")
        return FakeResponse({"response": "ok"})
    monkeypatch.setattr(httpx, "post", flaky)
    assert llm.generate("q", num_predict=5) == "ok"
    assert len(calls) == 2


def test_generate_raises_bad_output_on_empty(monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse({"response": "   "}))
    with pytest.raises(llm.LLMBadOutput):
        llm.generate("q", num_predict=5)


def test_generate_json_parses(monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse({"response": '{"label": "refunds"}'}))
    assert llm.generate_json("q", num_predict=5) == {"label": "refunds"}


def test_generate_json_raises_bad_output_on_invalid(monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse({"response": "not json"}))
    with pytest.raises(llm.LLMBadOutput):
        llm.generate_json("q", num_predict=5)


def test_ping_false_when_down(monkeypatch):
    def down(*_a, **_k):
        raise httpx.ConnectError("down")
    monkeypatch.setattr(httpx, "get", down)
    assert llm.ping() is False


def test_ping_true_when_up(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: FakeResponse({}, status=200))
    assert llm.ping() is True
