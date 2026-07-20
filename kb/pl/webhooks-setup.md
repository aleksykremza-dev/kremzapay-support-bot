---
id: KB-013
category: integration
lang: pl
title: Konfiguracja webhooków
---

# Konfiguracja webhooków

Webhooki pozwalają kremzaPay powiadamiać Twój serwer za każdym razem, gdy płatność zmienia status, dzięki czemu nie musisz odpytywać API.

## Ustaw adres URL powiadomień

1. Zaloguj się do Panelu kremzaPay.
2. Otwórz sekcję **Ustawienia**.
3. Przejdź do zakładki **Powiadomienia**.
4. Wpisz adres URL powiadomień i zapisz.

Wymagania dla adresu URL:

- Musi być **publiczny** — dostępny z internetu, a nie adres localhost ani prywatny.
- Musi używać **HTTPS**.

## Co wysyła kremzaPay

Przy każdej zmianie statusu (na przykład pending → authorized → completed lub przejście do failed czy expired) kremzaPay wysyła żądanie HTTP **POST** na Twój adres powiadomień. Treść żądania zawiera dane płatności dla danego zdarzenia.

## Jak potwierdzić odbiór

Twój punkt końcowy musi odpowiedzieć statusem HTTP **200** i treścią **`OK`**. To informuje kremzaPay, że powiadomienie zostało odebrane.

Jeśli odpowiesz czymkolwiek innym — innym kodem statusu, inną treścią lub niczym — kremzaPay uzna powiadomienie za niedostarczone i ponowi próbę.

## Szybka lista kontrolna

- Adres URL jest publiczny i serwowany przez HTTPS.
- Punkt końcowy przyjmuje żądania POST.
- Punkt końcowy odczytuje dane płatności z treści żądania.
- Punkt końcowy zwraca `200` z treścią `OK`.

Zachowanie przy ponowieniach i ręczne wysyłanie opisano w artykule o potwierdzeniach i ponowieniach webhooków. Jeśli powiadomienia nie docierają, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
