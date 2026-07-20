---
id: KB-083
category: payouts
lang: pl
title: Uzgadnianie wypłat z zamówieniami
---

# Uzgadnianie wypłat z zamówieniami

Uzgadnianie polega na potwierdzeniu, że każda płatność w wypłacie kremzaPay odpowiada zamówieniu w Twoim własnym systemie. Kluczem do rzetelnego wykonania tego zadania jest **sessionId**.

Każdy wiersz płatności w raporcie rozliczeniowym zawiera unikalny **sessionId**. W momencie utworzenia płatności ten sam sessionId jest dostępny po Twojej stronie, dzięki czemu możesz przypisać każdą rozliczoną płatność do konkretnego zamówienia, którego dotyczy.

Zalecamy prostą, codzienną rutynę:

1. Otwórz **Reports** i wyeksportuj dane rozliczeniowe do pliku CSV dla danego dnia (lub wybranego zakresu).
2. Dla każdego wiersza pobierz **sessionId** i dopasuj go do identyfikatora zamówienia w Twoim systemie.
3. Potwierdź, że kwota i waluta zgadzają się z tym, czego oczekiwałeś dla danego zamówienia.
4. Odłóż wszystkie **niedopasowane wiersze** — płatności bez odpowiadającego zamówienia lub zamówienia bez pasującej płatności.
5. Przeanalizuj niedopasowane wiersze przed skontaktowaniem się z pomocą.

Większość niedopasowanych wierszy ma proste wyjaśnienie: zwrot naliczony w późniejszym dniu, płatność wciąż w statusie `pending` zamiast `completed`, albo zamówienie zapisane pod innym oznaczeniem. Samodzielne przejrzenie ich najpierw zwykle szybko wyjaśnia rozbieżność.

Wykonywanie tego codziennie utrzymuje niewielką liczbę pozycji i ułatwia wychwytywanie problemów, zamiast pozwalać, by różnice kumulowały się przez cały miesiąc.

Jeśli po sprawdzeniu sessionId i kwot dany wiersz nadal nie ma sensu, załóż zgłoszenie w panelu lub napisz na pomoc@kremzapay.demo (pon.–pt., 8:00–18:00 CET). Podaj sessionId oraz identyfikator wypłaty, abyśmy mogli go od razu prześledzić.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
