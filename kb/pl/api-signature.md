---
id: KB-012
category: integration
lang: pl
title: Podpis żądania (SHA-384)
---

# Podpis żądania (SHA-384)

kremzaPay weryfikuje każde żądanie za pomocą podpisu. Podpis to skrót SHA-384 zbudowany z ustalonego zestawu pól, w ustalonej kolejności.

## Jak go zbudować

Połącz poniższe pola i policz z nich skrót SHA-384:

1. `sessionId`
2. `merchantId`
3. `amount`
4. `currency`
5. `crcKey`

Otrzymany skrót wyślij jako podpis żądania. `crcKey` wchodzi wyłącznie do danych skrótu — nigdy nie jest wysyłany jako osobne pole.

## Uwagi do pól

- **amount** podawany jest w najmniejszej jednostce waluty (grosze dla PLN, centy dla EUR/USD). Na przykład 49,90 PLN to `4990`.
- **currency** używa standardowego kodu: PLN, EUR, USD, GBP lub CZK.
- Powyższa kolejność pól jest wymagana. Jej zmiana daje inny skrót i żądanie zostaje odrzucone.

## Najczęstsze błędy

- **Zła kolejność pól** — pola trzeba połączyć dokładnie tak, jak podano wyżej.
- **Kwota w złotych zamiast w groszach** — wysłanie `49.90` zamiast `4990` daje podpis, który nie zgadza się z tym, co wylicza kremzaPay.
- **Klucz crc_key z sandboxa użyty na produkcji** — każde środowisko ma własny crc_key. Klucz z sandboxa nigdy nie zweryfikuje się na produkcji.

Jeśli podpis się nie zgadza, kremzaPay zwraca błąd nieprawidłowego podpisu. Sprawdź ponownie kolejność pól, jednostkę kwoty oraz środowisko crc_key. Po pomoc zgłoś się z Panelu lub napisz na pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
