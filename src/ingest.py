"""Ingest: читает статьи kb/, режет на куски, превращает в эмбеддинги, грузит в Qdrant."""
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
CHUNK_SIZE = 800  # символов в одном куске (~1-2 абзаца)


def parse_article(path):
    """Разбирает файл статьи: паспорт (frontmatter) отдельно, текст отдельно."""
    raw = open(path, encoding="utf-8").read()
    _, front, body = raw.split("---", 2)
    meta = {}
    for line in front.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    body = body.rsplit("---", 1)[0]  # отрезаем дисклеймер в конце
    return meta, body.strip()


def split_chunks(body):
    """Режет текст на куски ~CHUNK_SIZE символов, не разрывая абзацы."""
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
    print(f"Статей найдено: {len(articles)}")

    texts, payloads = [], []
    for path in articles:
        meta, body = parse_article(path)
        for i, chunk in enumerate(split_chunks(body)):
            texts.append(meta["title"] + "\n" + chunk)
            payloads.append({**meta, "chunk": i, "text": chunk})
    print(f"Кусков получилось: {len(texts)}")

    print("Считаю эмбеддинги (первый запуск качает модель ~200 МБ, потом быстро)...")
    embedder = TextEmbedding(EMBED_MODEL)
    vectors = list(embedder.embed(texts))

    client = QdrantClient(url=QDRANT_URL)
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)  # повторный запуск = перезаливка с нуля
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=v.tolist(), payload=p)
        for v, p in zip(vectors, payloads)
    ]
    client.upsert(COLLECTION, points)
    print(f"Готово: {len(points)} точек в коллекции '{COLLECTION}'")


if __name__ == "__main__":
    main()
