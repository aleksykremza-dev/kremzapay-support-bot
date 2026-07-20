---
id: KB-094
category: security
lang: pl
title: Dwuskładnikowe logowanie do Panelu
---

# Dwuskładnikowe logowanie do Panelu

Uwierzytelnianie dwuskładnikowe (2FA) dodaje drugi krok do logowania w Panelu. Obok hasła wpisujesz tymczasowy kod z aplikacji authenticator, więc samo skradzione hasło nie wystarczy, aby uzyskać dostęp do konta.

kremzaPay używa kodów TOTP generowanych przez standardową aplikację authenticator na Twoim telefonie. 2FA jest wymagane dla każdego z rolą Admin i zalecane dla wszystkich członków zespołu, niezależnie od roli.

Aby je włączyć:

1. Otwórz w Panelu Settings → Security.
2. Wybierz konfigurację uwierzytelniania dwuskładnikowego.
3. Zeskanuj wyświetlony kod QR aplikacją authenticator.
4. Wpisz aktualny kod z aplikacji, aby potwierdzić.

Po włączeniu przy każdym logowaniu poprosimy Cię o kod z aplikacji.

Podczas konfiguracji 2FA Panel jednorazowo pokazuje zestaw kodów zapasowych. Pozwalają one zalogować się, gdy telefon jest niedostępny. Zapisz je offline — na przykład wydrukowane lub w menedżerze haseł — ponieważ są pokazywane tylko ten jeden raz i nie da się ich wyświetlić ponownie. Każdy kod zapasowy działa jednokrotnie.

Jeśli stracisz urządzenie oraz kody zapasowe, wciąż możesz odzyskać dostęp. Skontaktuj się ze wsparciem, aby rozpocząć odzyskiwanie konta; przed zresetowaniem 2FA konieczne będzie potwierdzenie tożsamości. Otwórz zgłoszenie w Panelu z konta innego zalogowanego członka zespołu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET). Nie ma wsparcia telefonicznego, więc trzymaj kody zapasowe w bezpiecznym miejscu, aby uniknąć opóźnień.

Dostępem zespołu zarządzasz w Settings → Team — zadbaj, aby każdy Admin miał włączone 2FA.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
