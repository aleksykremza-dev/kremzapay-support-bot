# Support Bot: silnik bota wsparcia na własnej dokumentacji

Bot, który odpowiada klientom wyłącznie na podstawie Twojej dokumentacji
(pomoc, FAQ, regulaminy), do każdej odpowiedzi podaje źródło, a gdy nie wie,
przekazuje sprawę człowiekowi zamiast zmyślać. Działa po polsku i angielsku,
w całości lokalnie (Ollama + Qdrant), bez płatnych API.

Repozytorium zawiera silnik: rozpoznawanie spraw, wyszukiwanie w dokumentacji,
generowanie odpowiedzi z kontrolą, panel podglądu. **Baza wiedzy nie jest
częścią repozytorium**: podłączasz własną według instrukcji niżej. Silnik był
rozwijany na dokumentacji operatora płatności, dlatego przykładowa lista spraw
w `data/` dotyczy płatności; do innego tematu trzeba ją przerobić (opisane
w sekcji „Własna dokumentacja”).

W kodzie i panelu występuje nazwa `kremzaPay`: to robocza nazwa projektu.

## Jak to działa

Klient pisze pytanie na czacie. Zanim dostanie odpowiedź, pytanie przechodzi
przez pięć etapów. Każdy etap ma swoje zadanie i swój plik w `src/`.

**1. Ukrycie danych osobowych.** Jeśli w pytaniu jest numer karty, IBAN, PESEL,
telefon albo e-mail, program zamienia go na etykietę typu `[KARTA]`. Robi to od
razu, zanim tekst zobaczy jakikolwiek model AI i zanim cokolwiek zapisze się
w logach. Dzięki temu dane klienta nie wyciekają ani do modelu, ani do plików.

**2. Ustalenie, o co właściwie pyta klient.** Bot ma listę typowych spraw
(np. „gdzie jest mój zwrot”, „jak włączyć BLIK”, „chcę zmienić konto bankowe”),
pogrupowanych w kategorie. Musi dopasować pytanie do jednej z nich. Robi to
w trzech krokach, od najtańszego do najdroższego:

- **Reguły.** Zwykłe wzorce tekstowe, bez żadnego modelu. Wyłapują to, na co bot
  w ogóle nie powinien odpowiadać: próby zmanipulowania bota („zignoruj
  instrukcje i…”), prośby o pomoc w oszustwie, pytania o konkurencję, pytania
  spoza tematu. Zajmuje to ułamek milisekundy.
- **Porównanie z przykładami.** Bot ma bazę przykładowych pytań z przypisaną
  sprawą. Sprawdza, do których nowe pytanie jest najbardziej podobne
  znaczeniowo (technicznie: kNN na wektorach). Jeśli podobieństwo jest wysokie,
  sprawa ustalona i model AI w ogóle nie jest potrzebny.
- **Model językowy (LLM).** Dopiero gdy dwa poprzednie kroki nie są pewne,
  pytanie idzie do lokalnego modelu AI, który czyta je i wybiera sprawę z listy.
  To najdokładniejszy krok, ale najwolniejszy (sekundy), dlatego jest ostatni.

**3. Znalezienie odpowiedzi w dokumentacji.** Twoje artykuły są pocięte na
krótkie fragmenty i zapisane w bazie Qdrant, która umie szukać po znaczeniu,
a nie po słowach. Wielkość bazy zależy tylko od Ciebie: od kilkunastu
artykułów do pełnego centrum pomocy. Bot wyciąga fragmenty pasujące do pytania,
ale tylko z kategorii ustalonej w kroku 2. Bez tego filtra pytanie o zwrot
ciągnęło artykuły o chargebackach, bo tam słowo „zwrot” pada najczęściej.

**4. Napisanie odpowiedzi.** Lokalny model (qwen2.5, 7 mld parametrów, działa na
zwykłym komputerze albo na serwerze) dostaje pytanie i znalezione fragmenty
i pisze odpowiedź tylko na ich podstawie. Na końcu dopisuje, z którego artykułu
pochodzi informacja: „Źródło: KB-042”. Klient może sprawdzić.

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

## Co się dzieje, gdy bot nie jest pewny

Błędne rozpoznanie sprawy nie oznacza błędnej odpowiedzi dla klienta, bo po
drodze są trzy zabezpieczenia:

