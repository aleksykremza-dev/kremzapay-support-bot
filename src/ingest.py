# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import sys
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

import config
import embeddings

NO_KB_MESSAGE = (
    "Baza wiedzy nie jest częścią repozytorium. "
    "Umieść artykuły w kb/ (format: README, sekcja \"Własna dokumentacja\")."
)


def parse_article(path: Path) -> tuple[dict, str]:
    with open(path, encoding="utf-8") as handle:
        raw = handle.read()
    _, front, body = raw.split("---", 2)
    meta = {}
    for line in front.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    body = body.rsplit("---", 1)[0]
    return meta, body.strip()


def split_chunks(body: str) -> list[str]:
    chunks, current = [], ""
    for paragraph in body.split("\n\n"):
        if len(current) + len(paragraph) > config.CHUNK_SIZE and current:
            chunks.append(current.strip())
            current = ""
        current += paragraph + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def find_articles(kb_dir: Path) -> list[Path]:
    if not kb_dir.is_dir():
        return []
    return sorted(kb_dir.glob("*/*.md"))


def main(kb_dir: Path = config.KB_DIR) -> int:
    articles = find_articles(kb_dir)
    if not articles:
        print(NO_KB_MESSAGE)
        return 2
    print(f"Articles found: {len(articles)}")

    texts, payloads = [], []
    for path in articles:
        meta, body = parse_article(path)
        for index, chunk in enumerate(split_chunks(body)):
            texts.append(meta["title"] + "\n" + chunk)
            payloads.append({**meta, "chunk": index, "text": chunk})
    print(f"Chunks produced: {len(texts)}")

    print("Computing embeddings (first run downloads the model, then fast)...")
    embedder = embeddings.model(config.EMBED_MODEL)
    vectors = list(embedder.embed(embeddings.prefixed(config.EMBED_MODEL, texts, "passage")))

    client = QdrantClient(url=config.QDRANT_URL)
    if client.collection_exists(config.COLLECTION):
        client.delete_collection(config.COLLECTION)
    client.create_collection(
        config.COLLECTION,
        vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE),
    )
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vector.tolist(), payload=payload)
        for vector, payload in zip(vectors, payloads)
    ]
    client.upsert(config.COLLECTION, points)
    print(f"Done: {len(points)} points in collection '{config.COLLECTION}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
