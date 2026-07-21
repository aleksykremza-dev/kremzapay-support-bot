"""Stage 7: judge (output-rail) — checks the finished answer against sources before sending."""
# [JUDGE] Output guardrail: groundedness fact-check
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("ANSWER_MODEL", "qwen2.5:7b-instruct")


def grounded(answer, chunks):
    """True if every factual claim in the answer is backed by the sources."""
    context = "\n\n---\n\n".join(chunks)
    prompt = (
        "You are a strict fact-checker.\n"
        f"SOURCES:\n{context}\n\nANSWER TO CHECK:\n{answer}\n\n"
        "Is every factual claim in the answer supported by the sources? "
        "Style phrases and the source line do not count as claims. "
        "Reply one word: yes or no."
    )
    r = httpx.post(OLLAMA_URL + "/api/generate",
                   json={"model": MODEL, "prompt": prompt, "stream": False,
                         "options": {"temperature": 0, "num_predict": 5}},
                   timeout=90)
    return r.json().get("response", "").strip().lower().startswith("yes")
