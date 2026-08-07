# Project Doctor — raport statyczny

- **Projekt:** demo_repository
- **Klient:** Demo klienta
- **ID audytu:** `PD-20260720-517C4B1C`
- **Wygenerowano:** 2026-07-20T22:41:44Z
- **Pokrycie:** complete

## Wynik

**45/100 — podwyższone ryzyko**

100 minus jawne kary za statyczne znaleziska; wynik nie jest certyfikatem bezpieczeństwa.

| Krytyczne | Wysokie | Średnie | Niskie | Informacyjne |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 2 | 1 | 6 | 1 |

## Zakres skanu

- Pliki: 4 (555 bajtów)
- Tekstowo przeanalizowane pliki: 3
- Pliki tekstowe pominięte z powodu limitu lub odczytu: 0
- Limit plików: 10000; limit łączny: 262144000 bajtów; limit pliku: 2097152 bajtów.

## Inwentaryzacja

- Pliki źródłowe: 1
- Wykryte pliki testowe: 0 (nie uruchamiano)
- Linie kodu źródłowego: 19
- Języki: Python: 1

## Priorytety naprawy

1. **HIGH: Znaleziono subprocess z shell=True** — Przekazuj listę argumentów i unikaj shell=True dla danych, które mogą pochodzić od użytkownika.
2. **HIGH: Nie znaleziono testów** — Dodaj przynajmniej testy krytycznych funkcji i konfiguracji.
3. **MEDIUM: Znaleziono adres HTTP bez TLS** — Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej.
4. **LOW: Ogólny except utrudnia diagnozowanie błędów** — Łap jawne wyjątki i loguj przyczynę błędu.
5. **LOW: Brak changelogu** — Dodaj prosty changelog, aby klient wiedział, co zmieniło się między wydaniami.

## Wszystkie znaleziska

| Priorytet | Kategoria | Znalezisko | Dowód | Zalecenie |
| --- | --- | --- | --- | --- |
| high | bezpieczeństwo | Znaleziono subprocess z shell=True | src/service.py | Przekazuj listę argumentów i unikaj shell=True dla danych, które mogą pochodzić od użytkownika. |
| high | testy | Nie znaleziono testów | — | Dodaj przynajmniej testy krytycznych funkcji i konfiguracji. |
| medium | bezpieczeństwo | Znaleziono adres HTTP bez TLS | src/service.py | Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej. |
| low | bezpieczeństwo | Ogólny except utrudnia diagnozowanie błędów | src/service.py | Łap jawne wyjątki i loguj przyczynę błędu. |
| low | dokumentacja | Brak changelogu | — | Dodaj prosty changelog, aby klient wiedział, co zmieniło się między wydaniami. |
| low | dokumentacja | Brak wskazówek dla współtwórców | — | Dodaj krótkie zasady instalacji, testów i zgłaszania zmian. |
| low | dokumentacja | Brak jednoznacznej licencji | — | Dodaj licencję lub jasno określ warunki użycia kodu. |
| low | dostarczanie | Brak widocznego workflow CI | — | Dodaj minimalny workflow CI, który uruchamia testy przy zmianach. |
| low | zależności | Brak pliku blokady zależności | — | Dodaj lockfile albo używaj przypiętych wersji, aby ograniczyć różnice między środowiskami. |
| info | jakość kodu | Pozostały oznaczenia TODO/FIXME | src/service.py | Przejrzyj oznaczenia i przekształć istotne zadania w elementy backlogu. |

## Kontrole

- **docs.readme** (pass): Znaleziono główny README. Dowód: README.md
- **docs.license** (warn): Brak jednoznacznej licencji Dowód: —
- **docs.changelog** (warn): Brak changelogu Dowód: —
- **docs.contributing** (warn): Brak wskazówek dla współtwórców Dowód: —
- **hygiene.gitignore** (pass): Znaleziono wymagany artefakt. Dowód: .gitignore
- **dependencies.manifest** (pass): Znaleziono manifest zależności. Dowód: requirements.txt
- **dependencies.lock** (warn): Nie znaleziono pliku blokady zależności. Dowód: —
- **tests.discovered** (warn): Nie znaleziono rozpoznawalnych plików testowych. Dowód: —
- **ci.workflow** (warn): Nie znaleziono workflow CI. Dowód: —
- **repository.git** (not_run): Nie potwierdzono metadanych Git w przekazanym katalogu. Dowód: —
- **execution.tests** (not_run): Testy, instalacja zależności i kod projektu nie były uruchamiane. Dowód: —

## Ograniczenia

- Audyt jest statyczny: nie uruchamia kodu, testów, instalatorów ani poleceń Git klienta.
- Raport nie jest pentestem ani gwarancją braku podatności.
- Zawartość plików z nazwami sugerującymi sekret nie jest odczytywana; raport zawiera wyłącznie względne ścieżki i typy znalezisk.
- Testy są tylko wykrywane, nigdy uruchamiane. Wynik 'not_run' nie oznacza powodzenia testów.
