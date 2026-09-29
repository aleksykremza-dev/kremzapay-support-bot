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

Klient pisze pytanie na czacie. Zanim dostanie odpowiedź, tekst przechodzi przez
kolejne etapy; każdy etap ma swój plik w `src/`.

1. **Maskowanie danych osobowych** (`pii.py`). Numer karty, IBAN, PESEL, telefon
   i e-mail są zamieniane na etykiety `<CARD_1>`, `<IBAN_1>`, `<PESEL_1>`,
   `<PHONE_1>`, `<EMAIL_1>` zanim tekst zobaczy jakikolwiek model i zanim trafi
   do bazy. Do modeli i do SQLite idzie wyłącznie tekst zamaskowany.
2. **L0, reguły** (`rules.py`). Wzorce tekstowe bez modelu: manipulacja botem
   i prośby o pomoc w oszustwie kończą się odmową (`unsafe_refuse`), pytania
   o inne produkty i o podatki przekierowaniem (`redirect`), wyraźna prośba
   o człowieka przekazaniem rozmowy (`handoff`). Ułamek milisekundy.
3. **L1, kNN** (`knn_router.py`). Pytanie jest porównywane znaczeniowo
   (embeddingi) z korpusem przykładowych pytań z przypisaną intencją. Z 10
   najbliższych zwycięska intencja musi mieć co najmniej 5 głosów i średnie
   podobieństwo >= `T_ACCEPT` (0,62); wtedy jest przyjęta bez modelu. Pewność:
   `high` przy podobieństwie >= `CONF_HIGH` (0,72), inaczej `medium`.
4. **L2, klasyfikator LLM** (`llm_classifier.py`). Gdy kNN nie jest pewny (także
   gdy najbliższy przykład ma podobieństwo < `T_OOS`, 0,45), lokalny model w dwóch
   krokach wybiera kategorię albo klasę specjalną, potem intencję w kategorii,
   i zwraca JSON z pewnością `high|medium|low` oraz flagą `wants_human`.
5. **Decyzja** (`cascade.py`). Klasy specjalne dają gotową akcję: small talk ->
   `chitchat_reply`, treść niebezpieczna -> `unsafe_refuse`, poza zakresem ->
   `redirect`, temat w zakresie bez pasującej intencji -> `ticket`; `wants_human`
   -> `handoff`; pewność `low` -> `clarify` (bot dopytuje). W pozostałych
   przypadkach najlepszy fragment z Qdrant musi mieć wynik >= `RETRIEVAL_OK`
   (0,45), inaczej `ticket` z powodem `no_knowledge`.
6. **Odpowiedź** (`answer_gen.py`). Wyszukiwanie w Qdrant z filtrem po kategorii
   intencji (przy mniej niż 2 trafieniach filtr jest zdejmowany), 3 najlepsze
   fragmenty (`TOP_N`) trafiają do promptu; model pisze odpowiedź tylko na ich
   podstawie i kończy linią `Źródło: KB-###` (`Source:` po angielsku).
7. **Sędzia** (`judge.py`). Drugie wywołanie modelu: czy każde twierdzenie ma
   pokrycie we fragmentach, odpowiedź `yes`/`no`. Przy `no` odpowiedź nie
   wychodzi; klient dostaje informację o zgłoszeniu (`ticket_not_grounded`).

Każdy etap dopisuje swój wynik do jednego obiektu `TurnState` (czasy warstw,
wynik reguł, kNN, LLM, retrieval, decyzja). Obiekt trafia do SQLite razem
z wiadomością i jest widoczny na `/dashboard`, więc pytanie „dlaczego bot
odpowiedział właśnie tak” nie wymaga grzebania w logach. Historia sesji jest
zapisywana, ale przy odpowiadaniu nie jest używana: każde pytanie jest
rozpatrywane osobno. Język (`pl`/`en`) jest wykrywany po polskich znakach
diakrytycznych i liście typowych polskich słów.

