---
id: KB-117
category: service
lang: pl
title: Wiele płatności wisi w pending
---

# Wiele płatności wisi w pending

Jeśli duża liczba Twoich płatności nagle utknęła jednocześnie w statusie **pending**, jest to niemal zawsze incydent po stronie banku lub metody płatności — a nie problem z Twoją integracją. Gdy dotyczy to wielu sprzedawców naraz, przyczyna leży wyżej, po stronie banku lub konkretnej metody płatności, a z Twoim kodem czy konfiguracją wszystko jest w porządku.

**Co zrobić**

1. **Najpierw sprawdź stronę statusu.** Otwórz status.kremzapay.demo i spójrz na komponent Płatności. Podczas incydentu po stronie dostawcy pokaże on stan ograniczony lub niedostępny, często z adnotacją o dotkniętej metodzie.
2. **Nie wysyłaj płatności ponownie.** Tworzenie nowych transakcji dla tych samych zamówień niczego nie przyspieszy i może prowadzić do duplikatów.
3. **Nie anuluj ich.** Anulowanie zawieszonych płatności jest zbędne. Statusy aktualizują się automatycznie po rozwiązaniu incydentu — płatność w stanie pending sama przejdzie do completed lub failed.

**Dlaczego czekanie jest właściwym krokiem**

Podczas takich incydentów transakcja zwykle została już wysłana do banku, a opóźnione jest potwierdzenie zwrotne do kremzaPay. Gdy problem po stronie dostawcy zostanie usunięty, zakolejkowane potwierdzenia napłyną, a statusy Twoich płatności nadrobią zaległości bez żadnego działania z Twojej strony.

**Kiedy zgłosić ticket**

Zgłoś ticket tylko wtedy, gdy pojedyncze płatności pozostają w stanie pending długo po tym, jak incydent na stronie statusu został oznaczony jako rozwiązany. W takim przypadku zgłoś to z Panelu i podaj sessionId dotkniętych płatności oraz znaczniki czasu, abyśmy mogli je prześledzić.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
