import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

_spec = importlib.util.spec_from_file_location(
    "knn_router_real", Path(__file__).resolve().parent.parent / "src" / "knn_router.py")
knn_router = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(knn_router)

CLASSES = np.array(["chitchat", "payout_schedule", "refund_how_to"])


class FakeEmbedder:
    calls = 0

    def __init__(self, *_args, **_kwargs):
        self.seen = []

    def embed(self, texts, **_kwargs):
        FakeEmbedder.calls += 1
        for text in texts:
            self.seen.append(text)
            base = {"r": [1.0, 0.1, 0.0], "p": [0.0, 1.0, 0.1], "c": [0.1, 0.0, 1.0]}
            yield np.array(base[text.split()[-1][0]], dtype=np.float32) + 0.01 * len(text)


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    cases = ([{"q": f"zwrot {i} r", "intent": "refund_how_to"} for i in range(6)]
             + [{"q": f"wyplata {i} p", "intent": "payout_schedule"} for i in range(6)]
             + [{"q": f"hej {i} c", "intent": "chitchat"} for i in range(6)])
    (corpus_dir / "corpus-a1.json").write_text(json.dumps({"cases": cases}), encoding="utf-8")
    monkeypatch.setattr(knn_router.config, "CORPUS_DIR", corpus_dir)
    monkeypatch.setattr(knn_router.config, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(knn_router.config, "INDEX_DIR", tmp_path / "no-index")
    monkeypatch.setattr(knn_router.config, "ROUTER_EMBED_MODEL", "fake/model")
    monkeypatch.setattr(knn_router, "TextEmbedding", FakeEmbedder)
    monkeypatch.setattr(knn_router, "_embedder", None)
    monkeypatch.setattr(knn_router, "_vectors", None)
    monkeypatch.setattr(knn_router, "_model", None)
    FakeEmbedder.calls = 0
    return cases


def test_decide_accepts_confident_top_intent(monkeypatch):
    monkeypatch.setattr(knn_router.config, "P_ACCEPT", 0.6)
    monkeypatch.setattr(knn_router.config, "T_OOS", 0.45)
    verdict = knn_router.decide([("refund_how_to", 0.7), ("payout_schedule", 0.2)], max_sim=0.8)
    assert verdict["decision"] == "accepted"
    assert verdict["intent"] == "refund_how_to"
    assert verdict["confidence"] == 0.7
    assert verdict["top"] == [("refund_how_to", 0.7), ("payout_schedule", 0.2)]


def test_decide_grey_below_accept_threshold(monkeypatch):
    monkeypatch.setattr(knn_router.config, "P_ACCEPT", 0.6)
    monkeypatch.setattr(knn_router.config, "T_OOS", 0.45)
    verdict = knn_router.decide([("refund_how_to", 0.5), ("payout_schedule", 0.4)], max_sim=0.8)
    assert verdict["decision"] == "grey"
    assert verdict["intent"] == "refund_how_to"


def test_decide_oos_candidate_on_low_similarity(monkeypatch):
    monkeypatch.setattr(knn_router.config, "P_ACCEPT", 0.6)
    monkeypatch.setattr(knn_router.config, "T_OOS", 0.45)
    verdict = knn_router.decide([("refund_how_to", 0.9)], max_sim=0.3)
    assert verdict["decision"] == "oos_candidate"
    assert verdict["intent"] is None


def test_ranked_orders_by_probability_and_limits(monkeypatch):
    monkeypatch.setattr(knn_router.config, "LLM_CANDIDATES", 2)
    ranked = knn_router.ranked(np.array([0.2, 0.5, 0.3]), CLASSES)
    assert ranked == [("payout_schedule", 0.5), ("refund_how_to", 0.3)]


def test_probabilities_match_sklearn():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(30, 4)).astype(np.float32)
    y = np.array(["a", "b", "c"] * 10)
    clf = LogisticRegression(C=4.0, max_iter=2000).fit(x, y)
    params = {"coef": clf.coef_, "intercept": clf.intercept_, "classes": clf.classes_}
    np.testing.assert_allclose(knn_router.probabilities(params, x[:5]), clf.predict_proba(x[:5]), atol=1e-5)


def test_cache_key_depends_on_model_corpus_and_c():
    cases = [{"q": "a", "intent": "x"}]
    base = knn_router.cache_key("m1", cases, 16.0)
    assert base == knn_router.cache_key("m1", [{"q": "a", "intent": "x"}], 16.0)
    assert base != knn_router.cache_key("m2", cases, 16.0)
    assert base != knn_router.cache_key("m1", [{"q": "a", "intent": "y"}], 16.0)
    assert base != knn_router.cache_key("m1", cases, 4.0)


def test_index_is_fitted_once_then_loaded_from_cache(corpus, monkeypatch):
    knn_router.warm()
    files = sorted(path.name for path in knn_router.config.CACHE_DIR.iterdir())
    key = knn_router.cache_key("fake/model", corpus, knn_router.config.CLF_C)
    assert files == [f"router-{key}.npz"]
    first = knn_router.classify("zwrot pieniedzy r")
    monkeypatch.setattr(knn_router, "_vectors", None)
    monkeypatch.setattr(knn_router, "_model", None)
    monkeypatch.setattr(knn_router, "_fit", lambda *_args: pytest.fail("refit despite cache"))
    calls_before = FakeEmbedder.calls
    second = knn_router.classify("zwrot pieniedzy r")
    assert FakeEmbedder.calls == calls_before + 1
    assert first["top"] == second["top"]
    assert second["top"][0][0] == "refund_how_to"


def test_tracked_index_is_used_without_embedding_corpus(corpus, tmp_path, monkeypatch):
    index_dir = tmp_path / "index"
    written = knn_router.export_index(index_dir)
    key = knn_router.cache_key("fake/model", corpus, knn_router.config.CLF_C)
    assert written == index_dir / f"router-{key}.npz"
    for path in knn_router.config.CACHE_DIR.iterdir():
        path.unlink()
    monkeypatch.setattr(knn_router.config, "INDEX_DIR", index_dir)
    monkeypatch.setattr(knn_router, "_vectors", None)
    monkeypatch.setattr(knn_router, "_model", None)
    monkeypatch.setattr(knn_router, "_fit", lambda *_args: pytest.fail("refit despite tracked index"))
    calls_before = FakeEmbedder.calls
    verdict = knn_router.classify("wyplata kiedy p")
    assert FakeEmbedder.calls == calls_before + 1
    assert verdict["top"][0][0] == "payout_schedule"
    assert list(knn_router.config.CACHE_DIR.iterdir()) == []


def test_stale_tracked_index_is_ignored_and_cache_rebuilt(corpus, tmp_path, monkeypatch):
    index_dir = tmp_path / "index"
    index_dir.mkdir()
    (index_dir / "router-0000000000000000.npz").write_bytes(b"stale")
    monkeypatch.setattr(knn_router.config, "INDEX_DIR", index_dir)
    knn_router.warm()
    key = knn_router.cache_key("fake/model", corpus, knn_router.config.CLF_C)
    assert (knn_router.config.CACHE_DIR / f"router-{key}.npz").exists()
    assert knn_router.classify("hej c")["top"][0][0] == "chitchat"


def test_query_prefix_is_applied_for_e5(corpus, monkeypatch):
    monkeypatch.setattr(knn_router.config, "ROUTER_EMBED_MODEL", "intfloat/multilingual-e5-large")
    knn_router.warm()
    knn_router.classify("hej c")
    assert knn_router._embedder.seen[-1] == "query: hej c"
    assert knn_router._embedder.seen[0].startswith("query: ")
