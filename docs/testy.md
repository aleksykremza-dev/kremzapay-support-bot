# Testy i pomiary

Wszystkie cele make, ich progi, scenariusze ręczne, porównanie modeli i pomiar na zewnętrznej bazie.

[Wróć do README](../README.md)

## Testy

Testy żywe łączą się z botem pod `http://localhost:8020` (zmienna `API_URL` albo
`--url`) i wymagają Ollama oraz Qdrant z kolekcją; `test-accuracy` woła kaskadę
bez serwera HTTP. Raporty JSON trafiają do `data/reports/` (w `.gitignore`).

| Cel `make` | Co sprawdza | Co musi działać | Zaliczenie (inaczej kod 1) |
|---|---|---|---|
| `test` | `pytest -q`: reguły, PII, kaskada, API, ingest, klient LLM; Ollama i Qdrant zastąpione atrapami | nic | wszystkie testy passed, zero failed, kod 0 |
| `style` | `tools/check_style.py`: nagłówek licencji, komentarze, docstringi, długa kreska | nic | `STYLE_EXIT=0`, kod 0 |
| `test-func` | `tests/live/func_by_category.py`: po 1 pytaniu z gold setu na każdą intencję i klasę specjalną przez `POST /chat` | bot + usługi | żadna klasa specjalna nie zawiodła, trafność intencji >= 0,6 (`--min-intent-accuracy`) |
| `test-oos` | `tests/live/out_of_scope.py`: 22 pytania (injection, oszustwo, inne produkty, podatki, tematy obce; tematy obce muszą dać `redirect`, nie zgłoszenie) muszą dać oczekiwaną akcję; przypadki dla warstwy reguł nie mogą mieć w `timings_ms` kluczy `llm` ani `retrieval` | bot + usługi | 22/22 ok |
| `test-accuracy` | `src/eval_cascade.py`: 288 pytań gold setu, `accuracy_all`, `accuracy_dev`, `accuracy_test`, macro-F1 (wszystkie i test), recall klas specjalnych, najczęstsze pomyłki; `--limit N` skraca przebieg; `--subset dev\|test\|all` (domyślnie `all`) wybiera część z `split.json`, przy `dev` próg sprawdza `accuracy_dev` | Ollama, Qdrant | `accuracy_test` >= 0,87 (`MIN_ACCURACY`, `--min-accuracy`); próg to pomiar 0,891 na `qwen2.5:7b-instruct` minus 0,02, zaokrąglony w dół do setnych, jako zapas na przyszłe aktualizacje modelu, zależności i promptów; przy temperature 0 i stałym seed przebieg jest powtarzalny (dwa przebiegi 04.10 zgodne 288/288) |
| `test-load` | `tests/live/load.py --users 3`: 3 równoległych klientów, czyli `MAX_INFLIGHT` + 1, normalne obciążenie; 100 żądań do `/chat` (`--requests`); 503 z `X-Reason: overloaded` liczone osobno jako „degraded”; cztery pomiary 02.10.2026 na GTX 1050 Ti po 100 żądań: od 0 do 20 odpowiedzi 503 `overloaded`, p95 odpowiedzi 200 od 50,4 do 53,5 s, kod 0 | bot + usługi | zero odpowiedzi 500, innych 5xx i błędów transportu; udział degraded <= 0,3 (`--max-degraded`); p95 odpowiedzi 200 <= 60 000 ms (`--p95-ms`) |
| `test-stress` | `tests/live/stress.py`: pusty tekst, 5000 znaków, same emoji, mieszanka pl/en, 10 numerów kart, 100 powtórzeń tego samego pytania, ponowne użycie `session_id`, na końcu `/health` | bot + usługi | każda odpowiedź to 200 albo 503 z JSON zawierającym `reply` |
| `test-stability` | `tests/live/stability.py --minutes 60`: sonda co 20 s (`--interval-s`), RSS i liczba deskryptorów procesu `uvicorn api:app` z `/proc` (Linux; `--pid`) | bot + usługi | zero 5xx, wzrost RSS <= 200 MB (`--max-rss-growth-mb`), wzrost liczby otwartych plików <= 50 (`--max-fd-growth`); pomiar 04.10.2026, 20 minut: RSS +4,2 MB (2250 -> 2254 MB), otwarte pliki 9 -> 9 (połączenia SQLite są zamykane po każdej operacji) |
| `test-all` | `test`, `test-func`, `test-oos`, `test-accuracy`, `test-load`, `test-stress` po kolei (bez `test-stability`) | wszystko | każdy cel kod 0, na końcu `ALL TESTS PASSED` |
| `codemap` | `tools/codemap.py --out data/reports/codemap.json` | git z remote `origin` | plik zapisany, kod 0 |
| `coverage` | `tools/question_coverage.py`: pokrycie intencji pytaniami | nic | kod 0 (z `--strict` kod 1 przy brakach) |
| `ingest` | `src/ingest.py` w kontenerze `api` (`docker compose run --rm api`) | Docker, `kb/` | `Done: M points ...`, kod 0 |
| `ingest-local` | `src/ingest.py` w lokalnym `.venv` | Qdrant, `kb/` | `Done: M points ...`, kod 0 |
| `up` / `down` / `logs` | `docker compose up -d --build` / `down` / `logs -f api` | Docker | kontenery `api` i `qdrant` działają |

