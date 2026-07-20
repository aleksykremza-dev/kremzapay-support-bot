---
id: KB-079
category: integration
lang: pl
title: Adresy IP i firewall
---

# Adresy IP i firewall

Jeśli Twój serwer filtruje ruch przychodzący za pomocą firewalla, musisz zezwolić powiadomieniom webhook kremzaPay na dotarcie do Twojego endpointu. Ta strona wyjaśnia, które adresy dopuścić i jak działa ruch API w drugą stronę.

## Adresy źródłowe webhooków

Powiadomienia webhook pochodzą ze zdefiniowanego zakresu adresów IP. Aktualny zakres jest podany w Panel → Ustawienia → Powiadomienia. Jeśli Twój serwer ogranicza połączenia przychodzące, dodaj ten zakres do listy dozwolonych, aby powiadomienia nie były blokowane, zanim dotrą do Twojego endpointu webhook.

Sprawdzaj podany zakres okresowo. Jeśli się zmieni, odpowiednio zaktualizuj reguły firewalla — w przeciwnym razie powiadomienia mogą zacząć się nie udawać. Pamiętaj, że kremzaPay ponawia niedostarczony webhook do 8 razy w ciągu 24 godzin, a Twój endpoint powinien odpowiedzieć statusem HTTP `200` i treścią `OK` po odebraniu i zaakceptowaniu powiadomienia.

## Ruch wychodzący do API

Zapytania, które wysyłasz do API kremzaPay, trafiają do publicznych endpointów HTTPS, więc nie jest dla nich potrzebna żadna specjalna reguła firewalla dla ruchu przychodzącego. Endpointy wymagają TLS 1.2 lub wyższego — upewnij się, że Twój klient HTTP i biblioteki TLS są aktualne, aby połączenie nie zostało odrzucone.

Hosty API to:

- Sandbox: `api.sandbox.kremzapay.demo`
- Produkcja: `api.kremzapay.demo`

## Lista kontrolna

1. Dopuść zakres IP webhooków z Panel → Ustawienia → Powiadomienia.
2. Potwierdź, że Twój endpoint webhook odpowiada `200 OK`.
3. Upewnij się, że połączenia wychodzące używają TLS 1.2 lub wyższego.

Jeśli po dopuszczeniu zakresu powiadomienia nadal nie docierają, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