Gdy bot nie jest pewny, błąd rozpoznania nie zamienia się w błędną odpowiedź:
niska pewność -> dopytanie (`clarify`); temat w zakresie, ale bez intencji albo
bez pokrycia w dokumentacji -> zgłoszenie (`ticket`); prośba o człowieka ->
`handoff`; odpowiedź bez pokrycia u sędziego -> zgłoszenie zamiast odpowiedzi.

| Termin | Co to jest | Gdzie |
|---|---|---|
| Embeddingi | wektory liczb: teksty o podobnym znaczeniu są blisko siebie; jeden model dla pl i en (`EMBED_MODEL`, fastembed) | `config.py`, `knn_router.py`, `search.py` |
| Qdrant | baza wektorów z fragmentami dokumentacji; znajduje najbliższe do pytania | `docker-compose.yml`, `search.py` |
| Progi | `K`, `T_ACCEPT`, `T_OOS`, `RETRIEVAL_OK`, `CONF_HIGH`, `TOP_K`, `TOP_N`, `CHUNK_SIZE`, `MIN_ACCURACY` | `config.py` |
| Klient Ollama | jedno miejsce wywołań modelu: timeout, powtórka, `LLMUnavailable`, `LLMBadOutput` | `llm.py` |
| Taksonomia | intencje z kategorią i definicją oraz klasy specjalne; wczytywana raz | `taxonomy.py`, `data/taxonomy.json` |
| Korpus | pytania z etykietą intencji dla warstwy kNN; indeks w `data/cache/` | `data/corpus/` |
| Gold set | pytania z oczekiwaną etykietą, tylko do mierzenia; rozłączny z korpusem | `data/goldset/` |
| Trafność, macro-F1, recall | odsetek trafionych etykiet; F1 uśrednione po etykietach; wykrywalność klas specjalnych | `eval_cascade.py` |

## Wymagania

