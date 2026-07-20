---
id: KB-097
category: security
lang: pl
title: Jak weryfikowani są płacący
---

# Jak weryfikowani są płacący

Każda płatność realizowana przez kremzaPay jest weryfikowana, zanim środki zostaną przesłane. Większość tej weryfikacji odbywa się po stronie banku kupującego, a kremzaPay dokłada własne kontrole na tej podstawie. Jako sprzedawca nigdy nie widzisz danych bankowych kupującego.

## Weryfikacja po stronie banku

Sposób potwierdzenia zależy od tego, jak kupujący zdecyduje się zapłacić:

- **BLIK** — kupujący potwierdza płatność w aplikacji bankowej, zwykle kodem i zatwierdzeniem w aplikacji.
- **Karty** — płatności kartą przechodzą uwierzytelnianie 3DS2, więc kupujący potwierdza je w swoim banku metodą, której bank wymaga.
- **Szybkie przelewy** — kupujący loguje się do własnego banku, aby bezpośrednio autoryzować przelew.

W każdym przypadku kupujący uwierzytelnia się w swoim banku, a nie u Ciebie. Hasła, numery kart i kody jednorazowe pozostają między kupującym a jego bankiem.

## Ocena ryzyka na tej podstawie

Gdy bank potwierdzi płacącego, kremzaPay stosuje własną ocenę ryzyka. Ta warstwa analizuje sygnały związane z transakcją, aby pomóc wychwycić działania oszukańcze lub nietypowe, które przechodzą uwierzytelnianie bankowe, a mimo to wyglądają podejrzanie. Działa dyskretnie w tle i nie wymaga od Ciebie żadnych działań.

## Co sprzedawca widzi, a czego nie

Otrzymujesz informacje potrzebne do realizacji zamówienia i rozliczenia płatności. Nie otrzymujesz danych bankowych kupującego, pełnych numerów kart ani kodów uwierzytelniających. Dzięki temu wrażliwe dane kupującego pozostają poza Twoimi systemami, a Ty i tak masz to, czego potrzebujesz do prowadzenia działalności.

Jeśli wynik płatności wygląda błędnie, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
