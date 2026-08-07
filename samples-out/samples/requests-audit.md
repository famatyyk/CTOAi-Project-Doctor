# Project Doctor — raport statyczny

- **Projekt:** pd-sample-requests
- **Klient:** nie podano
- **ID audytu:** `PD-20260807-01DD8397`
- **Wygenerowano:** 2026-08-07T07:03:34Z
- **Pokrycie:** partial

## Wynik

**18/100 — podwyższone ryzyko**

100 minus jawne kary za statyczne znaleziska; wynik nie jest certyfikatem bezpieczeństwa.

| Krytyczne | Wysokie | Średnie | Niskie | Informacyjne |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 2 | 4 | 8 | 5 |

## Zakres skanu

- Pliki: 129 (2262084 bajtów)
- Tekstowo przeanalizowane pliki: 92
- Pliki tekstowe pominięte z powodu limitu lub odczytu: 0
- Limit plików: 10000; limit łączny: 262144000 bajtów; limit pliku: 2097152 bajtów.

Pominięte elementy:
- excluded_directory: 1
- file_size_limit: 1

## Inwentaryzacja

- Pliki źródłowe: 37
- Wykryte pliki testowe: 42 (nie uruchamiano)
- Linie kodu źródłowego: 12068
- Języki: Python: 37

## Priorytety naprawy

1. **HIGH: Znaleziono odczyt pickle** — Nie ładuj pickle z niezaufanego źródła; użyj bezpieczniejszego formatu danych.
2. **HIGH: Znaleziono pliki mogące zawierać poświadczenia** — Nie wersjonuj sekretów. Przenieś je do bezpiecznego magazynu lub lokalnego pliku ignorowanego przez Git.
3. **MEDIUM: Znaleziono adres HTTP bez TLS** — Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej.
4. **MEDIUM: Znaleziono adres HTTP bez TLS** — Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej.
5. **MEDIUM: Znaleziono adres HTTP bez TLS** — Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej.

## Wszystkie znaleziska

| Priorytet | Kategoria | Znalezisko | Dowód | Zalecenie |
| --- | --- | --- | --- | --- |
| high | bezpieczeństwo | Znaleziono odczyt pickle | tests/test_requests.py | Nie ładuj pickle z niezaufanego źródła; użyj bezpieczniejszego formatu danych. |
| high | bezpieczeństwo | Znaleziono pliki mogące zawierać poświadczenia | tests/certs/expired/ca/ca-private.key, tests/certs/expired/server/server.key, tests/certs/expired/server/server.pem, tests/certs/mtls/client/client.key, tests/certs/mtls/client/client.pem, tests/certs/valid/server/server.key, tests/certs/valid/server/server.pem | Nie wersjonuj sekretów. Przenieś je do bezpiecznego magazynu lub lokalnego pliku ignorowanego przez Git. |
| medium | bezpieczeństwo | Znaleziono adres HTTP bez TLS | src/requests/sessions.py | Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej. |
| medium | bezpieczeństwo | Znaleziono adres HTTP bez TLS | tests/test_adapters.py | Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej. |
| medium | bezpieczeństwo | Znaleziono adres HTTP bez TLS | tests/test_requests.py | Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej. |
| medium | bezpieczeństwo | Znaleziono adres HTTP bez TLS | tests/test_utils.py | Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej. |
| low | dokumentacja | Brak wskazówek dla współtwórców | — | Dodaj krótkie zasady instalacji, testów i zgłaszania zmian. |
| low | jakość kodu | Bardzo duży plik źródłowy | src/requests/adapters.py | Rozważ podział pliku na mniejsze moduły z wyraźną odpowiedzialnością. |
| low | jakość kodu | Bardzo duży plik źródłowy | src/requests/models.py | Rozważ podział pliku na mniejsze moduły z wyraźną odpowiedzialnością. |
| low | jakość kodu | Bardzo duży plik źródłowy | src/requests/sessions.py | Rozważ podział pliku na mniejsze moduły z wyraźną odpowiedzialnością. |
| low | jakość kodu | Bardzo duży plik źródłowy | src/requests/utils.py | Rozważ podział pliku na mniejsze moduły z wyraźną odpowiedzialnością. |
| low | jakość kodu | Bardzo duży plik źródłowy | tests/test_requests.py | Rozważ podział pliku na mniejsze moduły z wyraźną odpowiedzialnością. |
| low | jakość kodu | Bardzo duży plik źródłowy | tests/test_utils.py | Rozważ podział pliku na mniejsze moduły z wyraźną odpowiedzialnością. |
| low | zależności | Brak pliku blokady zależności | — | Dodaj lockfile albo używaj przypiętych wersji, aby ograniczyć różnice między środowiskami. |
| info | jakość kodu | Pozostały oznaczenia TODO/FIXME | src/requests/_types.py | Przejrzyj oznaczenia i przekształć istotne zadania w elementy backlogu. |
| info | jakość kodu | Pozostały oznaczenia TODO/FIXME | src/requests/adapters.py | Przejrzyj oznaczenia i przekształć istotne zadania w elementy backlogu. |
| info | jakość kodu | Pozostały oznaczenia TODO/FIXME | src/requests/hooks.py | Przejrzyj oznaczenia i przekształć istotne zadania w elementy backlogu. |
| info | jakość kodu | Pozostały oznaczenia TODO/FIXME | src/requests/models.py | Przejrzyj oznaczenia i przekształć istotne zadania w elementy backlogu. |
| info | jakość kodu | Pozostały oznaczenia TODO/FIXME | tests/test_testserver.py | Przejrzyj oznaczenia i przekształć istotne zadania w elementy backlogu. |

