"""Retrieval v2: поиск по смыслу + опциональный фильтр по категории статей."""
import os
import sys

from dotenv import load_dotenv
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6335")
COLLECTION = "kremzapay_kb"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5

_embedder = None
_client = None


def _lazy():
    global _embedder, _client
    if _embedder is None:
        _embedder = TextEmbedding(EMBED_MODEL)
        _client = QdrantClient(url=QDRANT_URL)


def search(question, category=None):
    """Топ-K кусков; с category ищем только в статьях этой категории.

    Фильтр сужает поиск («zwrot» больше не утащит в chargeback-статьи),
    а если в категории нашлось мало — честно откатываемся на всю базу.
    """
    _lazy()
    vector = list(_embedder.embed([question]))[0].tolist()
    flt = None
    if category:
        flt = Filter(must=[FieldCondition(key="category", match=MatchValue(value=category))])
    hits = _client.query_points(COLLECTION, query=vector, limit=TOP_K,
                                query_filter=flt).points
    if category and len(hits) < 2:          # категория пустовата -> вся база
        hits = _client.query_points(COLLECTION, query=vector, limit=TOP_K).points
    return hits


def main():
    question = " ".join(sys.argv[1:]) or "How do I refund a payment?"
    print(f"Вопрос: {question}\n-- без фильтра:")
    for h in search(question)[:3]:
        print(f"  [{h.score:.3f}] {h.payload['id']} ({h.payload['category']}) {h.payload['title']}")
    print("-- фильтр category=refunds:")
    for h in search(question, category="refunds")[:3]:
        print(f"  [{h.score:.3f}] {h.payload['id']} ({h.payload['category']}) {h.payload['title']}")


if __name__ == "__main__":
    main()
