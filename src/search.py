# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import logging
import sys

from qdrant_client import QdrantClient

import config
import embeddings

log = logging.getLogger(__name__)

_embedder = None
_client = None


class SearchUnavailable(Exception):
    pass


def _lazy() -> None:
    global _embedder, _client
    if _embedder is None:
        _embedder = embeddings.model(config.EMBED_MODEL)
        _client = QdrantClient(url=config.QDRANT_URL)


def warm() -> None:
    _lazy()
    list(_embedder.embed(["warmup"]))


def search(question: str) -> list:
    _lazy()
    vector = list(_embedder.embed(embeddings.prefixed(config.EMBED_MODEL, [question], "query")))[0].tolist()
    try:
        hits = _client.query_points(config.COLLECTION, query=vector, limit=config.TOP_K).points
    except Exception as exc:
        log.warning("qdrant %s failed: %s", config.QDRANT_URL, exc)
        raise SearchUnavailable(f"{config.QDRANT_URL}: {exc}") from exc
    return hits


def ping() -> bool:
    try:
        client = QdrantClient(url=config.QDRANT_URL, timeout=int(config.PING_TIMEOUT_S))
        return bool(client.collection_exists(config.COLLECTION))
    except Exception as exc:
        log.warning("qdrant %s not reachable: %s", config.QDRANT_URL, exc)
        return False


def main() -> int:
    question = " ".join(sys.argv[1:]) or "How do I refund a payment?"
    print(f"Question: {question}")
    for hit in search(question)[:3]:
        print(f"  [{hit.score:.3f}] {hit.payload['id']} ({hit.payload['category']}) {hit.payload['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