## Kontrole

- **docs.readme** (pass): Znaleziono główny README. Dowód: README.md
- **docs.license** (pass): Znaleziono wymagany artefakt. Dowód: LICENSE
- **docs.changelog** (pass): Znaleziono wymagany artefakt. Dowód: HISTORY.md
- **docs.contributing** (warn): Brak wskazówek dla współtwórców Dowód: —
- **hygiene.gitignore** (pass): Znaleziono wymagany artefakt. Dowód: .gitignore
- **dependencies.manifest** (pass): Znaleziono manifest zależności. Dowód: pyproject.toml, docs/requirements.txt, setup.py
- **dependencies.lock** (warn): Nie znaleziono pliku blokady zależności. Dowód: —
- **tests.discovered** (not_run): Znaleziono pliki testowe; nie zostały uruchomione przez Project Doctor. Dowód: tests/__init__.py, tests/compat.py, tests/conftest.py, tests/test_adapters.py, tests/test_help.py, tests/test_hooks.py, tests/test_lowlevel.py, tests/test_packages.py, tests/test_requests.py, tests/test_structures.py, tests/test_testserver.py, tests/test_utils.py, tests/utils.py, tests/testserver/__init__.py, tests/testserver/server.py, tests/certs/README.md, tests/certs/valid/ca, tests/certs/valid/server/cert.cnf, tests/certs/valid/server/Makefile, tests/certs/valid/server/server.csr
- **ci.workflow** (pass): Znaleziono workflow CI. Dowód: .github/workflows/zizmor.yml, .github/workflows/lock-issues.yml, .github/workflows/lint.yml, .github/workflows/run-tests.yml, .github/workflows/codeql-analysis.yml, .github/workflows/close-issues.yml, .github/workflows/typecheck.yml, .github/workflows/publish.yml
- **repository.git** (pass): Katalog wygląda na repozytorium Git. Dowód: —
- **execution.tests** (not_run): Testy, instalacja zależności i kod projektu nie były uruchamiane. Dowód: —

## Ograniczenia

- Audyt jest statyczny: nie uruchamia kodu, testów, instalatorów ani poleceń Git klienta.
- Raport nie jest pentestem ani gwarancją braku podatności.
- Zawartość plików z nazwami sugerującymi sekret nie jest odczytywana; raport zawiera wyłącznie względne ścieżki i typy znalezisk.
- Testy są tylko wykrywane, nigdy uruchamiane. Wynik 'not_run' nie oznacza powodzenia testów.
