---
id: KB-020
category: payouts
lang: pl
title: Jak czytać raport wypłaty
---

# Jak czytać raport wypłaty

Każda wypłata ma raport rozliczeniowy, który pokazuje dokładnie, jak obliczono przekazaną kwotę. Raporty znajdziesz w Panelu kremzaPay w sekcji Raporty.

## Co zawiera raport

Każdy raport dotyczy pojedynczej wypłaty i zawiera:

- **Kwotę brutto** — sumę wszystkich płatności ujętych w wypłacie.
- **Prowizję** — opłatę pobraną zgodnie z Twoją umową.
- **Kwotę netto** — kwotę brutto pomniejszoną o prowizję i ewentualne zwroty. To właśnie ta wartość trafia na Twój rachunek bankowy.

Zależność jest prosta:

`Netto = Brutto − Prowizja − Zwroty`

## Wiersze płatności

Raport wymienia każdą płatność składającą się na wypłatę. Każdy wiersz płatności zawiera własny `sessionId`, który pozwala dopasować pozycję w raporcie do odpowiadającej jej transakcji w Twoich rejestrach. Użyj tego identyfikatora przy uzgadnianiu ksiąg lub wyjaśnianiu konkretnej płatności.

## Eksport

Każdy raport rozliczeniowy możesz wyeksportować do pliku CSV na potrzeby księgowości lub uzgodnień. Plik CSV zawiera te same wiersze i identyfikatory, które widać w Panelu, więc można go bezpośrednio zaimportować do narzędzi księgowych.

Jeśli któraś wartość w raporcie jest niejasna, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET), podając wypłatę i odpowiedni sessionId.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
