"""Retrieval: вопрос → топ-5 ближайших по смыслу кусков из Qdrant."""
import os
import sys

from dotenv import load_dotenv
from fastembed import TextEmbedding
from qdrant_client import QdrantClient

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6335")
COLLECTION = "kremzapay_kb"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5


def search(question):
    """Возвращает TOP_K самых близких по смыслу кусков с оценкой похожести."""
    embedder = TextEmbedding(EMBED_MODEL)
    vector = list(embedder.embed([question]))[0].tolist()
    client = QdrantClient(url=QDRANT_URL)
    return client.query_points(COLLECTION, query=vector, limit=TOP_K).points


def main():
    question = " ".join(sys.argv[1:]) or "How do I refund a payment?"
    print(f"Вопрос: {question}\n")
    for hit in search(question):
        p = hit.payload
        print(f"[{hit.score:.3f}] {p['id']} ({p['lang']}) — {p['title']}")
        print(f"    {p['text'][:150]}...\n")


if __name__ == "__main__":
    main()
