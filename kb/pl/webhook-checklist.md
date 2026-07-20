---
id: KB-119
category: service
lang: pl
title: Webhooki nie przychodzą — checklista
---

# Webhooki nie przychodzą — checklista

Jeśli Twój serwer nie otrzymuje powiadomień webhook, przejdź przez tę checklistę po kolei. Większość problemów z dostarczaniem wynika z błędu konfiguracji lub odpowiedzi serwera, który te kroki pomogą wykryć.

1. **Sprawdź stronę statusu.** Otwórz status.kremzapay.demo i spójrz na komponent Webhooki. Jeśli pokazuje stan ograniczony lub niedostępny, dostarczanie jest opóźnione po naszej stronie i nie musisz nic robić.
2. **Zweryfikuj adres URL powiadomień.** W Panel → Ustawienia → Powiadomienia sprawdź, czy adres URL powiadomień jest poprawny i wskazuje na **publiczny endpoint HTTPS**. Adresy lokalne i adresy bez HTTPS nie mogą odbierać webhooków.
3. **Odpowiadaj szybko 200 "OK".** Twój endpoint musi odpowiadać kodem HTTP **200** i treścią **"OK"** w czasie poniżej 10 sekund. Wolne odpowiedzi są traktowane jako niepowodzenia i wywołują ponowne próby.
4. **Zezwól na nasz zakres IP.** Upewnij się, że Twój firewall przepuszcza zakres adresów IP wskazany w Panel → Ustawienia → Powiadomienia. Jeśli te adresy są zablokowane, powiadomienia nigdy nie dotrą do Twojego serwera.
5. **Sprawdź ponowne próby w widoku płatności.** Otwórz daną płatność w Panelu, aby zobaczyć próby dostarczenia. kremzaPay wykonuje do 8 ponownych prób w ciągu 24 godzin, więc chwilowo nieosiągalny serwer zostanie ponowiony.
6. **Użyj przycisku ponownego wysłania.** Dla konkretnej płatności użyj przycisku ponownego wysłania w widoku płatności, aby wyzwolić dostarczenie ponownie po usunięciu przyczyny.

**Nadal nic?**

Jeśli webhooki nadal nie przychodzą po wszystkich sześciu krokach, zgłoś ticket z Panelu. Dołącz sessionId dotkniętej płatności oraz odpowiednie znaczniki czasu, abyśmy mogli prześledzić dostarczanie po naszej stronie.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
