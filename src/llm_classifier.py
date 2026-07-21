"""Cascade layer 2: LLM classifier for the grey zone (two-stage: category -> intent)."""
# [L2-LLM] Layer 2: two-stage LLM classifier
import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("ANSWER_MODEL", "qwen2.5:7b-instruct")

_tax = json.load(open("data/taxonomy.json", encoding="utf-8"))
CATEGORIES = {}
for it in _tax["intents"]:
    CATEGORIES.setdefault(it["category"], []).append(it)
SPECIAL = {s["id"]: s["definition"] for s in _tax["special_classes"]}


def _ask_json(prompt):
    """A single Ollama call with forced JSON output."""
    r = httpx.post(OLLAMA_URL + "/api/generate",
                   json={"model": MODEL, "prompt": prompt, "stream": False,
                         "format": "json",
                         "options": {"temperature": 0, "num_predict": 220}},
                   timeout=90)
    return json.loads(r.json()["response"])


def _stage1_category(text):
    cats = "\n".join(f"- {c}" for c in CATEGORIES)
    spec = "\n".join(f"- {k}: {v}" for k, v in SPECIAL.items())
    prompt = (
        "You classify support requests for kremzaPay (online payments, Poland).\n"
        f"Categories of supported topics:\n{cats}\n"
        f"Special classes (use INSTEAD of a category when they fit):\n{spec}\n\n"
        "Rules: chitchat = ONLY light small talk (greetings, jokes, thanks). "
        "Complaints, frustration or dissatisfaction with the bot/service are NOT chitchat - "
        "pick the matching category instead. wants_human=true if the user explicitly OR "
        "unambiguously wants a live person: asks for one, or is angry AT THE BOT/SERVICE itself. Frustration about a payment problem alone is NOT wants_human - classify the problem instead.\n\n"
        f"User message: {text}\n\n"
        'Reply JSON: {"reasoning": "<one short sentence>", '
        '"label": "<one category OR special class id>", "wants_human": true|false}'
    )
    return _ask_json(prompt)


def _stage2_intent(text, category):
    menu = "\n".join(
        f"- {i['id']}: {i['definition']}" + (f" NOT: {i['not'][0]}" if i.get("not") else "")
        for i in CATEGORIES[category]
    )
    prompt = (
        f"You classify support requests for kremzaPay. Category: {category}.\n"
        f"Intents:\n{menu}\n- other_in_scope: fits the topic but none of the intents above\n\n"
        f"User message: {text}\n\n"
        "Rules: think first (reasoning), then decide. If the message contains TWO goals, "
        "set secondary_intent. confidence: high = ready to act without a human check, "
        "medium = probably right, low = unsure. wants_human=true ONLY if the user asks "
        "for a live person or is angry at the bot/service itself; frustration about "
        "the problem alone is NOT wants_human.\n"
        'Reply JSON: {"reasoning": "...", "intent": "<id>", "secondary_intent": "<id or null>", '
        '"confidence": "high|medium|low", "sentiment": "negative|neutral|positive", '
        '"urgency": "high|normal", "wants_human": true|false}'
    )
    return _ask_json(prompt)


def classify(text):
    """Full layer 2 verdict."""
    s1 = _stage1_category(text)
    label = s1.get("label", "")
    if label in SPECIAL:
        return {"layer": 2, "intent": label, "scope": label, "confidence": "high",
                "reasoning": s1.get("reasoning", ""), "wants_human": bool(s1.get("wants_human"))}
    if label not in CATEGORIES:
        return {"layer": 2, "intent": "other_in_scope", "scope": "other_in_scope",
                "confidence": "low", "reasoning": f"unknown label {label!r}", "wants_human": False}
    s2 = _stage2_intent(text, label)
    valid = {i["id"] for i in CATEGORIES[label]} | {"other_in_scope"}
    intent = s2.get("intent") if s2.get("intent") in valid else "other_in_scope"
    return {"layer": 2, "intent": intent, "scope": "in_scope" if intent != "other_in_scope" else "other_in_scope",
            "category": label, "secondary_intent": s2.get("secondary_intent"),
            "confidence": s2.get("confidence", "low"), "sentiment": s2.get("sentiment"),
            "urgency": s2.get("urgency"), "wants_human": bool(s2.get("wants_human")),
            "reasoning": s2.get("reasoning", "")}


if __name__ == "__main__":
    import sys
    queries = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else [
        "payment stuck in pending since morning",
        "Do you accept Bitcoin payments?",
        "czy planujecie integracje z Allegro?",
        "ten czat mi nie pomaga, trzeci raz pisze to samo!!",
    ]
    for q in queries:
        v = classify(q)
        print(f"\n> {q}\n  intent={v['intent']} scope={v['scope']} conf={v['confidence']} "
              f"wants_human={v.get('wants_human')} sent={v.get('sentiment')}\n  reasoning: {v['reasoning'][:100]}")
