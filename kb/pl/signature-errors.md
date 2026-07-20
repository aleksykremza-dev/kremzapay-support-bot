---
id: KB-071
category: integration
lang: pl
title: Naprawa błędów podpisu
---

# Naprawa błędów podpisu

Błąd podpisu oznacza, że przesłany podpis SHA-384 nie zgadza się z tym, który kremzaPay wylicza po swojej stronie. Podpis budowany jest z `{sessionId, merchantId, amount, currency, crcKey}`. Niemal każdy błąd wynika z drobnej różnicy w sposobie łączenia tych wartości. Przejdź przez poniższą listę kontrolną.

**1. Dokładna kolejność pól**

Połącz pola w dokładnie tej kolejności: `sessionId`, `merchantId`, `amount`, `currency`, `crcKey`. Inna kolejność daje inny skrót, nawet gdy wszystkie wartości są poprawne.

**2. Kwota w groszach, nie w złotych**

`amount` musi być najmniejszą jednostką waluty. Wyślij `4990` dla 49,90 PLN, a nie `49.90` ani `49,90`. Kropka lub przecinek dziesiętny w kwocie to częsta przyczyna błędów.

**3. crc_key właściwego środowiska**

Użyj `crc_key` należącego do środowiska, do którego się łączysz. crc_key sandboxa nigdy nie przejdzie walidacji na adresie produkcyjnym i odwrotnie.

**4. UTF-8 bez BOM**

Zakoduj ciąg jako UTF-8 bez znacznika kolejności bajtów (BOM). Wiodący BOM zmienia bajty poddawane haszowaniu i psuje podpis.

**5. Brak dodatkowych białych znaków**

Nie dodawaj spacji, tabulatorów, znaków nowej linii ani separatorów między polami. Łącz surowe wartości bezpośrednio i usuń końcowe białe znaki z każdej wartości.

**Jak debugować**

1. Wypisz dokładny połączony ciąg przed haszowaniem.
2. Potwierdź, że kolejność pól odpowiada powyższej liście.
3. Potwierdź, że kwota jest liczbą całkowitą w groszach.
4. Potwierdź, że crc_key pasuje do środowiska.
5. Przelicz ponownie skrót SHA-384 i porównaj.

Jeśli podpis nadal zawodzi po tych krokach, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
