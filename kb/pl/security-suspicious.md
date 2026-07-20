---
id: KB-092
category: security
lang: pl
title: Podejrzana transakcja — co robić
---

# Podejrzana transakcja — co robić

Nawet gdy płatność osiągnie status `completed`, zamówienie wciąż może wyglądać podejrzanie. Antyfraud kremzaPay działa po stronie płatności, ale to Ty znasz swoje produkty, marże i typowych kupujących lepiej niż jakikolwiek system. Zaufaj temu wyczuciu.

Zwróć uwagę na te sygnały ostrzegawcze:

1. Niespójne dane kupującego — imię, e-mail, dane do rozliczeń i adres dostawy do siebie nie pasują albo adres wydaje się niezwiązany z kupującym.
2. Nietypowa seria kwot — kilka zamówień o tej samej wysokiej wartości w krótkim czasie lub kwoty odbiegające od normalnych zakupów.
3. Kilka kart na jeden adres dostawy — różne karty lub różni kupujący wielokrotnie wysyłający na ten sam adres.

Jeśli coś budzi Twoje wątpliwości, nie wysyłaj przesyłki. Odzyskanie towaru po nadaniu jest znacznie trudniejsze niż wstrzymanie zamówienia.

Wykonaj następujące kroki:

1. Wstrzymaj wysyłkę. Nie przekazuj jeszcze paczki kurierowi.
2. Zweryfikuj zamówienie z kupującym. Skontaktuj się przez dane, którym ufasz, i potwierdź, że to on je złożył. Prawdziwy klient zwykle odpowie; oszukańcze zamówienie często milczy.
3. Otwórz zgłoszenie w Panelu i podaj `sessionId` płatności, abyśmy mogli sprawdzić ją po naszej stronie.

Utrzymuj zamówienie jako wstrzymane do czasu uzyskania jednoznacznej odpowiedzi. Jeśli nie możesz potwierdzić kupującego, potraktuj zamówienie jako wysokiego ryzyka.

Płatność i jej `sessionId` znajdziesz w sekcji Payments w Panelu. Po pomoc otwórz zgłoszenie lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET). Zawsze podawaj `sessionId` — pozwala nam szybko odnaleźć konkretną transakcję.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
