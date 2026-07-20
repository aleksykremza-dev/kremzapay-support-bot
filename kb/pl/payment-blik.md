---
id: KB-007
category: payments
lang: pl
title: Płatności BLIK
---

# Płatności BLIK

BLIK to popularna w Polsce metoda płatności, która pozwala klientom płacić bezpośrednio z aplikacji bankowej za pomocą krótkiego, jednorazowego kodu. To jedna z metod dostępnych w kremzaPay, obok kart z 3D Secure 2, szybkich przelewów, Google Pay i Apple Pay.

## Jak przebiega płatność BLIK

1. Podczas płatności klient wybiera BLIK jako metodę.
2. Klient otwiera aplikację bankową i generuje **6-cyfrowy kod BLIK**.
3. Klient wpisuje kod na stronie płatności.
4. Bank wysyła prośbę o potwierdzenie do aplikacji. Klient zatwierdza tam płatność.
5. Po potwierdzeniu płatność przechodzi w status completed i pojawia się w sekcji **Payments**.

## Ważny czas

Kod BLIK jest ważny przez **2 minuty** od momentu wygenerowania. Jeśli klient zbyt długo zwleka z wpisaniem kodu albo nie zdąży potwierdzić operacji w aplikacji bankowej, kod przestaje działać.

## Typowy błąd: wygasły kod

Najczęstszą przyczyną nieudanej płatności BLIK jest **wygasły kod**. Jeśli tak się stanie:

- Klient nie został obciążony.
- Poproś klienta o wygenerowanie nowego 6-cyfrowego kodu i ponowną próbę.
- Jeśli wygasła sama sesja płatności, klient musi rozpocząć nową płatność.

## Potrzebujesz pomocy

Jeśli płatności BLIK Twoich klientów regularnie kończą się niepowodzeniem, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
