# kremzaPay Support Bot: silnik bota wsparcia na własnej dokumentacji

Silnik bota wsparcia, który odpowiada klientom wyłącznie na podstawie Twojej
dokumentacji (pomoc, FAQ, regulaminy), do każdej odpowiedzi podaje źródło, a gdy
nie jest pewny, przekazuje sprawę człowiekowi zamiast zmyślać. Działa po polsku
i po angielsku, w całości lokalnie (Ollama + Qdrant), bez płatnych API. Nazwa
`kremzaPay` w kodzie i w panelu to robocza nazwa projektu.

## Dlaczego w repozytorium nie ma bazy wiedzy

Silnik był rozwijany na prawdziwej dokumentacji, która należy do jej właściciela
i jest objęta umową o ochronie danych, dlatego baza wiedzy nie jest publikowana.
Repozytorium zawiera silnik oraz instrukcję podłączenia własnej dokumentacji
(sekcja „Własna dokumentacja”). Bez katalogu `kb/` bot nie ma na czym odpowiadać.

## Jak to działa

Pytanie z czatu przechodzi przez kolejne etapy; każdy ma swój plik w `src/`.

1. **Maskowanie danych osobowych** (`pii.py`). Numer karty, IBAN, PESEL, telefon
   i e-mail stają się etykietami `<CARD_1>`, `<IBAN_1>`, `<PESEL_1>`, `<PHONE_1>`,
   `<EMAIL_1>` zanim tekst zobaczy model i zanim trafi do bazy SQLite.
2. **L0, reguły** (`rules.py`). Wzorce tekstowe bez modelu: manipulacja botem
   i prośby o pomoc w oszustwie -> odmowa (`unsafe_refuse`); inne produkty
   i podatki -> `redirect`; wyraźna prośba o człowieka -> `handoff`.
3. **L1, kNN** (`knn_router.py`). Pytanie jest porównywane znaczeniowo z korpusem
   pytań z intencją. Z 10 najbliższych zwycięska intencja musi mieć co najmniej
   5 głosów i średnie podobieństwo >= `T_ACCEPT` (0,62); wtedy jest przyjęta bez
   modelu, z pewnością `high` przy >= `CONF_HIGH` (0,72), inaczej `medium`.
4. **L2, klasyfikator LLM** (`llm_classifier.py`). Gdy kNN nie jest pewny (także
   przy podobieństwie < `T_OOS`, 0,45), lokalny model jednym wywołaniem najpierw
   ustala, kto pisze (kupujący w sklepie czy sprzedawca), potem wybiera etykietę
   spośród do `LLM_CANDIDATES` (5) unikalnych intencji z 10 sąsiadów kNN
   (z definicjami), klas specjalnych albo `other_in_scope`; etykieta spoza tej listy
   daje `other_in_scope` z pewnością `low`; zwraca JSON z pewnością
   `high|medium|low` i `wants_human`.
5. **Decyzja** (`cascade.py`). Klasy specjalne dają akcję: small talk ->
   `chitchat_reply`, treść niebezpieczna -> `unsafe_refuse`, poza zakresem ->
   `redirect`, temat w zakresie bez intencji -> `ticket`; `wants_human` ->
   `handoff`; pewność `low` -> `clarify` (dopytanie). Inaczej najlepszy fragment
   z Qdrant musi mieć wynik >= `RETRIEVAL_OK` (0,45), w przeciwnym razie `ticket`.
6. **Odpowiedź** (`answer_gen.py`). Wyszukiwanie z filtrem po kategorii intencji
   (przy mniej niż 2 trafieniach filtr jest zdejmowany), 3 najlepsze fragmenty
   (`TOP_N`) idą do promptu; model odpowiada tylko na ich podstawie i kończy
   linią `Źródło: KB-###` (`Source:` po angielsku).
7. **Sędzia** (`judge.py`). Drugie wywołanie modelu: czy każde twierdzenie ma
   pokrycie we fragmentach (`yes`/`no`). Przy `no` odpowiedź nie wychodzi,
   zamiast niej powstaje zgłoszenie (`ticket_not_grounded`).

