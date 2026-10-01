import json
import sys

import config
import eval_cascade


def _row(q, gold, pred, split):
    return {"q": q, "gold": gold, "pred": pred, "action": "answer", "style": "plain",
            "lang": "en", "hit": gold == pred, "split": split}


def test_split_file_has_192_test_and_96_dev_without_overlap():
    with open(config.SPLIT_PATH, encoding="utf-8") as handle:
        split = json.load(handle)
    gold = {case["q"] for case in eval_cascade.load_gold()}
    assert split["seed"] == 42
    assert len(split["test"]) == 192
    assert len(split["dev"]) == 96
    assert set(split["test"]) | set(split["dev"]) == gold
    assert not set(split["test"]) & set(split["dev"])


def test_run_marks_rows_by_split(monkeypatch):
    monkeypatch.setattr(eval_cascade.cascade, "route", lambda text: {
        "decision": {"action": "answer"}, "classification": {"intent": "a", "scope": "in_scope"}})
    cases = [{"q": "one", "expected_intent": "a", "expected_scope": "in_scope"},
             {"q": "two", "expected_intent": "b", "expected_scope": "in_scope"}]
    rows = eval_cascade.run(cases, {"two"})
    assert [row["split"] for row in rows] == ["dev", "test"]


def test_report_has_all_dev_and_test_accuracy():
    rows = [_row("1", "a", "a", "dev"), _row("2", "a", "b", "dev"),
            _row("3", "a", "a", "test"), _row("4", "b", "b", "test"),
            _row("5", "b", "a", "test"), _row("6", "b", "b", "test")]
    report = eval_cascade.build_report(rows, 1.0)
    assert report["accuracy_all"] == 0.667
    assert report["accuracy_dev"] == 0.5
    assert report["accuracy_test"] == 0.75
    assert report["macro_f1_test"] == 0.734


def _main(monkeypatch, tmp_path, rows, threshold):
    monkeypatch.setattr(eval_cascade, "load_gold", lambda: [{"q": row["q"]} for row in rows])
    monkeypatch.setattr(eval_cascade, "load_split", lambda: set())
    monkeypatch.setattr(eval_cascade, "run", lambda cases, test_questions: rows)
    monkeypatch.setattr(sys, "argv", ["eval_cascade.py", "--out", str(tmp_path / "r.json"),
                                      "--min-accuracy", str(threshold)])
    return eval_cascade.main()


def test_threshold_applies_to_test_not_all(monkeypatch, tmp_path):
    rows = [_row(str(i), "a", "a", "dev") for i in range(8)] + \
           [_row("t1", "a", "a", "test"), _row("t2", "a", "b", "test")]
    assert _main(monkeypatch, tmp_path, rows, 0.8) == 1
    rows = [_row(str(i), "a", "b", "dev") for i in range(8)] + \
           [_row("t1", "a", "a", "test"), _row("t2", "b", "b", "test")]
    assert _main(monkeypatch, tmp_path, rows, 0.8) == 0


def test_no_test_rows_fails(monkeypatch, tmp_path):
    rows = [_row("1", "a", "a", "dev")]
    assert _main(monkeypatch, tmp_path, rows, 0.5) == 1
