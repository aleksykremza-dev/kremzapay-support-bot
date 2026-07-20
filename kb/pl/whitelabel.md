---
id: KB-077
category: integration
lang: pl
title: Strona płatności white-label
---

# Strona płatności white-label

Strona płatności white-label pozwala udostępniać stronę płatności kremzaPay z Twojej własnej domeny, na przykład `pay.yourshop.example`, zamiast z adresu kremzaPay. Kupujący widzą Twoją domenę przez cały czas trwania płatności, co wzmacnia zaufanie i utrzymuje spójność procesu zakupu z Twoją marką. Opcja jest dostępna na podstawie umowy, więc należy ją uzgodnić z kremzaPay przed konfiguracją.

## Wymagania

- **Umowa** — domena white-label musi być włączona dla Twojego konta w ramach umowy o świadczenie usług.
- **Konfiguracja DNS** — tworzysz rekord DNS kierujący wybraną subdomenę (na przykład `pay.yourshop.example`) na cel wskazany przez kremzaPay.
- **Certyfikat** — ważny certyfikat TLS musi obejmować domenę, aby strona płatności była udostępniana przez HTTPS. W zależności od umowy certyfikat jest wystawiany dla Ciebie lub dostarczany przez Ciebie.

## Konfiguracja

1. Potwierdź, że opcja white-label jest aktywna dla Twojego konta.
2. Dodaj rekord DNS dla swojej subdomeny zgodnie z instrukcją.
3. Upewnij się, że certyfikat jest na miejscu, a domena działa przez HTTPS.
4. Sprawdź, czy strona płatności otwiera się poprawnie w Twojej domenie.

## Branding

Wszelki branding skonfigurowany w Ustawienia → Branding — na przykład logo i kolory — jest automatycznie stosowany na stronie white-label. Zaktualizuj te ustawienia najpierw, aby strona pasowała do Twojego sklepu, zanim skierujesz na nią prawdziwych klientów.

Wykonaj testową płatność w sandbox na własnej domenie przed uruchomieniem, aby potwierdzić, że certyfikat, przekierowanie i powiadomienia działają od początku do końca. W razie potrzeby załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
