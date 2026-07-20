---
id: KB-093
category: security
lang: pl
title: Bezpieczne przechowywanie kluczy API
---

# Bezpieczne przechowywanie kluczy API

Twoje klucze API kremzaPay autoryzują dostęp do konta. Każdy, kto zdobędzie klucz produkcyjny, może działać w Twoim imieniu, dlatego traktuj klucze jak hasła i trzymaj je z dala od miejsc, które mogą odczytać inni.

Gdzie klucze powinny się znajdować:

1. W zmiennych środowiskowych na Twoim serwerze, lub
2. W dedykowanym menedżerze sekretów.

Gdzie klucze nigdy nie mogą się pojawić:

1. W kodzie repozytorium — nigdy nie zapisuj klucza w Git, nawet w repozytorium prywatnym.
2. W kodzie frontendu — wszystko, co działa w przeglądarce, jest widoczne dla odwiedzających.
3. W aplikacji mobilnej — spakowane aplikacje można rozpakować i przejrzeć.
4. W e-mailach, wiadomościach na czacie ani zrzutach ekranu.

Oddzielaj klucze sandbox i produkcyjne. Używaj klucza sandbox do developmentu i testów, a klucza produkcyjnego wyłącznie w środowisku produkcyjnym. Zapobiega to przypadkowemu przenoszeniu prawdziwych pieniędzy przez kod testowy i ogranicza szkody w razie wycieku klucza deweloperskiego.

Jeśli podejrzewasz, że klucz został ujawniony — na przykład trafił do repozytorium, został wysłany w wiadomości lub pojawił się w logach — natychmiast go zrotuj. Nie czekaj na potwierdzenie nadużycia.

Aby zrotować klucz:

1. Wejdź w Panelu do Settings → API keys.
2. Wybierz właściwy klucz i użyj opcji Regenerate.
3. Stary klucz przestaje działać natychmiast, więc od razu zaktualizuj serwer lub menedżer sekretów nową wartością, aby uniknąć przerwania płatności.

Ponieważ regeneracja od razu unieważnia stary klucz, zaplanuj krótką chwilę na wdrożenie nowego. Jeśli potrzebujesz pomocy w ustaleniu, gdzie klucz mógł zostać ujawniony, otwórz zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
