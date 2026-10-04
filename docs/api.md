# API, zgłoszenia i przekazanie człowiekowi

Endpointy, kształt odpowiedzi, limit równoległych żądań, dokąd trafiają zgłoszenia i jak działa przekazanie rozmowy człowiekowi.

[Wróć do README](../README.md)

## API

FastAPI; interaktywna dokumentacja pod `/docs`, specyfikacja pod `/openapi.json`.

| Metoda i ścieżka | Co robi |
|---|---|
| `GET /` | strona czatu (`web/index.html`) |
| `GET /health` | `{"status": "ok" lub "degraded", "ollama": bool, "qdrant": bool}`; `ok` tylko gdy obie usługi odpowiadają |
| `POST /chat` | żądanie `ChatIn`: `text` (wymagane), `session_id` (opcjonalne, brak = nowa sesja); odpowiedź `ChatOut` |
| `GET /dashboard` | panel (`web/dashboard.html`) |
| `GET /api/stats` | JSON dla panelu: `sessions`, `actions`, ostatnie 50 dialogów, ostatnie 20 zgłoszeń, `handoff_queue` (otwarte przekazania z rozmową w masce, bez kontaktu) |
| `POST /api/tickets/{id}/close` | zamyka zgłoszenie i jego sesję; `{"id": N, "status": "closed"}`, 404 dla nieznanego numeru |

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
`generation_not_grounded`, `service_unavailable`, `overloaded`, `handoff`), kategoria, intencja,
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

## Przekazanie człowiekowi

Rozmowa trafia do człowieka, gdy klient wprost o to prosi (reguła
`explicit_human_request` w `rules.py`) albo gdy klasyfikator uzna, że chce
rozmawiać z człowiekiem (`wants_human`). Wtedy:

1. Powstaje zgłoszenie z powodem `handoff` i priorytetem `high` (z intencją, jeśli
   jest znana), a klient dostaje jego numer i prośbę: „Przekazuję rozmowę do
   konsultanta, zgłoszenie #N. Zostaw e-mail lub telefon, odezwiemy się.”
2. Sesja dostaje status `handoff`. Kolejne wiadomości w tej sesji nie trafiają
   do kaskady ani do modelu: zapisują się w `messages` z numerem tego samego
   zgłoszenia, a klient widzi „Twoja wiadomość została dodana do zgłoszenia #N.”
3. Kontakt tylko w zgłoszeniu: e-mail i telefon z wiadomości (także z tej, która
   wywołała przekazanie) trafiają w oryginale wyłącznie do kolumny
   `tickets.contact`. W `messages`, w logach, w `/api/stats` i w modelu zostaje
   maska (`<EMAIL_1>`, `<PHONE_1>`).
4. Kolejka w panelu: na górze `/dashboard` blok „Czeka na człowieka” z liczbą
   otwartych przekazań (także w tytule karty jako „(N) …”), a przy każdym numer,
   czas, temat, informacja, czy jest kontakt, i cała rozmowa. Przycisk „Zamknij”
   (`POST /api/tickets/{id}/close`) zamyka zgłoszenie i sesję; następna wiadomość
   w tej sesji znowu trafia do bota.

Starsze bazy dostają kolumny `tickets.contact` i `messages.ticket_id` automatycznie
(`ALTER TABLE` przy pierwszym połączeniu).