Scenariusz ręczny, przeciążenie (więcej klientów niż `MAX_INFLIGHT` + 1):

```bash
uv run python tests/live/load.py --users 5 --max-degraded 1.0
```

Oczekiwane: około 30% odpowiedzi to 503 z nagłówkiem `X-Reason: overloaded`
(w wyniku linia `degraded (503 overloaded)`), zero odpowiedzi 500, innych 5xx
i błędów transportu, serwer działa dalej (`/health` zwraca `ok`). Pomiar
02.10.2026 na GTX 1050 Ti: trzy przebiegi po 100 żądań, od 29 do 32 odpowiedzi
503 `overloaded`, p95 odpowiedzi 200 od 52 do 60 s.

Scenariusz ręczny, awaria Qdrant (nie ma go w `make`, bo zatrzymuje kontener):

```bash
docker compose stop qdrant
curl -s -i -X POST localhost:8020/chat -H "Content-Type: application/json" \
  -d '{"text": "jak zrobić zwrot płatności?"}'
curl -s localhost:8020/health
docker compose start qdrant
```

Oczekiwane: `HTTP/1.1 503`, nagłówek `x-reason: service_unavailable`, w treści
`action` = `ticket` i tekst „Usługa jest chwilowo niedostępna…” z numerem
zgłoszenia; `/health` zwraca `{"status":"degraded","ollama":true,"qdrant":false}`;
w logu serwera linie `qdrant http://localhost:6335 failed: … Connection refused`
i `service unavailable for session …`; proces działa dalej, a po
`docker compose start qdrant` `/health` wraca do `ok`.

Gold set jest podzielony na stałe w `data/goldset/split.json` (seed 42): część
test (192 pytania) i część dev (96). Podawana trafność i próg `MIN_ACCURACY` to
`accuracy_test`; na części dev dobiera się progi i prompty, żeby wynik testu nie
był dopasowany do pytań, na których coś stroiono.

Wybór klasyfikatora tematu (04.10.2026, tylko część dev i walidacja krzyżowa
5-krotna na korpusie; trafność top-1 i obecność właściwego tematu wśród 5
kandydatów dla 72 pytań dev z intencją):

| Warstwa 1 | dev top-1 | dev wśród 5 | korpus top-1 (CV) | embeddingi korpusu na CPU | RAM procesu |
|---|---|---|---|---|---|
| kNN, `paraphrase-multilingual-MiniLM-L12-v2` (wersja 1.0.0) | 0,764 | 0,889 | 0,721 | 76 s | 1,0 GB |
| kNN, `paraphrase-multilingual-mpnet-base-v2` | 0,819 | 0,972 | 0,744 | 201 s | 2,4 GB |
| kNN, `intfloat/multilingual-e5-large` | 0,861 | 0,986 | 0,841 | 1194 s | 2,7 GB |
| regresja logistyczna `C` 64, `multilingual-e5-large` (obecna) | 0,972 | 1,000 | 0,931 | 1194 s, w repo gotowy indeks | 2,7 GB |

Cała kaskada na części dev: 0,802 (kNN MiniLM) -> 0,948 (obecna). Przy `P_ACCEPT`
0,3 klasyfikator LLM jest wołany przy 4 z 88 pytań dev, które nie zatrzymały się
na regułach (wcześniej 38). Dwa przebiegi wszystkich 288 pytań 04.10.2026
(drugi po dodaniu reguły `out_of_scope` i wzorców VAT oraz cudzej pracy) dały
te same 288 odpowiedzi: `accuracy_all` 0,910, `accuracy_dev` 0,948,
`accuracy_test` 0,891, macro-F1 test 0,888, 2,4 do 2,8 minuty.

