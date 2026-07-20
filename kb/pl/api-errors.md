---
id: KB-015
category: integration
lang: pl
title: Najczęstsze kody błędów API
---

# Najczęstsze kody błędów API

Gdy żądania nie da się przetworzyć, API kremzaPay zwraca kod błędu. Poniżej zebrano najczęstsze kody i sposoby ich rozwiązania.

| Kod błędu | Znaczenie | Jak naprawić |
|---|---|---|
| `err-invalid-signature` | Podpis żądania się nie zgadza. | Sprawdź crc_key oraz kolejność pól użytych do zbudowania podpisu SHA-384. Upewnij się, że kwota jest w groszach/centach. |
| `err-session-exists` | Płatność z tym `sessionId` została już zarejestrowana. | Używaj unikalnego `sessionId` dla każdej nowej płatności. Nie powtarzaj identyfikatora. |
| `err-amount-mismatch` | Kwota wysłana do weryfikacji różni się od kwoty, z jaką zarejestrowano sesję. | Wyślij tę samą kwotę, którą zarejestrowałeś, w najmniejszej jednostce waluty. |
| `err-session-expired` | Minęła 60-minutowa sesja płatności. | Zarejestruj nową sesję i rozpocznij płatność ponownie. |
| `err-unauthorized` | api_key jest błędny lub należy do innego środowiska. | Sprawdź api_key i upewnij się, że używasz klucza dla właściwego środowiska (sandbox lub produkcja). |

## Jak czytać te błędy

- **Błędy podpisu i kwoty** niemal zawsze wynikają z niezgodności między tym, co wysyłasz, a tym, co wylicza kremzaPay. Sprawdź kolejność pól oraz to, że kwoty są w najmniejszej jednostce.
- **Błędy sesji** dotyczą cyklu życia płatności: `sessionId` musi być unikalny, a sesja jest ważna przez 60 minut, zanim wygaśnie.
- **Błędy autoryzacji** zwykle oznaczają, że klucz z sandboxa trafił na produkcję lub odwrotnie.

Jeśli błąd utrzymuje się po tych sprawdzeniach, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET), podając sessionId i kod błędu.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
