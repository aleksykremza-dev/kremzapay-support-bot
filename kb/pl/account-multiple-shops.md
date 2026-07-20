---
id: KB-050
category: account
lang: pl
title: Kilka sklepów na jednym koncie
---

# Kilka sklepów na jednym koncie

Jeśli prowadzisz więcej niż jeden sklep, nie potrzebujesz osobnego konta kremzaPay dla każdego z nich. Jedno konto może obejmować kilka sklepów, z których każdy jest wyraźnie oddzielony.

## Jak działa wiele sklepów

Każdy dodany sklep otrzymuje własny **merchant_id** oraz własny zestaw kluczy. Dzięki temu integracja każdego sklepu jest niezależna, więc zmiana w jednym sklepie nie wpływa na pozostałe. Oznacza to również:

- **Osobne raporty** — każdy sklep ma własną historię transakcji w sekcji Raporty, więc widzisz, jak radzi sobie z osobna.
- **Osobne wypłaty** — środki są rozliczane per sklep, więc pieniądze z każdego sklepu są wypłacane i uzgadniane niezależnie.

Taki podział ułatwia prowadzenie odrębnych marek, sklepów lub linii biznesowych na jednym loginie.

## Dodawanie sklepu

1. Zaloguj się do Panelu.
2. Otwórz **Ustawienia → Sklepy**.
3. Dodaj nowy sklep i potwierdź jego dane.
4. Zapisz nowy **merchant_id** i wygeneruj klucze dla tego sklepu.

W integracji danego sklepu używaj jego własnego merchant_id i kluczy. Pamiętaj, że klucze sandbox i produkcyjne są osobne, więc skonfiguruj każde środowisko właściwymi kluczami dla odpowiedniego sklepu.

## Utrzymanie porządku między sklepami

Nadaj każdemu sklepowi czytelną nazwę, aby jego raporty i wypłaty łatwo było odróżnić. Jeśli potrzebujesz pomocy przy konfiguracji dodatkowego sklepu, skontaktuj się z nami przez zgłoszenie w Panelu lub pod adresem pomoc@kremzapay.demo, od poniedziałku do piątku, 8:00–18:00 CET.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
