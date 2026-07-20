---
id: KB-068
category: integration
lang: pl
title: Środowiska i adresy API
---

# Środowiska i adresy API

kremzaPay udostępnia dwa oddzielne środowiska API. Środowiska sandbox używaj do tworzenia i testowania integracji, a produkcyjnego do realnych płatności od kupujących.

**Adresy**

- Sandbox: `api.sandbox.kremzapay.demo`
- Produkcja: `api.kremzapay.demo`

Każde środowisko jest w pełni odizolowane. Transakcje, sesje i raporty utworzone w sandboxie nigdy nie pojawiają się w produkcji i odwrotnie.

**Klucze są osobne dla każdego środowiska**

Każde środowisko ma własny zestaw danych uwierzytelniających, w tym klucz API oraz crc_key używany do podpisów. Klucze wygenerowane w sandboxie nie działają w produkcji. Przechodząc na produkcję, wygeneruj nowy zestaw kluczy produkcyjnych w Panelu w sekcji Ustawienia i wymień zarówno adres bazowy, jak i klucze.

**Najczęstszy błąd**

Najczęstszym błędem integracji jest wysyłanie kluczy produkcyjnych na adres sandbox (lub odwrotnie). Ponieważ środowiska są odizolowane, żądanie zostaje odrzucone jako nieautoryzowane, mimo że sam klucz jest prawidłowy. Jeśli po zmianie środowiska widzisz błędy uwierzytelniania, sprawdź, czy adres bazowy i zestaw kluczy należą do tego samego środowiska.

**Lista kontrolna przed wdrożeniem produkcyjnym**

1. Zamień adres sandbox na adres produkcyjny.
2. Zamień klucz API sandbox na produkcyjny klucz API.
3. Zamień crc_key sandbox na produkcyjny crc_key.
4. Wykonaj żądanie testowe (zobacz artykuł o teście połączenia) na adresie produkcyjnym.

Jeśli żądanie zawiedzie, przed kontaktem z pomoc@kremzapay.demo upewnij się, że adres i klucz należą do tego samego środowiska.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
