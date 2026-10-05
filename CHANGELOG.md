# Changelog

Wszystkie istotne zmiany w projekcie. Format według
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), numeracja według
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- CI i `make lint`: `ruff check` (zestaw domyślny) oraz sprawdzenie nagłówka
  licencji zamiast własnego skryptu stylu; cel `make style` zastąpiony przez
  `make lint`.
- Panel: polski podtytuł.

## [1.1.0] - 2026-10-05

Trafniejsze rozpoznanie tematu i odpowiedzi z właściwego artykułu.

### Uwaga przy aktualizacji

- Wyszukiwanie w bazie używa teraz `intfloat/multilingual-e5-large`
  (`EMBED_MODEL`, wektory 1024 zamiast 384): po aktualizacji trzeba ponownie
  wczytać bazę (`make ingest` albo `uv run python src/ingest.py`).

### Changed

- Wyszukiwanie fragmentów do odpowiedzi: samym pytaniem w całej bazie, modelem
  `multilingual-e5-large` (prefiksy `query: ` i `passage: `), zamiast w kategorii
  rozpoznanego tematu z definicją tematu w zapytaniu i jednego powtórzenia
  w całej bazie. Jedna instancja modelu embeddingów dla tematu i wyszukiwania.
- Linię źródła składa kod: identyfikatory z odpowiedzi modelu są porównywane
  z identyfikatorami znalezionych fragmentów (literówka -> najbliższy id, inna
  etykieta przed id też rozpoznawana, bez id -> pierwszy fragment); sędzia widzi
  tylko wskazane fragmenty.
- Pomiar na zewnętrznej bazie (59 artykułów, 100 pytań, część testowa 51
  nieużywana przy strojeniu): właściwy artykuł wśród odpowiedzi na pytania
  z bazy 39 z 54 -> 34 z 34 na części testowej i 66 z 67 na wszystkich 100;
  odpowiedzi 54 -> 67 z 85; pytania spoza bazy 15 z 15 (po dodaniu reguły dla
  pytań o bieżącą awarię, dodanej po analizie błędu na części testowej); mediana
  czasu 10,2 -> 12,3 s (więcej odpowiedzi, odpowiedź trwa dłużej niż zgłoszenie).
- `RETRIEVAL_OK` (0,45) z `multilingual-e5-large` w praktyce nie odsiewa
  pytań (wyniki powyżej 0,8); opisane w docs/architektura.md.

- Rozpoznanie tematu (warstwa 1): zamiast głosowania kNN na embeddingach
  `paraphrase-multilingual-MiniLM-L12-v2` klasyfikator regresji logistycznej
  (`CLF_C` 64) na embeddingach `intfloat/multilingual-e5-large`
  (`ROUTER_EMBED_MODEL`, prefiks `query: `), wytrenowany na 5412 pytaniach
  korpusu. Temat jest przyjęty bez modelu językowego, gdy prawdopodobieństwo
  najlepszego >= `P_ACCEPT` (0,3); inaczej 5 najbardziej prawdopodobnych tematów
  idzie do klasyfikatora LLM. `CONF_HIGH` 0,7. Usunięte `K` i `T_ACCEPT`.
  Indeks tematów i trafność bez zmian po przejściu wyszukiwania na e5.
- Trafność `accuracy_test` 0,755 -> 0,891, `accuracy_dev` 0,802 -> 0,948,
  macro-F1 test 0,753 -> 0,888; klasyfikator LLM wołany przy 4 z 88 pytań dev
  zamiast 38. `MIN_ACCURACY` 0,73 -> 0,87.
- Pytanie spoza tematu: gdy warstwa 1 stawia `out_of_scope` na pierwszym miejscu,
  a model wybierze `other_in_scope`, wynik to `out_of_scope` (`redirect`), nie
  zgłoszenie.

### Added

- Pytania o bieżącą awarię (temat `service_down_question`) zawsze kończą się
  zgłoszeniem z powodem `service_status`, bez wyszukiwania i odpowiedzi modelu.
- Gotowy indeks warstwy 1 w repozytorium (`data/index/router-<klucz>.npz`,
  wektory korpusu i wagi klasyfikatora, bez pickle, 20,8 MB); klucz to model
  embeddingów, `CLF_C` i skrót korpusu. Przy zgodnym kluczu start nie liczy
  embeddingów korpusu (około 20 minut na CPU); przy niezgodnym indeks powstaje
  w `data/cache/`. `make router-index` odbudowuje plik w `data/index/`.
- Reguły: pytania o prawo VAT (odliczenie, stawki, deklaracje, split payment
  w VAT) w grupie podatków; prośby o cudzą pracę (napisz umowę, esej,
  wypracowanie, wiersz, kod; po angielsku essay, poem, homework, contract)
  dają `redirect` z powodem `foreign_work`.
- Zależność `scikit-learn`.

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
