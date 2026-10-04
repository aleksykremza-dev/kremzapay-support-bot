# Architektura

Jak działa silnik krok po kroku, ile kosztuje jedno pytanie, gdzie są ograniczenia i który plik za co odpowiada.

[Wróć do README](../README.md)

## Jak to działa

Pytanie z czatu przechodzi przez kolejne etapy; każdy ma swój plik w `src/`.

1. **Maskowanie danych osobowych** (`pii.py`). Numer karty, IBAN, PESEL, telefon
   i e-mail stają się etykietami `<CARD_1>`, `<IBAN_1>`, `<PESEL_1>`, `<PHONE_1>`,
   `<EMAIL_1>` zanim tekst zobaczy model i zanim trafi do bazy SQLite.
2. **L0, reguły** (`rules.py`). Wzorce tekstowe bez modelu: manipulacja botem
   i prośby o pomoc w oszustwie -> odmowa (`unsafe_refuse`); inne produkty
   i podatki (w tym prawo VAT) -> `redirect`; prośba o cudzą pracę (napisz umowę,
   esej, wiersz, kod) -> `redirect`; wyraźna prośba o człowieka -> `handoff`.
3. **L1, klasyfikator tematu** (`knn_router.py`). Pytanie zamienia się w wektor
   modelem `intfloat/multilingual-e5-large` (`ROUTER_EMBED_MODEL`, prefiks
   `query: `), a regresja logistyczna (`CLF_C` 64) wytrenowana na wektorach 5412
   pytań korpusu daje prawdopodobieństwo każdej z 52 intencji i 4 klas
   specjalnych. Najlepsza etykieta z prawdopodobieństwem >= `P_ACCEPT` (0,3) jest
   przyjęta bez modelu językowego, z pewnością `high` przy >= `CONF_HIGH` (0,7),
   inaczej `medium`. Wektory korpusu i wagi klasyfikatora leżą gotowe
   w `data/index/` (klucz: model embeddingów, `CLF_C`, skrót korpusu).
4. **L2, klasyfikator LLM** (`llm_classifier.py`). Gdy L1 nie jest pewny (także
   przy podobieństwie do najbliższego pytania korpusu < `T_OOS`, 0,45), lokalny
   model jednym wywołaniem najpierw ustala, kto pisze (kupujący w sklepie czy
   sprzedawca), potem wybiera etykietę spośród `LLM_CANDIDATES` (5) najbardziej
   prawdopodobnych etykiet L1 (z definicjami), klas specjalnych albo
   `other_in_scope`; etykieta spoza tej listy daje `other_in_scope` z pewnością
   `low`; zwraca JSON z pewnością `high|medium|low` i `wants_human`.
5. **Decyzja** (`cascade.py`). Gdy L1 postawił `out_of_scope` na pierwszym
   miejscu, a model wybrał `other_in_scope`, wynik to `out_of_scope`. Klasy
   specjalne dają akcję: small talk -> `chitchat_reply`, treść niebezpieczna ->
   `unsafe_refuse`, poza zakresem -> `redirect`, temat w zakresie bez intencji ->
   `ticket`; `wants_human` -> `handoff`; pewność `low` -> `clarify` (dopytanie).
   Inaczej najlepszy fragment z Qdrant musi mieć wynik >= `RETRIEVAL_OK` (0,45),
   w przeciwnym razie `ticket`.
6. **Odpowiedź** (`answer_gen.py`). Wyszukiwanie z filtrem po kategorii intencji
   (przy mniej niż 2 trafieniach filtr jest zdejmowany); jeśli żaden fragment nie
   ma wyniku >= `RETRIEVAL_OK`, wyszukiwanie idzie od razu po całej bazie.
   3 najlepsze fragmenty (`TOP_N`) idą do promptu; model odpowiada tylko na ich
   podstawie i kończy linią `Źródło: KB-###` (`Source:` po angielsku; źródło jest
   rozpoznawane także na końcu ostatniego akapitu). Jeśli we fragmentach nie ma
   odpowiedzi, model zwraca `NO_ANSWER`: wtedy jedno ponowne wyszukiwanie w całej
   bazie i ponowne wywołanie modelu, a przy kolejnym `NO_ANSWER` zgłoszenie
   (`no_knowledge`).
7. **Sędzia** (`judge.py`). Drugie wywołanie modelu sprawdza dwie rzeczy: czy
   fragmenty odpowiadają na zadane pytanie, a nie tylko na pokrewny temat, i czy
   każde twierdzenie odpowiedzi ma w nich pokrycie (`yes`/`no`). Sędzia widzi tylko
   fragmenty wskazane w linii źródła. Przy `no` odpowiedź nie wychodzi, zamiast
   niej powstaje zgłoszenie (`generation_not_grounded`).

