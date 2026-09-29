# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import llm


def grounded(answer: str, chunks: list[str]) -> bool:
    context = "\n\n---\n\n".join(chunks)
    prompt = (
        "You are a strict fact-checker.\n"
        f"SOURCES:\n{context}\n\nANSWER TO CHECK:\n{answer}\n\n"
        "Is every factual claim in the answer supported by the sources? "
        "Style phrases and the source line do not count as claims. "
        "Reply one word: yes or no."
    )
    try:
        verdict = llm.generate(prompt, num_predict=5)
    except llm.LLMBadOutput:
        return False
    return verdict.strip().lower().startswith("yes")
