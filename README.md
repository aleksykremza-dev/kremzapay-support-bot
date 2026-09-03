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

Historia rozmowy jest zapisywana (sesja, kolejne wiadomości, zgłoszenia), ale
na razie bot z niej nie korzysta przy odpowiadaniu: każde pytanie traktuje
osobno, bez kontekstu poprzednich. Pamięć rozmowy to następny krok.

## Co wyszło

Żeby wiedzieć, jak bot faktycznie działa, mam stały egzamin: 288 pytań, do których
sam wcześniej ustaliłem poprawną odpowiedź (jaka to sprawa, czy pytanie jest
w zakresie, czy to próba nadużycia). Ten zestaw jest zamrożony i nie pokrywa się
z przykładami, na których bot się „uczy”, inaczej egzamin byłby ściągnięty.
Po każdej zmianie w bocie przepuszczam te same 288 pytań jeszcze raz.

| Co sprawdzam | Wynik |
|---|---|
| Ile z 288 pytań bot przypisał do właściwej sprawy | 71,9 % |
| Ile pytań spoza zakresu (podatki, konkurencja, pogoda) bot poprawnie odrzucił zamiast odpowiadać | 85 % |
| Ile prób nadużycia (manipulacja botem, prośba o pomoc w oszustwie) bot zatrzymał | 60 % |
| Ile zwykłych, możliwych do obsłużenia pytań bot niepotrzebnie odesłał do człowieka (na 288) | 6 |

Co to znaczy w praktyce: z każdych 100 pytań o podatki czy konkurencję bot
przepuszcza 15 i próbuje na nie odpowiadać. Z każdych 100 prób nadużycia łapie 60.
Daleko od ideału, ale liczby są zmierzone, nie odczute, i każdą kolejną poprawkę
da się sprawdzić tym samym egzaminem.

**Co się dzieje, gdy bot nie jest pewny.** Błędne rozpoznanie sprawy nie oznacza
błędnej odpowiedzi dla klienta, bo po drodze są trzy zabezpieczenia:

- pewność rozpoznania jest niska → bot nie odpowiada, tylko dopytuje klienta,
  czego dokładnie dotyczy sprawa;
- temat jest nasz, ale bot nie rozpoznał sprawy albo nie ma o niej nic
  w dokumentacji → otwiera zgłoszenie do człowieka i mówi o tym klientowi;
- odpowiedź została napisana, ale sędzia nie znalazł jej potwierdzenia
  w dokumentacji → odpowiedź nie wychodzi, zamiast niej zgłoszenie.

Błąd bota kończy się więc dopytaniem albo przekazaniem sprawy człowiekowi,
a nie zmyśloną odpowiedzią.

**Czas i koszt.** Pytania, które załatwiają reguły albo porównanie z przykładami
(powitania, ataki, oczywiste sprawy), dostają odpowiedź w ok. 0,4 s. Pytania,
które wymagają modelu, to kilkanaście–kilkadziesiąt sekund na zwykłym laptopie;
na serwerze z kartą graficzną odpowiednio szybciej. Koszt użycia: 0 zł, wszystko
działa lokalnie, bez płatnych usług.

## Ograniczenia i co dalej

- **Bot nie pamięta rozmowy.** Każde pytanie traktuje osobno, więc „a ile to
  potrwa?” po pytaniu o zwrot nie zostanie zrozumiane. Następny krok: podawać
  modelowi kilka poprzednich wiadomości z sesji.
- **Testy nie obejmują całości.** 41 testów sprawdza reguły, maskowanie danych
  i routing, ale nie generowanie odpowiedzi ani sędziego, bo te wymagają
  działającego modelu. Do zrobienia: testy z nagranymi odpowiedziami modelu.
- **Dokumentacja i pytania testowe są syntetyczne.** Wyniki mówią, jak bot radzi
  sobie z tym zestawem, nie z prawdziwymi klientami. Sprawdzian: pilot na
  prawdziwej dokumentacji jednego serwisu.
- **Pewność bota to etykieta, nie liczba.** „Wysoka” i „średnia” są ustawione
  progiem ręcznie. Do zrobienia: kalibracja na danych, żeby 80 % pewności
  znaczyło 80 % trafień.

