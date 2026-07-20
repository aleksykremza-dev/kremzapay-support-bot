---
id: KB-091
category: security
lang: pl
title: Jak działa antyfraud kremzaPay
---

# Jak działa antyfraud kremzaPay

Każda płatność realizowana przez kremzaPay przechodzi automatyczną ocenę ryzyka, zanim będzie mogła się zakończyć. Cel jest prosty: zatrzymać transakcje oszukańcze, a jednocześnie pozwolić prawdziwym kupującym płacić bez zbędnych przeszkód.

Silnik oceny analizuje w czasie rzeczywistym szeroki zestaw sygnałów. Należą do nich:

1. Kontrola velocity — ile prób pochodzi z tej samej karty, od tego samego kupującego lub z tego samego urządzenia w krótkim czasie.
2. Sygnały geograficzne i dotyczące urządzenia — lokalizacja, urządzenie i sieć stojące za płatnością oraz to, czy pasują do oczekiwanego wzorca.
3. Zachowanie karty — powtarzające się odrzucenia, nietypowe kwoty lub kombinacje, które często wskazują na testowanie lub skradzione karty.

W przypadku płatności kartą uznanych za ryzykowne kremzaPay wymusza uwierzytelnienie 3DS2. Kupujący potwierdza płatność w swoim banku, co przenosi odpowiedzialność i dodaje mocny krok weryfikacji. Płatności o niskim ryzyku mogą przejść bez tego dodatkowego kroku.

Gdy płatność uzyska zbyt wysoką ocenę ryzyka, nie kończy się powodzeniem. W Panelu zobaczysz ją ze statusem `failed`. Kupujący jest proszony o użycie innej metody lub kontakt z bankiem.

Ze względów bezpieczeństwa kremzaPay nie ujawnia, dlaczego dana płatność została oceniona jako ryzykowna ani które sygnały zadecydowały o wyniku. Ujawnienie tej logiki pomogłoby oszustom ją obchodzić. Dlatego sprzedawcy widzą wyłącznie status końcowy — `pending`, `authorized`, `completed`, `failed` lub `expired` — a nie wewnętrzne uzasadnienie.

Nie musisz nic konfigurować, aby antyfraud działał; jest zawsze aktywny. Jeśli uważasz, że prawidłowe płatności są blokowane nietypowo często, otwórz zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET), podając identyfikatory płatności, a przeanalizujemy wzorzec.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
