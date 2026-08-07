# Project Doctor — przykładowe audyty

To repozytorium pokazuje, co potrafi **CTOAi Project Doctor** — narzędzie do
statycznego przeglądu repozytoriów Python/AI. Każdy plik w `samples/` to raport
wygenerowany automatycznie z publicznego repozytorium.

> ⚠️ **Ważne:** Raporty te NIE są oceną bezpieczeństwa ani jakości projektu.
> Project Doctor to statyczny MVP — pokazuje, *co narzędzie wykrywa*
> (struktura, testy, CI, sekrety, ryzyka kodu). Traktuj to jako demo możliwości.

## Przykład: `requests`

[samples/requests-audit.md](samples/requests-audit.md) — audyt `psf/requests`
(najpopularniejszej biblioteki HTTP w Pythonie).

Wynik: **18/100** (wysokie kary za pickle, potencjalne sekrety, HTTP bez TLS
w przykładach/testach). To nie znaczy, że `requests` jest "złe" — znaczy, że
narzędzie zgłasza rzeczy, które w prawdziwym projekcie warto przejrzeć.

## Chcesz taki audyt dla swojego repo?

🚀 **Zamów audyt: https://ctoai-funnel.fly.dev/**

- **Cena: od 19 €**
- Raport Markdown + JSON w 24–48h
- Wynik Project Health 0–100, priorytety naprawy, przegląd testów/CI/sekretów,
  5 kroków naprawczych

---

*Project Doctor nie uruchamia Twojego kodu, nie instaluje zależności i nie
czyta plików z nazwami sugerującymi sekrety. Audyt jest w 100% statyczny.*
