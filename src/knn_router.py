# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import hashlib
import json
import logging
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

import config
import embeddings

log = logging.getLogger(__name__)

_embedder = None
_vectors = None
_model = None


def _load_corpus() -> list[dict]:
    cases: list[dict] = []
    for path in sorted(config.CORPUS_DIR.glob("corpus-*.json")):
        with open(path, encoding="utf-8") as handle:
            cases += json.load(handle)["cases"]
    return cases


def cache_key(model: str, cases: list[dict], c_value: float) -> str:
    digest = hashlib.sha256(f"{model}\n{c_value}\n".encode("utf-8"))
    for case in cases:
        digest.update(f"{case['intent']}\t{case['q']}\n".encode("utf-8"))
    return digest.hexdigest()[:16]


def _embed(texts: list[str]) -> np.ndarray:
    prefixed = embeddings.prefixed(config.ROUTER_EMBED_MODEL, texts, "query")
    vectors = np.array(list(_embedder.embed(prefixed)), dtype=np.float32)
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def _fit(vectors: np.ndarray, labels: list[str]) -> dict:
    clf = LogisticRegression(C=config.CLF_C, max_iter=3000).fit(vectors, np.array(labels))
    return {"coef": clf.coef_, "intercept": clf.intercept_, "classes": clf.classes_}


def probabilities(params: dict, vectors: np.ndarray) -> np.ndarray:
    logits = vectors @ params["coef"].T + params["intercept"]
    logits -= logits.max(axis=1, keepdims=True)
    exp = np.exp(logits)
    return exp / exp.sum(axis=1, keepdims=True)


def _index_name() -> str:
    return f"router-{cache_key(config.ROUTER_EMBED_MODEL, _load_corpus(), config.CLF_C)}.npz"


def _read(path: Path) -> bool:
    global _vectors, _model
    if not path.exists():
        return False
    with np.load(path, allow_pickle=False) as stored:
        _vectors = stored["vectors"]
        _model = {name: stored[name] for name in ("coef", "intercept", "classes")}
    log.info("router index loaded: %s", path)
    return True


def _write(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, vectors=_vectors, coef=_model["coef"], intercept=_model["intercept"],
                        classes=_model["classes"].astype(str))
    return path


def _ensure_index() -> None:
    global _embedder, _vectors, _model
    if _model is not None:
        return
    if _embedder is None:
        _embedder = embeddings.model(config.ROUTER_EMBED_MODEL)
    name = _index_name()
    if _read(config.INDEX_DIR / name) or _read(config.CACHE_DIR / name):
        return
    cases = _load_corpus()
    log.info("indexing corpus: %d examples with %s", len(cases), config.ROUTER_EMBED_MODEL)
    _vectors = _embed([case["q"] for case in cases])
    _model = _fit(_vectors, [case["intent"] for case in cases])
    log.info("router cache written: %s", _write(config.CACHE_DIR / name))


def warm() -> None:
    _ensure_index()


def export_index(index_dir: Path) -> Path:
    _ensure_index()
    return _write(index_dir / _index_name())


def ranked(proba: np.ndarray, classes: np.ndarray) -> list[tuple[str, float]]:
    order = np.argsort(-proba)[:config.LLM_CANDIDATES]
    return [(str(classes[i]), float(proba[i])) for i in order]


def decide(top: list[tuple[str, float]], max_sim: float) -> dict:
    intent, prob = top[0]
    if max_sim < config.T_OOS:
        return {"layer": 1, "decision": "oos_candidate", "intent": None,
                "confidence": max_sim, "top": top}
    decision = "accepted" if prob >= config.P_ACCEPT else "grey"
    return {"layer": 1, "decision": decision, "intent": intent, "confidence": prob, "top": top}


def classify(text: str) -> dict:
    _ensure_index()
    query = _embed([text])
    max_sim = float((_vectors @ query[0]).max())
    proba = probabilities(_model, query)[0]
    return decide(ranked(proba, _model["classes"]), max_sim)
