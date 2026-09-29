# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import cascade
import config

ACTION_TO_LABEL = {
    "chitchat_reply": "chitchat",
    "unsafe_refuse": "unsafe",
    "redirect": "out_of_scope",
}
SPECIAL = ["other_in_scope", "out_of_scope", "chitchat", "unsafe"]


def predicted_label(ts: dict) -> str:
    action = ts["decision"]["action"]
    if action in ACTION_TO_LABEL:
        return ACTION_TO_LABEL[action]
    if action == "handoff":
        return "handoff"
    cls = ts.get("classification") or {}
    if cls.get("scope") == "other_in_scope":
        return "other_in_scope"
    return cls.get("intent") or "unknown"


def load_gold() -> list[dict]:
    cases: list[dict] = []
    for path in sorted(config.GOLD_DIR.glob("gold-*.json")):
        with open(path, encoding="utf-8") as handle:
            cases += json.load(handle)["cases"]
    return cases


def f1_scores(rows: list[dict]) -> tuple[dict, float]:
    labels = {row["gold"] for row in rows} | {row["pred"] for row in rows}
    per = {}
    for label in labels:
        tp = sum(1 for row in rows if row["gold"] == label and row["pred"] == label)
        fp = sum(1 for row in rows if row["gold"] != label and row["pred"] == label)
        fn = sum(1 for row in rows if row["gold"] == label and row["pred"] != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per[label] = {"precision": round(precision, 3), "recall": round(recall, 3),
                      "f1": round(f1, 3), "support": tp + fn}
    gold_labels = [label for label in per if per[label]["support"] > 0]
    macro = sum(per[label]["f1"] for label in gold_labels) / len(gold_labels)
    return per, round(macro, 3)


def run(cases: list[dict]) -> list[dict]:
    rows, started = [], time.time()
    for number, case in enumerate(cases, 1):
        expected = case.get("expected_intent") or case["expected_scope"]
        try:
            ts = cascade.route(case["q"])
            pred, action = predicted_label(ts), ts["decision"]["action"]
        except Exception as exc:
            pred, action = "ERROR", "error"
            print(f"  error on case {number}: {exc}")
        rows.append({"q": case["q"], "gold": expected, "pred": pred, "action": action,
                     "style": case.get("style"), "lang": case.get("lang"), "hit": pred == expected})
        if number % 10 == 0:
            accuracy = sum(row["hit"] for row in rows) / len(rows)
            print(f"  {number}/{len(cases)}  accuracy so far: {accuracy:.0%}  "
                  f"({(time.time() - started) / 60:.1f} min)")
    return rows


def build_report(rows: list[dict], minutes: float) -> dict:
    per, macro = f1_scores(rows)
    accuracy = sum(row["hit"] for row in rows) / len(rows)
    confusions = Counter((row["gold"], row["pred"]) for row in rows if not row["hit"])
    by_style: dict = defaultdict(lambda: [0, 0])
    for row in rows:
        by_style[row["style"]][0] += row["hit"]
        by_style[row["style"]][1] += 1
    return {"total": len(rows), "accuracy": round(accuracy, 3), "macro_f1": macro,
            "oos_recall": {label: per.get(label, {}).get("recall") for label in SPECIAL},
            "by_style": {key: f"{value[0]}/{value[1]}" for key, value in by_style.items()},
            "actions": dict(Counter(row["action"] for row in rows)),
            "top_confusions": [f"{gold} -> {pred}: {count}" for (gold, pred), count in confusions.most_common(15)],
            "per_label": per, "rows": rows, "minutes": round(minutes, 1)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--min-accuracy", type=float, default=config.MIN_ACCURACY)
    args = parser.parse_args()

    cases = load_gold()
    if args.limit:
        cases = cases[:args.limit]
    started = time.time()
    rows = run(cases)
    report = build_report(rows, (time.time() - started) / 60)

    out = args.out or config.REPORTS_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-accuracy.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)

    print("=" * 60)
    print(f"CASCADE EXAM: {report['total']} cases in {report['minutes']} min")
    print(f"  accuracy:  {report['accuracy']:.1%}")
    print(f"  macro-F1:  {report['macro_f1']}")
    print(f"  OOS-recall: {report['oos_recall']}")
    print(f"  decisions: {report['actions']}")
    for line in report["top_confusions"][:10]:
        print(f"    {line}")
    print(f"Report: {out}")
    if report["accuracy"] < args.min_accuracy:
        print(f"FAIL: accuracy {report['accuracy']} below {args.min_accuracy}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
