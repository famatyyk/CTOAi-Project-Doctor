"""Statyczna analiza C++ i Lua dla Project Doctor.

Moduł celowo NIE używa clang/LLVM (brak zależności, bezpieczne, szybkie).
Szuka wyjaśnialnych sygnałów ryzyka przez ograniczone wyrażenia regularne
i proste liczniki strukturalne. Nie uruchamia kodu, nie instaluje niczego.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from .models import Finding

CXX_EXTENSIONS = frozenset({".cpp", ".cc", ".cxx", ".hpp", ".h", ".hxx", ".c"})
LUA_EXTENSIONS = frozenset({".lua"})

# C++ ryzyka
CXX_RISK_PATTERNS: tuple[tuple[str, re.Pattern[str], str, str, str], ...] = (
    (
        "cxx.raw-new-no-delete",
        re.compile(r"\bnew\s+\w+\s*[(\[]"),
        "medium",
        "Surowe `new` bez widocznego zarządzania pamięcią",
        "Użyj std::unique_ptr / std::shared_ptr zamiast surowego new, by uniknąć wycieków.",
    ),
    (
        "cxx.goto",
        re.compile(r"\bgoto\s+\w+"),
        "low",
        "Użyto instrukcji goto",
        "Unikaj goto; zamiast tego użyj pętli, funkcji lub std::expected do sterowania przepływem.",
    ),
    (
        "cxx.reinterpret-cast",
        re.compile(r"\breinterpret_cast\s*<"),
        "medium",
        "Użyto reinterpret_cast",
        "Upewnij się, że rzutowanie jest konieczne i bezpieczne; rozważ std::bit_cast (C++20) lub przeprojektowanie interfejsu.",
    ),
    (
        "cxx.c-style-cast",
        re.compile(r"\(\s*(?:int|long|char|float|double|void|unsigned|size_t)\s*\*?\s*\)\s*\w+"),
        "low",
        "Rzutowanie w stylu C",
        "Wolaj statycznych rzutowań C++ (static_cast / const_cast) dla lepszej czytelności i bezpieczeństwa typów.",
    ),
    (
        "cxx.macro-include-guard-missing",
        re.compile(r"#ifndef\s+\w+\s*\n#define\s+\w+", re.M),
        "info",
        "Plik nagłówkowy bez klasycznej guardy (sprawdź include guard / #pragma once)",
        "Dodaj #pragma once lub include guard, by uniknąć wielokrotnej kompilacji.",
    ),
    (
        "cxx.printf-format",
        re.compile(r"\b(printf|sprintf|fprintf)\s*\(\s*[^,]*,[^)]*\%"),
        "low",
        "Użyto printf-family z formatowaniem",
        "Preferuj std::format / std::print (C++20/23) — bezpieczniejsze i typowane.",
    ),
    (
        "cxx.unsafe-func",
        re.compile(r"\b(strcpy|strcat|gets|scanf|sprintf)\s*\("),
        "high",
        "Funkcja C uznawana za niebezpieczną (strcpy/strcat/gets/scanf/sprintf)",
        "Użyj bezpiecznych odpowiedników: std::string, std::format, snprintf z kontrolą rozmiaru.",
    ),
)


def _analyse_cxx(entry, content: str, findings: list[Finding], seen) -> None:
    for rule_id, pattern, severity, title, recommendation in CXX_RISK_PATTERNS:
        if pattern.search(content):
            seen_key = (f"cxx.{rule_id}", (entry.relative_path,))
            if seen_key in seen:
                continue
            seen.add(seen_key)
            findings.append(
                Finding(
                    rule_id=f"cxx.{rule_id}",
                    severity=severity,
                    category="jakość kodu C++",
                    title=title,
                    evidence=(entry.relative_path,),
                    recommendation=recommendation,
                )
            )


LUA_RISK_PATTERNS: tuple[tuple[str, re.Pattern[str], str, str, str], ...] = (
    (
        "lua.load",
        re.compile(r"\b(load|loadstring|loadfile)\s*\("),
        "high",
        "Użyto load/loadstring/loadfile",
        "Nie ładuj kodu z niezaufanego źródła; jeśli konieczne, izoluj w sandboxie i weryfikuj.",
    ),
    (
        "lua.os-execute",
        re.compile(r"\bos\.execute\s*\("),
        "high",
        "Użyto os.execute",
        "Unikaj wywoływania powłoki z danymi zewnętrznymi; użyj bezpieczniejszego API lub allowlisty komend.",
    ),
    (
        "lua.global-assign",
        re.compile(r"^\s*(?:(?:local\s+)?\w+\s*,\s*)*\w+\s*=\s*[^=]*\b(?:_G|_ENV)\b", re.M),
        "low",
        "Modyfikacja globalnej przestrzeni (_G / _ENV)",
        "Ogranicz zanieczyszczanie globali; używaj lokalnych modułów (require).",
    ),
    (
        "lua.pcall-missing",
        re.compile(r"\bpcall\s*\(\s*function"),
        "info",
        "Blok pcall — upewnij się, że błędy są obsłużone",
        "Wewnątrz pcall loguj/obsługuj błędy, by uniknąć cichego niepowodzenia.",
    ),
)


def _analyse_lua(entry, content: str, findings: list[Finding], seen) -> None:
    for rule_id, pattern, severity, title, recommendation in LUA_RISK_PATTERNS:
        if pattern.search(content):
            seen_key = (f"lua.{rule_id}", (entry.relative_path,))
            if seen_key in seen:
                continue
            seen.add(seen_key)
            findings.append(
                Finding(
                    rule_id=f"lua.{rule_id}",
                    severity=severity,
                    category="bezpieczeństwo Lua",
                    title=title,
                    evidence=(entry.relative_path,),
                    recommendation=recommendation,
                )
            )


def analyse_cxx_lua(entry, content: str, findings: list[Finding], seen) -> str | None:
    """Zwraca nazwę języka, jeśli rozpoznano (do statystyk)."""
    suffix = entry.path.suffix.lower()
    if suffix in CXX_EXTENSIONS:
        _analyse_cxx(entry, content, findings, seen)
        lang = "C++" if suffix != ".h" and suffix != ".hpp" and suffix != ".hxx" else "C/C++ header"
        return "C++" if suffix in (".cpp", ".cc", ".cxx", ".c") else "C/C++ header"
    if suffix in LUA_EXTENSIONS:
        _analyse_lua(entry, content, findings, seen)
        return "Lua"
    return None
