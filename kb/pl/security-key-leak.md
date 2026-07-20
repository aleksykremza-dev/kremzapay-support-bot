---
id: KB-096
category: security
lang: pl
title: Wyciek kluczy API — plan działania
---

# Wyciek kluczy API — plan działania

Jeśli klucz API został ujawniony — trafił do publicznego repozytorium, został wklejony na czacie lub wyciekł w inny sposób — zareaguj natychmiast. Wykradziony klucz może służyć do wywoływania API w Twoim imieniu, dopóki nie zostanie unieważniony.

## 1. Wygeneruj klucze ponownie

1. Otwórz **Ustawienia → Klucze API**.
2. Wybierz **Wygeneruj ponownie**.

Stary klucz przestaje działać natychmiast. Każde żądanie, które nadal go używa, od razu zaczyna zwracać błąd, co zatrzymuje atakującego, ale też wstrzymuje Twoją integrację do czasu wykonania kolejnego kroku.

## 2. Zaktualizuj nowy klucz w integracji

Skopiuj nowo wygenerowany klucz i zastąp starą wartość wszędzie tam, gdzie integracja ją przechowuje — w zmiennych środowiskowych, menedżerze sekretów lub konfiguracji. Wdróż zmianę, aby ruch produkcyjny korzystał z nowego klucza.

## 3. Sprawdź ostatnie transakcje

Otwórz **Płatności** i przejrzyj ostatnią aktywność pod kątem nieoczekiwanych zdarzeń: płatności, których nie rozpoznajesz, nietypowych kwot lub zwrotów, których nie zainicjowałeś. Zanotuj wszystko, co wygląda podejrzanie.

## 4. Zgłoś do wsparcia

Załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt., 8:00–18:00 CET). Podaj, kiedy klucz mógł wyciec, oraz wykryte nieprawidłowości, aby wsparcie pomogło Ci ocenić skutki.

## Jeśli wyciekł także crc_key

Klucz `crc_key` weryfikuje podpisy webhooków. Jeśli również został ujawniony, zrotuj go, aby przychodzące powiadomienia webhook były weryfikowane wobec nowego sekretu, a następnie zaktualizuj logikę weryfikacji webhooków tak, by używała zrotowanej wartości.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