Błąd rozpoznania kończy się więc dopytaniem, zgłoszeniem albo przekazaniem
człowiekowi, nie zmyśloną odpowiedzią. Każdy etap dopisuje wynik do jednego
obiektu `TurnState` (czasy warstw, reguły, kNN, LLM, retrieval, decyzja), który
trafia do SQLite razem z wiadomością i jest widoczny na `/dashboard`. Historia
sesji jest zapisywana, ale każde pytanie jest rozpatrywane osobno. Język
(`pl`/`en`) jest wykrywany po polskich znakach i liście typowych polskich słów.

| Termin | Co to jest | Gdzie |
|---|---|---|
| Embeddingi | wektory liczb: teksty o podobnym znaczeniu są blisko siebie; jeden model dla pl i en (`EMBED_MODEL`, fastembed) | `knn_router.py`, `search.py` |
| Progi | `K`, `T_ACCEPT`, `T_OOS`, `RETRIEVAL_OK`, `CONF_HIGH`, `TOP_K`, `TOP_N`, `CHUNK_SIZE`, `MIN_ACCURACY` | `config.py` |
| Klient Ollama | jedno miejsce wywołań modelu: timeout, powtórka, `LLMUnavailable`, `LLMBadOutput` | `llm.py` |
| Taksonomia | intencje z kategorią i definicją oraz klasy specjalne; wczytywana raz | `taxonomy.py`, `data/taxonomy.json` |
| Korpus i gold set | pytania z etykietą dla kNN (indeks w `data/cache/`); pytania egzaminacyjne do liczenia trafności i macro-F1, rozłączne z korpusem | `data/corpus/`, `data/goldset/`, `eval_cascade.py` |

## Wymagania

