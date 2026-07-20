---
id: KB-090
category: security
lang: pl
title: PCI DSS a Twój sklep
---

# PCI DSS a Twój sklep

PCI DSS to standard bezpieczeństwa, który obowiązuje każdą firmę przechowującą, przetwarzającą lub przesyłającą dane kart płatniczych. Wielu sprzedawców zakłada, że oznacza to kosztowne audyty i skomplikowaną infrastrukturę. W większości przypadków tak nie jest — bo przy kremzaPay Twój sklep w ogóle nie dotyka numerów kart.

Gdy kupujący płaci kartą, dane karty wpisuje na stronie płatności lub w widżecie kremzaPay. Trafiają one bezpośrednio do kremzaPay i są przetwarzane po naszej stronie. Twój sklep otrzymuje wyłącznie identyfikator płatności i jej status (pending, authorized, completed, failed lub expired). Numery kart, daty ważności i kody bezpieczeństwa nigdy nie docierają na Twoje serwery.

Dzięki temu typowy sklep pozostaje poza najbardziej wymagającą częścią zakresu PCI. Nie przechowujesz wrażliwych danych kart, więc nie odpowiadasz za ich ochronę we własnych systemach.

Aby tak zostało, przestrzegaj kilku prostych zasad:

1. Nigdy nie buduj własnego formularza karty. Zawsze kieruj kupujących na stronę płatności kremzaPay lub osadzaj oficjalny widżet.
2. Nigdy nie proś klientów o przesyłanie numerów kart e-mailem, na czacie ani telefonicznie i nie zapisuj ich w bazie, logach czy arkuszach.
3. Ogranicz integrację do identyfikatorów i statusów zwracanych przez kremzaPay.

Jeśli wtyczka, szablon lub zewnętrzne narzędzie próbuje zbierać surowe dane kart w Twoim checkoucie, potraktuj to jako sygnał ostrzegawczy i przestań go używać.

Jeśli nie masz pewności, czy jakaś część Twojej konfiguracji pobiera dane kart do Twoich systemów, otwórz zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET), a pomożemy to sprawdzić.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
