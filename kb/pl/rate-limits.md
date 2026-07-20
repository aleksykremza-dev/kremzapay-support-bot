---
id: KB-078
category: integration
lang: pl
title: Limity zapytań API
---

# Limity zapytań API

Aby utrzymać stabilność platformy dla wszystkich, API kremzaPay stosuje limit 100 zapytań na minutę na sprzedawcę. Limit liczony jest w skali konta, więc obejmuje wszystkie zapytania wykonywane Twoimi kluczami, niezależnie od tego, który serwer je wysyła.

## Co się dzieje po przekroczeniu limitu

Gdy przekroczysz 100 zapytań w ciągu minuty, API odpowiada statusem HTTP `429 Too Many Requests`. Odpowiedź zawiera nagłówek `Retry-After`, który wskazuje, ile sekund należy odczekać przed wysłaniem kolejnych zapytań. Odczytaj ten nagłówek i wstrzymaj wywołania do zresetowania okna, zamiast ponawiać próby natychmiast.

## Co nie jest liczone

- **Punkty wsadowe (batch)** — zapytania do punktów wsadowych nie są wliczane do limitu na minutę, więc korzystaj z nich, gdy musisz przetworzyć wiele elementów naraz.
- **Webhooki** — powiadomienia, które kremzaPay wysyła na Twój serwer, nie są wliczane do limitu. Webhooki to zalecany sposób na poznanie zmian statusu, a poleganie na nich pozwala uniknąć wielokrotnego odpytywania API.

## Jak mieścić się w limicie

- Korzystaj z webhooków zamiast odpytywać o status płatności.
- Używaj punktów wsadowych do operacji masowych.
- Rozkładaj w czasie zapytania niepilne, zamiast wysyłać je w seriach.
- Obsługuj odpowiedzi `429` poprawnie, respektując `Retry-After` i stosując wycofanie.

## Potrzebujesz wyższego limitu

Jeśli Twój normalny ruch regularnie zbliża się do 100 zapytań na minutę, skontaktuj się z pomocą, aby poprosić o wyższy limit. Załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET) i opisz oczekiwany wolumen zapytań.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
