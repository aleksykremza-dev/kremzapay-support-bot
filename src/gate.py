"""Gate: первый слой обороны. Вердикты: answer / ticket / off_topic."""
import os
import sys

import httpx
from dotenv import load_dotenv

from search import search

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("ANSWER_MODEL", "qwen2.5:7b-instruct")
SCORE_THRESHOLD = 0.45
TOP_N_CONTEXT = 3


def ask_yes_no(prompt):
    """Один вопрос модели, ответ одним словом yes/no (температура 0)."""
    r = httpx.post(
        OLLAMA_URL + "/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": False,
              "options": {"temperature": 0, "num_predict": 5}},
        timeout=60,
    )
    return r.json().get("response", "").strip().lower().startswith("yes")


def build_context(hits):
    return "\n\n---\n\n".join(h.payload["text"] for h in hits[:TOP_N_CONTEXT])


def check_grounded(question, hits):
    """Хватает ли найденных кусков для строгого ответа."""
    return ask_yes_no(
        "Excerpts from documentation:\n" + build_context(hits) +
        f"\n\nQuestion: {question}\n\n"
        "Can a support agent answer this question using ONLY these excerpts? "
        "Note: if the excerpts list all available options and the asked "
        "thing is not among them, answering that it is not offered IS a "
        "valid answer. Reply with one word: yes or no."
    )


def is_on_topic(question):
    """Вопрос вообще про платежи/наш сервис?"""
    return ask_yes_no(
        f"Question from a user: {question}\n\n"
        "Is this question related to online payments, refunds, payouts, "
        "e-commerce or the kremzaPay payment service? "
        "Reply with one word: yes or no."
    )


def decide(question):
    """Вердикт первого слоя обороны."""
    hits = search(question)
    top_score = hits[0].score if hits else 0.0
    if top_score >= SCORE_THRESHOLD:
        if check_grounded(question, hits):
            return {"action": "answer", "reason": "ok", "top_score": top_score, "hits": hits}
        return {"action": "ticket", "reason": "not_grounded", "top_score": top_score, "hits": hits}
    if is_on_topic(question):
        return {"action": "ticket", "reason": "low_score", "top_score": top_score, "hits": hits}
    return {"action": "off_topic", "reason": "off_topic", "top_score": top_score, "hits": hits}


def main():
    question = " ".join(sys.argv[1:]) or "How do I refund a payment?"
    verdict = decide(question)
    print(f"Вопрос: {question}")
    print(f"Лучший score: {verdict['top_score']:.3f}  (порог {SCORE_THRESHOLD})")
    labels = {
        "answer": "→ отвечаю сам из базы",
        "ticket": f"→ предлагаю оформить обращение, тикет в очередь (причина: {verdict['reason']})",
        "off_topic": "→ редирект: «задайте, пожалуйста, вопрос про платежи» (без очереди)",
    }
    print("РЕШЕНИЕ:", labels[verdict["action"]])


if __name__ == "__main__":
    main()
