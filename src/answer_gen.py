# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import difflib
import re

import config
import llm
from search import search

SOURCE_LINE = re.compile(r"^(Źródło|Source)\s*:", re.I)
LABEL_TAIL = re.compile(r"(?:^|\s)(\S+)\s*:\s*([^:\n]+)$")
ID_TOKEN = re.compile(r"[^\s,;]+")
ID_MATCH_CUTOFF = 0.8
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


def _match_id(token: str, ids: list[str]) -> str | None:
    clean = token.strip(".`'\"[]()<>").lower().replace("_", "-")
    if clean in ids:
        return clean
    close = difflib.get_close_matches(clean, ids, n=1, cutoff=ID_MATCH_CUTOFF)
    return close[0] if close else None


def _ids_in(text: str, ids: list[str]) -> list[str]:
    return [found for found in (_match_id(token, ids) for token in ID_TOKEN.findall(text)) if found]


def _split_source(answer: str, ids: list[str]) -> tuple[str, list[str]]:
    body, cited = [], []
    for line in answer.strip().splitlines():
        if SOURCE_LINE.match(line.strip()):
            cited += _ids_in(SOURCE_LINE.sub("", line.strip()), ids)
        else:
            body.append(line)
    while body and not body[-1].strip():
        body.pop()
    tail = LABEL_TAIL.search(body[-1]) if body else None
    if tail:
        tokens = ID_TOKEN.findall(tail.group(2))
        found = [_match_id(token, ids) for token in tokens]
        if tokens and all(found):
            cited += found
            body[-1] = body[-1][:tail.start()].rstrip()
    return "\n".join(body).rstrip(), list(dict.fromkeys(cited))


def _with_source(answer: str, hits: list, language: str) -> tuple[str, list]:
    ids = [hit.payload["id"] for hit in hits]
    body, cited = _split_source(answer, ids)
    cited = cited or ids[:1]
    label = "Źródło" if language == "pl" else "Source"
    return f"{body}\n\n{label}: {', '.join(cited)}", [hit for hit in hits if hit.payload["id"] in cited]


def _ask(question: str, hits: list, language: str) -> str | None:
    try:
        return llm.generate(_build_prompt(question, hits, language), num_predict=400)
    except llm.LLMBadOutput:
        return None


def generate(question: str, language: str = "en") -> dict | None:
    hits = search(question)[:config.TOP_N]
    if not hits:
        return None
    text = _ask(question, hits, language)
    if text is None:
        return None
    sources = [f"{hit.payload['id']} : {hit.payload['title']}" for hit in hits]
    if is_no_answer(text):
        return {"answer": text, "sources": sources, "chunks": [hit.payload["text"] for hit in hits]}
    text, cited = _with_source(text, hits, language)
    return {"answer": text, "sources": sources, "chunks": [hit.payload["text"] for hit in cited]}
