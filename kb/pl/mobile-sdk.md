---
id: KB-075
category: integration
lang: pl
title: SDK mobilne (iOS i Android)
---

# SDK mobilne (iOS i Android)

SDK mobilne kremzaPay pozwalają przyjmować płatności wewnątrz natywnych aplikacji iOS i Android. SDK wyświetla natywny arkusz płatności, dzięki czemu kupujący pozostają w Twojej aplikacji zamiast być przekierowywani do zewnętrznej przeglądarki.

## Co obsługuje SDK

- Wyświetlanie arkusza płatności i hostowanej strony płatności wewnątrz aplikacji.
- Uruchamianie uwierzytelnienia 3D Secure (3DS), gdy wymaga tego wydawca karty.
- Zwracanie wyniku płatności do aplikacji, abyś mógł zaktualizować interfejs.

SDK obsługuje część procesu widoczną dla klienta. Nie zastępuje jednak Twojego backendu.

## Co nadal robi backend

Transakcja musi być zawsze rejestrowana po stronie serwera. Twój backend wywołuje API kremzaPay, aby utworzyć transakcję, odbiera identyfikator płatności i przekazuje aplikacji tylko dane potrzebne do otwarcia arkusza płatności. Serwer odbiera też powiadomienie webhook potwierdzające ostateczny status płatności — i to powiadomienie pozostaje źródłem prawdy przy aktualizacji zamówienia.

## Bezpieczeństwo

Nigdy nie umieszczaj klucza `crc_key` w aplikacji mobilnej. Wszystko, co znajduje się w aplikacji, można wydobyć, a `crc_key` służy do podpisywania żądań algorytmem SHA-384. Przechowuj go wyłącznie na serwerze i tam wykonuj wszystkie podpisy. Aplikacja powinna korzystać z krótkotrwałych danych zwracanych przez backend, a nie z Twoich kluczy tajnych.

## Środowiska

Na czas rozwoju i testów użyj środowiska sandbox (`api.sandbox.kremzapay.demo`), a przy publikacji przełącz na produkcję (`api.kremzapay.demo`). Każde środowisko ma własne klucze.

Przetestuj cały proces, w tym 3DS oraz anulowane płatności, przed opublikowaniem aplikacji. W razie potrzeby załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
