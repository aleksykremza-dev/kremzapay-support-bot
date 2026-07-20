---
id: KB-058
category: payments
lang: pl
title: Płatności cykliczne i tokeny kart
---

# Płatności cykliczne i tokeny kart

Płatności cykliczne pozwalają obciążać zapisaną kartę bez konieczności przechodzenia przez pełny proces płatności za każdym razem. Sprawdza się to przy subskrypcjach, członkostwach i każdym regularnym rozliczaniu.

## Jak powstaje token karty

Pierwsza płatność zawsze przebiega jako zwykła transakcja z uwierzytelnieniem 3D Secure. Gdy osiągnie status **completed**, kremzaPay zapisuje token karty powiązany z tą kartą. Token jest odwołaniem — nie ujawnia pełnego numeru karty.

## Obciążanie tokenem w przyszłości

Kolejne obciążenia są inicjowane przez sprzedawcę i realizowane przez API z użyciem tokenu. Nie wymagają żadnej akcji kupującego ani sesji płatności.

1. Wyślij żądanie obciążenia z tokenem karty.
2. Podaj kwotę w najmniejszej jednostce (grosze).
3. kremzaPay realizuje obciążenie na zapisanej karcie.

Obciążenia inicjowane przez sprzedawcę nie otwierają 60-minutowej sesji płatności, ponieważ kupujący nie jest obecny.

## Informowanie kupującego

Przed zapisaniem tokenu musisz poinformować kupującego o harmonogramie rozliczeń: jak często i jaką kwotą będzie obciążany oraz jak zrezygnować. Jest to wymóg, a nie opcja.

## Usuwanie tokenu

Token można usunąć na dwa sposoby:

- Usuń go przez API, gdy kupujący rezygnuje lub harmonogram się kończy.
- Staje się nieaktywny automatycznie, gdy karta zostanie zablokowana lub wygaśnie.

Po usunięciu tokenu każda kolejna próba obciążenia zakończy się niepowodzeniem. Zakończone płatności i ich tokeny pozostają widoczne w sekcji **Payments**. Jeśli obciążenie się nie powiedzie, sprawdź status płatności i skontaktuj się z kupującym w sprawie aktualizacji karty.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
