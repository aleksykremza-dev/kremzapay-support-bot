# kremzaPay Support Bot

Bot wsparcia dla fikcyjnego operatora płatności. Odpowiada po polsku i angielsku
wyłącznie na podstawie 242 artykułów dokumentacji, do każdej odpowiedzi podaje
źródło, a gdy nie wie, przekazuje sprawę człowiekowi zamiast zmyślać.
Wszystko działa lokalnie (Ollama + Qdrant), bez płatnych API.

## Jak to działa

Każde pytanie przechodzi przez pięć kroków:

1. **Maskowanie danych osobowych.** Numery kart, IBAN, PESEL, telefony i e-maile
   są zamazywane, zanim tekst trafi do modelu i do logów.
2. **Rozpoznanie intencji, od taniego do drogiego.** Najpierw reguły
   (ataki na prompt, prośby o oszustwo, pytania o konkurencję, podatki):
   0 ms, bez modelu. Potem podobieństwo do przykładów (kNN). Dopiero gdy to
   nie wystarcza, model LLM. Razem 52 intencje w 10 kategoriach.
3. **Szukanie w dokumentacji** (Qdrant, 643 fragmenty), zawężone do kategorii
   z kroku 2.
4. **Generowanie odpowiedzi** lokalnym modelem qwen2.5:7b, z dopiskiem
   „Źródło: KB-###”.
5. **Sędzia.** Osobne sprawdzenie: czy każdy fakt w odpowiedzi jest w znalezionych
   fragmentach? Jeśli nie, odpowiedź nie wychodzi, otwiera się ticket.

Cały przebieg rozmowy zapisuje się w SQLite jako jeden JSON (TurnState) i jest
widoczny na panelu `/dashboard`: dlaczego bot odpowiedział tak, a nie inaczej.

## Co wyszło

Mam zamrożony zestaw 288 pytań testowych, osobny od danych treningowych. Każdą
zmianę mierzę na tych samych 288, inaczej nie wiadomo, czy coś poprawiłem.

| | Przed | Po poprawkach |
|---|---|---|
| Trafność rozpoznania intencji | 65,6 % | 71,9 % |
| Wyłapane pytania spoza zakresu | 45 % | 85 % |
| Wyłapane próby nadużyć | 27 % | 60 % |
| Pytania niepotrzebnie odesłane do człowieka | 20 | 6 |

Szybka ścieżka (powitania, ataki, oczywiste pytania) odpowiada w ok. 0,4 s.
Odpowiedź z modelem to kilkanaście–kilkadziesiąt sekund na zwykłym laptopie.
Koszt: 0 zł, żadnych API.

## Czego się nauczyłem

- Pierwsza wersja miała 65 % i wyglądała dobrze na łatwych pytaniach. Dopiero
  analiza błędów pokazała dwie dziury: pytania o konkurencję przechodziły przez
  kNN przez samo podobieństwo słów, a „chcę rozmawiać z człowiekiem” model widział
  w każdej złości klienta. Obie naprawiłem regułami i poprawką promptu, stąd +6 pp.
- Słowo „zwrot” najczęściej występuje w artykułach o chargebackach, więc
  wyszukiwarka ciągnęła złe artykuły. Rozwiązanie: filtr po kategorii intencji.
  Znalezione na żywym teście, nie w teorii.
- Model 7B zamiast 3B: polski w 3B był za słaby. Wolniej, ale to portfolio,
  nie produkcja.
- Podczas automatycznych testów panelu wyszedł XSS (innerHTML). Naprawiony.

## Co bym zrobił inaczej

- Testy jednostkowe od pierwszego dnia, nie na końcu. Teraz jest ich 41 i pokrywają
  reguły, maskowanie PII i routing kaskady, ale nie generowanie ani sędziego.
- Mniej dokumentów „badawczych”, więcej działającego kodu.
- Pamięć rozmowy. Teraz każde pytanie jest osobne.

## Słowniczek: co za co odpowiada

