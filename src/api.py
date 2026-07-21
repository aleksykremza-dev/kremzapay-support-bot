"""Этап 9: HTTP API. Конвейер: PII-маскер -> каскад -> ветка ответа -> хранилище."""
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

import answer_gen
import cascade
import judge
import pii
import store

app = FastAPI(title="kremzaPay Support Bot")

REPLIES = {
    "handoff": {"pl": "Przekazuję rozmowę do konsultanta. Zostaw wiadomość — odezwiemy się.",
                "en": "I'm handing this over to a human agent. Leave a message and we'll get back to you."},
    "chitchat_reply": {"pl": "Miło mi! Jestem botem wsparcia kremzaPay — chętnie pomogę z płatnościami, zwrotami czy wypłatami. W czym mogę pomóc?",
                       "en": "Nice to meet you! I'm the kremzaPay support bot — happy to help with payments, refunds or payouts. What can I do for you?"},
    "unsafe_refuse": {"pl": "Nie mogę pomóc w tej sprawie. Jeśli masz pytanie o płatności kremzaPay — chętnie odpowiem.",
                      "en": "I can't help with that. If you have a question about kremzaPay payments, I'm happy to help."},
    "redirect": {"pl": "Pomagam wyłącznie w sprawach płatności kremzaPay (płatności, zwroty, wypłaty, integracja). Zadaj proszę pytanie z tego zakresu.",
                 "en": "I only help with kremzaPay payment matters (payments, refunds, payouts, integration). Please ask a question in that area."},
    "clarify": {"pl": "Chcę dobrze zrozumieć sprawę — możesz doprecyzować, czego dokładnie dotyczy pytanie?",
                "en": "I want to get this right — could you clarify what exactly your question is about?"},
}


class ChatIn(BaseModel):
    text: str
    session_id: str | None = None


@app.get("/")
def page():
    return FileResponse("web/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(msg: ChatIn):
    sid = msg.session_id or store.create_session("web")
    masked, mapping = pii.mask(msg.text)
    ts = cascade.route(masked)
    action = ts["decision"]["action"]
    lang = ts["language"]

    if action == "ticket":
        cls = ts.get("classification") or {}
        tid = store.create_ticket(sid, ts["decision"]["reason"],
                                  category=cls.get("scope"), intent=cls.get("intent"))
        reply = (f"Nie znalazłem pełnej odpowiedzi w dokumentacji, więc utworzyłem zgłoszenie #{tid}. "
                 f"Zespół wróci do Ciebie." if lang == "pl" else
                 f"I couldn't find a complete answer, so I've created ticket #{tid}. "
                 f"Our team will get back to you.")
    elif action == "answer":
        cls = ts.get("classification") or {}
        gen = answer_gen.generate(masked, intent=cls.get("intent"), language=lang)
        if gen and judge.grounded(gen["answer"], gen["chunks"]):
            reply = gen["answer"]
        else:
            tid = store.create_ticket(sid, "generation_not_grounded",
                                      intent=cls.get("intent"))
            reply = (f"Nie mogę teraz odpowiedzieć rzetelnie na to pytanie, więc "
                     f"utworzyłem zgłoszenie #{tid} — zespół wróci do Ciebie."
                     if lang == "pl" else
                     f"I can't answer this reliably right now, so I've created "
                     f"ticket #{tid} — our team will get back to you.")
    else:
        reply = REPLIES[action][lang]

    store.add_message(sid, "user", masked, turn_state=ts)
    store.add_message(sid, "bot", reply)
    return {"session_id": sid, "reply": reply,
            "debug": {"action": action, "intent": (ts.get("classification") or {}).get("intent"),
                      "language": lang, "timings_ms": ts["timings_ms"]}}


@app.get("/dashboard")
def dashboard():
    return FileResponse("web/dashboard.html")


@app.get("/api/stats")
def stats():
    return store.get_stats()
