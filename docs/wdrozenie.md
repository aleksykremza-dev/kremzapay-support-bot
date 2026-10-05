# Od laptopa do wdrożenia w firmie

Plan przejścia z wersji na jeden komputer do wdrożenia w firmie z wieloma
użytkownikami. Wszystkie kroki poniżej to plan, nie gotowe funkcje; przy każdym
jest opis, co dziś robi kod, co się zmienia i jak sprawdzić, że działa.

[Wróć do README](../README.md)

## Zasada

Logika silnika (kaskada, reguły, sędzia, przekazanie człowiekowi, maskowanie
danych) zostaje bez zmian. Wymieniane są części wokół niej. Jest to możliwe, bo
każda zależność zewnętrzna ma w kodzie jedno miejsce:

| Zależność | Jedyne miejsce w kodzie |
|---|---|
| Model językowy | `src/llm.py` (`generate`, `generate_json`, `ping`) |
| Baza danych | `src/store.py` (sesje, wiadomości, zgłoszenia, migracje) |
| Baza wiedzy | `src/search.py` (zapytania) i `src/ingest.py` (zapis) |
| Ustawienia | `src/config.py` i `.env` |

## Kolejność kroków

1. Ustawienia w jednym pliku i panel administracyjny.
2. Logowanie, role, klucze API.
3. Pakiet dziedziny.
4. Jakość: trafność, ocena przy każdej zmianie, poprawki operatorów.
5. Model, dane i ruch: vLLM albo hostowany LLM, Postgres, Redis, wiele kopii.
6. Monitoring.
7. Kanały i helpdesk.
8. RODO.
9. Orkiestracja.

Kolejność wynika z ryzyka: najpierw to, bez czego nie da się bezpiecznie wpuścić
pracowników firmy (dostęp, ustawienia), potem skala.

## 1. Ustawienia i panel administracyjny

- **Teraz:** progi w `src/config.py`, teksty odpowiedzi w `REPLIES` (`src/api.py`),
  wzorce reguł w `src/rules.py`, głos marki w `BRAND_VOICE` (`src/answer_gen.py`).
  Zmiana wymaga edycji kodu.
- **Zmiana:** jeden plik ustawień dziedziny (progi, teksty, wzorce, języki,
  godziny pracy) wczytywany przy starcie; panel administracyjny do edycji z
  historią wersji.
- **Sprawdzenie:** zmiana tekstu odpowiedzi w panelu widoczna w czacie bez
  restartu; testy jednostkowe na walidację pliku ustawień.

## 2. Logowanie, role, klucze API

- **Teraz:** `/dashboard`, `/api/stats` i `POST /api/tickets/{id}/close` nie mają
  logowania.
- **Zmiana:** logowanie przez SSO (OpenID Connect, np. Microsoft Entra ID albo
  Keycloak) dla panelu; role operator i administrator; klucze API dla kanałów,
  które wołają `/chat`; tabela dziennika działań (kto zamknął zgłoszenie, kto
  zmienił ustawienia).
- **Sprawdzenie:** testy: bez tokenu 401, operator nie zmienia ustawień (403),
  każde zamknięcie zgłoszenia ma wpis w dzienniku.

## 3. Pakiet dziedziny

- **Teraz:** jedna dziedzina: `data/taxonomy*.json`, `data/corpus/`,
  `data/goldset/`, wzorce w `src/rules.py`, teksty w `src/api.py`, nazwa kolekcji
  w `config.py`.
- **Zmiana:** katalog `domains/<nazwa>/` ze wszystkimi tymi elementami; zmienna
  `DOMAIN` wybiera pakiet; każdy klient ma własną kolekcję w Qdrant i własny zbiór
  kontrolny.
- **Sprawdzenie:** dwa pakiety (np. płatności i procedury HR) na tym samym kodzie,
  każdy ze swoją bramką trafności.

## 4. Jakość

