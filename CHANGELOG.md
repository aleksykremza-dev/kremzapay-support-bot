# Changelog

Wszystkie istotne zmiany w projekcie. Format według
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), numeracja według
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-04

Pierwsze wydanie silnika po przebudowie z 29 i 30.09.2026.

### Added

- Kaskada rozpoznania pytania: reguły warstwy 0 (próby obejścia instrukcji,
  oszustwa, w tym fałszywe dokumenty, cudze karty i klucze, wypłata z cudzego
  konta, prośba o człowieka), router kNN na korpusie 5412 przykładów i klasyfikator
  LLM, który wybiera etykietę spośród kandydatów kNN w jednym wywołaniu.
- Odpowiedzi tylko z dokumentacji (RAG na Qdrant) ze źródłem „Źródło: <id>”;
  wyszukiwanie w kategorii intencji, a gdy w niej nic nie pasuje albo model
  odpowie `NO_ANSWER`, jedno ponowne wyszukiwanie w całej bazie.
- Sędzia odpowiedzi: sprawdza, czy źródła odpowiadają na zadane pytanie i czy
  każde twierdzenie ma w nich oparcie; w przeciwnym razie zgłoszenie.
- Przekazanie człowiekowi: zgłoszenie `handoff` z priorytetem `high`, sesja
  w statusie `handoff` omija bota, e-mail i telefon w oryginale tylko w
  `tickets.contact`, blok „Czeka na człowieka” w panelu i
  `POST /api/tickets/{id}/close`.
- Limit równoległych żądań `/chat` (`MAX_INFLIGHT`, kolejka `QUEUE_TIMEOUT_S`);
  nadmiar i awarie usług dostają 503 z nagłówkiem `X-Reason` i gotowym zgłoszeniem.
- Rozgrzewanie przy starcie: indeks kNN i model embeddingów ładują się przed
  pierwszym żądaniem, indeks zapisuje się w `data/cache/`.
- Przełącznik `LLM_THINK` przekazywany do Ollama.
- Stały podział gold setu na dev (96) i test (192); `eval_cascade --subset`,
  próg `MIN_ACCURACY` liczony na części test.
- Testy na żywo: według kategorii, poza zakresem, obciążenie, stres, stabilność
  (RSS i otwarte pliki); narzędzia mapy kodu i pokrycia pytań.
- Obraz Docker (użytkownik bez uprawnień root, `HEALTHCHECK` na `/health`),
  `docker-compose.yml` z usługami `api` i `qdrant`, profil `ollama` i plik
  `docker-compose.gpu.yml`; cele `make up`, `down`, `logs`, `ingest`.
- GitHub Actions: `uv sync --frozen`, `pytest`, bramka stylu
  `tools/check_style.py` (`make style`); workflow publikacji obrazu w GHCR
  po tagu `v*`.
- Licencja PolyForm Noncommercial 1.0.0.

### Changed

- Jedna konfiguracja (`config.py`, `.env`) i jeden klient Ollama; `/health`
  sprawdza Ollama i Qdrant naprawdę; testy jednostkowe bez usług zewnętrznych.
- Domyślny model `qwen2.5:7b-instruct` po porównaniu z `qwen3:8b`;
  `MIN_ACCURACY` 0,73 na części test.
- `make ingest` działa w kontenerze; dotychczasowe wczytanie lokalne to
  `make ingest-local`.
- Kontener Qdrant bez stałej nazwy, więc druga instalacja na tej samej
  maszynie nie koliduje nazwą.
- Obraz Qdrant przypięty do `v1.18.2`.
- README po polsku: własna baza wiedzy, szybki start, API, zgłoszenia,
  przekazanie człowiekowi, testy, koszty, ograniczenia.

### Fixed

- Sędzia widzi tylko artykuły zacytowane w odpowiedzi; źródło jest rozpoznawane
  także na końcu ostatniego akapitu.
- Odpowiedź „w dokumentacji nie ma informacji” nie trafia już do klienta jako
  odpowiedź, tylko jako zgłoszenie.
- Połączenia SQLite są zamykane po każdej operacji.
- Przywrócone pierwotne brzmienie promptu klasyfikatora; stały `LLM_SEED`.

### Security

- Dane osobowe (karta, IBAN, PESEL, telefon, e-mail) są maskowane przed
  zapisem, logiem i modelem; oryginalny kontakt klienta tylko w zgłoszeniu.

[1.0.0]: https://github.com/aleksykremza-dev/kremzapay-support-bot/releases/tag/v1.0.0
