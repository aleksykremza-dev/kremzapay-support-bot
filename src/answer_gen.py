"""Этап 7: генерация ответа из найденных кусков. Голос бренда — в BRAND_VOICE."""
import json
import os

import httpx
from dotenv import load_dotenv

from search import search

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("ANSWER_MODEL", "qwen2.5:7b-instruct")
TOP_N = 3

# Голос бренда — правь свободно, это лицо kremzaPay.
BRAND_VOICE = (
    "You are the kremzaPay support assistant. Style: warm but concise, "
    "address the user informally ('ty' in Polish, 'you' in English), "
    "no corporate jargon, no exclamation marks, short paragraphs or numbered "
    "steps. Always answer in {lang_name}."
)

_tax = json.load(open("data/taxonomy.json", encoding="utf-8"))
INTENT_CATEGORY = {i["id"]: i["category"] for i in _tax["intents"]}
INTENT_DEF = {i["id"]: i["definition"] for i in _tax["intents"]}


def generate(question, intent=None, language="en"):
    """Возвращает {'answer', 'sources', 'chunks'} или None при пустом retrieval."""
    category = INTENT_CATEGORY.get(intent)
    # Подмешиваем определение интента в запрос: якорит поиск на основной статье
    # темы, а не на её крайних случаях (баг «zwrot -> статья про 180 дней»).
    query = f"{question}. {INTENT_DEF[intent]}" if intent in INTENT_DEF else question
    hits = search(query, category=category)[:TOP_N]
    if not hits:
        return None
    context = "\n\n---\n\n".join(
        f"[{h.payload['id']} — {h.payload['title']}]\n{h.payload['text']}" for h in hits
    )
    lang_name = "Polish" if language == "pl" else "English"
    prompt = (
        BRAND_VOICE.format(lang_name=lang_name) + "\n\n"
        "Answer the QUESTION using ONLY the documentation excerpts below. "
        "Do not invent facts, numbers or features. If the excerpts are not "
        "enough, say so plainly.\n"
        "End with one line: 'Źródło: <id>' (PL) or 'Source: <id>' (EN) "
        "listing the article id(s) you actually used.\n\n"
        f"EXCERPTS:\n{context}\n\nQUESTION: {question}\n\nANSWER (in {lang_name}):"
    )
    r = httpx.post(OLLAMA_URL + "/api/generate",
                   json={"model": MODEL, "prompt": prompt, "stream": False,
                         "options": {"temperature": 0, "num_predict": 400}},
                   timeout=120)
    text = r.json().get("response", "").strip()
    if not text:
        return None
    sources = [f"{h.payload['id']} — {h.payload['title']}" for h in hits]
    return {"answer": text, "sources": sources,
            "chunks": [h.payload["text"] for h in hits]}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "jak zrobic zwrot?"
    result = generate(q, intent="refund_how", language="pl")
    print(result["answer"] if result else "retrieval пуст")
    if result:
        print("\nИсточники:", "; ".join(result["sources"]))
