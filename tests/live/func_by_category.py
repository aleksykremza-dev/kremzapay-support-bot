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
import taxonomy

SPECIAL_ACTIONS = {
    "chitchat": "chitchat_reply",
    "unsafe": "unsafe_refuse",
    "out_of_scope": "redirect",
    "other_in_scope": "ticket",
}
REQUEST_TIMEOUT_S = 180.0


def load_gold() -> list[dict]:
    cases: list[dict] = []
    for path in sorted(config.GOLD_DIR.glob("gold-*.json")):
        with open(path, encoding="utf-8") as handle:
            cases += json.load(handle)["cases"]
    return cases


def pick_intent_cases(cases: list[dict], intent_id: str, limit: int) -> list[dict]:
    matched = [case for case in cases
               if case.get("expected_intent") == intent_id and case.get("expected_scope") == "in_scope"]
    return matched[:limit]


def pick_special_cases(cases: list[dict], special_id: str, limit: int) -> list[dict]:
    matched = [case for case in cases if case.get("expected_scope") == special_id]
    return matched[:limit]


def ask(client: httpx.Client, text: str) -> dict:
    try:
        response = client.post("/chat", json={"text": text})
        body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        return {"status": 0, "action": "error", "intent": None, "error": str(exc)}
    return {"status": response.status_code, "action": body.get("action"),
            "intent": body.get("intent"), "error": None}


def check_intent(client: httpx.Client, intent_id: str, case: dict) -> dict:
    result = ask(client, case["q"])
    return {"label": intent_id, "kind": "intent", "q": case["q"], "expected": intent_id,
            "got": result["intent"], "action": result["action"], "status": result["status"],
            "ok": result["intent"] == intent_id}


def check_special(client: httpx.Client, special_id: str, case: dict) -> dict:
    result = ask(client, case["q"])
    expected = SPECIAL_ACTIONS[special_id]
    return {"label": special_id, "kind": "special", "q": case["q"], "expected": expected,
            "got": result["action"], "action": result["action"], "status": result["status"],
            "ok": result["action"] == expected}


def run_all(client: httpx.Client, cases: list[dict], per_intent: int) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    missing: list[str] = []
    for item in taxonomy.intents():
        picked = pick_intent_cases(cases, item["id"], per_intent)
        if not picked:
            missing.append(item["id"])
        rows += [check_intent(client, item["id"], case) for case in picked]
    for special_id in taxonomy.special():
        picked = pick_special_cases(cases, special_id, per_intent)
        if not picked:
            missing.append(special_id)
        rows += [check_special(client, special_id, case) for case in picked]
    return rows, missing


def print_table(rows: list[dict]) -> None:
    width = max(len(row["label"]) for row in rows) if rows else 10
    print(f"{'intent':<{width}} | {'expected':<28} | {'got':<28} | ok")
    for row in rows:
        mark = "ok" if row["ok"] else "FAIL"
        print(f"{row['label']:<{width}} | {row['expected']:<28} | {str(row['got']):<28} | {mark}")


def build_report(rows: list[dict], missing: list[str]) -> dict:
    intent_rows = [row for row in rows if row["kind"] == "intent"]
    special_rows = [row for row in rows if row["kind"] == "special"]
    intent_hits = sum(1 for row in intent_rows if row["ok"])
    accuracy = intent_hits / len(intent_rows) if intent_rows else 0.0
    return {"total": len(rows), "passed": sum(1 for row in rows if row["ok"]),
            "intent_total": len(intent_rows), "intent_hits": intent_hits,
            "intent_accuracy": round(accuracy, 3),
            "special_total": len(special_rows),
            "special_failed": [row["label"] for row in special_rows if not row["ok"]],
            "intents_without_gold": missing, "rows": rows}


def write_report(report: dict) -> Path:
    out = config.REPORTS_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-func-by-category.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8020"))
    parser.add_argument("--per-intent", type=int, default=1)
    parser.add_argument("--min-intent-accuracy", type=float, default=0.6)
    args = parser.parse_args()

    cases = load_gold()
    with httpx.Client(base_url=args.url, timeout=REQUEST_TIMEOUT_S) as client:
        rows, missing = run_all(client, cases, args.per_intent)
    report = build_report(rows, missing)
    out = write_report(report)

    print_table(rows)
    print(f"cases: {report['total']}  passed: {report['passed']}")
    print(f"intent accuracy: {report['intent_accuracy']:.1%} ({report['intent_hits']}/{report['intent_total']})")
    print(f"special failed: {report['special_failed']}")
    print(f"intents without gold question: {missing}")
    print(f"Report: {out}")
    if report["special_failed"]:
        print("FAIL: special class case failed")
        return 1
    if report["intent_accuracy"] < args.min_intent_accuracy:
        print(f"FAIL: intent accuracy {report['intent_accuracy']} below {args.min_intent_accuracy}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