| Co | Po co | Sprawdzenie |
|---|---|---|
| Python 3.12 (`.python-version`) i [uv](https://github.com/astral-sh/uv) | środowisko `.venv` z `pyproject.toml` | `uv --version` |
| Własna [Ollama](https://ollama.com) z modelem z `.env` (`ANSWER_MODEL`, domyślnie `qwen2.5:7b-instruct`) | klasyfikator, odpowiedzi i sędzia; jeden model na wszystkie warstwy | `curl http://localhost:11434/api/tags` zwraca listę modeli z tym tagiem |
| Własny Qdrant; w repo `docker-compose.yml` z przypiętym obrazem `qdrant/qdrant:v1.18.2`, port `6335` na hoście, dane w `qdrant_data/` | fragmenty dokumentacji i wyszukiwanie znaczeniowe | `curl http://localhost:6335/collections` zwraca JSON |
| Docker (dla Qdrant) | uruchomienie kontenera | `docker compose ps` |
| Własna dokumentacja w `kb/` | bez niej `ingest.py` kończy się kodem 2 | sekcja „Własna dokumentacja” |

Po starcie bota obie zależności sprawdza `curl http://localhost:8020/health` ->
`{"status":"ok","ollama":true,"qdrant":true}`; `degraded`, gdy któraś usługa nie
odpowiada; `qdrant` jest `true` dopiero po `ingest.py` (istnieje kolekcja
`kremzapay_kb`). Plik `.env` jest opcjonalny; zmienne z `.env.example`:
`OLLAMA_URL`, `ANSWER_MODEL`, `QDRANT_URL`, `KB_DIR`, `DB_PATH`, `LLM_TIMEOUT_S`,
`LLM_SEED`, `LLM_THINK` (domyślnie `false`: modele z trybem myślenia, np. `qwen3:8b`,
`gemma4:e4b`, odpowiadają od razu w polu `response`), `MAX_INFLIGHT`, `QUEUE_TIMEOUT_S`
(limit równoczesnych żądań `/chat`, sekcja „API”);
w `config.py` są jeszcze `EMBED_MODEL` (fastembed), `COLLECTION` i `LLM_RETRIES`.

## Uruchomienie

```bash
git clone https://github.com/aleksykremza-dev/kremzapay-support-bot.git
cd kremzapay-support-bot
uv sync                                   # środowisko .venv z pyproject.toml
cp .env.example .env                      # opcjonalnie: inne adresy albo model
docker compose up -d                      # Qdrant na porcie 6335
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

## Własna dokumentacja

Artykuł to plik Markdown w `kb/<kategoria>/<id>.md`. `ingest.py` czyta wzorzec
`kb/*/*.md` (jeden poziom podkatalogów); nazwa podkatalogu nie jest przez kod
używana, kategoria pochodzi z nagłówka. Nagłówek między dwiema liniami `---` ma
pola `title`, `category`, `id`; `category` musi być jedną z kategorii
w `data/taxonomy.json`, bo wyszukiwanie filtruje po niej fragmenty. Treść jest
cięta na fragmenty po akapitach (pusta linia między nimi) do ok. 800 znaków
(`CHUNK_SIZE`); każdy fragment dostaje tytuł artykułu. Jeśli po treści jest
jeszcze linia `---`, wszystko za ostatnią z nich jest odcinane. Wersja polska
i angielska to osobne pliki (np. `kb/refunds/KB-030-pl.md` i `KB-030-en.md`);
dodatkowe pola nagłówka, np. `lang`, trafiają do payloadu w Qdrant. Minimalny
`kb/refunds/KB-030-pl.md`:

```
---
id: KB-030
category: refunds
title: Gdzie jest mój zwrot
---

Zwrot na kartę trwa zwykle od 3 do 7 dni roboczych od zlecenia przez sprzedawcę.
Status zwrotu widać w panelu w zakładce Zwroty.

Jeśli po 7 dniach roboczych środki nie wróciły, przygotuj numer transakcji.
```

Po każdej zmianie w artykułach: `uv run python src/ingest.py` (`make ingest`).
Skrypt kasuje kolekcję i buduje ją od zera. Oczekiwany wynik:

```
Articles found: 12
Chunks produced: 31
Computing embeddings (first run downloads the model, then fast)...
Done: 31 points in collection 'kremzapay_kb'
```

Bez katalogu `kb/` (albo bez plików `.md` w nim) skrypt wypisuje jedną linię
i kończy się kodem wyjścia 2, kolekcja nie powstaje:

```
Baza wiedzy nie jest częścią repozytorium. Umieść artykuły w kb/ (format: README, sekcja "Własna dokumentacja").
```

Sprawdzenie wyszukiwania bez bota: `uv run python src/search.py "gdzie jest mój
zwrot"` wypisuje 3 najlepsze fragmenty w postaci `[wynik] id (kategoria) tytuł`.

## Własny zbiór pytań

Rozpoznawanie intencji opiera się na trzech zbiorach w `data/`; wszystkie
dotyczą wsparcia płatności i trzymają się `data/taxonomy.json`:

- `taxonomy.json`: 52 intencje w 10 kategoriach (`account`, `billing`, `buyers`,
  `disputes`, `integration`, `payments`, `payouts`, `refunds`, `security`,
  `service`) plus klasy specjalne `other_in_scope`, `out_of_scope`, `chitchat`,
  `unsafe`; sklejany z `data/taxonomy/part-*.json` przez
  `uv run python src/merge_taxonomy.py` (powtórzone `id` kończy się kodem 1).
- `corpus/corpus-*.json`: 5412 pytań z etykietą intencji, używane przez kNN.
- `goldset/gold-*.json`: 288 pytań z oczekiwaną etykietą dla `make test-accuracy`
  i `make test-func`; żadne pytanie z gold setu nie występuje w korpusie.
- `goldset/split.json`: podział gold setu na test (192) i dev (96), seed 42.

Kto podłącza dokumentację z innej dziedziny, przygotowuje własną taksonomię,
korpus i gold set w tych samych kształtach JSON (taksonomia, wpis korpusu, wpis
gold setu):

```json
{"version": 1,
 "intents": [{"id": "refund_status_time", "category": "refunds", "definition": "...",
              "examples": ["..."], "not": ["..."]}],
 "special_classes": [{"id": "out_of_scope", "definition": "...", "examples": ["..."]}]}
```
```json
{"cases": [{"q": "Ile trwa zwrot?", "intent": "refund_status_time", "lang": "pl",
            "style": "plain"}]}
{"cases": [{"q": "Ile trwa zwrot?", "expected_intent": "refund_status_time",
            "expected_scope": "in_scope", "lang": "pl", "style": "plain"}]}
```

W gold secie `expected_scope` to `in_scope` albo id klasy specjalnej (wtedy
`expected_intent` ma tę samą wartość). `uv run python tools/question_coverage.py`
(`make coverage`) wypisuje tabelę intencja -> liczba pytań w korpusie i w gold
secie oraz etykiety poniżej progu (mniej niż 20 w korpusie albo 0 w gold secie;
`--strict` zwraca wtedy kod 1). Po zmianie korpusu skasuj `data/cache/`, inaczej
kNN używa starego indeksu. Do dopasowania są też wzorce w `src/rules.py`
i `BRAND_VOICE` w `src/answer_gen.py`.

## API

FastAPI; interaktywna dokumentacja pod `/docs`, specyfikacja pod `/openapi.json`.

| Metoda i ścieżka | Co robi |
|---|---|
| `GET /` | strona czatu (`web/index.html`) |
| `GET /health` | `{"status": "ok" lub "degraded", "ollama": bool, "qdrant": bool}`; `ok` tylko gdy obie usługi odpowiadają |
| `POST /chat` | żądanie `ChatIn`: `text` (wymagane), `session_id` (opcjonalne, brak = nowa sesja); odpowiedź `ChatOut` |
| `GET /dashboard` | panel (`web/dashboard.html`) |
| `GET /api/stats` | JSON dla panelu: `sessions`, `actions`, ostatnie 50 dialogów, ostatnie 20 zgłoszeń |

`ChatOut`: `session_id`, `reply` (tekst dla klienta), `action` (`answer`,
`clarify`, `ticket`, `handoff`, `chitchat_reply`, `unsafe_refuse`, `redirect`),
`intent` (albo `null`), `language` (`pl`/`en`), `ticket_id` (numer albo `null`),
`timings_ms` (czas warstw `rules`, `knn`, `llm`, `retrieval`; klucze pokazują
drogę pytania). Gdy Ollama albo Qdrant nie odpowiada, `/chat` zwraca kod 503
z tym samym kształtem: `action` = `ticket`, zgłoszenie już utworzone,
`timings_ms` puste; adres usługi i błąd idą do logu, proces żyje dalej.

Jednocześnie obsługiwane są najwyżej `MAX_INFLIGHT` (domyślnie 2) żądania `/chat`.
Żądanie czeka w kolejce na wolne miejsce najwyżej `QUEUE_TIMEOUT_S` (domyślnie
30 s, czyli około dwóch odpowiedzi modelu); potem dostaje 503 w kształcie `ChatOut`
z `action` = `ticket` i tekstem „Usługa jest teraz przeciążona…”; zgłoszenie
z powodem `overloaded` jest już utworzone, a w logu jest linia `overloaded`.
Każda odpowiedź 503 ma nagłówek `X-Reason`: `overloaded` (przeciążenie)
albo `service_unavailable` (Ollama lub Qdrant nie odpowiada).

```bash
curl -s -X POST http://localhost:8020/chat -H "Content-Type: application/json" \
  -d '{"text": "Gdzie jest mój zwrot za zamówienie z zeszłego tygodnia?"}'
```
```json
{"session_id": "3f9c1a2b7d4e",
 "reply": "Zwrot na kartę trwa zwykle od 3 do 7 dni roboczych.\n\nŹródło: KB-030",
 "action": "answer", "intent": "refund_status_time", "language": "pl",
 "ticket_id": null, "timings_ms": {"rules": 0.1, "knn": 41.7, "retrieval": 38.2}}
```

## Dokąd trafiają zgłoszenia

Zgłoszenie to wiersz w tabeli `tickets` bazy SQLite (`data/kremzapay.db`, ścieżka
w `DB_PATH`): sesja, powód (`no_knowledge`, `other_in_scope`,
`generation_not_grounded`, `service_unavailable`), kategoria, intencja,
priorytet, status `new`, czas. Widać je na `/dashboard` i w `/api/stats`. Nie ma
integracji z e-mailem, Telegramem ani CRM: nikt nie zostanie powiadomiony, dopóki
ktoś nie zajrzy do panelu albo do bazy. Klient widzi (`REPLIES` w `src/api.py`):

- brak odpowiedzi w dokumentacji: „Nie znalazłem pełnej odpowiedzi w dokumentacji,
  więc utworzyłem zgłoszenie #{tid}. Zespół wróci do Ciebie.”
- sędzia odrzucił odpowiedź: „Nie mogę teraz odpowiedzieć rzetelnie na to pytanie,
  więc utworzyłem zgłoszenie #{tid}. Zespół wróci do Ciebie.”
- awaria Ollama lub Qdrant: „Usługa jest chwilowo niedostępna, przekazałem sprawę
  do zespołu, zgłoszenie #{tid}.”

Jeśli SQLite lub panel nie wystarczą, napisz do autora, pomogę podłączyć inne
rozwiązanie: https://github.com/aleksykremza-dev.

## Testy

Testy żywe łączą się z botem pod `http://localhost:8020` (zmienna `API_URL` albo
`--url`) i wymagają Ollama oraz Qdrant z kolekcją; `test-accuracy` woła kaskadę
bez serwera HTTP. Raporty JSON trafiają do `data/reports/` (w `.gitignore`).

| Cel `make` | Co sprawdza | Co musi działać | Zaliczenie (inaczej kod 1) |
|---|---|---|---|
| `test` | `pytest -q`: reguły, PII, kaskada, API, ingest, klient LLM; Ollama i Qdrant zastąpione atrapami | nic | wszystkie testy passed, zero failed, kod 0 |
| `test-func` | `tests/live/func_by_category.py`: po 1 pytaniu z gold setu na każdą intencję i klasę specjalną przez `POST /chat` | bot + usługi | żadna klasa specjalna nie zawiodła, trafność intencji >= 0,6 (`--min-intent-accuracy`) |
| `test-oos` | `tests/live/out_of_scope.py`: 22 pytania (injection, oszustwo, inne produkty, podatki, tematy obce) muszą dać oczekiwaną akcję; przypadki dla warstwy reguł nie mogą mieć w `timings_ms` kluczy `llm` ani `retrieval` | bot + usługi | 22/22 ok |
| `test-accuracy` | `src/eval_cascade.py`: 288 pytań gold setu, `accuracy_all`, `accuracy_dev`, `accuracy_test`, macro-F1 (wszystkie i test), recall klas specjalnych, najczęstsze pomyłki; `--limit N` skraca przebieg; `--subset dev\|test\|all` (domyślnie `all`) wybiera część z `split.json`, przy `dev` próg sprawdza `accuracy_dev` | Ollama, Qdrant | `accuracy_test` >= 0,73 (`MIN_ACCURACY`, `--min-accuracy`); próg to pomiar 0,755 na `qwen2.5:7b-instruct` minus 0,02, zaokrąglony w dół do setnych, jako zapas na przyszłe aktualizacje modelu, zależności i promptów; przy temperature 0 i stałym seed przebieg jest powtarzalny (dwa przebiegi 01.10 zgodne 288/288) |
| `test-load` | `tests/live/load.py`: 5 równoległych klientów (`--users`), 100 żądań do `/chat` (`--requests`); 503 z `X-Reason: overloaded` liczone osobno jako „degraded” | bot + usługi | zero odpowiedzi 500, innych 5xx i błędów transportu; udział degraded <= 0,3 (`--max-degraded`); p95 odpowiedzi 200 <= 60 000 ms (`--p95-ms`) |
| `test-stress` | `tests/live/stress.py`: pusty tekst, 5000 znaków, same emoji, mieszanka pl/en, 10 numerów kart, 100 powtórzeń tego samego pytania, ponowne użycie `session_id`, na końcu `/health` | bot + usługi | każda odpowiedź to 200 albo 503 z JSON zawierającym `reply` |
| `test-stability` | `tests/live/stability.py --minutes 60`: sonda co 20 s (`--interval-s`), RSS i liczba deskryptorów procesu `uvicorn api:app` z `/proc` (Linux; `--pid`) | bot + usługi | zero 5xx, wzrost RSS <= 200 MB (`--max-rss-growth-mb`), wzrost liczby otwartych plików <= 50 (`--max-fd-growth`; liczba waha się o kilkanaście, bo połączenia SQLite zwalnia odśmiecacz) |
| `test-all` | `test`, `test-func`, `test-oos`, `test-accuracy`, `test-load`, `test-stress` po kolei (bez `test-stability`) | wszystko | każdy cel kod 0, na końcu `ALL TESTS PASSED` |
| `codemap` | `tools/codemap.py --out data/reports/codemap.json` | git z remote `origin` | plik zapisany, kod 0 |
| `coverage` | `tools/question_coverage.py`: pokrycie intencji pytaniami | nic | kod 0 (z `--strict` kod 1 przy brakach) |
| `ingest` | `src/ingest.py` | Qdrant, `kb/` | `Done: M points ...`, kod 0 |

Scenariusz ręczny, awaria Qdrant (nie ma go w `make`, bo zatrzymuje kontener):

```bash
docker compose stop
curl -s -i -X POST localhost:8020/chat -H "Content-Type: application/json" \
  -d '{"text": "jak zrobić zwrot płatności?"}'
curl -s localhost:8020/health
docker compose start
```

Oczekiwane: `HTTP/1.1 503`, nagłówek `x-reason: service_unavailable`, w treści
`action` = `ticket` i tekst „Usługa jest chwilowo niedostępna…” z numerem
zgłoszenia; `/health` zwraca `{"status":"degraded","ollama":true,"qdrant":false}`;
w logu serwera linie `qdrant http://localhost:6335 failed: … Connection refused`
i `service unavailable for session …`; proces działa dalej, a po
`docker compose start` `/health` wraca do `ok`.

Gold set jest podzielony na stałe w `data/goldset/split.json` (seed 42): część
test (192 pytania) i część dev (96). Podawana trafność i próg `MIN_ACCURACY` to
`accuracy_test`; na części dev dobiera się progi i prompty, żeby wynik testu nie
był dopasowany do pytań, na których coś stroiono.

Porównanie modeli z obecnym promptem klasyfikatora, przed dodaniem reguły
o wypłacie z cudzego konta (01.10.2026, Ollama 0.35.0, GTX 1050 Ti 4 GB,
`LLM_THINK=false`, 288 pytań, raporty w `data/reports/`):

| Model | `accuracy_test` | macro-F1 (test) | Minuty |
|---|---|---|---|
| `qwen2.5:7b-instruct` | 0,750 | 0,751 | 18,9 |
| `qwen3:8b` | 0,750 | 0,756 | 40,8 |
| `gemma4:e4b` | 0,729 | 0,751 | 30,7 |
| `qwen3:4b-instruct` | 0,714 | 0,720 | 16,0 |

Obecny kod (02.10.2026, z regułą o wypłacie z cudzego konta) na części test (192):

| Model | `accuracy_test` | macro-F1 (test) | Minuty (192 pytania) |
|---|---|---|---|
| `qwen2.5:7b-instruct` | 0,755 | 0,753 | 15,2 |

Wariant promptu z podobieństwem kandydatów i `other_in_scope` tylko wtedy, gdy
żaden kandydat nie pasuje nawet częściowo, sprawdzony na części dev, nie poprawił
trafności (`qwen2.5:7b-instruct` 0,755 na teście, `qwen3:8b` 0,740), a dał więcej
pomyłek kupujący/sprzedawca (12 zamiast 8), więc nie został przyjęty.

Domyślny `ANSWER_MODEL` to `qwen2.5:7b-instruct`: najwyższa `accuracy_test`;
`qwen3:8b` byłby domyślny tylko przy przewadze co najmniej 0,03, a w pomiarze
z 01.10 miał tę samą trafność (0,750) przy 2,2 raza dłuższym przebiegu.

Do CI nadaje się wyłącznie `make test`: nie potrzebuje modelu ani Dockera i trwa
kilka sekund; pozostałe cele uruchamia się lokalnie przy działających usługach.

## Koszty

Modele działają lokalnie, więc koszt to sprzęt i prąd, nie tokeny. Wyjście
modelu jest ograniczone (`num_predict`): 220 tokenów na klasyfikator, 400 na odpowiedź, 5 na sędziego; temperatura 0. Wywołania:

| Ścieżka | Wywołania modelu | Szacunek tokenów wejście / wyjście |
|---|---|---|
| reguły albo kNN z gotową akcją; kNN przyjęty, ale brak pokrycia w bazie | 0 | 0 |
| odpowiedź po kNN | odpowiedź + sędzia (2) | ok. 2 400 / 260 |
| odpowiedź po klasyfikatorze LLM | klasyfikator + odpowiedź + sędzia (3) | ok. 3 150 / 350 |
| zgłoszenie albo dopytanie po klasyfikatorze LLM | 1 | ok. 750 / 90 |

Szacunki wynikają z rozmiarów promptów tej kaskady (3 fragmenty po ok. 800
znaków w kontekście odpowiedzi) i są przybliżone; na modelu hostowanym
i rozliczanym za tokeny wyszłoby od kilku do kilkudziesięciu dolarów na 1000
pytań. Inny model w Ollama to zmiana `ANSWER_MODEL`; inny dostawca to `src/llm.py`.

## Ograniczenia

- Trafność (`make test-accuracy`) mierzy tylko rozpoznanie intencji i klasy;
  jakość tekstu odpowiedzi nie jest mierzona, jedyną kontrolą jest sędzia tak/nie.
- Próg kNN `T_ACCEPT` był dobierany na tym samym gold secie, na którym liczona
  jest trafność, więc wynik jest optymistyczny; na własnych danych progi
  w `config.py` trzeba dobrać od nowa.
- Próg `MIN_ACCURACY` (0,73) leży co najmniej 0,02 poniżej `accuracy_test` (0,755) jako zapas na
  przyszłe aktualizacje modelu, zależności i promptów; przy temperature 0 i stałym
  seed przebieg jest powtarzalny (dwa przebiegi 01.10 zgodne 288/288).
- Zgłoszenia nigdzie nie są dostarczane: tylko SQLite i panel.
- Jeden model (`ANSWER_MODEL`) obsługuje klasyfikację, odpowiedź i sędziego;
  nie ma zapasowego LLM, awaria Ollama oznacza 503 i zgłoszenie.
- Przepustowość ogranicza lokalny model: Ollama domyślnie obsługuje żądania po
  kolei, a na GTX 1050 Ti 4 GB `qwen2.5:7b-instruct` działa częściowo na CPU.
  Bez limitu przy 10 równoległych klientach mediana odpowiedzi wyniosła 114,5 s
  (pomiar 02.10.2026), dlatego `/chat` przyjmuje najwyżej `MAX_INFLIGHT` żądań
  naraz, a nadmiarowe po `QUEUE_TIMEOUT_S` dostają 503 ze zgłoszeniem `overloaded`.
  Na mocniejszym sprzęcie oba parametry można podnieść w `.env`.
- Tylko polski i angielski; inne języki są traktowane jak angielski.
- Filtr kategorii przy wyszukiwaniu działa tylko, gdy `category` w nagłówkach
  artykułów pokrywa się z kategoriami w `data/taxonomy.json`; przy rozjeździe
  wyszukiwanie po cichu wraca do wyników bez filtra.

## Mapa kodu

`make codemap` uruchamia `tools/codemap.py` i buduje `data/reports/codemap.json`:
dla każdej funkcji, klasy i metody w `src/` i `tools/` plik, zakres linii,
sygnatura i link do tych linii na GitHubie w bieżącym commicie. Moduły w `src/`:

| Moduł | Rola |
|---|---|
| `config.py` | ustawienia, progi i ścieżki (od katalogu repozytorium), odczyt `.env` |
| `llm.py` | jedyny klient Ollama: `generate`, `generate_json`, `ping`; timeout, powtórka, wyjątki |
| `taxonomy.py` | wczytanie `data/taxonomy.json` raz; słowniki intencja -> kategoria / definicja |
| `pii.py` | maskowanie danych osobowych przed modelem i przed zapisem |
| `rules.py` | warstwa 0: wzorce ataków, oszustw, innych produktów, podatków, prośby o człowieka |
| `knn_router.py` | warstwa 1: indeks embeddingów korpusu (cache w `data/cache/`), głosowanie sąsiadów |
| `llm_classifier.py` | warstwa 2: wybór etykiety z kandydatów kNN jednym wywołaniem modelu (najpierw kupujący czy sprzedawca), wynik w JSON |
| `search.py` | embedding pytania i zapytanie do Qdrant z opcjonalnym filtrem kategorii; `ping` |
| `cascade.py` | sklejenie warstw, wykrycie języka, decyzja, `TurnState` |
| `answer_gen.py` | prompt z fragmentami, odpowiedź ze źródłem |
| `judge.py` | kontrola pokrycia odpowiedzi we fragmentach |
| `store.py` | SQLite: sesje, wiadomości, zgłoszenia, statystyki dla panelu |
| `api.py` | FastAPI: `/`, `/health`, `/chat`, `/dashboard`, `/api/stats`, teksty odpowiedzi |
| `ingest.py` | wczytanie `kb/`, cięcie na fragmenty, embeddingi, zapis do Qdrant |
| `eval_cascade.py` | egzamin trafności na `data/goldset/`, raport JSON, kod 1 poniżej progu |
| `merge_taxonomy.py` | sklejenie `data/taxonomy/part-*.json` w `data/taxonomy.json` |

## Licencja

[PolyForm Noncommercial 1.0.0](LICENSE), Copyright (c) 2026 Oleksii Kremza.
Użycie komercyjne wymaga wcześniejszej pisemnej zgody właściciela praw autorskich.
