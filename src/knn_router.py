# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import json
import logging

import numpy as np
from fastembed import TextEmbedding

import config

log = logging.getLogger(__name__)

_embedder = None
_vectors = None
_labels = None


def _load_corpus() -> list[dict]:
    cases: list[dict] = []
    for path in sorted(config.CORPUS_DIR.glob("corpus-*.json")):
        with open(path, encoding="utf-8") as handle:
            cases += json.load(handle)["cases"]
    return cases


def _ensure_index() -> None:
    global _embedder, _vectors, _labels
    if _vectors is not None:
        return
    _embedder = TextEmbedding(config.EMBED_MODEL)
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    vectors_path = config.CACHE_DIR / "corpus_vectors.npy"
    labels_path = config.CACHE_DIR / "corpus_labels.json"
    if vectors_path.exists() and labels_path.exists():
        _vectors = np.load(vectors_path)
        with open(labels_path, encoding="utf-8") as handle:
            _labels = json.load(handle)
        return
    cases = _load_corpus()
    log.info("indexing corpus: %d examples", len(cases))
    texts = [case["q"] for case in cases]
    _vectors = np.array([vector for vector in _embedder.embed(texts)], dtype=np.float32)
    _vectors /= np.linalg.norm(_vectors, axis=1, keepdims=True)
    _labels = [case["intent"] for case in cases]
    np.save(vectors_path, _vectors)
    with open(labels_path, "w", encoding="utf-8") as handle:
        json.dump(_labels, handle)
    log.info("corpus cache written: %s", vectors_path)


def warm() -> None:
    _ensure_index()


def classify(text: str) -> dict:
    _ensure_index()
    query = np.array(list(_embedder.embed([text]))[0], dtype=np.float32)
    query /= np.linalg.norm(query)
    sims = _vectors @ query
    top_idx = np.argsort(sims)[-config.K:][::-1]
    top = [(_labels[i], float(sims[i])) for i in top_idx]

    votes: dict[str, list[float]] = {}
    for label, sim in top:
        votes.setdefault(label, []).append(sim)
    winner = max(votes, key=lambda label: (len(votes[label]), sum(votes[label])))
    win_conf = sum(votes[winner]) / len(votes[winner])
    max_sim = top[0][1]

    if max_sim < config.T_OOS:
        return {"layer": 1, "decision": "oos_candidate", "intent": None,
                "confidence": max_sim, "top": top}
    if win_conf >= config.T_ACCEPT and len(votes[winner]) >= config.K // 2:
        return {"layer": 1, "decision": "accepted", "intent": winner,
                "confidence": win_conf, "top": top}
    return {"layer": 1, "decision": "grey", "intent": winner,
            "confidence": win_conf, "top": top}
