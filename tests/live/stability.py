# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import config

REQUEST_TIMEOUT_S = 180.0
PROCESS_PATTERN = "uvicorn api:app"
KB_PER_MB = 1024

QUESTIONS = [
    "How do I pay for my order with BLIK?",
    "Kiedy dostanę zwrot za zwrócony towar?",
    "When are payouts to my bank account sent?",
    "Jak podłączyć bramkę do sklepu na WooCommerce?",
]


def find_candidate_pids() -> list[int]:
    completed = subprocess.run(["pgrep", "-f", PROCESS_PATTERN], capture_output=True, text=True)
    return [int(line) for line in completed.stdout.split() if line.strip().isdigit()]


def read_rss_mb(pid: int) -> float:
    with open(f"/proc/{pid}/status", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return round(int(line.split()[1]) / KB_PER_MB, 1)
    raise RuntimeError(f"VmRSS not found for pid {pid}")


def count_open_fds(pid: int) -> int:
    return len(os.listdir(f"/proc/{pid}/fd"))


def resolve_pid(explicit: int | None) -> int:
    if explicit:
        return explicit
    candidates = find_candidate_pids()
    if not candidates:
        raise RuntimeError(f"no process matching '{PROCESS_PATTERN}', pass --pid")
    return max(candidates, key=read_rss_mb)


def send_probe(client: httpx.Client, text: str) -> tuple[int, float]:
    started = time.monotonic()
    try:
        status = client.post("/chat", json={"text": text}).status_code
    except httpx.HTTPError:
        status = 0
    return status, round((time.monotonic() - started) * 1000, 1)


def take_sample(client: httpx.Client, pid: int, index: int, started: float) -> dict:
    status, latency_ms = send_probe(client, QUESTIONS[index % len(QUESTIONS)])
    return {"elapsed_s": round(time.monotonic() - started, 1), "status": status,
            "latency_ms": latency_ms, "rss_mb": read_rss_mb(pid), "fds": count_open_fds(pid)}


def print_row(sample: dict) -> None:
    minute = sample["elapsed_s"] / 60
    print(f"{minute:6.1f} min  status={sample['status']}  latency={sample['latency_ms']} ms  "
          f"rss={sample['rss_mb']} MB  fds={sample['fds']}")


def run_loop(client: httpx.Client, pid: int, minutes: float, interval_s: float) -> list[dict]:
    samples: list[dict] = []
    started = time.monotonic()
    deadline = started + minutes * 60
    last_logged_minute = -1
    while True:
        sample = take_sample(client, pid, len(samples), started)
        samples.append(sample)
        current_minute = int(sample["elapsed_s"] // 60)
        if current_minute != last_logged_minute:
            print_row(sample)
            last_logged_minute = current_minute
        if time.monotonic() + interval_s > deadline:
            return samples
        time.sleep(interval_s)


def summarize(samples: list[dict], max_growth_mb: float) -> dict:
    rss_values = [sample["rss_mb"] for sample in samples]
    growth = round(max(rss_values) - rss_values[0], 1) if rss_values else 0.0
    server_errors = sum(1 for sample in samples if sample["status"] >= 500)
    transport_errors = sum(1 for sample in samples if sample["status"] == 0)
    return {"samples": len(samples), "rss_start_mb": rss_values[0] if rss_values else 0.0,
            "rss_max_mb": max(rss_values) if rss_values else 0.0, "rss_growth_mb": growth,
            "fds_start": samples[0]["fds"] if samples else 0, "fds_max": max(s["fds"] for s in samples) if samples else 0,
            "server_errors": server_errors, "transport_errors": transport_errors,
            "growth_ok": growth <= max_growth_mb}


def write_report(report: dict) -> Path:
    out = config.REPORTS_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-stability.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8020"))
    parser.add_argument("--minutes", type=float, default=60)
    parser.add_argument("--interval-s", type=float, default=20)
    parser.add_argument("--pid", type=int, default=None)
    parser.add_argument("--max-rss-growth-mb", type=float, default=200)
    args = parser.parse_args()

    pid = resolve_pid(args.pid)
    print(f"monitoring pid {pid} for {args.minutes} min every {args.interval_s} s")
    with httpx.Client(base_url=args.url, timeout=REQUEST_TIMEOUT_S) as client:
        samples = run_loop(client, pid, args.minutes, args.interval_s)
    summary = summarize(samples, args.max_rss_growth_mb)
    report = {"pid": pid, "minutes": args.minutes, "interval_s": args.interval_s,
              "max_rss_growth_mb": args.max_rss_growth_mb, **summary, "rows": samples}
    out = write_report(report)

    print(f"samples: {summary['samples']}  rss: {summary['rss_start_mb']} -> {summary['rss_max_mb']} MB "
          f"(growth {summary['rss_growth_mb']} MB)  fds: {summary['fds_start']} -> {summary['fds_max']}")
    print(f"server errors: {summary['server_errors']}  transport errors: {summary['transport_errors']}")
    print(f"Report: {out}")
    if summary["server_errors"]:
        print(f"FAIL: {summary['server_errors']} requests returned 5xx")
        return 1
    if not summary["growth_ok"]:
        print(f"FAIL: RSS growth {summary['rss_growth_mb']} MB above {args.max_rss_growth_mb} MB")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
