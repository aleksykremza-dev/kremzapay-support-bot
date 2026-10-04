# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import time
import uuid
from contextlib import contextmanager

import config
import knn_router
import llm_classifier
import rules
from search import search

SPECIAL_ACTIONS = {
    "chitchat": "chitchat_reply",
    "unsafe": "unsafe_refuse",
    "out_of_scope": "redirect",
    "other_in_scope": "ticket",
}

PL_WORDS = {"jak", "czy", "gdzie", "nie", "moge", "mogę", "zwrot", "platnosc",
            "płatność", "wyplata", "wypłata", "dzien", "dzień", "prosze", "proszę"}


def detect_language(text: str) -> str:
    lowered = text.lower()
    if any(ch in "ąćęłńóśźż" for ch in lowered):
        return "pl"
    if set(lowered.replace("?", " ").replace("!", " ").split()) & PL_WORDS:
        return "pl"
    return "en"


@contextmanager
def _timed(ts: dict, key: str):
    started = time.monotonic()
    yield
    ts["timings_ms"][key] = round((time.monotonic() - started) * 1000, 1)


def _retrieval_signal(text: str) -> float:
    hits = search(text)
    return float(hits[0].score) if hits else 0.0


def _layer0(ts: dict) -> bool:
    with _timed(ts, "rules"):
        ts["rules"] = rules.check(ts["raw_text"])
    if not ts["rules"]:
        return False
    ts["decision"] = {"action": ts["rules"]["action"], "reason": ts["rules"]["reason"],
                      "confidence": "high"}
    return True


def _candidates(top: list[tuple[str, float]]) -> list[tuple[str, float]]:
    unique: dict[str, float] = {}
    for label, sim in top:
        unique.setdefault(label, sim)
    return list(unique.items())[:config.LLM_CANDIDATES]


def _classify(ts: dict) -> tuple:
    with _timed(ts, "knn"):
        knn = knn_router.classify(ts["raw_text"])
    ts["knn"] = {key: knn[key] for key in ("decision", "intent", "confidence")}
    if knn["decision"] == "accepted":
        intent = knn["intent"]
        scope = intent if intent in SPECIAL_ACTIONS else "in_scope"
        conf = "high" if knn["confidence"] >= config.CONF_HIGH else "medium"
        wants_human = False
    else:
        with _timed(ts, "llm"):
            verdict = llm_classifier.classify(ts["raw_text"], _candidates(knn["top"]))
        ts["llm"] = {key: verdict.get(key) for key in
                     ("intent", "scope", "confidence", "wants_human", "sentiment", "reasoning")}
        intent, scope, conf = verdict["intent"], verdict["scope"], verdict["confidence"]
        if scope == "other_in_scope" and knn["top"] and knn["top"][0][0] == "out_of_scope":
            intent = scope = "out_of_scope"
        wants_human = bool(verdict.get("wants_human", False))
    ts["classification"] = {"intent": intent, "scope": scope, "confidence": conf}
    return intent, scope, conf, wants_human


def _decide(ts: dict, scope: str, conf: str, wants_human: bool) -> None:
    if wants_human:
        ts["decision"] = {"action": "handoff", "reason": "wants_human", "confidence": conf}
        return
    if scope in SPECIAL_ACTIONS:
        ts["decision"] = {"action": SPECIAL_ACTIONS[scope], "reason": scope, "confidence": conf}
        return
    if conf == "low":
        ts["decision"] = {"action": "clarify", "reason": "low_confidence", "confidence": conf}
        return
    with _timed(ts, "retrieval"):
        top_score = _retrieval_signal(ts["raw_text"])
    ts["retrieval"] = {"top_score": round(top_score, 3)}
    if top_score >= config.RETRIEVAL_OK:
        ts["decision"] = {"action": "answer", "reason": "ok", "confidence": conf}
    else:
        ts["decision"] = {"action": "ticket", "reason": "no_knowledge", "confidence": conf}


def route(text: str) -> dict:
    ts = {"turn_id": str(uuid.uuid4())[:8], "raw_text": text,
          "language": detect_language(text), "timings_ms": {}}
    if _layer0(ts):
        return ts
    _intent, scope, conf, wants_human = _classify(ts)
    _decide(ts, scope, conf, wants_human)
    return ts