- **Teraz:** bramka trafności `make test-accuracy` (próg `MIN_ACCURACY`) i sędzia
  każdej odpowiedzi; trafność rozpoznania tematu 89,1% na pytaniach
  niewidzianych przy strojeniu (91% na wszystkich 288); na zewnętrznej bazie
  właściwy artykuł w 34 z 34 odpowiedzi części testowej (66 z 67 na wszystkich
  100 pytaniach).
- **Zmiana:** mierzenie trafności
  odpowiedzi automatycznych razem z udziałem pytań, na które bot odpowiada sam;
  przycisk w panelu „temat był inny”, z którego po przeglądzie powstają nowe
  przykłady w korpusie; ocena przy każdej zmianie na maszynie z GPU.
- **Sprawdzenie:** raport trafności przy każdej zmianie w CI; spadek poniżej progu
  blokuje wdrożenie.

## 5. Model, dane i ruch

- **Teraz:** Ollama obsługuje żądania po kolei; `/chat` przyjmuje `MAX_INFLIGHT`
  (2) żądania naraz w jednym procesie; SQLite; jeden proces API.
- **Zmiana:**
  - `src/llm.py`: drugi dostawca obok Ollamy, API zgodne z OpenAI
    (`/v1/chat/completions`), które wystawia vLLM na własnych GPU albo hostowany
    model; wybór zmienną `LLM_PROVIDER`; vLLM przetwarza wiele pytań jednocześnie;
  - `src/store.py`: Postgres zamiast SQLite, migracje wersjonowane;
  - limit równoległych żądań wspólny dla wszystkich kopii (Redis) zamiast
    semafora w jednym procesie; cache odpowiedzi na powtarzalne pytania;
  - kilka kopii API za load balancerem (stan rozmowy jest w bazie, nie w pamięci).
- **Sprawdzenie:** `tests/live/load.py` z celem 1000+ pytań na godzinę i p95 czasu
  odpowiedzi, z zapisanym raportem; ten sam test co dziś, większa liczba klientów.

## 6. Monitoring

- **Teraz:** `/health` sprawdza Ollama i Qdrant; czas każdego kroku kaskady jest
  zapisywany w bazie przy każdej wiadomości.
- **Zmiana:** endpoint metryk dla Prometheus (czas kroków, liczba zgłoszeń według
  powodu, odpowiedzi 503, długość kolejki), wykresy w Grafana, alerty: rośnie
  udział zgłoszeń, rośnie p95, model niedostępny.
- **Sprawdzenie:** sztuczna awaria Qdrant (scenariusz z `docs/testy.md`) wywołuje
  alert w ciągu minuty.

## 7. Kanały i helpdesk

- **Teraz:** czat WWW; zgłoszenia w SQLite i w panelu.
- **Zmiana:** widget na stronę klienta, e-mail, Teams, WhatsApp jako adaptery,
  które wołają ten sam `/chat` z własnym `session_id`; nowe zgłoszenie trafia
  z całą rozmową do Zendesk albo Jira.
- **Sprawdzenie:** pytanie z e-maila kończy się odpowiedzią albo zgłoszeniem
  w helpdesku z tą samą treścią co w panelu.

## 8. RODO

- **Teraz:** dane osobowe maskowane przed modelem, logami i bazą; kontakt klienta
  w oryginale tylko w zgłoszeniu.
- **Zmiana:** czas przechowywania rozmów z automatycznym usuwaniem; usuwanie
  danych osoby na żądanie; hosting i model w UE; rejestr czynności przetwarzania.
- **Sprawdzenie:** test: rozmowa starsza niż ustawiony czas znika; żądanie
  usunięcia czyści wiadomości i kontakt.

## 9. Orkiestracja

- **Teraz:** obraz Docker (bez roota, `HEALTHCHECK`), `docker-compose.yml`, CI,
  obraz w GHCR.
- **Zmiana:** wdrożenie w Kubernetes albo Docker Swarm: kilka kopii API, sondy
  gotowości na `/health`, sekrety poza obrazem, aktualizacja bez przerwy.
- **Sprawdzenie:** aktualizacja wersji przy ruchu z `load.py` bez odpowiedzi 5xx.
