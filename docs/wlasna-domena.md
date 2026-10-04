# Własna dokumentacja i własna dziedzina

Jak podłączyć własne artykuły i jak przygotować taksonomię, korpus i zbiór kontrolny dla innej dziedziny niż płatności.

[Wróć do README](../README.md)

## Własna dokumentacja

Artykuł to plik Markdown w `kb/<kategoria>/<id>.md`. `ingest.py` czyta wzorzec
`kb/*/*.md` (jeden poziom podkatalogów); nazwa podkatalogu nie jest przez kod
używana, kategoria pochodzi z nagłówka. Nagłówek między dwiema liniami `---` ma
pola `title`, `category`, `id`; `category` musi być jedną z kategorii
w `data/taxonomy.json`, bo wyszukiwanie filtruje po niej fragmenty. Treść jest
cięta na fragmenty po akapitach (pusta linia między nimi) do ok. 800 znaków
(`CHUNK_SIZE`); każdy fragment dostaje tytuł artykułu. Jeśli po treści jest
jeszcze linia `---`, wszystko za ostatnią z nich jest odcinane. Wersja polska
i angielska to osobne pliki (np. `kb/refunds/KB-030-pl.md` i `KB-030-en.md`);
dodatkowe pola nagłówka, np. `lang`, trafiają do payloadu w Qdrant. Minimalny
`kb/refunds/KB-030-pl.md`:

```
---
id: KB-030
category: refunds
title: Gdzie jest mój zwrot
---

Zwrot na kartę trwa zwykle od 3 do 7 dni roboczych od zlecenia przez sprzedawcę.
Status zwrotu widać w panelu w zakładce Zwroty.

Jeśli po 7 dniach roboczych środki nie wróciły, przygotuj numer transakcji.
```

Po każdej zmianie w artykułach: `make ingest` (Docker) albo `uv run python src/ingest.py` (`make ingest-local`).
Skrypt kasuje kolekcję i buduje ją od zera. Oczekiwany wynik:

```
Articles found: 12
Chunks produced: 31
Computing embeddings (first run downloads the model, then fast)...
Done: 31 points in collection 'kremzapay_kb'
```

Bez katalogu `kb/` (albo bez plików `.md` w nim) skrypt wypisuje jedną linię
i kończy się kodem wyjścia 2, kolekcja nie powstaje:

```
Baza wiedzy nie jest częścią repozytorium. Umieść artykuły w kb/ (format: README, sekcja "Własna dokumentacja").
```

Sprawdzenie wyszukiwania bez bota: `uv run python src/search.py "gdzie jest mój
zwrot"` wypisuje 3 najlepsze fragmenty w postaci `[wynik] id (kategoria) tytuł`.

## Własny zbiór pytań

Rozpoznawanie intencji opiera się na trzech zbiorach w `data/`; wszystkie
dotyczą wsparcia płatności i trzymają się `data/taxonomy.json`:

- `taxonomy.json`: 52 intencje w 10 kategoriach (`account`, `billing`, `buyers`,
  `disputes`, `integration`, `payments`, `payouts`, `refunds`, `security`,
  `service`) plus klasy specjalne `other_in_scope`, `out_of_scope`, `chitchat`,
  `unsafe`; sklejany z `data/taxonomy/part-*.json` przez
  `uv run python src/merge_taxonomy.py` (powtórzone `id` kończy się kodem 1).
- `corpus/corpus-*.json`: 5412 pytań z etykietą intencji, na których uczy się
  klasyfikator tematu (warstwa 1).
- `goldset/gold-*.json`: 288 pytań z oczekiwaną etykietą dla `make test-accuracy`
  i `make test-func`; żadne pytanie z gold setu nie występuje w korpusie.
- `goldset/split.json`: podział gold setu na test (192) i dev (96), seed 42.

Kto podłącza dokumentację z innej dziedziny, przygotowuje własną taksonomię,
korpus i gold set w tych samych kształtach JSON (taksonomia, wpis korpusu, wpis
gold setu):

```json
{"version": 1,
 "intents": [{"id": "refund_status_time", "category": "refunds", "definition": "...",
              "examples": ["..."], "not": ["..."]}],
 "special_classes": [{"id": "out_of_scope", "definition": "...", "examples": ["..."]}]}
```
```json
{"cases": [{"q": "Ile trwa zwrot?", "intent": "refund_status_time", "lang": "pl",
            "style": "plain"}]}
{"cases": [{"q": "Ile trwa zwrot?", "expected_intent": "refund_status_time",
            "expected_scope": "in_scope", "lang": "pl", "style": "plain"}]}
```

W gold secie `expected_scope` to `in_scope` albo id klasy specjalnej (wtedy
`expected_intent` ma tę samą wartość). `uv run python tools/question_coverage.py`
(`make coverage`) wypisuje tabelę intencja -> liczba pytań w korpusie i w gold
secie oraz etykiety poniżej progu (mniej niż 20 w korpusie albo 0 w gold secie;
`--strict` zwraca wtedy kod 1). Indeks tematów ma w nazwie skrót korpusu, więc po
zmianie korpusu przy starcie powstaje nowy w `data/cache/`; `make router-index`
zapisuje go w `data/index/` (stary plik jest usuwany), żeby inne instalacje nie
liczyły go od nowa. Do dopasowania są też wzorce w `src/rules.py`
i `BRAND_VOICE` w `src/answer_gen.py`.
