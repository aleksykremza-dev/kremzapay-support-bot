# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import logging
import threading

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import answer_gen
import cascade
import config
import judge
import llm
import pii
import search
import store

log = logging.getLogger(__name__)
app = FastAPI(title="kremzaPay Support Bot")
_slots = threading.BoundedSemaphore(config.MAX_INFLIGHT)

REPLIES = {
    "handoff": {
        "pl": "Przekazuję rozmowę do konsultanta. Zostaw wiadomość, odezwiemy się.",
        "en": "I'm handing this over to a human agent. Leave a message and we'll get back to you.",
    },
    "chitchat_reply": {
        "pl": "Miło mi! Jestem botem wsparcia kremzaPay, chętnie pomogę z płatnościami, zwrotami czy wypłatami. W czym mogę pomóc?",
        "en": "Nice to meet you! I'm the kremzaPay support bot, happy to help with payments, refunds or payouts. What can I do for you?",
    },
    "unsafe_refuse": {
        "pl": "Nie mogę pomóc w tej sprawie. Jeśli masz pytanie o płatności kremzaPay, chętnie odpowiem.",
        "en": "I can't help with that. If you have a question about kremzaPay payments, I'm happy to help.",
    },
    "redirect": {
        "pl": "Pomagam wyłącznie w sprawach płatności kremzaPay (płatności, zwroty, wypłaty, integracja). Zadaj proszę pytanie z tego zakresu.",
        "en": "I only help with kremzaPay payment matters (payments, refunds, payouts, integration). Please ask a question in that area.",
    },
    "clarify": {
        "pl": "Chcę dobrze zrozumieć sprawę. Możesz doprecyzować, czego dokładnie dotyczy pytanie?",
        "en": "I want to get this right. Could you clarify what exactly your question is about?",
    },
    "ticket_no_knowledge": {
        "pl": "Nie znalazłem pełnej odpowiedzi w dokumentacji, więc utworzyłem zgłoszenie #{tid}. Zespół wróci do Ciebie.",
        "en": "I couldn't find a complete answer, so I've created ticket #{tid}. Our team will get back to you.",
    },
    "ticket_not_grounded": {
        "pl": "Nie mogę teraz odpowiedzieć rzetelnie na to pytanie, więc utworzyłem zgłoszenie #{tid}. Zespół wróci do Ciebie.",
        "en": "I can't answer this reliably right now, so I've created ticket #{tid}. Our team will get back to you.",
    },
    "ticket_service_down": {
        "pl": "Usługa jest chwilowo niedostępna, przekazałem sprawę do zespołu, zgłoszenie #{tid}.",
        "en": "The service is temporarily unavailable, I've passed this to the team, ticket #{tid}.",
    },
    "ticket_overloaded": {
        "pl": "Usługa jest teraz przeciążona, przekazałem sprawę do zespołu, zgłoszenie #{tid}.",
        "en": "The service is overloaded right now, I've passed this to the team, ticket #{tid}.",
    },
}


class ChatIn(BaseModel):
    text: str
    session_id: str | None = None


class ChatOut(BaseModel):
    session_id: str
    reply: str
    action: str
    intent: str | None = None
    language: str
    ticket_id: int | None = None
    timings_ms: dict[str, float] = {}


class HealthOut(BaseModel):
    status: str
    ollama: bool
    qdrant: bool


def _ticket_reply(sid: str, lang: str, reason: str, template: str, cls: dict) -> tuple[str, int]:
    tid = store.create_ticket(sid, reason, category=cls.get("scope"), intent=cls.get("intent"))
    return REPLIES[template][lang].format(tid=tid), tid


def _handle(masked: str, sid: str) -> ChatOut:
    ts = cascade.route(masked)
    action = ts["decision"]["action"]
    lang = ts["language"]
    cls = ts.get("classification") or {}
    ticket_id = None
    if action == "ticket":
        reply, ticket_id = _ticket_reply(sid, lang, ts["decision"]["reason"], "ticket_no_knowledge", cls)
    elif action == "answer":
        generated = answer_gen.generate(masked, intent=cls.get("intent"), language=lang)
        if generated and judge.grounded(generated["answer"], generated["chunks"]):
            reply = generated["answer"]
        else:
            action = "ticket"
            ts["decision"] = {"action": action, "reason": "generation_not_grounded",
                              "confidence": ts["decision"].get("confidence")}
            reply, ticket_id = _ticket_reply(sid, lang, "generation_not_grounded", "ticket_not_grounded", cls)
    else:
        reply = REPLIES[action][lang]
    store.add_message(sid, "user", masked, turn_state=ts)
    store.add_message(sid, "bot", reply)
    return ChatOut(session_id=sid, reply=reply, action=action, intent=cls.get("intent"),
                   language=lang, ticket_id=ticket_id, timings_ms=ts["timings_ms"])


@app.get("/")
def page():
    return FileResponse(config.WEB_DIR / "index.html")


@app.get("/health", response_model=HealthOut)
def health():
    ollama_ok = llm.ping()
    qdrant_ok = search.ping()
    status = "ok" if ollama_ok and qdrant_ok else "degraded"
    return HealthOut(status=status, ollama=ollama_ok, qdrant=qdrant_ok)


@app.post("/chat", response_model=ChatOut, responses={503: {"model": ChatOut}})
def chat(msg: ChatIn):
    sid = msg.session_id or store.create_session("web")
    masked, _mapping = pii.mask(msg.text)
    if not _slots.acquire(timeout=config.QUEUE_TIMEOUT_S):
        log.warning("overloaded for session %s: no free slot of %d in %.1fs",
                    sid, config.MAX_INFLIGHT, config.QUEUE_TIMEOUT_S)
        return _unavailable(sid, masked, "overloaded", "ticket_overloaded")
    try:
        return _handle(masked, sid)
    except (llm.LLMUnavailable, search.SearchUnavailable) as exc:
        log.error("service unavailable for session %s: %s", sid, exc)
        return _unavailable(sid, masked, "service_unavailable", "ticket_service_down")
    finally:
        _slots.release()


def _unavailable(sid: str, masked: str, reason: str, template: str) -> JSONResponse:
    lang = cascade.detect_language(masked)
    reply, tid = _ticket_reply(sid, lang, reason, template, {})
    store.add_message(sid, "user", masked)
    store.add_message(sid, "bot", reply)
    out = ChatOut(session_id=sid, reply=reply, action="ticket", language=lang, ticket_id=tid)
    return JSONResponse(status_code=503, content=out.model_dump())


@app.get("/dashboard")
def dashboard():
    return FileResponse(config.WEB_DIR / "dashboard.html")


@app.get("/api/stats")
def stats():
    return store.get_stats()