- pewność rozpoznania jest niska → bot nie odpowiada, tylko dopytuje klienta,
  czego dokładnie dotyczy sprawa;
- temat jest w zakresie, ale bot nie rozpoznał sprawy albo nie ma o niej nic
  w dokumentacji → otwiera zgłoszenie do człowieka i mówi o tym klientowi;
- odpowiedź została napisana, ale sędzia nie znalazł jej potwierdzenia
  w dokumentacji → odpowiedź nie wychodzi, zamiast niej zgłoszenie.

Błąd bota kończy się więc dopytaniem albo przekazaniem sprawy człowiekowi,
a nie zmyśloną odpowiedzią.

## Jak mierzyć jakość na swojej bazie

W repo jest gotowy egzamin: skrypt `src/eval_cascade.py` przepuszcza przez bota
zestaw pytań z ustaloną poprawną odpowiedzią (`data/goldset/`) i liczy, ile
spraw rozpoznano właściwie, ile pytań spoza zakresu odrzucono, ile prób
nadużycia zatrzymano i ile zwykłych pytań niepotrzebnie poszło do człowieka.

Zasada: zestaw egzaminacyjny jest zamrożony i nie pokrywa się z przykładami,
na których bot się „uczy”, inaczej egzamin byłby ściągnięty. Po każdej zmianie
w bocie przepuszczasz te same pytania jeszcze raz i porównujesz. Liczby są
zmierzone, nie odczute.

Zestaw w repo dotyczy płatności. Na własnym temacie przygotuj własny (format
w sekcji „Własna dokumentacja”).

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
- **Przykładowe sprawy dotyczą płatności.** Lista spraw, przykłady pytań
  i egzamin w `data/` są pod operatora płatności. Na inny temat trzeba je
  przerobić, sam silnik jest niezależny od tematu.
- **Pewność bota to etykieta, nie liczba.** „Wysoka” i „średnia” są ustawione
  progiem ręcznie. Do zrobienia: kalibracja na danych, żeby 80 % pewności
  znaczyło 80 % trafień.