| Co | Po co | Sprawdzenie |
|---|---|---|
| Python 3.12 (`.python-version`) i [uv](https://github.com/astral-sh/uv) | środowisko `.venv` z `pyproject.toml` | `uv --version` |
| Własna [Ollama](https://ollama.com) z modelem z `.env` (`ANSWER_MODEL`, domyślnie `qwen2.5:7b-instruct`) | klasyfikator, odpowiedzi i sędzia; jeden model na wszystkie warstwy | `curl http://localhost:11434/api/tags` zwraca listę modeli z tym tagiem |
| Własny Qdrant; w repo `docker-compose.yml` z przypiętym obrazem `qdrant/qdrant:v1.13.2`, port `6335` na hoście, dane w `qdrant_data/` | fragmenty dokumentacji i wyszukiwanie znaczeniowe | `curl http://localhost:6335/collections` zwraca JSON |
| Docker (dla Qdrant) | uruchomienie kontenera | `docker compose ps` |
| Własna dokumentacja w `kb/` | bez niej `ingest.py` kończy się kodem 2 | sekcja „Własna dokumentacja” |

Po starcie bota obie zależności sprawdza `GET /health`:
`curl http://localhost:8020/health` -> `{"status":"ok","ollama":true,"qdrant":true}`.
`status` to `degraded`, gdy któraś usługa nie odpowiada. Pole `qdrant` jest `true`
dopiero, gdy istnieje kolekcja `kremzapay_kb`, czyli po `ingest.py`.

Zmienne z `.env.example` (plik `.env` jest opcjonalny, bez niego działają
wartości domyślne z `config.py`): `OLLAMA_URL`, `ANSWER_MODEL`, `QDRANT_URL`,
`KB_DIR`, `DB_PATH`, `LLM_TIMEOUT_S`. W `config.py` są jeszcze `EMBED_MODEL`
(domyślnie `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`,
pobierany przez fastembed przy pierwszym użyciu), `COLLECTION` i `LLM_RETRIES`.

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

Po komunikacie `Application startup complete` otwórz http://localhost:8020
(czat) i http://localhost:8020/dashboard (panel z przebiegiem każdej rozmowy).
Pierwsze pytanie wymagające modelu trwa dłużej, bo model ładuje się do pamięci.
Wszystkie ścieżki (`kb/`, `data/`, `.env`) `config.py` liczy od katalogu
repozytorium, nie od bieżącego katalogu, więc skrypty można uruchamiać
z dowolnego miejsca, np.
`uv run --project ~/kremzapay-support-bot python ~/kremzapay-support-bot/src/ingest.py`.
Zatrzymanie: `Ctrl+C` w oknie uvicorn, potem `docker compose down` (dane
w `qdrant_data/` zostają).

## Własna dokumentacja

Artykuł to plik Markdown w `kb/<kategoria>/<id>.md`. `ingest.py` czyta wzorzec
`kb/*/*.md` (dokładnie jeden poziom podkatalogów); nazwa podkatalogu nie jest
przez kod używana, kategoria pochodzi z nagłówka. Nagłówek między dwiema liniami
`---` ma pola `title`, `category`, `id`; `category` musi być jedną z kategorii
w `data/taxonomy.json`, bo wyszukiwanie filtruje po niej fragmenty. Treść jest
cięta na fragmenty po akapitach (pusta linia między nimi) do ok. 800 znaków
(`CHUNK_SIZE`); każdy fragment dostaje tytuł artykułu. Jeśli po treści jest
jeszcze linia `---`, wszystko za ostatnią z nich jest odcinane (miejsce na
notatki, których nie chcesz indeksować). Wersja polska i angielska to osobne
pliki (np. `kb/refunds/KB-030-pl.md` i `kb/refunds/KB-030-en.md`); dodatkowe
pola nagłówka, np. `lang`, trafiają do payloadu w Qdrant. Minimalny przykład,
`kb/refunds/KB-030-pl.md`:

```
---
id: KB-030
category: refunds
title: Gdzie jest mój zwrot
---

Zwrot środków na kartę trwa zwykle od 3 do 7 dni roboczych od jego zlecenia
przez sprzedawcę. Status zwrotu widać w panelu w zakładce Zwroty.

Jeśli po 7 dniach roboczych środki nie wróciły, przygotuj numer transakcji
i skontaktuj się z obsługą sprzedawcy.
```

Po każdej zmianie w artykułach: `uv run python src/ingest.py` (to samo co
`make ingest`). Skrypt kasuje kolekcję i buduje ją od zera. Oczekiwany wynik:

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

Sprawdzenie wyszukiwania bez uruchamiania bota:
`uv run python src/search.py "gdzie jest mój zwrot"` wypisuje 3 najlepsze
fragmenty w postaci `[wynik] id (kategoria) tytuł`.

## Własny zbiór pytań

Rozpoznawanie intencji opiera się na trzech zbiorach w `data/`; wszystkie
dotyczą wsparcia płatności i trzymają się `data/taxonomy.json`:

- `taxonomy.json`: 52 intencje w 10 kategoriach (`account`, `billing`, `buyers`,
  `disputes`, `integration`, `payments`, `payouts`, `refunds`, `security`,
  `service`) plus klasy specjalne `other_in_scope`, `out_of_scope`, `chitchat`,
  `unsafe`. Źródłem są części `data/taxonomy/part-*.json`, sklejane przez
  `uv run python src/merge_taxonomy.py` (powtórzone `id` kończy się kodem 1).
- `corpus/corpus-*.json`: 5412 pytań z etykietą intencji, używane przez kNN.
- `goldset/gold-*.json`: 288 pytań z oczekiwaną etykietą, używane przez test
  trafności (`make test-accuracy`) i test funkcjonalny (`make test-func`).
  Żadne pytanie z gold setu nie występuje w korpusie.

Kto podłącza dokumentację z innej dziedziny, przygotowuje własną taksonomię,
korpus i gold set w tych samych kształtach JSON:

```json
{"version": 1,
 "intents": [{"id": "refund_status_time", "category": "refunds", "definition": "...",
              "examples": ["..."], "not": ["..."]}],
 "special_classes": [{"id": "out_of_scope", "definition": "...", "examples": ["..."]}]}
```
```json
{"cases": [{"q": "Ile trwa zwrot?", "intent": "refund_status_time",
            "lang": "pl", "style": "plain"}]}
```
```json
{"cases": [{"q": "Ile trwa zwrot?", "expected_intent": "refund_status_time",
            "expected_scope": "in_scope", "lang": "pl", "style": "plain"}]}
```

W gold secie `expected_scope` to `in_scope` albo id klasy specjalnej (wtedy
`expected_intent` ma tę samą wartość). `uv run python tools/question_coverage.py`
(`make coverage`) wypisuje tabelę intencja -> liczba pytań w korpusie i w gold
secie oraz listę etykiet poniżej progu (mniej niż 20 w korpusie albo 0 w gold
secie; `--strict` zwraca wtedy kod 1). Po zmianie korpusu skasuj `data/cache/`,
inaczej kNN dalej używa starego indeksu. Do dopasowania są też wzorce innych
produktów i podatków w `src/rules.py` oraz `BRAND_VOICE` w `src/answer_gen.py`.

## API

FastAPI; interaktywna dokumentacja pod `/docs`, specyfikacja pod `/openapi.json`.

| Metoda i ścieżka | Co robi |
|---|---|
| `GET /` | strona czatu (`web/index.html`) |
| `GET /health` | `{"status": "ok" lub "degraded", "ollama": bool, "qdrant": bool}`; `ok` tylko gdy obie usługi odpowiadają |
| `POST /chat` | żądanie `ChatIn`: `text` (wymagane), `session_id` (opcjonalne, brak = nowa sesja); odpowiedź `ChatOut` |
| `GET /dashboard` | panel (`web/dashboard.html`) |
| `GET /api/stats` | JSON dla panelu: `sessions`, `actions`, ostatnie 50 dialogów, ostatnie 20 zgłoszeń |

`ChatOut`: `session_id`, `reply` (tekst dla klienta), `action` (jedna z
`answer`, `clarify`, `ticket`, `handoff`, `chitchat_reply`, `unsafe_refuse`,
`redirect`), `intent` (albo `null`), `language` (`pl`/`en`), `ticket_id`
(numer zgłoszenia albo `null`), `timings_ms` (czas warstw; klucze `rules`,
`knn`, `llm`, `retrieval` pokazują, którędy przeszło pytanie). Gdy Ollama albo
Qdrant nie odpowiada, `/chat` zwraca kod 503 z tym samym kształtem `ChatOut`:
`action` = `ticket`, zgłoszenie już utworzone, `timings_ms` puste; adres usługi
i błąd trafiają do logu, proces działa dalej.

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
priorytet, status `new`, czas. Zgłoszenia widać na `/dashboard` i w `/api/stats`.
Nie ma integracji z e-mailem, Telegramem ani CRM: nikt nie zostanie powiadomiony,
dopóki ktoś nie zajrzy do panelu albo do bazy. Klient widzi wtedy (teksty
w `REPLIES` w `src/api.py`):

- brak odpowiedzi w dokumentacji: „Nie znalazłem pełnej odpowiedzi w dokumentacji,
  więc utworzyłem zgłoszenie #{tid}. Zespół wróci do Ciebie.”
- sędzia odrzucił odpowiedź: „Nie mogę teraz odpowiedzieć rzetelnie na to pytanie,
  więc utworzyłem zgłoszenie #{tid}. Zespół wróci do Ciebie.”
- awaria Ollama lub Qdrant: „Usługa jest chwilowo niedostępna, przekazałem sprawę
  do zespołu, zgłoszenie #{tid}.”

Jeśli SQLite lub panel nie wystarczą, napisz do autora, pomogę podłączyć inne
rozwiązanie: https://github.com/aleksykremza-dev.

## Testy

Testy żywe łączą się z botem pod `http://localhost:8020` (zmienna `API_URL`
albo `--url`) i wymagają Ollama oraz Qdrant z kolekcją; `test-accuracy` woła
kaskadę bezpośrednio, bez serwera HTTP. Raporty trafiają do `data/reports/`
(katalog w `.gitignore`), np. `2026-09-29-2130-accuracy.json`.

| Cel `make` | Co sprawdza | Co musi działać | Zaliczenie (inaczej kod 1) |
|---|---|---|---|
| `test` | `pytest -q`: reguły, PII, kaskada, API, ingest, klient LLM; Ollama i Qdrant zastąpione atrapami | nic | 70 passed, kod 0 |
| `test-func` | `tests/live/func_by_category.py`: po 1 pytaniu z gold setu na każdą intencję i klasę specjalną przez `POST /chat` | bot + usługi | żadna klasa specjalna nie zawiodła, trafność intencji >= 0,6 (`--min-intent-accuracy`) |
| `test-oos` | `tests/live/out_of_scope.py`: 22 pytania (injection, oszustwo, inne produkty, podatki, tematy obce) muszą dać oczekiwaną akcję; przypadki dla warstwy reguł nie mogą mieć w `timings_ms` kluczy `llm` ani `retrieval` | bot + usługi | 22/22 ok |
| `test-accuracy` | `src/eval_cascade.py`: 288 pytań gold setu, accuracy, macro-F1, recall klas specjalnych, najczęstsze pomyłki; `--limit N` skraca przebieg | Ollama, Qdrant | accuracy >= 0,719 (`MIN_ACCURACY`, `--min-accuracy`) |
| `test-load` | `tests/live/load.py --users 10 --requests 100`: 10 równoległych klientów, 100 żądań do `/chat` | bot + usługi | zero odpowiedzi 5xx i błędów transportu, p95 <= 15 000 ms (`--p95-ms`) |
| `test-stress` | `tests/live/stress.py`: pusty tekst, 5000 znaków, same emoji, mieszanka pl/en, 10 numerów kart, 100 powtórzeń tego samego pytania, ponowne użycie `session_id`, na końcu `/health` | bot + usługi | każda odpowiedź to 200 albo 503 z JSON zawierającym `reply` |
| `test-stability` | `tests/live/stability.py --minutes 60`: sonda co 20 s (`--interval-s`), RSS i liczba deskryptorów procesu `uvicorn api:app` z `/proc` (Linux; `--pid`) | bot + usługi | zero 5xx, wzrost RSS <= 200 MB (`--max-rss-growth-mb`) |
| `test-all` | `test`, `test-func`, `test-oos`, `test-accuracy`, `test-load`, `test-stress` po kolei (bez `test-stability`) | wszystko | każdy cel kod 0, na końcu `ALL TESTS PASSED` |
| `codemap` | `tools/codemap.py --out data/reports/codemap.json` | git z remote `origin` | plik zapisany, kod 0 |
| `coverage` | `tools/question_coverage.py`: pokrycie intencji pytaniami | nic | kod 0 (z `--strict` kod 1 przy brakach) |
| `ingest` | `src/ingest.py` | Qdrant, `kb/` | `Done: M points ...`, kod 0 |

Do CI nadaje się wyłącznie `make test`: nie potrzebuje modelu ani Dockera i trwa
kilka sekund; pozostałe cele uruchamia się lokalnie przy działających usługach.

## Koszty

Wszystkie modele działają lokalnie, więc koszt to sprzęt i prąd, nie tokeny.
Każde wywołanie modelu ma ograniczoną długość wyjścia (`num_predict`): 220
tokenów na każdy z dwóch etapów klasyfikatora, 400 na odpowiedź, 5 na sędziego;
temperatura 0. Liczba wywołań zależy od ścieżki pytania:

| Ścieżka | Wywołania modelu | Szacunek tokenów wejście / wyjście |
|---|---|---|
| reguły albo kNN z gotową akcją; kNN przyjęty, ale brak pokrycia w bazie | 0 | 0 |
| odpowiedź po kNN | odpowiedź + sędzia (2) | ok. 2 400 / 260 |
| odpowiedź po klasyfikatorze LLM | 2 etapy klasyfikatora + odpowiedź + sędzia (4) | ok. 3 250 / 440 |
| zgłoszenie albo dopytanie po klasyfikatorze LLM | 2 | ok. 850 / 180 |

Szacunki tokenów wynikają z rozmiarów promptów tej kaskady (3 fragmenty po ok.
800 znaków w kontekście odpowiedzi) i są przybliżone. Ta sama kaskada na modelu
hostowanym i rozliczanym za tokeny kosztowałaby od kilku do kilkudziesięciu
dolarów na 1000 pytań, zależnie od cennika. Zmiana modelu w Ollama to zmiana
`ANSWER_MODEL`; inny dostawca wymaga zmiany wyłącznie w `src/llm.py`.

## Ograniczenia

- Trafność (`make test-accuracy`) mierzy tylko rozpoznanie intencji i klasy;
  jakość tekstu odpowiedzi nie jest mierzona, jedyną kontrolą jest sędzia tak/nie.
- Próg kNN `T_ACCEPT` był dobierany na tym samym gold secie, na którym liczona
  jest trafność, więc wynik jest optymistyczny; na własnych danych progi
  w `config.py` trzeba dobrać od nowa.
- Zgłoszenia nigdzie nie są dostarczane: tylko SQLite i panel.
- Jeden model (`ANSWER_MODEL`) obsługuje klasyfikację, odpowiedź i sędziego;
  nie ma zapasowego LLM, awaria Ollama oznacza 503 i zgłoszenie.
- Tylko polski i angielski; wykrycie języka jest heurystyczne (polskie znaki
  i lista słów), inne języki są traktowane jak angielski.
- Filtr kategorii przy wyszukiwaniu działa tylko, gdy `category` w nagłówkach
  artykułów pokrywa się z kategoriami w `data/taxonomy.json`; przy rozjeździe
  wyszukiwanie po cichu wraca do wyników bez filtra.
- Bot nie używa historii rozmowy: każde pytanie rozpatruje osobno.

## Mapa kodu

`make codemap` uruchamia `tools/codemap.py` i buduje `data/reports/codemap.json`:
dla każdej funkcji, klasy i metody w `src/` i `tools/` plik, zakres linii,
sygnatura i link do tych linii na GitHubie w bieżącym commicie
(`--format table` wypisuje to samo w terminalu). Moduły w `src/`:

| Moduł | Rola |
|---|---|
| `config.py` | ustawienia, progi i ścieżki (od katalogu repozytorium), odczyt `.env` |
| `llm.py` | jedyny klient Ollama: `generate`, `generate_json`, `ping`; timeout, powtórka, wyjątki |
| `taxonomy.py` | wczytanie `data/taxonomy.json` raz; słowniki intencja -> kategoria / definicja |
| `pii.py` | maskowanie danych osobowych przed modelem i przed zapisem |
| `rules.py` | warstwa 0: wzorce ataków, oszustw, innych produktów, podatków, prośby o człowieka |
| `knn_router.py` | warstwa 1: indeks embeddingów korpusu (cache w `data/cache/`), głosowanie sąsiadów |
| `llm_classifier.py` | warstwa 2: dwuetapowa klasyfikacja modelem, wynik w JSON |
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
Użycie niekomercyjne na warunkach licencji; użycie komercyjne wymaga wcześniejszej
pisemnej zgody właściciela praw autorskich.
