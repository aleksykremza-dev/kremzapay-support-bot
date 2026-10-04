# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import logging
import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import answer_gen
import cascade
import config
import judge
import knn_router
import llm
import pii
import search
import store

log = logging.getLogger(__name__)


def _warm() -> None:
    for name, warm in (("knn", knn_router.warm), ("search", search.warm)):
        started = time.monotonic()
        try:
            warm()
        except Exception as exc:
            log.error("warmup %s failed, it will load on the first request: %s", name, exc)
            continue
        log.info("warmup %s done in %.1fs", name, time.monotonic() - started)


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    _warm()
    yield


app = FastAPI(title="kremzaPay Support Bot", lifespan=_lifespan)
_slots = threading.BoundedSemaphore(config.MAX_INFLIGHT)
CONTACT_TOKENS = ("<EMAIL_", "<PHONE_")

REPLIES = {
    "handoff": {
        "pl": "Przekazuję rozmowę do konsultanta, zgłoszenie #{tid}. Zostaw e-mail lub telefon, odezwiemy się.",
        "en": "I'm handing this over to a human agent, ticket #{tid}. Leave your e-mail or phone and we'll get back to you.",
    },
    "handoff_added": {
        "pl": "Twoja wiadomość została dodana do zgłoszenia #{tid}.",
        "en": "Your message has been added to ticket #{tid}.",
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


def _ticket_reply(sid: str, lang: str, reason: str, template: str, cls: dict,
                  priority: str = "normal") -> tuple[str, int]:
    tid = store.create_ticket(sid, reason, category=cls.get("scope"), intent=cls.get("intent"),
                              priority=priority)
    return REPLIES[template][lang].format(tid=tid), tid


def _answer(masked: str, sid: str, ts: dict, cls: dict) -> tuple[str, str, int | None]:
    lang = ts["language"]
    generated = answer_gen.generate(masked, intent=cls.get("intent"), language=lang)
    if generated and answer_gen.is_no_answer(generated["answer"]):
        reason, template = "no_knowledge", "ticket_no_knowledge"
    elif generated and judge.grounded(masked, generated["answer"], generated["chunks"]):
        return "answer", generated["answer"], None
    else:
        reason, template = "generation_not_grounded", "ticket_not_grounded"
    ts["decision"] = {"action": "ticket", "reason": reason, "confidence": ts["decision"].get("confidence")}
    reply, ticket_id = _ticket_reply(sid, lang, reason, template, cls)
    return "ticket", reply, ticket_id


def _contacts(mapping: dict[str, str]) -> list[str]:
    return [original for token, original in mapping.items() if token.startswith(CONTACT_TOKENS)]


def _save_contact(ticket_id: int, mapping: dict[str, str]) -> None:
    contacts = _contacts(mapping)
    if contacts:
        store.set_ticket_contact(ticket_id, contacts)


def _handle(masked: str, sid: str, mapping: dict[str, str]) -> ChatOut:
    ts = cascade.route(masked)
    action = ts["decision"]["action"]
    lang = ts["language"]
    cls = ts.get("classification") or {}
    ticket_id = None
    if action == "ticket":
        reply, ticket_id = _ticket_reply(sid, lang, ts["decision"]["reason"], "ticket_no_knowledge", cls)
    elif action == "answer":
        action, reply, ticket_id = _answer(masked, sid, ts, cls)
    elif action == "handoff":
        reply, ticket_id = _ticket_reply(sid, lang, "handoff", "handoff", cls, priority="high")
        store.set_session_status(sid, "handoff")
        _save_contact(ticket_id, mapping)
    else:
        reply = REPLIES[action][lang]
    linked = ticket_id if action == "handoff" else None
    store.add_message(sid, "user", masked, turn_state=ts, ticket_id=linked)
    store.add_message(sid, "bot", reply, ticket_id=linked)
    return ChatOut(session_id=sid, reply=reply, action=action, intent=cls.get("intent"),
                   language=lang, ticket_id=ticket_id, timings_ms=ts["timings_ms"])


def _handoff_followup(sid: str, masked: str, mapping: dict[str, str], ticket_id: int) -> ChatOut:
    lang = cascade.detect_language(masked)
    reply = REPLIES["handoff_added"][lang].format(tid=ticket_id)
    _save_contact(ticket_id, mapping)
    store.add_message(sid, "user", masked, ticket_id=ticket_id)
    store.add_message(sid, "bot", reply, ticket_id=ticket_id)
    return ChatOut(session_id=sid, reply=reply, action="handoff", language=lang, ticket_id=ticket_id)


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
    masked, mapping = pii.mask(msg.text)
    handoff_ticket = store.open_handoff_ticket(sid) if msg.session_id else None
    if handoff_ticket:
        return _handoff_followup(sid, masked, mapping, handoff_ticket)
    if not _slots.acquire(timeout=config.QUEUE_TIMEOUT_S):
        log.warning("overloaded for session %s: no free slot of %d in %.1fs",
                    sid, config.MAX_INFLIGHT, config.QUEUE_TIMEOUT_S)
        return _unavailable(sid, masked, "overloaded", "ticket_overloaded")
    try:
        return _handle(masked, sid, mapping)
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
    return JSONResponse(status_code=503, content=out.model_dump(), headers={"X-Reason": reason})


@app.get("/dashboard")
def dashboard():
    return FileResponse(config.WEB_DIR / "dashboard.html")


@app.get("/api/stats")
def stats():
    return store.get_stats()


@app.post("/api/tickets/{ticket_id}/close")
def close_ticket(ticket_id: int):
    if not store.close_ticket(ticket_id):
        return JSONResponse(status_code=404, content={"detail": f"ticket {ticket_id} not found"})
    return {"id": ticket_id, "status": "closed"}
