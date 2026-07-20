---
id: KB-011
category: integration
lang: pl
title: Gdzie znaleźć merchant_id, api_key i crc_key
---

# Gdzie znaleźć merchant_id, api_key i crc_key

Każda integracja z kremzaPay opiera się na trzech wartościach. Wszystkie znajdziesz w Panelu.

## Gdzie szukać

1. Zaloguj się do Panelu kremzaPay.
2. Otwórz sekcję **Ustawienia**.
3. Wybierz zakładkę **Klucze API**.

Strona pokazuje klucze dla środowiska, w którym aktualnie się znajdujesz. Klucze sandbox i produkcyjne są różne, więc upewnij się, że kopiujesz zestaw odpowiadający środowisku, na które kierujesz swój kod.

## Co oznacza każda wartość

- **merchant_id** — numeryczny identyfikator Twojego sklepu. Wskazuje kremzaPay, do którego konta należy żądanie.
- **api_key** — autoryzuje wywołania REST API. Wysyłaj go przy każdym żądaniu do API.
- **crc_key** — używany wyłącznie do budowania podpisu żądania. Nigdy nie jest wysyłany jako zwykłe pole w żądaniu — trafia do skrótu podpisu.

## Bezpieczeństwo kluczy

- Nigdy nie udostępniaj kluczy nikomu spoza swojego zespołu.
- Nigdy nie umieszczaj kluczy w repozytorium kodu, publicznym ani prywatnym. Przechowuj je w zmiennych środowiskowych lub menedżerze sekretów.
- Trzymaj klucze sandbox i produkcyjne osobno w konfiguracji, aby klucz testowy nigdy nie trafił na produkcję.

Jeśli klucz mógł zostać ujawniony, skontaktuj się z pomocą, aby go wymienić. Zgłoszenie założysz z Panelu lub mailowo na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