Pełna lista ograniczeń: [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Słowniczek: co za co odpowiada i gdzie to jest w kodzie

Kolejność jak w rozdziale „Jak to działa”.

| Termin | Co to jest i co robi | Gdzie |
|---|---|---|
| **Maskowanie PII** | PII to dane osobowe. Program zamienia numery kart, IBAN, PESEL, telefony i e-maile na etykiety, zanim tekst trafi do modelu lub do logów. | `src/pii.py` |
| **Reguły (warstwa 0)** | Wzorce tekstowe bez modelu: atak na bota, prośba o oszustwo, konkurencja, podatki. Odpowiedź natychmiast. | `src/rules.py` |
| **Porównanie z przykładami (warstwa 1, kNN)** | Bot ma tysiące przykładowych pytań z przypisaną sprawą. Szuka kilku najbardziej podobnych do nowego pytania i patrzy, jaką sprawę mają. Jeśli podobieństwo jest powyżej progu `T_ACCEPT`, sprawa przyjęta; jeśli poniżej `T_OOS`, pytanie uznane za spoza zakresu. | `src/knn_router.py` |
| **Klasyfikator LLM (warstwa 2)** | Model językowy dostaje pytanie i listę spraw, najpierw opisuje swoje rozumowanie, potem zwraca jedną wybraną sprawę w ścisłym formacie JSON. | `src/llm_classifier.py` |
| **Embeddingi** | Sposób zamiany tekstu na ciąg liczb tak, żeby teksty o podobnym znaczeniu miały podobne liczby. Dzięki temu „gdzie mój zwrot” i „nie dostałem pieniędzy z powrotem” są blisko siebie, choć nie mają wspólnych słów. Ten sam model dla polskiego i angielskiego. | `src/ingest.py`, `src/search.py` |
| **Qdrant** | Baza danych do takich ciągów liczb. Trzyma 643 fragmenty dokumentacji i szybko znajduje najbliższe do pytania. Działa w Dockerze. | `docker-compose.yml`, `src/search.py` |
| **Wyszukiwanie (retrieval)** | Pobranie z Qdrant fragmentów pasujących do pytania, tylko z kategorii ustalonej przez klasyfikator. | `src/search.py` |
| **Generowanie odpowiedzi** | Model pisze odpowiedź wyłącznie na podstawie znalezionych fragmentów i dopisuje `Źródło: KB-###`. | `src/answer_gen.py` |
| **Sędzia** | Drugie wywołanie modelu: sprawdza, czy każde zdanie odpowiedzi ma pokrycie we fragmentach. Brak pokrycia = odpowiedź odrzucona, zgłoszenie do człowieka. | `src/judge.py` |
| **TurnState** | Jeden obiekt JSON na każde pytanie. Każdy etap dopisuje do niego swój wynik. Ten sam obiekt trafia do bazy i na panel `/dashboard`. | `src/cascade.py`, `src/store.py` |
| **Pewność (confidence)** | Etykieta `high` albo `medium`, zależnie od tego, która warstwa rozpoznała sprawę i jak wysokie było podobieństwo (próg 0,72). Niska pewność = bot dopytuje. | `src/cascade.py` |
| **Zestaw egzaminacyjny (gold set)** | 288 pytań z ręcznie ustaloną poprawną odpowiedzią. Zamrożony, służy tylko do mierzenia. | `data/goldset/` |
| **Korpus przykładów** | 5412 pytań syntetycznych, z których korzysta porównanie z przykładami. Nie pokrywa się z zestawem egzaminacyjnym. | `data/corpus/` |
| **Trafność (accuracy)** | Odsetek pytań z egzaminu, którym bot przypisał właściwą sprawę. | `src/eval_cascade.py` |
| **Macro-F1** | Średnia jakość liczona osobno dla każdej sprawy, a potem uśredniona. Dzięki temu rzadkie sprawy liczą się tak samo jak częste, a wynik nie jest zawyżony przez kilka popularnych. | `src/eval_cascade.py` |
| **Wykrywalność (recall)** | Ile pytań danego typu bot faktycznie wyłapał. 85 % dla pytań spoza zakresu = z każdych 100 takich pytań 85 rozpoznane. | `data/eval/` |

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
