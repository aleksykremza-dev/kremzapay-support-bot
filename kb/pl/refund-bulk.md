---
id: KB-065
category: refunds
lang: pl
title: Zwroty masowe z pliku
---

# Zwroty masowe z pliku

Gdy musisz zwrócić wiele płatności naraz, możesz wgrać je w jednym pliku, zamiast przetwarzać każdą ręcznie.

Aby wykonać zwrot masowy:

1. Otwórz sekcję **Zwroty** w Panelu i wybierz **Import**.
2. Wgraj plik CSV z dwiema kolumnami: `sessionId` oraz `amount`.
3. Potwierdź import, aby dodać zwroty do kolejki.

`sessionId` to identyfikator pierwotnej płatności. `amount` podaje się w najmniejszej jednostce waluty — w groszach dla PLN, więc 25,00 PLN wpisujesz jako `2500`. Odpowiada to sposobowi obsługi kwot w API i pozwala uniknąć błędów zaokrągleń.

Każdy plik może zawierać do 500 wierszy. Jeśli masz więcej zwrotów do przetworzenia, podziel je na kilka plików i zaimportuj kolejno.

Po potwierdzeniu każdy wiersz jest przetwarzany oddzielnie i przechodzi przez zwykłe statusy: **utworzony**, **w trakcie**, a następnie **zakończony** lub **odrzucony**. Pojedynczy wiersz może się nie powieść — na przykład gdy `sessionId` jest nieznane albo kwota przekracza to, co pozostało do zwrotu w danej płatności — bez wpływu na pozostałe wiersze.

Po zakończeniu przetwarzania dostępny jest do pobrania raport wynikowy. Zawiera on każdy wiersz wraz z jego statusem, dzięki czemu widzisz dokładnie, które zwroty się powiodły, a które wymagają uwagi. Zwrócone kwoty są potrącane z Twojej najbliższej wypłaty.

Jeśli któryś wiersz zostanie odrzucony, a przyczyna jest niejasna, napisz zgłoszenie w Panelu lub na adres pomoc@kremzapay.demo (pon.–pt., 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
