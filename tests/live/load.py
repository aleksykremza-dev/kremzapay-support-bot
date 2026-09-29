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
        error = None
    except httpx.HTTPError as exc:
        status = TRANSPORT_ERROR_STATUS
        error = str(exc)
    latency_ms = round((time.monotonic() - started) * 1000, 1)
    return {"text": text, "status": status, "latency_ms": latency_ms, "error": error}


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


def summarize(results: list[dict], elapsed_s: float) -> dict:
    latencies = [row["latency_ms"] for row in results]
    server_errors = sum(1 for row in results if row["status"] >= 500)
    transport_errors = sum(1 for row in results if row["status"] == TRANSPORT_ERROR_STATUS)
    errors = server_errors + transport_errors
    return {"requests": len(results), "elapsed_s": round(elapsed_s, 2),
            "requests_per_s": round(len(results) / elapsed_s, 2) if elapsed_s else 0.0,
            "p50_ms": percentile(latencies, 0.5), "p95_ms": percentile(latencies, 0.95),
            "max_ms": max(latencies) if latencies else 0.0,
            "server_errors": server_errors, "transport_errors": transport_errors,
            "error_rate": round(errors / len(results), 3) if results else 0.0,
            "status_counts": count_statuses(results)}


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8020"))
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--p95-ms", type=float, default=15000)
    args = parser.parse_args()

    results, elapsed_s = run_load(args.url, args.users, args.requests)
    summary = summarize(results, elapsed_s)
    report = {"users": args.users, "p95_threshold_ms": args.p95_ms, **summary, "rows": results}
    out = write_report(report)

    print(f"requests: {summary['requests']}  users: {args.users}  elapsed: {summary['elapsed_s']}s")
    print(f"p50: {summary['p50_ms']} ms  p95: {summary['p95_ms']} ms  max: {summary['max_ms']} ms")
    print(f"error rate: {summary['error_rate']:.1%}  requests/sec: {summary['requests_per_s']}")
    print(f"status counts: {summary['status_counts']}")
    print(f"Report: {out}")
    if summary["server_errors"] or summary["transport_errors"]:
        print(f"FAIL: {summary['server_errors']} server errors, {summary['transport_errors']} transport errors")
        return 1
    if summary["p95_ms"] > args.p95_ms:
        print(f"FAIL: p95 {summary['p95_ms']} ms above {args.p95_ms} ms")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
