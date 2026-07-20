---
id: KB-008
category: payments
lang: pl
title: Płatności kartą i 3D Secure
---

# Płatności kartą i 3D Secure

kremzaPay obsługuje płatności kartą z **3D Secure 2 (3DS2)** — dodatkowym krokiem uwierzytelnienia, który potwierdza, że kartą płaci jej właściciel. To zabezpieczenie ogranicza oszustwa i nieautoryzowane obciążenia.

## Jak działa 3D Secure 2

1. Klient podaje dane karty na stronie płatności.
2. Bank wydający kartę uruchamia krok weryfikacji 3DS2.
3. Klient potwierdza płatność, zwykle zatwierdzając ją w aplikacji bankowej lub wpisując kod przesłany przez bank.
4. Po pozytywnej weryfikacji płatność zostaje autoryzowana, a następnie zakończona (completed).

Większość weryfikacji trwa kilka sekund i wymaga jednego zatwierdzenia w aplikacji bankowej.

## Dlaczego jest wymagane

Zgodnie z przepisami obowiązującymi w EOG (silne uwierzytelnianie klienta) weryfikacja 3D Secure jest **wymagana** dla większości płatności kartą w Europejskim Obszarze Gospodarczym. To wymóg banku i regulacji, a nie opcjonalne ustawienie.

## Gdy 3D Secure się nie powiedzie

Jeśli klient nie ukończy lub nie przejdzie kroku 3DS2, płatność kończy się statusem **failed**:

- Status płatności to failed.
- Klient **nie** został obciążony.
- Klient może rozpocząć nową płatność i spróbować ponownie, mając pod ręką aplikację bankową do potwierdzenia.

## Potrzebujesz pomocy

Jeśli Twoi klienci zgłaszają powtarzające się problemy z 3D Secure, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