Porównanie modeli językowych z routerem kNN z wersji 1.0.0, przed dodaniem reguły
o wypłacie z cudzego konta (01.10.2026, Ollama 0.35.0, GTX 1050 Ti 4 GB,
`LLM_THINK=false`, 288 pytań, raporty w `data/reports/`):

| Model | `accuracy_test` | macro-F1 (test) | Minuty |
|---|---|---|---|
| `qwen2.5:7b-instruct` | 0,750 | 0,751 | 18,9 |
| `qwen3:8b` | 0,750 | 0,756 | 40,8 |
| `gemma4:e4b` | 0,729 | 0,751 | 30,7 |
| `qwen3:4b-instruct` | 0,714 | 0,720 | 16,0 |

Wersja 1.0.0 (02.10.2026, router kNN, z regułą o wypłacie z cudzego konta) na części test (192):

| Model | `accuracy_test` | macro-F1 (test) | Minuty (192 pytania) |
|---|---|---|---|
| `qwen2.5:7b-instruct` | 0,755 | 0,753 | 15,2 |

Wariant promptu z podobieństwem kandydatów i `other_in_scope` tylko wtedy, gdy
żaden kandydat nie pasuje nawet częściowo, sprawdzony na części dev, nie poprawił
trafności (`qwen2.5:7b-instruct` 0,755 na teście, `qwen3:8b` 0,740), a dał więcej
pomyłek kupujący/sprzedawca (12 zamiast 8), więc nie został przyjęty.

Domyślny `ANSWER_MODEL` to `qwen2.5:7b-instruct`: najwyższa `accuracy_test`;
`qwen3:8b` byłby domyślny tylko przy przewadze co najmniej 0,03, a w pomiarze
z 01.10 miał tę samą trafność (0,750) przy 2,2 raza dłuższym przebiegu. Z obecnym
routerem modele językowe nie były porównywane ponownie.

Do CI nadaje się wyłącznie `make test`: nie potrzebuje modelu ani Dockera i trwa
kilka sekund; pozostałe cele uruchamia się lokalnie przy działających usługach.
GitHub Actions (`.github/workflows/ci.yml`) przy każdym push i pull request robi
`uv sync --frozen`, `pytest` i bramkę stylu `tools/check_style.py` (`make style`:
nagłówek licencji, zero komentarzy i docstringów, bez długiej kreski); bramka
kończy się kodem 1 przy pierwszym naruszeniu.

### Pomiar na zewnętrznej bazie

Pomiar na zewnętrznej bazie testowej (59 artykułów, inna baza niż korpus klasyfikatora (ta sama dziedzina płatności);
100 pytań po polsku; qwen2.5:7b-instruct, GTX 1050 Ti, 04.10.2026). Obecny kod
w porównaniu z wersją 1.0.0 (router kNN) na tych samych pytaniach:

| Metryka | 1.0.0 (kNN) | obecny kod (e5 + regresja logistyczna) |
|---|---|---|
| Pytania spoza bazy zakończone zgłoszeniem | 15/15 | 15/15 |
| Odpowiedzi na pytania z bazy | 54 z 85 | 54 z 85 |
| Odpowiedzi ze wskazaniem właściwego artykułu | 42 z 85 | 39 z 85 |
| Zgłoszenia na pytania, na które baza ma odpowiedź | 28 | 30 |
| Przekierowania pytań z bazy (`redirect`) | 3 | 1 |
| Mediana / p95 czasu odpowiedzi | 14,4 / 25,9 s | 10,2 / 22,8 s |

Wynik na zewnętrznej bazie nie poprawił się razem z trafnością tematu: klasyfikator
częściej wybiera konkretny temat zamiast `other_in_scope` (zgłoszenia z tego powodu
10 -> 5), ale część tych tematów prowadzi do kategorii, w której nie ma właściwego
artykułu (np. dwa pytania sprzedawcy o wyłączenie metody płatności rozpoznane jako
temat kupującego).

Na własnej domenie (zbiór kontrolny 192 pytań): trafność klasyfikacji 0,891.
