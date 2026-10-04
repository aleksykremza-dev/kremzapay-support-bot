# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    path = Path(value)
    return path if path.is_absolute() else BASE_DIR / path


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
ANSWER_MODEL = os.getenv("ANSWER_MODEL", "qwen2.5:7b-instruct")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
ROUTER_EMBED_MODEL = os.getenv("ROUTER_EMBED_MODEL", "intfloat/multilingual-e5-large")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6335")
COLLECTION = os.getenv("COLLECTION", "kremzapay_kb")
LLM_TIMEOUT_S = float(os.getenv("LLM_TIMEOUT_S", "120"))
LLM_RETRIES = int(os.getenv("LLM_RETRIES", "1"))
LLM_SEED = int(os.getenv("LLM_SEED", "42"))
LLM_THINK = os.getenv("LLM_THINK", "false").lower() == "true"
MAX_INFLIGHT = int(os.getenv("MAX_INFLIGHT", "2"))
QUEUE_TIMEOUT_S = float(os.getenv("QUEUE_TIMEOUT_S", "30"))
PING_TIMEOUT_S = 2.0

DATA_DIR = BASE_DIR / "data"
WEB_DIR = BASE_DIR / "web"
DB_PATH = _path("DB_PATH", DATA_DIR / "kremzapay.db")
KB_DIR = _path("KB_DIR", BASE_DIR / "kb")
CORPUS_DIR = DATA_DIR / "corpus"
CACHE_DIR = DATA_DIR / "cache"
TAXONOMY_PATH = DATA_DIR / "taxonomy.json"
TAXONOMY_PARTS_DIR = DATA_DIR / "taxonomy"
GOLD_DIR = DATA_DIR / "goldset"
REPORTS_DIR = DATA_DIR / "reports"
SPLIT_PATH = GOLD_DIR / "split.json"

LLM_CANDIDATES = 5
CLF_C = 64.0
P_ACCEPT = 0.3
T_OOS = 0.45
RETRIEVAL_OK = 0.45
CONF_HIGH = 0.7
TOP_K = 5
TOP_N = 3
CHUNK_SIZE = 800
MIN_ACCURACY = 0.87
