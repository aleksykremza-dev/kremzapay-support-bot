# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import llm
import taxonomy


def _stage1_category(text: str) -> dict:
    cats = "\n".join(f"- {name}" for name in taxonomy.categories())
    spec = "\n".join(f"- {key}: {value}" for key, value in taxonomy.special().items())
    prompt = (
        "You classify support requests for kremzaPay (online payments, Poland).\n"
        f"Categories of supported topics:\n{cats}\n"
        f"Special classes (use INSTEAD of a category when they fit):\n{spec}\n\n"
        "Rules: chitchat = ONLY light small talk (greetings, jokes, thanks). "
        "Complaints, frustration or dissatisfaction with the bot/service are NOT chitchat - "
        "pick the matching category instead. wants_human=true if the user explicitly OR "
        "unambiguously wants a live person: asks for one, or is angry AT THE BOT/SERVICE itself. "
        "Frustration about a payment problem alone is NOT wants_human - classify the problem instead.\n\n"
        f"User message: {text}\n\n"
        'Reply JSON: {"reasoning": "<one short sentence>", '
        '"label": "<one category OR special class id>", "wants_human": true|false}'
    )
    return llm.generate_json(prompt, num_predict=220)


def _stage2_intent(text: str, category: str) -> dict:
    menu = "\n".join(
        f"- {item['id']}: {item['definition']}" + (f" NOT: {item['not'][0]}" if item.get("not") else "")
        for item in taxonomy.categories()[category]
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
    return llm.generate_json(prompt, num_predict=220)


def _unsure(reason: str) -> dict:
    return {"layer": 2, "intent": "other_in_scope", "scope": "other_in_scope",
            "confidence": "low", "reasoning": reason, "wants_human": False}


def classify(text: str) -> dict:
    try:
        stage1 = _stage1_category(text)
    except llm.LLMBadOutput as exc:
        return _unsure(f"bad llm output: {exc}")
    label = stage1.get("label", "")
    if label in taxonomy.special():
        return {"layer": 2, "intent": label, "scope": label, "confidence": "high",
                "reasoning": stage1.get("reasoning", ""), "wants_human": bool(stage1.get("wants_human"))}
    if label not in taxonomy.categories():
        return _unsure(f"unknown label {label!r}")
    try:
        stage2 = _stage2_intent(text, label)
    except llm.LLMBadOutput as exc:
        return _unsure(f"bad llm output: {exc}")
    valid = {item["id"] for item in taxonomy.categories()[label]} | {"other_in_scope"}
    intent = stage2.get("intent") if stage2.get("intent") in valid else "other_in_scope"
    return {"layer": 2, "intent": intent,
            "scope": "in_scope" if intent != "other_in_scope" else "other_in_scope",
            "category": label, "secondary_intent": stage2.get("secondary_intent"),
            "confidence": stage2.get("confidence", "low"), "sentiment": stage2.get("sentiment"),
            "urgency": stage2.get("urgency"), "wants_human": bool(stage2.get("wants_human")),
            "reasoning": stage2.get("reasoning", "")}
