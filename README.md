# kremzaPay Support Bot

Bot wsparcia dla fikcyjnego operatora płatności. Odpowiada po polsku i angielsku
wyłącznie na podstawie 242 artykułów dokumentacji, do każdej odpowiedzi podaje
źródło, a gdy nie wie, przekazuje sprawę człowiekowi zamiast zmyślać.
Wszystko działa lokalnie (Ollama + Qdrant), bez płatnych API.

## Jak to działa

Klient pisze pytanie na czacie. Zanim dostanie odpowiedź, pytanie przechodzi
przez pięć etapów. Każdy etap ma swoje zadanie i swój plik w `src/`.

**1. Ukrycie danych osobowych.** Jeśli w pytaniu jest numer karty, IBAN, PESEL,
telefon albo e-mail, program zamienia go na etykietę typu `[KARTA]`. Robi to od
razu, zanim tekst zobaczy jakikolwiek model AI i zanim cokolwiek zapisze się
w logach. Dzięki temu dane klienta nie wyciekają ani do modelu, ani do plików.

**2. Ustalenie, o co właściwie pyta klient.** Bot ma listę 52 typowych spraw
(np. „gdzie jest mój zwrot”, „jak włączyć BLIK”, „chcę zmienić konto bankowe”),
pogrupowanych w 10 kategorii. Musi dopasować pytanie do jednej z nich. Robi to
w trzech krokach, od najtańszego do najdroższego:

- **Reguły.** Zwykłe wzorce tekstowe, bez żadnego modelu. Wyłapują to, na co bot
  w ogóle nie powinien odpowiadać: próby zmanipulowania bota („zignoruj
  instrukcje i…”), prośby o pomoc w oszustwie, pytania o konkurencję, pytania
  podatkowe. Zajmuje to ułamek milisekundy.
- **Porównanie z przykładami.** Bot ma bazę kilku tysięcy przykładowych pytań
  z przypisaną sprawą. Sprawdza, do których nowe pytanie jest najbardziej
  podobne znaczeniowo (technicznie: kNN na wektorach). Jeśli podobieństwo jest
  wysokie, sprawa ustalona i model AI w ogóle nie jest potrzebny.
- **Model językowy (LLM).** Dopiero gdy dwa poprzednie kroki nie są pewne,
  pytanie idzie do lokalnego modelu AI, który czyta je i wybiera sprawę z listy.
  To najdokładniejszy krok, ale najwolniejszy (sekundy), dlatego jest ostatni.

**3. Znalezienie odpowiedzi w dokumentacji.** Cała pomoc kremzaPay (242 artykuły)
jest pocięta na 643 krótkie fragmenty i zapisana w bazie Qdrant, która umie
szukać po znaczeniu, a nie po słowach. Bazę można dowolnie powiększać: jej
zakres zależy od regulaminów i możliwości konkretnego serwisu, a nie od bota.
Bot wyciąga fragmenty pasujące do pytania, ale tylko z kategorii ustalonej
w kroku 2. Bez tego filtra pytanie o zwrot ciągnęło artykuły o chargebackach,
bo tam słowo „zwrot” pada najczęściej.

**4. Napisanie odpowiedzi.** Lokalny model (qwen2.5, 7 mld parametrów, działa na
zwykłym komputerze albo na serwerze) dostaje pytanie i znalezione fragmenty i pisze odpowiedź
tylko na ich podstawie. Na końcu dopisuje, z którego artykułu pochodzi
informacja: „Źródło: KB-042”. Klient może sprawdzić.

**5. Kontrola przed wysłaniem.** Osobny przebieg modelu, „sędzia”, dostaje
odpowiedź i fragmenty i sprawdza zdanie po zdaniu: czy to jest w dokumentacji?
Jeśli którekolwiek zdanie nie ma pokrycia, odpowiedź nie wychodzi. Zamiast niej
klient dostaje informację, że sprawa trafia do człowieka, i otwiera się
zgłoszenie. Bot woli nie odpowiedzieć niż zmyślić.

**Co widać z zewnątrz.** Każda rozmowa zapisuje się w bazie SQLite razem z całą
ścieżką decyzji: co wykryły reguły, jakie było podobieństwo, którą sprawę wybrał
model, które fragmenty poszły do odpowiedzi, co powiedział sędzia. Panel
`/dashboard` pokazuje to dla każdej rozmowy. Odpowiada na pytanie „dlaczego bot
odpowiedział właśnie tak”, bez grzebania w logach.

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
