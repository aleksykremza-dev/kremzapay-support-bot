---
id: KB-059
category: payments
lang: pl
title: Preautoryzacja i pobranie środków
---

# Preautoryzacja i pobranie środków

Preautoryzacja pozwala zablokować środki na karcie kupującego bez ich natychmiastowego pobrania. Pobierasz pieniądze później, gdy jesteś gotów zrealizować zamówienie. Stosuje się to przy rezerwacjach, wynajmie i zamówieniach, w których ostateczna kwota jest potwierdzana po zakończeniu płatności.

## Authorized oznacza zablokowane, a nie pobrane

Gdy płatność osiąga status **authorized**, środki są zarezerwowane na karcie, ale nie opuściły konta kupującego. Żadne pieniądze nie trafiają do Ciebie, dopóki ich nie pobierzesz.

## Pobranie w ciągu 7 dni

Autoryzowaną płatność musisz pobrać w ciągu 7 dni. Jeśli tego nie zrobisz, blokada zostaje automatycznie zwolniona, a środki wracają do kupującego. Później konieczne będzie utworzenie nowej płatności.

Aby pobrać środki:

1. Otwórz płatność w sekcji **Payments**.
2. Potwierdź pobranie lub wyślij żądanie pobrania przez API.
3. Po pobraniu płatność przechodzi w status **completed**.

## Pobranie częściowe

Możesz pobrać mniej niż kwota autoryzowana — na przykład gdy część zamówienia jest niedostępna. Pobranie częściowe jest dozwolone **jednokrotnie** dla danej płatności. Gdy pobierzesz część kwoty, pozostała reszta jest automatycznie zwalniana na rzecz kupującego; nie możesz jej pobrać później.

Jeśli kupujący ma zostać ponownie obciążony zwolnioną kwotą, utwórz nową płatność. Jeśli pobranie się nie powiedzie, sprawdź status płatności i okno 7 dni przed ponowną próbą, a w razie błędnego statusu skontaktuj się z pomocą przez system zgłoszeń w Panelu lub pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
