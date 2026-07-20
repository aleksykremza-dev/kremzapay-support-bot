---
id: KB-073
category: integration
lang: pl
title: Test połączenia
---

# Test połączenia

Zanim zarejestrujesz pierwszą transakcję, potwierdź, że Twoje dane uwierzytelniające i adres bazowy współpracują ze sobą. kremzaPay udostępnia lekki endpoint dokładnie do tej kontroli.

**Żądanie**

Wyślij żądanie `GET` na `/test-access` z Twoim `api_key`. W poprawnym środowisku, z prawidłowym kluczem, endpoint zwraca HTTP `200`. Każda inna odpowiedź oznacza, że żądanie nie dotarło do działającego, autoryzowanego połączenia.

**Użyj tego jako pierwszego kroku**

Wykonaj ten test przed napisaniem jakiejkolwiek logiki płatności. Jeśli `/test-access` nie zwraca 200, nie ma sensu próbować rejestracji transakcji, bo te same dane i adres zawiodą również tam. Potwierdzenie połączenia w pierwszej kolejności oddziela problemy z konfiguracją od błędów integracji.

**Co mówi odpowiedź inna niż 200**

- Sprawdź, czy adres bazowy i `api_key` należą do tego samego środowiska. Klucz produkcyjny na adresie sandbox (lub odwrotnie) to najczęstsza przyczyna.
- Sprawdź, czy `api_key` został skopiowany dokładnie, bez dodatkowych białych znaków.
- Sprawdź, czy wywołujesz właściwy adres: `api.sandbox.kremzapay.demo` dla sandboxa, `api.kremzapay.demo` dla produkcji.

**Użyj tego w monitoringu**

Poza początkową konfiguracją, wywołuj `/test-access` okresowo z systemu monitoringu, aby otrzymać alert, gdy połączenie lub dane uwierzytelniające przestaną działać na produkcji. Pamiętaj o limicie 100 żądań na minutę; żądania powyżej niego otrzymują HTTP 429, więc rozłóż kontrole monitoringu rozsądnie w czasie.

Jeśli test nadal zawodzi po tych krokach, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
