# Project Doctor — raport statyczny

- **Projekt:** demo_cmake
- **Klient:** nie podano
- **ID audytu:** `PD-20260808-193A6352`
- **Wygenerowano:** 2026-08-08T06:20:51Z
- **Pokrycie:** complete

## Wynik

**35/100 — podwyższone ryzyko**

100 minus jawne kary za statyczne znaleziska; wynik nie jest certyfikatem bezpieczeństwa.

| Krytyczne | Wysokie | Średnie | Niskie | Informacyjne |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 2 | 2 | 7 | 0 |

## Zakres skanu

- Pliki: 1 (246 bajtów)
- Tekstowo przeanalizowane pliki: 1
- Pliki tekstowe pominięte z powodu limitu lub odczytu: 0
- Limit plików: 10000; limit łączny: 262144000 bajtów; limit pliku: 2097152 bajtów.

## Inwentaryzacja

- Pliki źródłowe: 0
- Wykryte pliki testowe: 0 (nie uruchamiano)
- Linie kodu źródłowego: 0
- Języki: C++ build: 1

## Priorytety naprawy

1. **HIGH: Brak głównego README** — Dodaj README z opisem produktu, konfiguracją i podstawową instrukcją uruchomienia.
2. **HIGH: Nie znaleziono testów** — Dodaj przynajmniej testy krytycznych funkcji i konfiguracji.
3. **MEDIUM: Brak .gitignore** — Dodaj .gitignore dla sekretów, cache, środowisk wirtualnych i artefaktów builda.
4. **MEDIUM: Brak manifestu zależności** — Dodaj śledzony manifest zależności, aby instalacja była powtarzalna.
5. **LOW: Użyto globalnego include_directories()** — Preferuj target_include_directories(&lt;tgt&gt; PRIVATE/PUBLIC) — izoluj zależności.

## Wszystkie znaleziska

| Priorytet | Kategoria | Znalezisko | Dowód | Zalecenie |
| --- | --- | --- | --- | --- |
| high | dokumentacja | Brak głównego README | — | Dodaj README z opisem produktu, konfiguracją i podstawową instrukcją uruchomienia. |
| high | testy | Nie znaleziono testów | — | Dodaj przynajmniej testy krytycznych funkcji i konfiguracji. |
| medium | higiena repozytorium | Brak .gitignore | — | Dodaj .gitignore dla sekretów, cache, środowisk wirtualnych i artefaktów builda. |
| medium | zależności | Brak manifestu zależności | — | Dodaj śledzony manifest zależności, aby instalacja była powtarzalna. |
| low | build C++ | Użyto globalnego include_directories() | CMakeLists.txt | Preferuj target_include_directories(&lt;tgt&gt; PRIVATE/PUBLIC) — izoluj zależności. |
| low | build C++ | Ustawiono globalne CMAKE_CXX_STANDARD bez target_compile_features | CMakeLists.txt | Użyj target_compile_features(&lt;tgt&gt; PRIVATE cxx_std_17) dla jawnych wymagań per-target. |
| low | build C++ | Hardkodowane -O3 w add_compile_options | CMakeLists.txt | Nie wymuszaj optymalizacji globalnie; steruj przez CMAKE_BUILD_TYPE / presets. |
| low | dokumentacja | Brak changelogu | — | Dodaj prosty changelog, aby klient wiedział, co zmieniło się między wydaniami. |
| low | dokumentacja | Brak wskazówek dla współtwórców | — | Dodaj krótkie zasady instalacji, testów i zgłaszania zmian. |
| low | dokumentacja | Brak jednoznacznej licencji | — | Dodaj licencję lub jasno określ warunki użycia kodu. |
| low | dostarczanie | Brak widocznego workflow CI | — | Dodaj minimalny workflow CI, który uruchamia testy przy zmianach. |

## Kontrole

- **docs.readme** (warn): Brak głównego README. Dowód: —
- **docs.license** (warn): Brak jednoznacznej licencji Dowód: —
- **docs.changelog** (warn): Brak changelogu Dowód: —
- **docs.contributing** (warn): Brak wskazówek dla współtwórców Dowód: —
- **hygiene.gitignore** (warn): Brak .gitignore Dowód: —
- **dependencies.manifest** (warn): Nie znaleziono manifestu zależności. Dowód: —
- **tests.discovered** (warn): Nie znaleziono rozpoznawalnych plików testowych. Dowód: —
- **ci.workflow** (warn): Nie znaleziono workflow CI. Dowód: —
- **repository.git** (not_run): Nie potwierdzono metadanych Git w przekazanym katalogu. Dowód: —
- **execution.tests** (not_run): Testy, instalacja zależności i kod projektu nie były uruchamiane. Dowód: —

## Ograniczenia

- Audyt jest statyczny: nie uruchamia kodu, testów, instalatorów ani poleceń Git klienta.
- Raport nie jest pentestem ani gwarancją braku podatności.
- Zawartość plików z nazwami sugerującymi sekret nie jest odczytywana; raport zawiera wyłącznie względne ścieżki i typy znalezisk.
- Testy są tylko wykrywane, nigdy uruchamiane. Wynik 'not_run' nie oznacza powodzenia testów.
