"""Ingest: reads kb/ articles, splits into chunks, turns them into embeddings, loads into Qdrant."""
# [INGEST] KB -> chunks -> embeddings -> Qdrant
import glob
import os
import uuid

from dotenv import load_dotenv
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6335")
COLLECTION = "kremzapay_kb"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 800  # characters per chunk (~1-2 paragraphs)


def parse_article(path):
    """Parses an article file: the passport (frontmatter) separately, the text separately."""
    raw = open(path, encoding="utf-8").read()
    _, front, body = raw.split("---", 2)
    meta = {}
    for line in front.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    body = body.rsplit("---", 1)[0]  # cut off the disclaimer at the end
    return meta, body.strip()


def split_chunks(body):
    """Splits text into chunks of ~CHUNK_SIZE characters without breaking paragraphs."""
    chunks, current = [], ""
    for paragraph in body.split("\n\n"):
        if len(current) + len(paragraph) > CHUNK_SIZE and current:
            chunks.append(current.strip())
            current = ""
        current += paragraph + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def main():
    articles = sorted(glob.glob("kb/*/*.md"))
    print(f"Articles found: {len(articles)}")

    texts, payloads = [], []
    for path in articles:
        meta, body = parse_article(path)
        for i, chunk in enumerate(split_chunks(body)):
            texts.append(meta["title"] + "\n" + chunk)
            payloads.append({**meta, "chunk": i, "text": chunk})
    print(f"Chunks produced: {len(texts)}")

    print("Computing embeddings (first run downloads the model ~200 MB, then fast)...")
    embedder = TextEmbedding(EMBED_MODEL)
    vectors = list(embedder.embed(texts))

    client = QdrantClient(url=QDRANT_URL)
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)  # re-run = full reload from scratch
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=v.tolist(), payload=p)
        for v, p in zip(vectors, payloads)
    ]
    client.upsert(COLLECTION, points)
    print(f"Done: {len(points)} points in collection '{COLLECTION}'")


if __name__ == "__main__":
    main()