| Termin | Co robi | Gdzie |
|---|---|---|
| **TurnState** | Jeden obiekt JSON na każde pytanie. Każdy krok dopisuje do niego swój wynik (intencja, znalezione fragmenty, odpowiedź, werdykt sędziego). Ten sam obiekt trafia do bazy i na panel. | `src/cascade.py`, `src/store.py` |
| **Kaskada intencji (L0 → L1 → L2)** | Trzy warstwy rozpoznawania, o co pyta klient. Tańsza warstwa próbuje pierwsza; droższa uruchamia się tylko, gdy tańsza nie jest pewna. | `src/cascade.py` |
| **L0: reguły** | Wzorce tekstowe bez modelu: atak na prompt, prośba o oszustwo, konkurencja, podatki. Odpowiedź w 0 ms. | `src/rules.py` |
| **L1: kNN router** | Porównuje pytanie z bankiem przykładów dla każdej intencji. Jeśli podobieństwo powyżej progu `t_accept`, intencja przyjęta; jeśli poniżej `t_oos`, pytanie spoza zakresu. | `src/knn_router.py` |
| **L2: klasyfikator LLM** | Model językowy dostaje pytanie i listę intencji, najpierw rozumuje, potem zwraca ścisły JSON z wybraną intencją. | `src/llm_classifier.py` |
| **Embeddingi** | Zamiana tekstu na wektor liczb, żeby porównywać znaczenie, a nie słowa. Model `paraphrase-multilingual-MiniLM`, ten sam dla PL i EN. | `src/ingest.py`, `src/search.py` |
| **Qdrant** | Baza wektorowa: trzyma 643 fragmenty dokumentacji i szuka najbliższych do pytania. | `docker-compose.yml`, `src/search.py` |
| **Retrieval** | Wyszukanie fragmentów dokumentacji pasujących do pytania, z filtrem po kategorii intencji. | `src/search.py` |
| **Generowanie z cytatem** | Model pisze odpowiedź tylko na podstawie znalezionych fragmentów i dopisuje `Źródło: KB-###`. | `src/answer_gen.py` |
| **Sędzia (groundedness judge)** | Drugi przebieg modelu: sprawdza, czy każde zdanie odpowiedzi ma pokrycie w fragmentach. Brak pokrycia = odpowiedź odrzucona, ticket. | `src/judge.py` |
| **Rail PII** | Maskowanie danych osobowych na wejściu, przed modelem i przed logami. | `src/pii.py` |
| **Gold set** | 288 pytań z ręcznie ustaloną poprawną intencją. Zamrożony w git, służy tylko do mierzenia. | `data/goldset/` |
| **Korpus treningowy** | 5412 pytań syntetycznych do budowy przykładów dla kNN. Nie pokrywa się z gold setem. | `data/corpus/` |
| **Accuracy / macro-F1** | Accuracy: ile pytań rozpoznano poprawnie. Macro-F1: średnia jakości po wszystkich intencjach, żeby rzadkie intencje liczyły się tak samo jak częste. | `src/eval_cascade.py` |
| **Recall (np. out_of_scope)** | Ile pytań danej klasy bot faktycznie wyłapał. 85 % = z każdych 100 pytań spoza zakresu 85 rozpoznane. | `data/eval/` |
| **confidence** | Pewność rozpoznania intencji: `high` lub `medium`, zależnie od tego, która warstwa zdecydowała i jak wysokie było podobieństwo w kNN (próg 0,72). | `src/cascade.py` |

## Uruchomienie

```bash
docker compose up -d                          # Qdrant
ollama pull qwen2.5:7b-instruct
uv sync
uv run python src/ingest.py                   # dokumentacja -> indeks
uv run uvicorn api:app --app-dir src --port 8020
```

Czat: http://localhost:8020 · panel: http://localhost:8020/dashboard ·
konfiguracja w `.env` (wzór: `.env.example`).

Testy jednostkowe (bez Dockera i modelu): `uv run pytest`. Pełna ewaluacja na
288 pytaniach (wymaga działającego Ollama i Qdrant): `uv run python src/eval_cascade.py`.

Ograniczenia: [docs/LIMITATIONS.md](docs/LIMITATIONS.md). Koszty: [docs/ECONOMICS.md](docs/ECONOMICS.md).

*kremzaPay nie istnieje. Dokumentacja i dane testowe są syntetyczne, stworzone
na potrzeby tego projektu.*
