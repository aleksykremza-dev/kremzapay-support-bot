import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location("live_load", Path(__file__).parent / "live" / "load.py")
load = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(load)


def _row(status, latency_ms=1000.0, reason=None):
    return {"text": "q", "status": status, "latency_ms": latency_ms, "reason": reason, "error": None}


def _summary(rows):
    return load.summarize(rows, elapsed_s=10.0)


def test_overloaded_503_is_degraded_not_server_error():
    summary = _summary([_row(200), _row(503, 50.0, "overloaded")])
    assert summary["degraded"] == 1
    assert summary["degraded_rate"] == 0.5
    assert summary["server_errors"] == 0


def test_503_with_other_reason_is_server_error():
    summary = _summary([_row(200), _row(503, 50.0, "service_unavailable")])
    assert summary["degraded"] == 0
    assert summary["server_errors"] == 1


def test_500_is_server_error():
    assert _summary([_row(200), _row(500)])["server_errors"] == 1


def test_p95_counts_only_successful_responses():
    rows = [_row(200, 1000.0)] * 19 + [_row(200, 2000.0)] + [_row(503, 1.0, "overloaded")] * 20
    summary = _summary(rows)
    assert summary["ok"] == 20
    assert summary["p95_ms"] == 1000.0
    assert summary["p50_ms"] == 1000.0


def test_gate_passes_when_degraded_share_within_limit():
    summary = _summary([_row(200)] * 8 + [_row(503, 50.0, "overloaded")] * 2)
    assert load.failures(summary, p95_ms=60000, max_degraded=0.3) == []


def test_gate_fails_when_degraded_share_above_limit():
    summary = _summary([_row(200)] * 8 + [_row(503, 50.0, "overloaded")] * 2)
    assert any("degraded" in reason for reason in load.failures(summary, p95_ms=60000, max_degraded=0.0))


@pytest.mark.parametrize("row", [_row(500), _row(503, 50.0, "service_unavailable"), _row(0, 180000.0)])
def test_gate_fails_on_server_or_transport_error(row):
    summary = _summary([_row(200)] * 9 + [row])
    assert load.failures(summary, p95_ms=60000, max_degraded=0.3)


def test_gate_fails_when_p95_of_successful_above_limit():
    summary = _summary([_row(200, 70000.0)] * 10)
    assert any("p95" in reason for reason in load.failures(summary, p95_ms=60000, max_degraded=0.3))


def test_gate_fails_without_successful_responses():
    summary = _summary([_row(503, 50.0, "overloaded")] * 2)
    assert load.failures(summary, p95_ms=60000, max_degraded=1.0)


def test_cli_defaults_are_five_users_and_60s_p95():
    args = load.build_parser().parse_args([])
    assert (args.users, args.requests, args.p95_ms, args.max_degraded) == (5, 100, 60000, 0.3)


def test_makefile_test_load_runs_three_users_with_default_thresholds():
    makefile = (Path(__file__).parents[1] / "Makefile").read_text(encoding="utf-8")
    recipe = makefile.split("test-load:")[1].split("\n\n")[0]
    assert "tests/live/load.py --users 3" in recipe
    assert "--p95-ms" not in recipe and "--max-degraded" not in recipe
