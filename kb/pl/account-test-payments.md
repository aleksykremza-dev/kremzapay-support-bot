---
id: KB-048
category: account
lang: pl
title: Płatności testowe
---

# Płatności testowe

Płatności testowe pozwalają sprawdzić integrację od początku do końca bez przepływu prawdziwych pieniędzy. Działają wyłącznie w środowisku sandbox, które jest całkowicie odrębne — ma własny Panel i własne klucze.

## Zanim zaczniesz

Upewnij się, że pracujesz w sandboxie, a nie na produkcji. Oba środowiska nie współdzielą kluczy ani danych, więc żądanie podpisane kluczami produkcyjnymi nigdy nie trafi do sandboxa i odwrotnie. Płatności testowe nigdy nie obciążają karty ani nie przenoszą środków.

## Karty testowe i BLIK

Do testów nie potrzebujesz danych własnej karty. Panel sandbox udostępnia wszystko, czego potrzebujesz:

1. Zaloguj się do Panelu sandbox.
2. Otwórz sekcję z danymi testowymi.
3. Użyj podanych tam **numerów kart testowych**, aby zasymulować różne scenariusze, na przykład płatność zakończoną sukcesem lub odrzuconą.
4. Skorzystaj z wbudowanego **symulatora BLIK**, aby przeprowadzić płatności BLIK bez prawdziwej aplikacji bankowej.

Ponieważ są to instrumenty symulowane, w przepływie zachowują się jak prawdziwe — przechodzą przez statusy takie jak pending, authorized i completed — ale nigdy nie następuje żadne obciążenie.

## Ważne zasady

- **Nigdy nie testuj prawdziwą kartą na produkcji.** Produkcja służy do rzeczywistych płatności klientów; prawdziwa karta oznacza tam realne obciążenie.
- Trzymaj klucze sandbox i produkcyjne osobno w kodzie i konfiguracji, aby przypadkiem nie pomylić środowisk.

Gdy testy w sandboxie przejdą pomyślnie, przełącz integrację na klucze produkcyjne, aby ją uruchomić. W razie potrzeby skontaktuj się z nami przez zgłoszenie w Panelu lub pod adresem pomoc@kremzapay.demo, od poniedziałku do piątku, 8:00–18:00 CET.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
