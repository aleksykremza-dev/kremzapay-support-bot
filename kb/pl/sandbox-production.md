---
id: KB-016
category: account
lang: pl
title: Sandbox a produkcja
---

# Sandbox a produkcja

kremzaPay udostępnia dwa osobne środowiska: sandbox do testów i produkcję do rzeczywistych transakcji. Zrozumienie różnicy chroni Twoje konto produkcyjne przed ruchem testowym.

## Sandbox

Sandbox to środowisko testowe. Zachowuje się jak produkcja, ale nie przetwarza **żadnych prawdziwych pieniędzy**. Zamiast prawdziwych banków i BLIK-a korzysta z symulatorów testowych, więc możesz przeprowadzić płatność przez każdy status — pending, authorized, completed, failed i expired — bez przepływu środków.

Sandbox ma:

- Własny zestaw kluczy (merchant_id, api_key, crc_key).
- Własny panel, oddzielny od produkcji.

Ponieważ klucze i panele są rozdzielone, płatność utworzona w sandboxie nigdy nie pojawia się na produkcji i odwrotnie.

## Produkcja

Produkcja to środowisko na żywo. Żądania używają tu Twoich kluczy produkcyjnych i skutkują rzeczywistymi obciążeniami. Raporty, Płatności, Zwroty i Wypłaty w panelu produkcyjnym odzwierciedlają realną aktywność klientów.

## Lista kontrolna przed uruchomieniem

Zanim przełączysz ruch na produkcję, potwierdź:

1. **Klucze produkcyjne na miejscu** — Twój kod używa produkcyjnych merchant_id, api_key i crc_key, a nie zestawu sandbox.
2. **Podpis zweryfikowany** — podpis SHA-384 poprawnie waliduje się z Twoim produkcyjnym crc_key.
3. **Adres webhooka dostępny** — Twój publiczny adres powiadomień HTTPS odpowiada `200`/`OK` i jest ustawiony w panelu produkcyjnym.
4. **Jedna prawdziwa płatność o niskiej kwocie przetestowana** — wykonaj jedną małą rzeczywistą płatność od początku do końca i potwierdź, że osiąga status completed oraz że webhook się uruchamia.

Jeśli którykolwiek punkt listy zawiedzie, pozostań na sandboxie do czasu naprawy. Po pomoc zgłoś się z Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
