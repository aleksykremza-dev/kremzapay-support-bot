---
id: KB-074
category: integration
lang: pl
title: Wtyczki dla sklepów
---

# Wtyczki dla sklepów

kremzaPay udostępnia oficjalne wtyczki dla najpopularniejszych platform sklepowych, dzięki czemu możesz przyjmować płatności bez samodzielnego pisania kodu integracji. Obsługiwane platformy to WooCommerce, PrestaShop, Magento i Shopify.

## Instalacja wtyczki

1. Otwórz marketplace wtyczek swojej platformy (na przykład katalog wtyczek WooCommerce, PrestaShop Addons, Magento Marketplace lub Shopify App Store) i zainstaluj oficjalną wtyczkę kremzaPay.
2. Aktywuj wtyczkę w panelu administracyjnym sklepu.
3. Otwórz ustawienia wtyczki i wprowadź trzy wartości z Panel → Ustawienia: `merchant_id`, `api_key` oraz `crc_key`. Klucz `crc_key` służy do podpisywania żądań algorytmem SHA-384, więc zachowaj go w poufności.
4. Wybierz środowisko. Na czas testów użyj środowiska sandbox (`api.sandbox.kremzapay.demo`), a przy uruchomieniu produkcyjnym przełącz na produkcję (`api.kremzapay.demo`). Każde środowisko korzysta z własnego zestawu kluczy.

## Test przed uruchomieniem

Zanim udostępnisz płatności prawdziwym klientom, wykonaj testową płatność w sandbox. Złóż testowe zamówienie w sklepie, opłać je na stronie płatności kremzaPay i sprawdź, czy status zamówienia aktualizuje się poprawnie po otrzymaniu powiadomienia. Upewnij się, że zwroty i powiadomienia o płatnościach również działają zgodnie z oczekiwaniami.

Jeśli status się nie zmienia, sprawdź, czy klucze odpowiadają wybranemu środowisku oraz czy sklep może odbierać powiadomienia webhook. Dostarczanie powiadomień możesz przejrzeć w Panel → Raporty.

Aktualizuj wtyczkę do najnowszej wersji, aby zawsze mieć aktualne metody płatności i poprawki bezpieczeństwa. W razie potrzeby załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo (pon.–pt. 8:00–18:00 CET).

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
