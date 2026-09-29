# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import config
import taxonomy


def load_cases(directory: Path, pattern: str) -> list[dict]:
    cases: list[dict] = []
    for path in sorted(directory.glob(pattern)):
        with open(path, encoding="utf-8") as handle:
            cases += json.load(handle)["cases"]
    return cases


def gold_label(case: dict) -> str:
    return case.get("expected_intent") or case["expected_scope"]


def count_labels(labels: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    return counts


def build_rows(corpus_counts: dict[str, int], gold_counts: dict[str, int], min_corpus: int) -> list[dict]:
    label_ids = [item["id"] for item in taxonomy.intents()] + list(taxonomy.special())
    rows = []
    for label in label_ids:
        corpus = corpus_counts.get(label, 0)
        gold = gold_counts.get(label, 0)
        rows.append({"intent": label, "corpus": corpus, "gold": gold,
                     "below": corpus < min_corpus or gold == 0})
    return rows


def print_table(rows: list[dict]) -> None:
    width = max(len(row["intent"]) for row in rows)
    print(f"{'intent':<{width}} | corpus questions | gold questions")
    for row in rows:
        print(f"{row['intent']:<{width}} | {row['corpus']:>16} | {row['gold']:>14}")


def write_report(report: dict) -> Path:
    out = config.REPORTS_DIR / f"{datetime.now():%Y-%m-%d-%H%M}-question-coverage.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-corpus", type=int, default=20)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    corpus_counts = count_labels([case["intent"] for case in load_cases(config.CORPUS_DIR, "corpus-*.json")])
    gold_counts = count_labels([gold_label(case) for case in load_cases(config.GOLD_DIR, "gold-*.json")])
    rows = build_rows(corpus_counts, gold_counts, args.min_corpus)
    below = [row["intent"] for row in rows if row["below"]]
    report = {"min_corpus": args.min_corpus, "labels": len(rows),
              "corpus_total": sum(corpus_counts.values()), "gold_total": sum(gold_counts.values()),
              "below_threshold": below, "rows": rows}
    out = write_report(report)

    print_table(rows)
    print(f"labels: {report['labels']}  corpus: {report['corpus_total']}  gold: {report['gold_total']}")
    print(f"below threshold (corpus < {args.min_corpus} or gold == 0): {below}")
    print(f"Report: {out}")
    if args.strict and below:
        print("FAIL: coverage below threshold")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
