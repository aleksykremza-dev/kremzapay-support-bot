import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("live_stability", Path(__file__).parent / "live" / "stability.py")
stability = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(stability)


def _sample(fds, rss_mb=1000.0, status=200):
    return {"elapsed_s": 0.0, "status": status, "latency_ms": 100.0, "rss_mb": rss_mb, "fds": fds}


def test_fd_growth_is_max_minus_start():
    summary = stability.summarize([_sample(13), _sample(23), _sample(15)], max_growth_mb=200, max_fd_growth=50)
    assert summary["fds_growth"] == 10
    assert summary["fds_ok"] is True


def test_gate_fails_when_fd_growth_above_limit():
    summary = stability.summarize([_sample(13), _sample(23)], max_growth_mb=200, max_fd_growth=0)
    assert summary["fds_ok"] is False
    assert any("open files" in reason for reason in stability.failures(summary, max_growth_mb=200, max_fd_growth=0))


def test_gate_passes_on_flat_fds_and_rss():
    summary = stability.summarize([_sample(13), _sample(13)], max_growth_mb=200, max_fd_growth=0)
    assert stability.failures(summary, max_growth_mb=200, max_fd_growth=0) == []


def test_gate_still_fails_on_5xx_and_rss_growth():
    summary = stability.summarize([_sample(13, 1000.0), _sample(13, 1300.0, 500)], max_growth_mb=200, max_fd_growth=50)
    reasons = stability.failures(summary, max_growth_mb=200, max_fd_growth=50)
    assert any("5xx" in reason for reason in reasons)
    assert any("RSS" in reason for reason in reasons)


def test_cli_default_fd_growth_limit_is_50():
    args = stability.build_parser().parse_args([])
    assert (args.minutes, args.max_rss_growth_mb, args.max_fd_growth) == (60, 200, 50)
