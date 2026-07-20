---
id: KB-080
category: integration
lang: pl
title: Migracja między wersjami API
---

# Migracja między wersjami API

kremzaPay wersjonuje swoje API, dzięki czemu możemy dodawać funkcje i poprawiać działanie bez psucia istniejących integracji. Aktualna wersja to v2. Wersja v1 jest wycofywana i przestanie być obsługiwana.

## Zasady wycofywania

Gdy wersja zostaje przeznaczona do usunięcia, data jej wycofania jest ogłaszana z co najmniej 6-miesięcznym wyprzedzeniem. Otrzymujesz powiadomienie na dwa sposoby: e-mailem na zarejestrowany adres kontaktowy oraz przez baner wyświetlany w Panelu. Daje Ci to przewidywalny czas na dokończenie migracji, zanim v1 przestanie działać.

## Planowanie migracji

1. Sprawdź, której wersji obecnie używa Twoja integracja.
2. Przejrzyj, co zmieniło się między wersjami. Pełna lista zmian jest publikowana w Panel → Raporty → Dziennik zmian API. Zapoznaj się z nią, aby zobaczyć, które endpointy, pola i zachowania różnią się w v2.
3. Zaktualizuj integrację do endpointów v2 i dostosuj obsługę żądań lub odpowiedzi, które uległy zmianie.

## Testowanie w okresie przejściowym

Środowisko sandbox (`api.sandbox.kremzapay.demo`) obsługuje obie wersje w okresie przejściowym, więc możesz przetestować integrację v2 bez zakłócania produkcyjnego ruchu v1. Wykonaj pełny zestaw testowych płatności, zwrotów i powiadomień webhook na v2 w sandbox przed przełączeniem produkcji.

Gdy nabierzesz pewności, przenieś ruch produkcyjny (`api.kremzapay.demo`) na v2. Śledź baner w Panelu i powiadomienia e-mail, aby dokończyć przełączenie przed datą wycofania v1.

Jeśli cokolwiek w dzienniku zmian jest niejasne lub krok migracji się nie powiedzie, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
