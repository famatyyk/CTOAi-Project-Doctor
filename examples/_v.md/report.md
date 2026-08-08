# Project Doctor — raport statyczny

- **Projekt:** demo_cpp
- **Klient:** nie podano
- **ID audytu:** `PD-20260807-758EA2D4`
- **Wygenerowano:** 2026-08-07T23:20:53Z
- **Pokrycie:** complete

## Wynik

**16/100 — podwyższone ryzyko**

100 minus jawne kary za statyczne znaleziska; wynik nie jest certyfikatem bezpieczeństwa.

| Krytyczne | Wysokie | Średnie | Niskie | Informacyjne |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 3 | 3 | 6 | 0 |

## Zakres skanu

- Pliki: 1 (360 bajtów)
- Tekstowo przeanalizowane pliki: 1
- Pliki tekstowe pominięte z powodu limitu lub odczytu: 0
- Limit plików: 10000; limit łączny: 262144000 bajtów; limit pliku: 2097152 bajtów.

## Inwentaryzacja

- Pliki źródłowe: 1
- Wykryte pliki testowe: 0 (nie uruchamiano)
- Linie kodu źródłowego: 13
- Języki: C++: 2

## Priorytety naprawy

1. **HIGH: Brak głównego README** — Dodaj README z opisem produktu, konfiguracją i podstawową instrukcją uruchomienia.
2. **HIGH: Funkcja C uznawana za niebezpieczną (strcpy/strcat/gets/scanf/sprintf)** — Użyj bezpiecznych odpowiedników: std::string, std::format, snprintf z kontrolą rozmiaru.
3. **HIGH: Nie znaleziono testów** — Dodaj przynajmniej testy krytycznych funkcji i konfiguracji.
4. **MEDIUM: Brak .gitignore** — Dodaj .gitignore dla sekretów, cache, środowisk wirtualnych i artefaktów builda.
5. **MEDIUM: Surowe \`new\` bez widocznego zarządzania pamięcią** — Użyj std::unique_ptr / std::shared_ptr zamiast surowego new, by uniknąć wycieków.

## Wszystkie znaleziska

| Priorytet | Kategoria | Znalezisko | Dowód | Zalecenie |
| --- | --- | --- | --- | --- |
| high | dokumentacja | Brak głównego README | — | Dodaj README z opisem produktu, konfiguracją i podstawową instrukcją uruchomienia. |
| high | jakość kodu C++ | Funkcja C uznawana za niebezpieczną (strcpy/strcat/gets/scanf/sprintf) | main.cpp | Użyj bezpiecznych odpowiedników: std::string, std::format, snprintf z kontrolą rozmiaru. |
| high | testy | Nie znaleziono testów | — | Dodaj przynajmniej testy krytycznych funkcji i konfiguracji. |
| medium | higiena repozytorium | Brak .gitignore | — | Dodaj .gitignore dla sekretów, cache, środowisk wirtualnych i artefaktów builda. |
| medium | jakość kodu C++ | Surowe \`new\` bez widocznego zarządzania pamięcią | main.cpp | Użyj std::unique_ptr / std::shared_ptr zamiast surowego new, by uniknąć wycieków. |
| medium | zależności | Brak manifestu zależności | — | Dodaj śledzony manifest zależności, aby instalacja była powtarzalna. |
| low | dokumentacja | Brak changelogu | — | Dodaj prosty changelog, aby klient wiedział, co zmieniło się między wydaniami. |
| low | dokumentacja | Brak wskazówek dla współtwórców | — | Dodaj krótkie zasady instalacji, testów i zgłaszania zmian. |
| low | dokumentacja | Brak jednoznacznej licencji | — | Dodaj licencję lub jasno określ warunki użycia kodu. |
| low | dostarczanie | Brak widocznego workflow CI | — | Dodaj minimalny workflow CI, który uruchamia testy przy zmianach. |
| low | jakość kodu C++ | Rzutowanie w stylu C | main.cpp | Wolaj statycznych rzutowań C++ (static_cast / const_cast) dla lepszej czytelności i bezpieczeństwa typów. |
| low | jakość kodu C++ | Użyto instrukcji goto | main.cpp | Unikaj goto; zamiast tego użyj pętli, funkcji lub std::expected do sterowania przepływem. |

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
