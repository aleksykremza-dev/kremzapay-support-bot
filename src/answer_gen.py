# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import re

import config
import llm
import taxonomy
from search import search

SOURCE_LINE = re.compile(r"^(Źródło|Source):", re.I)
BRAND_VOICE = (
    "You are the kremzaPay support assistant. Style: warm but concise, "
    "address the user informally ('ty' in Polish, 'you' in English), "
    "no corporate jargon, no exclamation marks, short paragraphs or numbered "
    "steps. Always answer in {lang_name}."
)


def _build_prompt(question: str, hits: list, language: str) -> str:
    context = "\n\n---\n\n".join(
        f"[{hit.payload['id']} : {hit.payload['title']}]\n{hit.payload['text']}" for hit in hits
    )
    lang_name = "Polish" if language == "pl" else "English"
    return (
        BRAND_VOICE.format(lang_name=lang_name) + "\n\n"
        "Answer the QUESTION using ONLY the documentation excerpts below. "
        "Do not invent facts, numbers or features. If the excerpts are not "
        "enough, say so plainly.\n"
        "End with one line: 'Źródło: <id>' (PL) or 'Source: <id>' (EN) "
        "listing the article id(s) you actually used.\n\n"
        f"EXCERPTS:\n{context}\n\nQUESTION: {question}\n\nANSWER (in {lang_name}):"
    )


def _cited(answer: str, hits: list) -> list:
    lines = [line for line in answer.splitlines() if SOURCE_LINE.match(line.strip())]
    if not lines:
        return hits
    cited = [hit for hit in hits
             if any(re.search(rf"\b{re.escape(hit.payload['id'])}\b", line) for line in lines)]
    return cited or hits


def generate(question: str, intent: str | None = None, language: str = "en") -> dict | None:
    definitions = taxonomy.intent_definition()
    category = taxonomy.intent_category().get(intent)
    query = f"{question}. {definitions[intent]}" if intent in definitions else question
    hits = search(query, category=category)[:config.TOP_N]
    if not hits:
        return None
    try:
        text = llm.generate(_build_prompt(question, hits, language), num_predict=400)
    except llm.LLMBadOutput:
        return None
    sources = [f"{hit.payload['id']} : {hit.payload['title']}" for hit in hits]
    return {"answer": text, "sources": sources, "chunks": [hit.payload["text"] for hit in _cited(text, hits)]}
