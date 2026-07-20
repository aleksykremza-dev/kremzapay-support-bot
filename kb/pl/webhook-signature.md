---
id: KB-072
category: integration
lang: pl
title: Weryfikacja podpisu webhooka
---

# Weryfikacja podpisu webhooka

Każdy webhook wysyłany przez kremzaPay zawiera podpis, dzięki któremu możesz potwierdzić, że powiadomienie naprawdę pochodzi od nas i nie zostało zmienione w drodze. Zawsze zweryfikuj podpis, zanim zaufasz danym i na ich podstawie zaczniesz działać.

**Jak działa podpis**

Webhook jest dostarczany jako żądanie `POST`. Jego podpis to skrót SHA-384 z ładunku (payload) połączonego z Twoim `crc_key`. Ponieważ crc_key znasz tylko Ty i kremzaPay, zgodny podpis dowodzi, że ładunek jest autentyczny i niezmieniony.

**Kroki weryfikacji**

1. Odczytaj surowy ładunek dokładnie tak, jak został odebrany, bez ponownego formatowania czy serializacji.
2. Wylicz skrót SHA-384 z ładunku, używając `crc_key` właściwego dla środowiska.
3. Porównaj wyliczoną wartość z podpisem przesłanym w webhooku.
4. Jeśli są zgodne, przetwórz powiadomienie. Jeśli nie, odrzuć je.

**Odrzucanie nieprawidłowych webhooków**

Jeśli podpis się nie zgadza, nie przetwarzaj danych. Odrzuć żądanie po cichu, odpowiadając kodem innym niż 200. kremzaPay traktuje każdą odpowiedź inną niż 200 jako nieudane dostarczenie i ponawia próbę automatycznie, do 8 razy w ciągu 24 godzin. Na prawidłowy webhook odpowiedz kodem HTTP 200 i treścią `OK`.

**Dobre praktyki**

- Weryfikuj przed uruchomieniem logiki biznesowej, aby zniekształcone lub podrobione ładunki nigdy nie trafiały do obsługi zamówień.
- Używaj crc_key z tego samego środowiska, które wysłało webhook.
- Jeśli prawidłowy webhook został pominięty, możesz wywołać ręczne ponowne wysłanie z Panelu.

Jeśli weryfikacja zachowuje się nieoczekiwanie, załóż zgłoszenie w Panelu lub napisz na pomoc@kremzapay.demo.

---
*kremzaPay to fikcyjny operator płatności. Ta strona jest dokumentacją demonstracyjną stworzoną na potrzeby projektu portfolio i nie ma wartości prawnej ani informacyjnej.*