Błąd rozpoznania kończy się więc dopytaniem, zgłoszeniem albo przekazaniem
człowiekowi, nie zmyśloną odpowiedzią. Każdy etap dopisuje wynik do jednego
obiektu `TurnState` (czasy warstw, reguły, L1 pod kluczem `knn`, LLM, retrieval, decyzja), który
trafia do SQLite razem z wiadomością i jest widoczny na `/dashboard`. Historia
sesji jest zapisywana, ale każde pytanie jest rozpatrywane osobno. Język
(`pl`/`en`) jest wykrywany po polskich znakach i liście typowych polskich słów.

| Termin | Co to jest | Gdzie |
|---|---|---|
| Embeddingi | wektory liczb: teksty o podobnym znaczeniu są blisko siebie; jeden model dla pl i en; temat: `ROUTER_EMBED_MODEL` (`multilingual-e5-large`), wyszukiwanie w bazie: `EMBED_MODEL` (`paraphrase-multilingual-MiniLM-L12-v2`), oba przez fastembed | `knn_router.py`, `search.py` |
| Regresja logistyczna | klasyfikator liniowy (scikit-learn) na wektorach korpusu; daje prawdopodobieństwo każdej etykiety | `knn_router.py`, `data/index/` |
| Progi | `CLF_C`, `P_ACCEPT`, `T_OOS`, `LLM_CANDIDATES`, `RETRIEVAL_OK`, `CONF_HIGH`, `TOP_K`, `TOP_N`, `CHUNK_SIZE`, `MIN_ACCURACY` | `config.py` |
| Klient Ollama | jedno miejsce wywołań modelu: timeout, powtórka, `LLMUnavailable`, `LLMBadOutput` | `llm.py` |
| Taksonomia | intencje z kategorią i definicją oraz klasy specjalne; wczytywana raz | `taxonomy.py`, `data/taxonomy.json` |
| Korpus i gold set | pytania z etykietą do trenowania L1 (gotowy indeks w `data/index/`, przy zmianie korpusu albo modelu nowy w `data/cache/`, `make router-index` zapisuje go w `data/index/`); pytania egzaminacyjne do liczenia trafności i macro-F1, rozłączne z korpusem | `data/corpus/`, `data/goldset/`, `eval_cascade.py` |

## Koszty

Modele działają lokalnie, więc koszt to sprzęt i prąd, nie tokeny. Wyjście
modelu jest ograniczone (`num_predict`): 220 tokenów na klasyfikator, 400 na odpowiedź, 5 na sędziego; temperatura 0. Wywołania:

| Ścieżka | Wywołania modelu | Szacunek tokenów wejście / wyjście |
|---|---|---|
| reguły albo L1 z gotową akcją; L1 przyjęty, ale brak pokrycia w bazie | 0 | 0 |
| odpowiedź po L1 | odpowiedź + sędzia (2) | ok. 2 400 / 260 |
| odpowiedź po klasyfikatorze LLM | klasyfikator + odpowiedź + sędzia (3) | ok. 3 150 / 350 |
| zgłoszenie albo dopytanie po klasyfikatorze LLM | 1 | ok. 750 / 90 |
| odpowiedź po `NO_ANSWER` i ponownym wyszukiwaniu w całej bazie | do 4 (klasyfikator, odpowiedź, odpowiedź, sędzia) | ok. 4 700 / 600 |
| przekazanie człowiekowi i wiadomości w sesji `handoff` | 0 | 0 |

Szacunki wynikają z rozmiarów promptów tej kaskady (3 fragmenty po ok. 800
znaków w kontekście odpowiedzi) i są przybliżone; na modelu hostowanym
i rozliczanym za tokeny wyszłoby od kilku do kilkudziesięciu dolarów na 1000
pytań. Inny model w Ollama to zmiana `ANSWER_MODEL`; inny dostawca to `src/llm.py`.

## Ograniczenia

- Panel (`/dashboard`, `/api/stats`, `POST /api/tickets/{id}/close`) nie ma
  logowania: każdy, kto dotrze do portu 8020, widzi rozmowy i może zamykać
  zgłoszenia. Uruchamiaj go tylko lokalnie albo za własnym uwierzytelnianiem.
- Szybkość zależy od sprzętu: na GTX 1050 Ti 4 GB mediana odpowiedzi to 10,2 s
  (pomiar na zewnętrznej bazie 04.10.2026), a pojedyncze odpowiedzi trwają do
  około 35 s.
- Trafność klasyfikacji `accuracy_test` to 0,891 (192 pytania, których nie
  używano przy strojeniu); około 1 na 9 pytań trafia do złego tematu.
- Trafność (`make test-accuracy`) mierzy tylko rozpoznanie intencji i klasy;
  jakość tekstu odpowiedzi nie jest mierzona, jedyną kontrolą jest sędzia tak/nie.
