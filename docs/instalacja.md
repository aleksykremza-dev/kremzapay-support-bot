# Instalacja i konfiguracja

Wymagania, instalacja bez Dockera, zmienne środowiskowe i druga instalacja na tej samej maszynie. Szybki start z Dockerem jest w README.

[Wróć do README](../README.md)

## Docker: Ollama na hoście albo w kontenerze

Kontener łączy się z Ollamana hoście przez `host.docker.internal:11434`. Jeśli
Ollama działa gdzie indziej (np. w WSL nasłuchuje tylko na 127.0.0.1), uruchom ją
z `OLLAMA_HOST=0.0.0.0` i wpisz jej adres w `.env` jako `OLLAMA_URL_DOCKER`.
Ollama w kontenerze: `docker compose --profile ollama up -d` (z GPU dodatkowo
`-f docker-compose.yml -f docker-compose.gpu.yml`), `OLLAMA_URL_DOCKER=http://ollama:11434`
w `.env` i `docker compose exec ollama ollama pull qwen2.5:7b-instruct`.
Instalacja bez Dockera: sekcja „Uruchomienie” niżej.

## Wymagania

| Co | Po co | Sprawdzenie |
|---|---|---|
| Python 3.12 (`.python-version`) i [uv](https://github.com/astral-sh/uv) | środowisko `.venv` z `pyproject.toml` | `uv --version` |
| Własna [Ollama](https://ollama.com) z modelem z `.env` (`ANSWER_MODEL`, domyślnie `qwen2.5:7b-instruct`) | klasyfikator, odpowiedzi i sędzia; jeden model na wszystkie warstwy | `curl http://localhost:11434/api/tags` zwraca listę modeli z tym tagiem |
| Własny Qdrant; w repo `docker-compose.yml` z przypiętym obrazem `qdrant/qdrant:v1.18.2`, port `6335` na hoście, dane w `qdrant_data/` | fragmenty dokumentacji i wyszukiwanie znaczeniowe | `curl http://localhost:6335/collections` zwraca JSON |
| Docker (dla Qdrant) | uruchomienie kontenera | `docker compose ps` |
| Własna dokumentacja w `kb/` | bez niej `ingest.py` kończy się kodem 2 | [wlasna-domena.md](wlasna-domena.md) |

Po starcie bota obie zależności sprawdza `curl http://localhost:8020/health` ->
`{"status":"ok","ollama":true,"qdrant":true}`; `degraded`, gdy któraś usługa nie
odpowiada; `qdrant` jest `true` dopiero po `ingest.py` (istnieje kolekcja
`kremzapay_kb`). Plik `.env` jest opcjonalny; zmienne z `.env.example`:
`OLLAMA_URL`, `ANSWER_MODEL`, `QDRANT_URL`, `KB_DIR`, `DB_PATH`, `LLM_TIMEOUT_S`,
`LLM_SEED`, `LLM_THINK` (domyślnie `false`: modele z trybem myślenia, np. `qwen3:8b`,
`gemma4:e4b`, odpowiadają od razu w polu `response`), `MAX_INFLIGHT`, `QUEUE_TIMEOUT_S`
(limit równoczesnych żądań `/chat`, [api.md](api.md));
w `config.py` są jeszcze `EMBED_MODEL` (fastembed), `COLLECTION` i `LLM_RETRIES`.

## Uruchomienie

```bash
git clone https://github.com/aleksykremza-dev/kremzapay-support-bot.git
cd kremzapay-support-bot
uv sync                                   # środowisko .venv z pyproject.toml
cp .env.example .env                      # opcjonalnie: inne adresy albo model
docker compose up -d qdrant               # sam Qdrant na porcie 6335
ollama pull qwen2.5:7b-instruct           # model z ANSWER_MODEL
uv run python src/ingest.py               # wymaga kb/ z artykułami, patrz niżej
uv run uvicorn api:app --app-dir src --port 8020
```

Przy starcie serwer ładuje model embeddingów i indeks kNN korpusu, zanim przyjmie
pierwsze żądanie. Przy pierwszym starcie w nowym katalogu indeks 5412 przykładów
powstaje od zera i zapisuje się w `data/cache/` (około 2 minut na GTX 1050 Ti,
pomiar 02.10.2026), kolejne starty czytają go z dysku w kilka sekund.
Po komunikacie `Application startup complete` otwórz http://localhost:8020
(czat) i http://localhost:8020/dashboard (panel z przebiegiem każdej rozmowy).
Pierwsze pytanie wymagające modelu trwa dłużej, bo Ollama ładuje model do pamięci
(także po kilku minutach bezczynności).
Ścieżki (`kb/`, `data/`, `.env`) `config.py` liczy od katalogu repozytorium, nie
od bieżącego katalogu, więc skrypty działają z dowolnego miejsca, np.
`uv run --project ~/kremzapay-support-bot python ~/kremzapay-support-bot/src/ingest.py`.
Zatrzymanie: `Ctrl+C` w oknie uvicorn, potem `docker compose down`.

Kontener Qdrant nie ma stałej nazwy: Docker Compose nadaje ją od nazwy projektu,
domyślnie nazwy katalogu (np. `kremzapay-support-bot-qdrant-1`). Druga instalacja
na tej samej maszynie w katalogu o tej samej nazwie potrzebuje własnej nazwy
projektu, np. `COMPOSE_PROJECT_NAME=kremzapay-test` w `.env` albo
`docker compose -p kremzapay-test up -d`. Port `6335` jest w `docker-compose.yml`
na stałe, więc dwie instalacje naraz wymagają zmiany portu w tym pliku i w
`QDRANT_URL` w `.env` drugiej instalacji.
