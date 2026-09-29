# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import json

import config

_cache = None


def load() -> dict:
    global _cache
    if _cache is None:
        with open(config.TAXONOMY_PATH, encoding="utf-8") as handle:
            _cache = json.load(handle)
    return _cache


def intents() -> list[dict]:
    return load()["intents"]


def categories() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for item in intents():
        grouped.setdefault(item["category"], []).append(item)
    return grouped


def special() -> dict[str, str]:
    return {item["id"]: item["definition"] for item in load()["special_classes"]}


def intent_category() -> dict[str, str]:
    return {item["id"]: item["category"] for item in intents()}


def intent_definition() -> dict[str, str]:
    return {item["id"]: item["definition"] for item in intents()}