Pełna lista ograniczeń: [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Słowniczek: co za co odpowiada i gdzie to jest w kodzie

Kolejność jak w rozdziale „Jak to działa”.

| Termin | Co to jest i co robi | Gdzie |
|---|---|---|
| **Maskowanie PII** | PII to dane osobowe. Program zamienia numery kart, IBAN, PESEL, telefony i e-maile na etykiety, zanim tekst trafi do modelu lub do logów. | `src/pii.py` |
| **Reguły (warstwa 0)** | Wzorce tekstowe bez modelu: atak na bota, prośba o oszustwo, konkurencja, tematy spoza zakresu. Odpowiedź natychmiast. | `src/rules.py` |
| **Porównanie z przykładami (warstwa 1, kNN)** | Bot ma przykładowe pytania z przypisaną sprawą. Szuka kilku najbardziej podobnych do nowego pytania i patrzy, jaką sprawę mają. Jeśli podobieństwo jest powyżej progu `T_ACCEPT`, sprawa przyjęta; jeśli poniżej `T_OOS`, pytanie uznane za spoza zakresu. | `src/knn_router.py` |
| **Klasyfikator LLM (warstwa 2)** | Model językowy dostaje pytanie i listę spraw, najpierw opisuje swoje rozumowanie, potem zwraca jedną wybraną sprawę w ścisłym formacie JSON. | `src/llm_classifier.py` |
| **Embeddingi** | Sposób zamiany tekstu na ciąg liczb tak, żeby teksty o podobnym znaczeniu miały podobne liczby. Dzięki temu „gdzie mój zwrot” i „nie dostałem pieniędzy z powrotem” są blisko siebie, choć nie mają wspólnych słów. Ten sam model dla polskiego i angielskiego. | `src/ingest.py`, `src/search.py` |
| **Qdrant** | Baza danych do takich ciągów liczb. Trzyma fragmenty dokumentacji i szybko znajduje najbliższe do pytania. Działa w Dockerze. | `docker-compose.yml`, `src/search.py` |
| **Wyszukiwanie (retrieval)** | Pobranie z Qdrant fragmentów pasujących do pytania, tylko z kategorii ustalonej przez klasyfikator. | `src/search.py` |
| **Generowanie odpowiedzi** | Model pisze odpowiedź wyłącznie na podstawie znalezionych fragmentów i dopisuje `Źródło: KB-###`. | `src/answer_gen.py` |
| **Sędzia** | Drugie wywołanie modelu: sprawdza, czy każde zdanie odpowiedzi ma pokrycie we fragmentach. Brak pokrycia = odpowiedź odrzucona, zgłoszenie do człowieka. | `src/judge.py` |
| **TurnState** | Jeden obiekt JSON na każde pytanie. Każdy etap dopisuje do niego swój wynik. Ten sam obiekt trafia do bazy i na panel `/dashboard`. | `src/cascade.py`, `src/store.py` |
| **Pewność (confidence)** | Etykieta `high` albo `medium`, zależnie od tego, która warstwa rozpoznała sprawę i jak wysokie było podobieństwo (próg 0,72). Niska pewność = bot dopytuje. | `src/cascade.py` |
| **Zestaw egzaminacyjny (gold set)** | Pytania z ręcznie ustaloną poprawną odpowiedzią. Zamrożony, służy tylko do mierzenia. W repo: 288 pytań o płatności. | `data/goldset/` |
| **Korpus przykładów** | Pytania, z których korzysta porównanie z przykładami. Nie pokrywa się z zestawem egzaminacyjnym. W repo: 5412 pytań o płatności. | `data/corpus/` |
| **Trafność (accuracy)** | Odsetek pytań z egzaminu, którym bot przypisał właściwą sprawę. | `src/eval_cascade.py` |
| **Macro-F1** | Średnia jakość liczona osobno dla każdej sprawy, a potem uśredniona. Dzięki temu rzadkie sprawy liczą się tak samo jak częste, a wynik nie jest zawyżony przez kilka popularnych. | `src/eval_cascade.py` |
| **Wykrywalność (recall)** | Ile pytań danego typu bot faktycznie wyłapał. 85 % dla pytań spoza zakresu = z każdych 100 takich pytań 85 rozpoznane. | `data/eval/` |

## Uruchomienie

### Co trzeba mieć

| Narzędzie | Po co | Skąd |
|---|---|---|
| Python 3.12 lub nowszy i [uv](https://github.com/astral-sh/uv) | uruchomienie kodu i instalacja zależności | `pip install uv` albo instalator ze strony uv |
| Docker | baza wektorowa Qdrant działa w kontenerze | Docker Desktop (Windows/macOS) lub pakiet `docker` (Linux) |
| [Ollama](https://ollama.com) | uruchamia model językowy lokalnie | instalator ze strony |
| ok. 6 GB miejsca na dysku i 8 GB RAM | model qwen2.5:7b to ok. 4,7 GB; na samym procesorze potrzebuje ok. 8 GB RAM, na karcie graficznej ok. 6 GB VRAM | — |
| **Własna dokumentacja** | bot nie ma wbudowanej bazy wiedzy; bez artykułów nie ma na czym odpowiadać | sekcja „Własna dokumentacja” niżej |

Działa na Linuksie, macOS i Windows (na Windows najwygodniej w WSL2).

### Krok po kroku

**1. Pobierz repozytorium i zależności**

```bash
git clone https://github.com/aleksykremza-dev/kremzapay-support-bot.git
cd kremzapay-support-bot
uv sync
```

`uv sync` tworzy środowisko `.venv` i instaluje wszystko z `pyproject.toml`.
Trwa minutę–dwie.

**2. Przygotuj dokumentację**

Utwórz katalog `kb/pl/` (i `kb/en/`, jeśli masz wersję angielską) i wrzuć do
niego artykuły w formacie opisanym w sekcji „Własna dokumentacja”. Na start
wystarczy kilkanaście artykułów.

**3. Uruchom bazę wektorową**

```bash
docker compose up -d
```

Qdrant startuje w tle i słucha na porcie 6335. Sprawdzenie:
`curl http://localhost:6335/collections` powinno zwrócić JSON, a nie błąd
połączenia. Dane bazy lądują w katalogu `qdrant_data/`.

**4. Pobierz i uruchom model**

```bash
ollama pull qwen2.5:7b-instruct
ollama serve
```

Pierwsze `pull` ściąga ok. 4,7 GB. `ollama serve` zostaw działające w osobnym
oknie (na Windows/macOS Ollama zwykle startuje sama jako usługa i ten krok
można pominąć). Sprawdzenie: `curl http://localhost:11434/api/tags` pokaże
listę modeli.

**5. Zbuduj indeks dokumentacji**

```bash
uv run python src/ingest.py
```

Skrypt czyta artykuły z `kb/`, tnie je na fragmenty, liczy dla nich embeddingi
i zapisuje do Qdrant. Przy pierwszym uruchomieniu pobiera model embeddingów
(ok. 200 MB). Na końcu wypisuje `Articles found: N` i `Chunks produced: M`.
Ponowne uruchomienie kasuje indeks i buduje go od zera, więc można je powtarzać
po każdej zmianie w artykułach.

**6. Uruchom bota**

```bash
uv run uvicorn api:app --app-dir src --port 8020
```

Po komunikacie `Application startup complete` otwórz:

- http://localhost:8020 — czat
- http://localhost:8020/dashboard — panel z przebiegiem każdej rozmowy
- http://localhost:8020/api/stats — te same dane jako JSON

Pierwsze pytanie wymagające modelu może potrwać dłużej (model ładuje się do
pamięci), kolejne są szybsze.

### Konfiguracja

Plik `.env` jest opcjonalny. Bez niego kod używa wartości domyślnych, takich
samych jak w `.env.example`:

```
OLLAMA_URL=http://localhost:11434
ANSWER_MODEL=qwen2.5:7b-instruct
QDRANT_URL=http://localhost:6335
```

Zmień je, gdy Ollama lub Qdrant działają na innej maszynie albo chcesz
podstawić inny model.

### Własna dokumentacja

**Format artykułu.** Każdy artykuł to plik Markdown w `kb/<język>/`,
z nagłówkiem:

```
---
id: KB-030
category: refunds
lang: pl
title: Gdzie jest mój zwrot
---

# Gdzie jest mój zwrot

Treść artykułu...
```

Pola: `id` unikalny numer (bot cytuje go w odpowiedzi), `category` jedna
z kategorii z pliku `data/taxonomy.json` (bot filtruje wyszukiwanie po
kategorii, więc nazwy muszą się zgadzać), `lang` to `pl` lub `en`, `title`
widoczny tytuł. Po zmianach: `uv run python src/ingest.py`.

**Jeśli Twój temat to płatności**, przykładowa lista spraw i kategorii w `data/`
może pasować od razu: przejrzyj `data/taxonomy.json`, użyj tych samych nazw
kategorii w artykułach i wystarczy dodać dokumentację.

**Jeśli temat jest inny**, oprócz artykułów trzeba przerobić to, co uczy bota
rozpoznawać sprawy:

| Co | Gdzie | Uwagi |
|---|---|---|
| Lista spraw i kategorii | `data/taxonomy/part-*.json`, potem `uv run python src/merge_taxonomy.py` | każda sprawa: `id`, `category`, `definition`, kilka `examples` |
| Przykłady pytań dla kNN | `data/corpus/corpus-*.json` | format `{"cases": [{"q": "...", "intent": "...", "lang": "pl"}]}`; po zmianie skasuj `data/cache/`, żeby indeks przykładów przebudował się |
| Reguły o konkurencji i tematach spoza zakresu | `src/rules.py`, listy `COMPETITORS` i `TAX` | reguły o atakach i oszustwach (`INJECTION`, `FRAUD`) są uniwersalne |
| Ton odpowiedzi i nazwa firmy | `src/answer_gen.py`, prompt na początku pliku | |
| Egzamin | `data/goldset/` | własne pytania z poprawną sprawą, żeby mierzyć jakość na swoim temacie |

Kolejność: lista spraw → przykłady → artykuły → `ingest` → reguły → test na
kilku pytaniach → dopiero potem egzamin.

### Testy i ewaluacja

```bash
uv run pytest                          # 41 testów jednostkowych, bez Dockera i modelu, kilka sekund
uv run python src/eval_cascade.py      # egzamin na zestawie z data/goldset, wymaga Qdrant i Ollama; 288 pytań to ok. 45 min na CPU
```

### Zatrzymanie

`Ctrl+C` w oknie z uvicorn, potem `docker compose down` (dane w `qdrant_data/`
zostają).

Koszty użycia modeli w porównaniu z usługami chmurowymi:
[docs/ECONOMICS.md](docs/ECONOMICS.md).
