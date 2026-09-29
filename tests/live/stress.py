# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import config

REQUEST_TIMEOUT_S = 180.0
ALLOWED_STATUSES = (200, 503)
REPEAT_COUNT = 100
LONG_TEXT_LENGTH = 5000
CARD_NUMBER = "4111 1111 1111 1111"
REPEATED_QUESTION = "Kiedy dostanę zwrot za zwrócony towar?"

SINGLE_CASES = [
    {"name": "empty_text", "text": ""},
    {"name": "long_text_5000", "text": ("Jak zrobić zwrot za zamówienie opłacone kartą? " * 200)[:LONG_TEXT_LENGTH]},
    {"name": "only_emoji", "text": "🙂🙂🙂"},
    {"name": "mixed_pl_en", "text": "Moja payment została declined, what should I zrobić now?"},
    {"name": "ten_card_numbers", "text": ", ".join([CARD_NUMBER] * 10)},
]


def post_chat(client: httpx.Client, text: str, session_id: str | None = None) -> dict:
    payload: dict = {"text": text}
    if session_id:
        payload["session_id"] = session_id
    try:
        response = client.post("/chat", json=payload)
    except httpx.HTTPError as exc:
        return {"status": 0, "body": None, "error": str(exc)}
    try:
        body = response.json()
    except ValueError as exc:
        return {"status": response.status_code, "body": None, "error": f"not json: {exc}"}
    return {"status": response.status_code, "body": body, "error": None}


def is_well_formed(result: dict) -> bool:
    body = result["body"]
    return isinstance(body, dict) and isinstance(body.get("reply"), str)


def is_ok(result: dict) -> bool:
    return result["status"] in ALLOWED_STATUSES and is_well_formed(result)


def run_single_case(client: httpx.Client, case: dict) -> dict:
    result = post_chat(client, case["text"])
    return {"name": case["name"], "status": result["status"], "error": result["error"],
            "well_formed": is_well_formed(result), "ok": is_ok(result)}


def run_repeated(client: httpx.Client) -> dict:
    statuses: list[int] = []
    malformed = 0
    for _ in range(REPEAT_COUNT):
        result = post_chat(client, REPEATED_QUESTION)
        statuses.append(result["status"])
        if not is_well_formed(result):
            malformed += 1
    counts = {str(status): statuses.count(status) for status in sorted(set(statuses))}
    ok = all(status in ALLOWED_STATUSES for status in statuses) and malformed == 0
    return {"name": f"repeated_{REPEAT_COUNT}", "status_counts": counts, "malformed": malformed,
            "status": max(statuses) if statuses else 0, "error": None, "well_formed": malformed == 0,
            "ok": ok}


def run_session_reuse(client: httpx.Client) -> dict:
    first = post_chat(client, "How do I pay with BLIK?")
    session_id = first["body"].get("session_id") if is_well_formed(first) else None
    second = post_chat(client, "And with a card?", session_id=session_id) if session_id else first
    same_session = bool(session_id) and is_well_formed(second) and second["body"].get("session_id") == session_id
    return {"name": "session_id_reuse", "status": second["status"], "error": second["error"],
            "session_id": session_id, "same_session": same_session,
            "well_formed": is_well_formed(second), "ok": is_ok(first) and is_ok(second) and same_session}


def fetch_health(client: httpx.Client) -> dict:
    try:
        response = client.get("/health")
        return {"status": response.status_code, "body": response.json(), "error": None}
    except (httpx.HTTPError, ValueError) as exc:
        return {"status": 0, "body": None, "error": str(exc)}


def write_report(report: dict) -> Path:
    out = config.REPORTS_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-stress.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8020"))
    args = parser.parse_args()

    with httpx.Client(base_url=args.url, timeout=REQUEST_TIMEOUT_S) as client:
        rows = [run_single_case(client, case) for case in SINGLE_CASES]
        rows.append(run_repeated(client))
        rows.append(run_session_reuse(client))
        health = fetch_health(client)
    failed = [row["name"] for row in rows if not row["ok"]]
    report = {"total": len(rows), "failed": failed, "health": health, "rows": rows}
    out = write_report(report)

    for row in rows:
        mark = "ok" if row["ok"] else "FAIL"
        print(f"{mark:<4} {row['name']:<20} status={row['status']} well_formed={row['well_formed']}")
    print(f"health: {health['status']} {health['body']}")
    print(f"cases: {report['total']}  failed: {len(failed)}")
    print(f"Report: {out}")
    print("Manual step: stop Qdrant and re-run to see 503 + health degraded")
    if failed:
        print(f"FAIL: {failed}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
