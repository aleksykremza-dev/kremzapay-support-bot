# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
from functools import lru_cache

from fastembed import TextEmbedding

import config


@lru_cache(maxsize=None)
def model(name: str) -> TextEmbedding:
    return TextEmbedding(name)


def prefixed(name: str, texts: list[str], kind: str) -> list[str]:
    query, passage = config.EMBED_PREFIXES.get(name, ("", ""))
    prefix = query if kind == "query" else passage
    return [prefix + text for text in texts]
