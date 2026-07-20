---
id: KB-084
category: payouts
lang: pl
title: Eksport raportów (CSV)
---

# Eksport raportów (CSV)

kremzaPay umożliwia eksport danych o transakcjach i rozliczeniach do pliku CSV, gotowego do księgowości lub uzgadniania.

Aby wyeksportować raport:

1. Otwórz **Reports** w panelu.
2. Kliknij **Export**.
3. Wybierz **zakres dat** dla potrzebnych danych.
4. Opcjonalnie zastosuj **filtr per sklep**, aby ograniczyć eksport do jednego sklepu.
5. Potwierdź, aby pobrać plik.

Wyeksportowany plik CSV zawiera następujące kolumny:

- **sessionId** — unikalny identyfikator służący do dopasowania każdej płatności do Twojego zamówienia.
- **amount** — wartość transakcji.
- **currency** — jedna z walut: PLN, EUR, USD, GBP lub CZK.
- **status** — status płatności (na przykład `completed`, `pending`, `failed`).
- **payout id** — wypłata, w której dany wiersz został rozliczony.

Szczegóły formatu pliku:

- Kodowanie to **UTF-8**, dzięki czemu polskie znaki i inne znaki diakrytyczne wyświetlają się poprawnie.
- Wartości są **rozdzielane średnikiem** (`;`), co odpowiada konwencji regionalnej i pozwala na bezproblemowy import do większości arkuszy kalkulacyjnych.

Jeśli eksportujesz dane regularnie, możesz zautomatyzować pobieranie zamiast robić to ręcznie. **Endpoint raportowy API** zwraca te same dane programowo, więc możesz pobierać raporty według harmonogramu i przekazywać je bezpośrednio do procesu księgowego lub uzgodnieniowego.

Otwierając plik w arkuszu kalkulacyjnym, upewnij się, że jest on wczytywany jako UTF-8 z separatorem w postaci średnika, aby kolumny ułożyły się prawidłowo.

Jeśli któraś kolumna wygląda na pustą lub przesuniętą, albo w eksporcie brakuje oczekiwanego wiersza, załóż zgłoszenie w panelu lub napisz na pomoc@kremzapay.demo (pon.–pt., 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
