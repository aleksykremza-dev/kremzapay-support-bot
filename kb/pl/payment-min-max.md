---
id: KB-057
category: payments
lang: pl
title: Minimalna i maksymalna kwota płatności
---

# Minimalna i maksymalna kwota płatności

Każda transakcja w kremzaPay musi mieścić się w dozwolonym zakresie kwot. Zakres ten chroni zarówno Ciebie, jak i kupujących przed przypadkowymi płatnościami o zerowej lub zbyt dużej wartości.

## Domyślny zakres

Domyślnie pojedyncza transakcja może wynosić od **1 PLN do 50 000 PLN**. Płatność poniżej minimum lub powyżej maksimum jest odrzucana, zanim się rozpocznie, a kupujący zostaje poproszony o podanie prawidłowej kwoty.

Dla sklepów w innej walucie obowiązuje odpowiedni zakres na podstawie waluty sklepu skonfigurowanej dla płatności.

## Podwyższanie limitów

Jeśli Twoja firma regularnie potrzebuje większych transakcji, wyższe limity są dostępne **na podstawie indywidualnej umowy**. Aby poprosić o podwyższenie, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo, od poniedziałku do piątku, 8:00–18:00 CET. Opisz typową wielkość swoich transakcji, aby limit został ustawiony odpowiednio.

## Kwoty w API

Gdy wysyłasz kwotę przez API, jest ona wyrażona w **najmniejszej jednostce waluty**, a nie w jednostkach całkowitych. Na przykład:

- 1 PLN wysyłasz jako **100** (grosze).
- 25,50 EUR wysyłasz jako **2550** (centy).

Zawsze mnóż kwotę w pełnej walucie przez 100 przed wysłaniem i dziel wartości otrzymane z API przez 100 przy ich wyświetlaniu. Użycie przez pomyłkę jednostek całkowitych to częsta przyczyna płatności 100 razy za dużych lub za małych.

Jeśli płatność zostanie odrzucona jako wykraczająca poza zakres, sprawdź zarówno kwotę, jak i jednostkę waluty przed ponowną próbą.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
