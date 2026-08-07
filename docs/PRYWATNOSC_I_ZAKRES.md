# Project Doctor — prywatność, bezpieczeństwo i zakres MVP

## Co narzędzie robi

Project Doctor czyta strukturę i wybrane pliki tekstowe lokalnego repozytorium,
aby utworzyć raport statyczny. Zapisuje raport wyłącznie do osobnego katalogu
podanego przez operatora.

## Czego narzędzie celowo nie robi

- nie wykonuje kodu klienta;
- nie importuje modułów klienta;
- nie uruchamia `pytest`, Git, linterów, instalatorów ani sieci;
- nie podąża za symlinkami, junctions ani innymi punktami ponownej analizy;
- nie odczytuje plików o nazwach sugerujących sekret, np. `.env`, `id_rsa`,
  `.pem`, `.key` lub `.pfx`;
- nie zapisuje wartości potencjalnych sekretów do raportu.

## Dane w raporcie

Raport może zawierać tylko:

- nazwę katalogu projektu, nie jego pełną ścieżkę;
- względne ścieżki plików;
- typ statycznego znaleziska, np. `credential_assignment`;
- liczniki, statusy kontroli i zalecenia.

Nie powinien zawierać treści kodu, tokenów, kluczy ani danych logowania. Przed
przekazaniem klientowi operator mimo to powinien przeczytać raport.

## Granice odpowiedzialności

Wynik to wskazówka techniczna, nie certyfikat bezpieczeństwa ani opinia prawna.
Każdą zmianę w kodzie i każde wykonanie testów trzeba zweryfikować w środowisku
kontrolowanym przez właściciela projektu.
