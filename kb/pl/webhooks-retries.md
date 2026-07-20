---
id: KB-014
category: integration
lang: pl
title: Potwierdzenia i ponowienia webhooków
---

# Potwierdzenia i ponowienia webhooków

kremzaPay oczekuje, że Twój punkt końcowy potwierdzi każdy webhook. Gdy tego nie zrobi, powiadomienie jest ponawiane według harmonogramu.

## Co liczy się jako potwierdzenie

Webhook jest potwierdzony, gdy Twój punkt końcowy odpowie statusem HTTP **200** i treścią **`OK`**. Każda inna odpowiedź — inny kod statusu, inna treść, przekroczenie czasu lub brak odpowiedzi — jest traktowana jako brak potwierdzenia.

## Harmonogram ponowień

Jeśli powiadomienie nie zostanie potwierdzone, kremzaPay ponawia je:

- Maksymalnie **8 razy**.
- W oknie **24 godzin** od pierwszej próby.
- W **rosnących odstępach**, więc wczesne ponowienia są blisko siebie, a późniejsze bardziej rozłożone w czasie.

Po 8 niepotwierdzonych próbach w ciągu 24 godzin powiadomienie zostaje **porzucone** i nie ma dalszych prób automatycznych.

## Status płatności pozostaje prawidłowy

Porzucone powiadomienie nie zmienia samej płatności. Status płatności w Panelu (pending, authorized, completed, failed lub expired) zawsze odzwierciedla rzeczywisty wynik, nawet jeśli Twój serwer nigdy nie potwierdził webhooka. W razie wątpliwości traktuj Panel jako źródło prawdy.

## Ręczne ponowne wysłanie

Każda płatność ma przycisk **wyślij ponownie powiadomienie**. Otwórz płatność w Panelu i użyj go, aby ponownie wywołać webhook — przydatne po naprawie punktu końcowego, który był niedostępny lub zwracał błędną odpowiedź.

Jeśli ponowienia wciąż zawodzą, sprawdź, czy punkt końcowy szybko zwraca `200`/`OK` i jest dostępny przez publiczne HTTPS. Po pomoc zgłoś się z Panelu lub napisz na pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