- Model embeddingów, `CLF_C` i `P_ACCEPT` dobierano tylko na części dev gold setu
  (96 pytań) i walidacji krzyżowej na korpusie; na własnych danych progi
  w `config.py` trzeba dobrać od nowa.
- Model `multilingual-e5-large` zajmuje 2,24 GB na dysku i razem z modelem wyszukiwania około 2,3 GB RAM
  procesu; temat liczy się na CPU w około 0,1 s na pytanie.
- Próg `MIN_ACCURACY` (0,87) leży co najmniej 0,02 poniżej `accuracy_test` (0,891) jako zapas na
  przyszłe aktualizacje modelu, zależności i promptów; przy temperature 0 i stałym
  seed przebieg jest powtarzalny (dwa przebiegi 04.10 zgodne 288/288).
- Zgłoszenia nigdzie nie są dostarczane: tylko SQLite i panel.
- Jeden model (`ANSWER_MODEL`) obsługuje klasyfikację, odpowiedź i sędziego;
  nie ma zapasowego LLM, awaria Ollama oznacza 503 i zgłoszenie.
- Przepustowość ogranicza lokalny model: Ollama domyślnie obsługuje żądania po
  kolei, a na GTX 1050 Ti 4 GB `qwen2.5:7b-instruct` działa częściowo na CPU.
  Bez limitu przy 10 równoległych klientach mediana odpowiedzi wyniosła 114,5 s
  (pomiar 02.10.2026), dlatego `/chat` przyjmuje najwyżej `MAX_INFLIGHT` żądań
  naraz, a nadmiarowe po `QUEUE_TIMEOUT_S` dostają 503 ze zgłoszeniem `overloaded`.
  Na mocniejszym sprzęcie oba parametry można podnieść w `.env`.
- Tylko polski i angielski; inne języki są traktowane jak angielski.
- Filtr kategorii przy wyszukiwaniu działa tylko, gdy `category` w nagłówkach
  artykułów pokrywa się z kategoriami w `data/taxonomy.json`; przy rozjeździe
  wyszukiwanie po cichu wraca do wyników bez filtra.

## Mapa kodu

`make codemap` uruchamia `tools/codemap.py` i buduje `data/reports/codemap.json`:
dla każdej funkcji, klasy i metody w `src/` i `tools/` plik, zakres linii,
sygnatura i link do tych linii na GitHubie w bieżącym commicie. Moduły w `src/`:

| Moduł | Rola |
|---|---|
| `config.py` | ustawienia, progi i ścieżki (od katalogu repozytorium), odczyt `.env` |
| `llm.py` | jedyny klient Ollama: `generate`, `generate_json`, `ping`; timeout, powtórka, wyjątki |
| `taxonomy.py` | wczytanie `data/taxonomy.json` raz; słowniki intencja -> kategoria / definicja |
| `pii.py` | maskowanie danych osobowych przed modelem i przed zapisem |
| `rules.py` | warstwa 0: wzorce ataków, oszustw, innych produktów, podatków (w tym VAT), cudzej pracy, prośby o człowieka |
| `knn_router.py` | warstwa 1: embeddingi e5, regresja logistyczna na korpusie, gotowy indeks z `data/index/` albo `data/cache/`, kandydaci dla warstwy 2 |
| `llm_classifier.py` | warstwa 2: wybór etykiety z kandydatów L1 jednym wywołaniem modelu (najpierw kupujący czy sprzedawca), wynik w JSON |
| `search.py` | embedding pytania i zapytanie do Qdrant z opcjonalnym filtrem kategorii; `ping` |
| `cascade.py` | sklejenie warstw, wykrycie języka, decyzja, `TurnState` |
| `answer_gen.py` | prompt z fragmentami, odpowiedź ze źródłem, `NO_ANSWER` i jedno ponowne wyszukiwanie w całej bazie |
| `judge.py` | kontrola, czy fragmenty odpowiadają na pytanie i pokrywają każde twierdzenie |
| `store.py` | SQLite: sesje, wiadomości, zgłoszenia, kontakt tylko w zgłoszeniu, kolejka przekazań, statystyki dla panelu, migracja starszych baz |
| `api.py` | FastAPI: `/`, `/health`, `/chat`, `/dashboard`, `/api/stats`, `POST /api/tickets/{id}/close`, limit równoległych żądań, przekazanie człowiekowi, teksty odpowiedzi |
| `ingest.py` | wczytanie `kb/`, cięcie na fragmenty, embeddingi, zapis do Qdrant |
| `eval_cascade.py` | egzamin trafności na `data/goldset/`, raport JSON, kod 1 poniżej progu |
| `merge_taxonomy.py` | sklejenie `data/taxonomy/part-*.json` w `data/taxonomy.json` |
