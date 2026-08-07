# CTOAi Project Doctor

Lekki, niezależny produkt do statycznego przeglądu repozytoriów Python/AI.

Project Doctor powstał poza głównym repozytorium CTOAi celowo: ma być prostą,
sprzedawalną usługą, a nie kolejnym modułem w dużym laboratorium. Wersja MVP
przyjmuje lokalny katalog projektu i tworzy raport Markdown + JSON.

## Co sprawdza MVP

- strukturę repozytorium, pliki dokumentacji i podstawową higienę;
- manifesty oraz lockfile zależności;
- obecność testów i workflow CI — testów klienta **nie uruchamia**;
- potencjalne nazwy plików z sekretami oraz wzorce sekretów w kodzie, bez
  zapisywania wartości sekretu do raportu;
- statyczne błędy składni Python oraz kilka prostych sygnałów ryzyka:
  `eval`/`exec`, `pickle`, `shell=True`, ogólny `except` i HTTP bez TLS;
- liczbę plików, języki, rozmiar oraz granice pokrycia skanu.

Nie jest to pentest, skaner zależności ani gwarancja bezpieczeństwa. To
powtarzalna diagnoza startowa: co najpierw poprawić, zanim projekt będzie
rozwijany lub przekazany klientowi.

## Szybki start

W PowerShell:

```powershell
cd C:\Users\zycie\CTOAi-Project-Doctor
python -m project_doctor audit C:\sciezka\do\projektu --output C:\raporty\projekt-01 --client "Nazwa klienta"
```

Wynik trafi wyłącznie do katalogu podanego w `--output`:

- `report.md` — czytelny raport dla klienta;
- `report.json` — dane źródłowe do dalszego przetwarzania.

Katalog wyjściowy musi znajdować się **poza** badanym repozytorium i być pusty
(chyba że świadomie użyjesz `--force`). To chroni audytowany projekt przed
jakimkolwiek zapisem.

Opcjonalna instalacja lokalnej komendy:

```powershell
python -m pip install -e .
project-doctor audit C:\sciezka\do\projektu --output C:\raporty\projekt-01
```

## Bezpieczeństwo działania

Project Doctor nie używa `subprocess`, nie wywołuje Git, nie instaluje
zależności, nie importuje kodu klienta i nie uruchamia jego testów. Walker
plików nie podąża za symlinkami ani punktami ponownej analizy Windows. Skan ma
limity liczby plików, łącznego rozmiaru i rozmiaru pojedynczego pliku.

Pełne zasady: [Prywatność i zakres](docs/PRYWATNOSC_I_ZAKRES.md).

## Oferta gotowa do sprzedaży

- [Oferta Project Doctor po polsku](docs/OFERTA_PL.md)
- [Formularz dla klienta](docs/FORMULARZ_KLIENTA.md)
- [Przykładowe repozytorium](examples/demo_repository/)
- [Przykładowy raport](examples/demo_report/report.md) — generowany z demo

## Rozwój po pierwszych klientach

1. Zebrać 3–5 płatnych audytów ręcznie i poprawić jakość rekomendacji.
2. Dodać opcjonalne uruchamianie testów tylko w izolowanym sandboxie.
3. Dodać płatny miesięczny re-check oraz porównanie zmian między raportami.
4. Dopiero potem budować formularz webowy i panel klienta.

## Testowanie projektu

```powershell
python -m unittest discover -s tests -v
```

Licencja: [MIT](LICENSE).
