# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import llm


def grounded(question: str, answer: str, chunks: list[str]) -> bool:
    context = "\n\n---\n\n".join(chunks)
    prompt = (
        "You are a strict fact-checker.\n"
        f"SOURCES:\n{context}\n\nQUESTION:\n{question}\n\nANSWER TO CHECK:\n{answer}\n\n"
        "Two checks. First: do the SOURCES answer the question that was asked, "
        "not only a related topic? Second: is every factual claim in the answer "
        "supported by the sources? Style phrases and the source line do not count as claims. "
        "Reply one word: yes if both checks pass, otherwise no."
    )
    try:
        verdict = llm.generate(prompt, num_predict=5)
    except llm.LLMBadOutput:
        return False
    return verdict.strip().lower().startswith("yes")
