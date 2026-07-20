---
id: KB-076
category: integration
lang: pl
title: Widżet płatności
---

# Widżet płatności

Widżet płatności kremzaPay to komponent JavaScript, który osadza wybór metody płatności bezpośrednio na Twojej stronie zamówienia. Kupujący wybiera metodę płatności bez opuszczania Twojej witryny, dzięki czemu proces zakupu pozostaje spójny z Twoim projektem.

## Jak to działa

1. Twój backend tworzy transakcję przez API kremzaPay i odbiera dane potrzebne do zainicjowania widżetu.
2. Strona zamówienia ładuje skrypt widżetu i renderuje wybór metody w kontenerze umieszczonym na stronie.
3. Kupujący wybiera metodę i potwierdza płatność. Dla większości metod płatność zostaje zrealizowana bezpośrednio na Twojej stronie.

Widżet odpowiada za prezentację i komunikację z kremzaPay. Twój backend nadal rejestruje transakcję po stronie serwera i opiera się na powiadomieniu webhook przy potwierdzaniu ostatecznego statusu.

## Przekierowanie awaryjne

Niektórych metod płatności nie da się zrealizować bezpośrednio na stronie, ponieważ wymagają uwierzytelnienia kupującego na zewnętrznej stronie — na przykład logowania do banku lub przejścia 3D Secure. Dla takich metod widżet wykonuje przekierowanie awaryjne: kupujący trafia na wymaganą stronę, a następnie wraca do Twojego zamówienia. Zaprojektuj stronę powrotu tak, aby po powrocie kupującego mogła wyświetlić czytelny wynik, i zawsze potwierdzaj rezultat na podstawie powiadomienia webhook, a nie samego przekierowania.

## Środowiska

Na czas integracji użyj środowiska sandbox (`api.sandbox.kremzapay.demo`), a następnie przełącz na produkcję (`api.kremzapay.demo`). Każde środowisko ma własne klucze.

Przetestuj zarówno proces bezpośredni, jak i przekierowanie awaryjne, przed uruchomieniem produkcyjnym. W razie potrzeby załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
