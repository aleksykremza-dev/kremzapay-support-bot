---
id: KB-022
category: security
lang: pl
title: Czym jest 3D Secure 2
---

# Czym jest 3D Secure 2

3D Secure 2 (3DS2) to etap weryfikacji płatności kartą realizowany po stronie banku. Gdy Twój klient płaci, bank wydający kartę może poprosić go o potwierdzenie transakcji — zwykle przez zatwierdzenie jej w aplikacji bankowej, użycie danych biometrycznych (odcisk palca lub twarz) albo wpisanie jednorazowego kodu. kremzaPay nie wykonuje tej weryfikacji samodzielnie; odbywa się ona bezpośrednio między klientem a jego bankiem.

W przypadku płatności na obszarze Europejskiego Obszaru Gospodarczego (EOG) 3DS2 jest wymagane zgodnie z zasadami silnego uwierzytelniania klienta. Większość płatności kartą realizowanych przez kremzaPay uruchomi więc monit o weryfikację.

## Dlaczego to ważne

3DS2 ogranicza oszustwa, potwierdzając, że osoba płacąca jest prawdziwym posiadaczem karty. Przenosi także odpowiedzialność za obciążenia zwrotne przy transakcjach oszukańczych: gdy płatność zostanie pomyślnie uwierzytelniona, odpowiedzialność za spory dotyczące oszustw zwykle przechodzi z Ciebie, sprzedawcy, na wydawcę karty.

## Co się dzieje, gdy weryfikacja się nie powiedzie

Jeśli klient nie ukończy weryfikacji bankowej — na przykład anuluje monit, wpisze błędny kod lub bank odrzuci transakcję — płatność kończy się niepowodzeniem. W panelu kremzaPay pojawia się ona jako płatność `failed`. W takim przypadku klient nie zostaje obciążony i żadne środki nie są przekazywane.

## Co powinieneś zrobić

1. Poproś klientów, aby mieli zainstalowaną i zaktualizowaną aplikację bankową.
2. Jeśli klient zgłasza nieudaną płatność, zaproponuj ponowną próbę i dokończenie potwierdzenia w banku.
3. Sprawdź status płatności w sekcji Payments w panelu, aby potwierdzić, czy uwierzytelnienie się powiodło.

Weryfikacja jest kontrolowana przez bank klienta, więc nie możesz jej pominąć ani wyłączyć dla płatności kartą w EOG.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
