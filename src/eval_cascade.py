"""6.7: экзамен каскада на золотом наборе. Метрики: accuracy, macro-F1, OOS-recall, confusion."""
import glob
import json
import os
import time
from collections import Counter, defaultdict

import cascade

# Во что каскад "переводит" свой вердикт для сравнения с ожиданием золотого набора.
ACTION_TO_LABEL = {
    "chitchat_reply": "chitchat",
    "unsafe_refuse": "unsafe",
    "redirect": "out_of_scope",
}


def predicted_label(ts):
    """Единая метка предсказания: спецкласс, handoff или конкретный интент."""
    action = ts["decision"]["action"]
    if action in ACTION_TO_LABEL:
        return ACTION_TO_LABEL[action]
    if action == "handoff":
        return "handoff"
    cls = ts.get("classification") or {}
    if cls.get("scope") == "other_in_scope":
        return "other_in_scope"
    return cls.get("intent") or "unknown"


def load_gold():
    cases = []
    for path in sorted(glob.glob("data/goldset/gold-*.json")):
        cases += json.load(open(path, encoding="utf-8"))["cases"]
    return cases


def f1_scores(rows):
    """Per-label precision/recall/F1 -> macro-F1."""
    labels = {r["gold"] for r in rows} | {r["pred"] for r in rows}
    per = {}
    for lab in labels:
        tp = sum(1 for r in rows if r["gold"] == lab and r["pred"] == lab)
        fp = sum(1 for r in rows if r["gold"] != lab and r["pred"] == lab)
        fn = sum(1 for r in rows if r["gold"] == lab and r["pred"] != lab)
        p = tp / (tp + fp) if tp + fp else 0.0
        rcl = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * p * rcl / (p + rcl) if p + rcl else 0.0
        per[lab] = {"precision": round(p, 3), "recall": round(rcl, 3),
                    "f1": round(f1, 3), "support": tp + fn}
    gold_labels = [l for l in per if per[l]["support"] > 0]
    macro = sum(per[l]["f1"] for l in gold_labels) / len(gold_labels)
    return per, round(macro, 3)


def main():
    gold = load_gold()
    rows, t0 = [], time.time()
    for n, c in enumerate(gold, 1):
        expected = c.get("expected_intent") or c["expected_scope"]
        try:
            ts = cascade.route(c["q"])
            pred = predicted_label(ts)
            action = ts["decision"]["action"]
        except Exception as exc:
            pred, action, ts = "ERROR", "error", {}
            print(f"  ! ошибка на кейсе {n}: {exc}")
        rows.append({"q": c["q"], "gold": expected, "pred": pred, "action": action,
                     "style": c.get("style"), "lang": c.get("lang"),
                     "hit": pred == expected})
        if n % 10 == 0:
            acc = sum(r["hit"] for r in rows) / len(rows)
            print(f"  {n}/{len(gold)}  точность пока: {acc:.0%}  "
                  f"({(time.time()-t0)/60:.1f} мин)")

    per, macro = f1_scores(rows)
    acc = sum(r["hit"] for r in rows) / len(rows)
    special = ["other_in_scope", "out_of_scope", "chitchat", "unsafe"]
    safety = {s: per.get(s, {}).get("recall") for s in special}
    confusions = Counter((r["gold"], r["pred"]) for r in rows if not r["hit"])
    by_style = defaultdict(lambda: [0, 0])
    for r in rows:
        by_style[r["style"]][0] += r["hit"]
        by_style[r["style"]][1] += 1
    actions = Counter(r["action"] for r in rows)

    report = {"total": len(rows), "accuracy": round(acc, 3), "macro_f1": macro,
              "oos_recall": safety, "by_style": {k: f"{v[0]}/{v[1]}" for k, v in by_style.items()},
              "actions": dict(actions),
              "top_confusions": [f"{g} -> {p}: {n}" for (g, p), n in confusions.most_common(15)],
              "per_label": per, "rows": rows,
              "minutes": round((time.time() - t0) / 60, 1)}
    os.makedirs("data/eval", exist_ok=True)
    out = "data/eval/baseline_cascade.json"
    json.dump(report, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("\n" + "=" * 60)
    print(f"ЭКЗАМЕН КАСКАДА: {len(rows)} кейсов за {report['minutes']} мин")
    print(f"  accuracy:  {acc:.1%}")
    print(f"  macro-F1:  {macro}")
    print(f"  OOS-recall (безопасность): {safety}")
    print(f"  по стилям: {report['by_style']}")
    print(f"  решения:   {dict(actions)}")
    print("  топ путаниц:")
    for line in report["top_confusions"][:10]:
        print(f"    {line}")
    print(f"Полный отчёт: {out}")


if __name__ == "__main__":
    main()
