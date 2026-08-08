"""Statyczna analiza buildów C++ (CMake / CMakePresets / ninja) dla Project Doctor.

Moduł NIE uruchamia cmake/ninja. Tylko czyta pliki tekstowe i szuka
wyjaśnialnych sygnałów jakości konfiguracji builda. Bezpieczne, szybkie.
"""

from __future__ import annotations

import re
from typing import Iterable

from .models import Finding

CMAKE_EXTS = frozenset({".cmake", ".txt"})
PRESETS_NAME = "CMakePresets.json"


def _check_cmake(content: str, findings: list[Finding], seen, path: str) -> None:
    rules = []

    # 1. cmake_minimum_required
    if not re.search(r"cmake_minimum_required\s*\(\s*VERSION", content):
        rules.append((
            "build.cmake-no-min-version", "medium",
            "Brak cmake_minimum_required(VERSION ...)",
            "Dodaj cmake_minimum_required(VERSION 3.16) na początku CMakeLists.txt.",
        ))

    # 2. globalne CMAKE_CXX_STANDARD zamiast target_compile_features
    if re.search(r"set\s*\(\s*CMAKE_CXX_STANDARD", content):
        if not re.search(r"target_compile_features", content):
            rules.append((
                "build.cmake-global-standard", "low",
                "Ustawiono globalne CMAKE_CXX_STANDARD bez target_compile_features",
                "Użyj target_compile_features(<tgt> PRIVATE cxx_std_17) dla jawnych wymagań per-target.",
            ))

    # 3. globalne include_directories
    if re.search(r"include_directories\s*\(", content):
        rules.append((
            "build.cmake-global-include", "low",
            "Użyto globalnego include_directories()",
            "Preferuj target_include_directories(<tgt> PRIVATE/PUBLIC) — izoluj zależności.",
        ))

    # 4. brak CMAKE_BUILD_TYPE / presets
    if "project(" in content and "CMAKE_BUILD_TYPE" not in content and "CMakePresets.json" not in content:
        rules.append((
            "build.cmake-no-build-type", "info",
            "Brak CMAKE_BUILD_TYPE ani CMakePresets.json",
            "Dodaj CMakePresets.json (Debug/Release) lub domyślny CMAKE_BUILD_TYPE=Debug.",
        ))

    # 5. hardcoded -O3 w add_compile_options
    if re.search(r"add_compile_options\s*\([^)]*-O3", content):
        rules.append((
            "build.cmake-hardcoded-opt", "low",
            "Hardkodowane -O3 w add_compile_options",
            "Nie wymuszaj optymalizacji globalnie; steruj przez CMAKE_BUILD_TYPE / presets.",
        ))

    # 6. add_executable bez target_link_libraries
    exes = re.findall(r"add_(executable|library)\s*\(\s*(\w+)", content)
    if exes and not re.search(r"target_link_libraries", content):
        rules.append((
            "build.cmake-no-link", "medium",
            "Znaleziono add_executable/add_library bez target_link_libraries",
            "Jawnie linkuj zależności przez target_link_libraries(), by uniknąć braku symboli.",
        ))

    # 7. vendored dep (brak find_package przy #include <external>)
    if re.search(r"find_package", content) is None and re.search(r"#include\s*<\w+/\w+>", content):
        rules.append((
            "build.cmake-no-find-package", "low",
            "Brak find_package() mimo #include <lib/...>",
            "Użyj find_package() + target_link_libraries() zamiast vendoringu lub ścieżek absolute.",
        ))

    for rule_id, severity, title, rec in rules:
        key = (rule_id, (path,))
        if key in seen or len(findings) >= 200:
            continue
        seen.add(key)
        findings.append(Finding(
            rule_id=rule_id, severity=severity, category="build C++",
            title=title, evidence=(path,), recommendation=rec,
        ))


def analyse_build(entry, content: str, findings: list[Finding], seen) -> bool:
    """Zwraca True, jeśli to plik buildowy CMake."""
    name = entry.path.name.lower()
    suffix = entry.path.suffix.lower()
    is_cmake = name == "cmakelists.txt" or suffix == ".cmake" or name == PRESETS_NAME.lower()
    if is_cmake:
        _check_cmake(content, findings, seen, entry.relative_path)
        return True
    return False
