# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import argparse
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import config

REQUEST_TIMEOUT_S = 180.0
TRANSPORT_ERROR_STATUS = 0
DEGRADED_REASON = "overloaded"

QUESTIONS = [
    "How do I pay for my order with BLIK?",
    "Płatność kartą została odrzucona, co mam zrobić?",
    "Money left my account but the shop says the order is unpaid.",
    "Kiedy dostanę zwrot za zwrócony towar?",
    "How do I cancel a recurring payment tied to my card?",
    "Jak podłączyć bramkę do sklepu na WooCommerce?",
    "When are payouts to my bank account sent?",
    "Jakie są prowizje od transakcji kartą?",
    "How do I issue a refund from the merchant panel?",
    "Gdzie znajdę klucze API do integracji?",
]


def send_one(client: httpx.Client, text: str) -> dict:
    started = time.monotonic()
    try:
        response = client.post("/chat", json={"text": text})
        status = response.status_code
        reason = response.headers.get("x-reason")
        error = None
    except httpx.HTTPError as exc:
        status = TRANSPORT_ERROR_STATUS
        reason = None
        error = str(exc)
    latency_ms = round((time.monotonic() - started) * 1000, 1)
    return {"text": text, "status": status, "latency_ms": latency_ms, "reason": reason, "error": error}


def run_load(url: str, users: int, requests: int) -> tuple[list[dict], float]:
    texts = [QUESTIONS[index % len(QUESTIONS)] for index in range(requests)]
    started = time.monotonic()
    with httpx.Client(base_url=url, timeout=REQUEST_TIMEOUT_S) as client:
        with ThreadPoolExecutor(max_workers=users) as pool:
            results = list(pool.map(lambda text: send_one(client, text), texts))
    return results, time.monotonic() - started


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def outcome(row: dict) -> str:
    if row["status"] == TRANSPORT_ERROR_STATUS:
        return "transport_error"
    if row["status"] == 503 and row.get("reason") == DEGRADED_REASON:
        return "degraded"
    if row["status"] >= 500:
        return "server_error"
    if row["status"] == 200:
        return "ok"
    return "other"


def summarize(results: list[dict], elapsed_s: float) -> dict:
    outcomes = [outcome(row) for row in results]
    ok_latencies = [row["latency_ms"] for row, kind in zip(results, outcomes) if kind == "ok"]
    total = len(results)
    degraded = outcomes.count("degraded")
    return {"requests": total, "elapsed_s": round(elapsed_s, 2),
            "requests_per_s": round(total / elapsed_s, 2) if elapsed_s else 0.0,
            "ok": outcomes.count("ok"), "degraded": degraded,
            "degraded_rate": round(degraded / total, 3) if total else 0.0,
            "server_errors": outcomes.count("server_error"),
            "transport_errors": outcomes.count("transport_error"), "other": outcomes.count("other"),
            "p50_ms": percentile(ok_latencies, 0.5), "p95_ms": percentile(ok_latencies, 0.95),
            "max_ms": max(ok_latencies) if ok_latencies else 0.0,
            "status_counts": count_statuses(results)}


def failures(summary: dict, p95_ms: float, max_degraded: float) -> list[str]:
    found = []
    if summary["server_errors"] or summary["transport_errors"] or summary["other"]:
        found.append(f"{summary['server_errors']} server errors, {summary['transport_errors']} transport errors, "
                     f"{summary['other']} other statuses")
    if summary["degraded_rate"] > max_degraded:
        found.append(f"degraded share {summary['degraded_rate']} above {max_degraded}")
    if not summary["ok"]:
        found.append("no successful 200 responses")
    elif summary["p95_ms"] > p95_ms:
        found.append(f"p95 of 200 responses {summary['p95_ms']} ms above {p95_ms} ms")
    return found


def count_statuses(results: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in results:
        key = str(row["status"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def write_report(report: dict) -> Path:
    out = config.REPORTS_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-load.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8020"))
    parser.add_argument("--users", type=int, default=5)
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--p95-ms", type=float, default=60000)
    parser.add_argument("--max-degraded", type=float, default=0.3)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    results, elapsed_s = run_load(args.url, args.users, args.requests)
    summary = summarize(results, elapsed_s)
    report = {"users": args.users, "p95_threshold_ms": args.p95_ms, "max_degraded": args.max_degraded,
              **summary, "rows": results}
    out = write_report(report)

    print(f"requests: {summary['requests']}  users: {args.users}  elapsed: {summary['elapsed_s']}s")
    print(f"ok: {summary['ok']}  degraded (503 {DEGRADED_REASON}): {summary['degraded']} "
          f"({summary['degraded_rate']:.1%}, limit {args.max_degraded:.0%})")
    print(f"server errors: {summary['server_errors']}  transport errors: {summary['transport_errors']}  "
          f"other: {summary['other']}")
    print(f"p50: {summary['p50_ms']} ms  p95: {summary['p95_ms']} ms  max: {summary['max_ms']} ms (200 only)")
    print(f"status counts: {summary['status_counts']}  requests/sec: {summary['requests_per_s']}")
    print(f"Report: {out}")
    found = failures(summary, args.p95_ms, args.max_degraded)
    for reason in found:
        print(f"FAIL: {reason}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
