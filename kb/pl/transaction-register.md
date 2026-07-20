---
id: KB-069
category: integration
lang: pl
title: Rejestracja transakcji
---

# Rejestracja transakcji

Rejestracja transakcji to pierwszy krok każdej płatności. Wysyłasz dane płatności do kremzaPay, otrzymujesz w odpowiedzi token i przekierowujesz kupującego na stronę płatności.

**Żądanie**

Wyślij żądanie `POST` na `/transaction/register` z następującymi polami:

- `merchantId` — identyfikator sprzedawcy z Panelu.
- `sessionId` — unikalny identyfikator tej płatności. Generuj nową wartość dla każdej próby; nigdy jej nie używaj ponownie.
- `amount` — kwota w najmniejszej jednostce waluty (groszach), więc 49,90 PLN wysyłasz jako `4990`.
- `currency` — kod waluty, na przykład `PLN`.
- `description` — krótki opis widoczny dla kupującego.
- `urlReturn` — adres, na który kupujący wraca po płatności.
- `signature` — podpis SHA-384 z `{sessionId, merchantId, amount, currency, crcKey}`.

**Odpowiedź**

Poprawna odpowiedź zawiera `token`. Zapisz go razem z `sessionId`, aby móc powiązać późniejszy webhook z właściwym zamówieniem.

**Przekierowanie kupującego**

Przekieruj kupującego na stronę płatności kremzaPay, używając zwróconego tokenu. Kupujący finalizuje tam płatność i zostaje odesłany na Twój `urlReturn`.

**Uwagi**

- Zarejestrowana sesja pozostaje ważna przez 60 minut. Jeśli kupujący nie zapłaci w tym czasie, sesja wygasa i musisz zarejestrować nową transakcję.
- Transakcja rozpoczyna się w statusie `pending` i przechodzi przez `authorized` do `completed`.
- `urlReturn` jedynie sprowadza kupującego z powrotem; nie jest potwierdzeniem płatności. Zawsze poczekaj na webhook i zweryfikuj transakcję.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
