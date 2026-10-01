# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import llm
import taxonomy

CONFIDENCE = {"high", "medium", "low"}


def _offered(candidates: list[tuple[str, float]]) -> list[dict]:
    known = {item["id"]: item for item in taxonomy.intents()}
    return [known[label] for label, _sim in candidates if label in known]


def _candidate_lines(offered: list[dict]) -> list[str]:
    lines = []
    for item in offered:
        label = item["id"]
        side = "buyer" if label.startswith("buyer_") else "merchant"
        line = f"- {label} [{side}]: {item['definition']}"
        if item.get("not"):
            line += f" NOT: {item['not'][0]}"
        lines.append(line)
    return lines


def _prompt(text: str, lines: list[str]) -> str:
    special = taxonomy.special()
    spec = "\n".join(f"- {key}: {value}" for key, value in special.items() if key != "other_in_scope")
    menu = "\n".join(lines) if lines else "- (no candidates)"
    return (
        "You classify support requests for kremzaPay (online payments, Poland).\n"
        "Step 1. Decide first who writes: a shop customer (buyer) or a merchant using kremzaPay. "
        "A buyer paid or wants to pay in someone's online shop and asks about their own purchase; "
        "a merchant runs the shop and asks about accepting payments, the panel, payouts, "
        "integration or the merchant account.\n"
        "Step 2. Pick one label. Candidate intents, most similar first, "
        "[buyer] or [merchant] marks who asks:\n"
        f"{menu}\n"
        f"Special classes (use INSTEAD of a candidate when they fit):\n{spec}\n"
        f"- other_in_scope: {special.get('other_in_scope', '')} Use it only when no candidate "
        "and no special class fits.\n\n"
        "Rules: prefer a candidate whose [buyer]/[merchant] mark matches the author from step 1. "
        "chitchat = ONLY light small talk (greetings, jokes, thanks). "
        "Complaints, frustration or dissatisfaction with the bot/service are NOT chitchat - "
        "pick the matching candidate instead. wants_human=true if the user explicitly OR "
        "unambiguously wants a live person: asks for one, or is angry AT THE BOT/SERVICE itself. "
        "Frustration about a payment problem alone is NOT wants_human - classify the problem instead. "
        "confidence: high = ready to act without a human check, medium = probably right, low = unsure.\n\n"
        f"User message: {text}\n\n"
        'Reply JSON: {"reasoning": "<one short sentence>", "author": "buyer|merchant", '
        '"label": "<candidate id, special class id or other_in_scope>", '
        '"confidence": "high|medium|low", "wants_human": true|false}'
    )


def _unsure(reason: str) -> dict:
    return {"layer": 2, "intent": "other_in_scope", "scope": "other_in_scope",
            "confidence": "low", "reasoning": reason, "wants_human": False}


def classify(text: str, candidates: list[tuple[str, float]]) -> dict:
    offered = _offered(candidates)
    try:
        answer = llm.generate_json(_prompt(text, _candidate_lines(offered)), num_predict=220)
    except llm.LLMBadOutput as exc:
        return _unsure(f"bad llm output: {exc}")
    label = answer.get("label", "")
    if label in taxonomy.special():
        scope = label
    elif label in {item["id"] for item in offered}:
        scope = "in_scope"
    else:
        return _unsure(f"label outside candidates {label!r}")
    confidence = answer.get("confidence")
    return {"layer": 2, "intent": label, "scope": scope,
            "category": taxonomy.intent_category().get(label),
            "author": answer.get("author"),
            "confidence": confidence if confidence in CONFIDENCE else "low",
            "wants_human": bool(answer.get("wants_human")),
            "reasoning": answer.get("reasoning", "")}
