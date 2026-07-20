---
id: KB-070
category: integration
lang: pl
title: Weryfikacja transakcji
---

# Weryfikacja transakcji

Weryfikacja to ostatni krok, który zamyka pętlę płatności. Po tym, jak kremzaPay wyśle webhook informujący o płatności, potwierdzasz nam jej wynik. Pominięcie tego kroku to najczęstszy błąd integracji.

**Dlaczego jest wymagana**

Webhook informuje, że status płatności się zmienił, ale Twoja integracja musi potwierdzić, że otrzymała i zaakceptowała poprawną kwotę oraz walutę. Dopóki nie zweryfikujesz płatności, pętla nie jest zamknięta i nie powinieneś traktować zamówienia jako opłaconego.

**Żądanie**

Po otrzymaniu webhooka wyślij żądanie `POST` na `/transaction/verify` z:

- `sessionId` — identyfikator potwierdzanej płatności.
- `amount` — kwota w groszach, zgodna z wartością z rejestracji.
- `currency` — kod waluty z pierwotnej rejestracji.
- `signature` — podpis SHA-384 z `{sessionId, merchantId, amount, currency, crcKey}`.

**Kolejność kroków**

1. Zarejestruj transakcję i przekieruj kupującego.
2. Odbierz webhook i zweryfikuj jego podpis.
3. Wyślij żądanie weryfikacji z powyższymi danymi.
4. Dopiero po poprawnej weryfikacji oznacz zamówienie jako opłacone i je zrealizuj.

**Częste błędy**

- Traktowanie powrotu kupującego na `urlReturn` jako potwierdzenia. Nim nie jest; płatność potwierdza wyłącznie weryfikacja.
- Weryfikacja z błędną `amount` lub `currency`. Muszą dokładnie odpowiadać zarejestrowanej transakcji.
- Całkowite pominięcie weryfikacji, przez co zamówienia pozostają niepotwierdzone.

Jeśli weryfikacja stale zawodzi, sprawdź kolejność pól i wartości użyte do zbudowania podpisu, a następnie skontaktuj się z pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
