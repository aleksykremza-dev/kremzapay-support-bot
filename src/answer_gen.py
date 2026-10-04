# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import re

import config
import llm
import taxonomy
from search import search

SOURCE_LINE = re.compile(r"^(Źródło|Source):", re.I)
SOURCE_TAIL = re.compile(r"(?:^|\s)(?:Źródło|Source)\s*:\s*([^\n]+)$", re.I)
NO_ANSWER = "NO_ANSWER"
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
        "Do not invent facts, numbers or features. If the excerpts do not "
        f"answer the QUESTION, reply with exactly {NO_ANSWER} and nothing else.\n"
        "End with one line: 'Źródło: <id>' (PL) or 'Source: <id>' (EN) "
        "listing the article id(s) you actually used.\n\n"
        f"EXCERPTS:\n{context}\n\nQUESTION: {question}\n\nANSWER (in {lang_name}):"
    )


def is_no_answer(answer: str) -> bool:
    return answer.strip().upper().startswith(NO_ANSWER)


def _source_lines(answer: str) -> list[str]:
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    found = [line for line in lines if SOURCE_LINE.match(line)]
    tail = SOURCE_TAIL.search(lines[-1]) if lines else None
    if tail and not SOURCE_LINE.match(lines[-1]):
        found.append(tail.group(1))
    return found


def _cited(answer: str, hits: list) -> list:
    lines = _source_lines(answer)
    if not lines:
        return hits
    cited = [hit for hit in hits
             if any(re.search(rf"\b{re.escape(hit.payload['id'])}\b", line) for line in lines)]
    return cited or hits


def _ask(question: str, hits: list, language: str) -> str | None:
    try:
        return llm.generate(_build_prompt(question, hits, language), num_predict=400)
    except llm.LLMBadOutput:
        return None


def generate(question: str, intent: str | None = None, language: str = "en") -> dict | None:
    definitions = taxonomy.intent_definition()
    category = taxonomy.intent_category().get(intent)
    query = f"{question}. {definitions[intent]}" if intent in definitions else question
    hits = search(query, category=category)[:config.TOP_N]
    can_retry = category is not None
    if can_retry and not any(hit.score >= config.RETRIEVAL_OK for hit in hits):
        hits = search(question)[:config.TOP_N]
        can_retry = False
    if not hits:
        return None
    text = _ask(question, hits, language)
    if text is not None and can_retry and is_no_answer(text):
        retry_hits = search(question)[:config.TOP_N]
        if retry_hits:
            hits = retry_hits
            text = _ask(question, hits, language)
    if text is None:
        return None
    sources = [f"{hit.payload['id']} : {hit.payload['title']}" for hit in hits]
    return {"answer": text, "sources": sources, "chunks": [hit.payload["text"] for hit in _cited(text, hits)]}
