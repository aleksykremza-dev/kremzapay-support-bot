---
id: KB-009
category: payments
lang: pl
title: Płatność zakończona, a sklep pokazuje pending
---

# Płatność zakończona, a sklep pokazuje pending

Czasem płatność ma status **completed** w Panelu kremzaPay, ale Twój sklep nadal pokazuje ją jako pending lub nieopłaconą. Prawie zawsze oznacza to, że sklep nie odebrał lub nie potwierdził powiadomienia (webhooka), które wysłał kremzaPay.

## Jak działają powiadomienia

Gdy płatność zmienia status, kremzaPay wysyła żądanie **POST** na adres powiadomień (notification URL) Twojego sklepu. Sklep musi odpowiedzieć kodem **HTTP 200** i treścią **OK**. Jeśli nie otrzymamy takiego potwierdzenia, ponawiamy próbę do **8 razy w ciągu 24 godzin** w rosnących odstępach.

Jeśli sklep nigdy nie potwierdzi, nie zaktualizuje zamówienia — mimo że płatność po naszej stronie zakończyła się powodzeniem.

## Jak to naprawić

1. Otwórz sekcję **Payments** w Panelu i znajdź transakcję.
2. Sprawdź, czy po naszej stronie status to completed.
3. Przejdź do **Settings** i zweryfikuj adres powiadomień. Upewnij się, że jest poprawny, dostępny i zwraca HTTP 200 z treścią OK.
4. Otwórz płatność i użyj przycisku **Resend notification**, aby ponownie wysłać webhooka.
5. Sprawdź, czy zamówienie w sklepie już się zaktualizowało.

## Częste przyczyny

- Adres powiadomień jest błędny, niedostępny lub blokowany przez firewall.
- Twój endpoint zwrócił błąd zamiast HTTP 200 / OK.
- Twój endpoint odpowiadał zbyt długo.

## Potrzebujesz pomocy

Jeśli po sprawdzeniu ustawień powiadomienia nadal nie docierają, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
