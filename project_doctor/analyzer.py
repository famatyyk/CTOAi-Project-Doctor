"""Static, redacted repository analysis for Project Doctor.

This module does not invoke subprocesses, import target modules, install
dependencies, or execute tests. It only inventories files and parses safe,
bounded UTF-8 source text.
"""

from __future__ import annotations

import ast
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .models import AuditResult, Finding, stable_findings
from .policy import (
    DEFAULT_MAX_FILE_BYTES,
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_TOTAL_BYTES,
    MAX_FINDINGS,
    SOURCE_EXTENSIONS,
    is_sensitive_file_name,
    is_text_candidate,
)
from .safe_fs import FileEntry, WalkResult, read_text_bounded, walk_repository
from .cpp_lua import analyse_cxx_lua


LANGUAGE_NAMES = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".h": "C/C++ header",
    ".hpp": "C/C++ header",
    ".hxx": "C/C++ header",
    ".lua": "Lua",
}

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "credential_assignment",
        re.compile(
            r"(?im)^\s*[A-Za-z_][A-Za-z0-9_]*?"
            r"(?:api[_-]?key|secret|token|password|passwd|private[_-]?key)"
            r"[A-Za-z0-9_]*"
            r"\s*[:=]\s*['\"][^'\"]{8,}['\"]"
        ),
    ),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    (
        "private_key_block",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
)

PLACEHOLDER_MARKERS = (
    "example",
    "placeholder",
    "changeme",
    "not-a-real",
    "your_",
    "your-",
    "dummy",
    "replace-me",
)

HTTP_URL_PATTERN = re.compile(r"\bhttp://[A-Za-z0-9][A-Za-z0-9.-]*(?::\d+)?(?:/[A-Za-z0-9._~:/?#[\]@!$&'()*+,;=%-]*)?")

HTTP_CHECK_EXTENSIONS = frozenset(
    {".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh"}
)


class _PythonRiskVisitor(ast.NodeVisitor):
    """Collect a small set of explainable static Python risk signals."""

    def __init__(self) -> None:
        self.signals: set[str] = set()

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
        if node.type is None:
            self.signals.add("bare_except")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        call_name = _call_name(node.func)
        if call_name in {"eval", "exec"}:
            self.signals.add("dynamic_execution")
        if call_name in {"pickle.load", "pickle.loads"}:
            self.signals.add("unsafe_deserialization")
        if call_name.startswith("subprocess.") and any(
            keyword.arg == "shell"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
            for keyword in node.keywords
        ):
            self.signals.add("subprocess_shell_true")
        self.generic_visit(node)


def _call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _check(
    check_id: str,
    status: str,
    severity: str,
    message: str,
    evidence: Iterable[str] = (),
    recommendation: str = "",
) -> dict[str, object]:
    return {
        "id": check_id,
        "status": status,
        "severity": severity,
        "message": message,
        "evidence": list(evidence),
        "recommendation": recommendation,
    }


def _is_test_file(entry: FileEntry) -> bool:
    lower = entry.relative_path.lower()
    name = Path(lower).name
    parts = Path(lower).parts
    return (
        "tests" in parts
        or "test" in parts
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".test.js")
        or name.endswith(".spec.js")
        or name.endswith(".test.ts")
        or name.endswith(".spec.ts")
    )


def _has_top_level(paths: set[str], names: Iterable[str]) -> str | None:
    lowered = {item.casefold(): item for item in paths}
    for name in names:
        match = lowered.get(name.casefold())
        if match:
            return match
    return None


def _looks_like_placeholder(match: str) -> bool:
    lowered = match.casefold()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def _safe_label(value: str | None) -> str | None:
    if not value:
        return None
    # A client name is optional but must not accidentally expose a local path.
    cleaned = " ".join(value.replace("\\", "/").split())
    if "/" in cleaned:
        cleaned = cleaned.rsplit("/", 1)[-1]
    return cleaned[:100] or None


def _severity_summary(findings: list[Finding]) -> dict[str, int]:
    counts = Counter(finding.severity for finding in findings)
    return {level: counts.get(level, 0) for level in ("critical", "high", "medium", "low", "info")}


def _score(findings: list[Finding]) -> dict[str, object]:
    penalties = {"critical": 25, "high": 15, "medium": 7, "low": 3, "info": 0}
    penalty = sum(penalties.get(finding.severity, 0) for finding in findings)
    value = max(0, 100 - penalty)
    if value >= 90:
        label = "dobry stan"
    elif value >= 75:
        label = "wymaga drobnych poprawek"
    elif value >= 55:
        label = "wymaga uwagi"
    else:
        label = "podwyższone ryzyko"
    return {
        "value": value,
        "label": label,
        "method": "100 minus jawne kary za statyczne znaleziska; wynik nie jest certyfikatem bezpieczeństwa.",
    }


def _add_finding(
    findings: list[Finding],
    seen: set[tuple[str, tuple[str, ...]]],
    *,
    rule_id: str,
    severity: str,
    category: str,
    title: str,
    evidence: Iterable[str],
    recommendation: str,
) -> None:
    safe_evidence = tuple(sorted(set(evidence)))
    identity = (rule_id, safe_evidence)
    if identity in seen or len(findings) >= MAX_FINDINGS:
        return
    seen.add(identity)
    findings.append(
        Finding(
            rule_id=rule_id,
            severity=severity,
            category=category,
            title=title,
            evidence=safe_evidence,
            recommendation=recommendation,
        )
    )


def _analyse_python(
    entry: FileEntry,
    content: str,
    findings: list[Finding],
    seen: set[tuple[str, tuple[str, ...]]],
) -> None:
    try:
        tree = ast.parse(content, filename=entry.relative_path)
    except SyntaxError:
        _add_finding(
            findings,
            seen,
            rule_id="python.syntax-error",
            severity="high",
            category="jakość kodu",
            title="Python zawiera błąd składni",
            evidence=[entry.relative_path],
            recommendation="Napraw błąd składni i uruchom testy w zaufanym środowisku.",
        )
        return

    visitor = _PythonRiskVisitor()
    visitor.visit(tree)
    rule_map = {
        "bare_except": (
            "python.bare-except",
            "low",
            "Ogólny except utrudnia diagnozowanie błędów",
            "Łap jawne wyjątki i loguj przyczynę błędu.",
        ),
        "dynamic_execution": (
            "python.dynamic-execution",
            "high",
            "Znaleziono eval lub exec",
            "Usuń dynamiczne wykonanie albo ogranicz je do wyraźnie zweryfikowanego, izolowanego wejścia.",
        ),
        "unsafe_deserialization": (
            "python.unsafe-pickle",
            "high",
            "Znaleziono odczyt pickle",
            "Nie ładuj pickle z niezaufanego źródła; użyj bezpieczniejszego formatu danych.",
        ),
        "subprocess_shell_true": (
            "python.subprocess-shell",
            "high",
            "Znaleziono subprocess z shell=True",
            "Przekazuj listę argumentów i unikaj shell=True dla danych, które mogą pochodzić od użytkownika.",
        ),
    }
    for signal in sorted(visitor.signals):
        rule_id, severity, title, recommendation = rule_map[signal]
        _add_finding(
            findings,
            seen,
            rule_id=rule_id,
            severity=severity,
            category="bezpieczeństwo",
            title=title,
            evidence=[entry.relative_path],
            recommendation=recommendation,
        )


def _analyse_text(
    entry: FileEntry,
    content: str,
    findings: list[Finding],
    seen: set[tuple[str, tuple[str, ...]]],
) -> int:
    """Analyze text without returning or storing any customer source content."""

    for secret_kind, pattern in SECRET_PATTERNS:
        match = pattern.search(content)
        if match and not _looks_like_placeholder(match.group(0)):
            _add_finding(
                findings,
                seen,
                rule_id=f"secrets.{secret_kind}",
                severity="critical",
                category="bezpieczeństwo",
                title="Możliwy sekret zapisany w śledzonym pliku",
                evidence=[entry.relative_path, f"typ: {secret_kind}"],
                recommendation="Usuń wartość z historii i kodu, unieważnij sekret oraz pobieraj go z bezpiecznej konfiguracji środowiska.",
            )
            break

    if entry.path.suffix.lower() in HTTP_CHECK_EXTENSIONS and HTTP_URL_PATTERN.search(content):
        _add_finding(
            findings,
            seen,
            rule_id="security.plain-http",
            severity="medium",
            category="bezpieczeństwo",
            title="Znaleziono adres HTTP bez TLS",
            evidence=[entry.relative_path],
            recommendation="Użyj HTTPS, chyba że komunikacja jest świadomie ograniczona do bezpiecznej sieci lokalnej.",
        )

    if "TODO" in content or "FIXME" in content:
        _add_finding(
            findings,
            seen,
            rule_id="quality.todo-marker",
            severity="info",
            category="jakość kodu",
            title="Pozostały oznaczenia TODO/FIXME",
            evidence=[entry.relative_path],
            recommendation="Przejrzyj oznaczenia i przekształć istotne zadania w elementy backlogu.",
        )

    line_count = content.count("\n") + (1 if content else 0)
    if entry.path.suffix.lower() == ".py":
        _analyse_python(entry, content, findings, seen)
    if entry.path.suffix.lower() in SOURCE_EXTENSIONS and line_count > 700:
        _add_finding(
            findings,
            seen,
            rule_id="quality.large-source-file",
            severity="low",
            category="jakość kodu",
            title="Bardzo duży plik źródłowy",
            evidence=[entry.relative_path],
            recommendation="Rozważ podział pliku na mniejsze moduły z wyraźną odpowiedzialnością.",
        )
    return line_count


def analyze_repository(
    target: Path,
    *,
    client: str | None = None,
    max_files: int = DEFAULT_MAX_FILES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> AuditResult:
    """Create a static audit result for a local repository.

    The caller supplies only a directory. All reports retain its basename, not
    the original absolute path.
    """

    walk = walk_repository(
        target,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
        max_file_bytes=max_file_bytes,
    )
    return _build_result(walk, client=client, max_files=max_files, max_total_bytes=max_total_bytes, max_file_bytes=max_file_bytes)


def _build_result(
    walk: WalkResult,
    *,
    client: str | None,
    max_files: int,
    max_total_bytes: int,
    max_file_bytes: int,
) -> AuditResult:
    files = walk.files
    paths = {entry.relative_path for entry in files}
    lower_paths = {path.casefold() for path in paths}
    findings: list[Finding] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()
    checks: list[dict[str, object]] = []

    extensions = Counter(entry.path.suffix.lower() or "[brak rozszerzenia]" for entry in files)
    languages = Counter(
        LANGUAGE_NAMES[entry.path.suffix.lower()]
        for entry in files
        if entry.path.suffix.lower() in LANGUAGE_NAMES
    )
    source_files = [entry for entry in files if entry.path.suffix.lower() in SOURCE_EXTENSIONS]
    test_files = [entry for entry in files if _is_test_file(entry)]
    sensitive_paths = [entry.relative_path for entry in files if is_sensitive_file_name(entry.path)]
    text_files_scanned = 0
    text_files_omitted = 0
    source_lines = 0

    for entry in files:
        if is_sensitive_file_name(entry.path):
            continue
        if not is_text_candidate(entry.path):
            continue
        content = read_text_bounded(entry)
        if content is None:
            text_files_omitted += 1
            continue
        text_files_scanned += 1
        line_count = _analyse_text(entry, content, findings, seen)
        lang = analyse_cxx_lua(entry, content, findings, seen)
        if lang:
            languages[lang] += 1
        if entry.path.suffix.lower() in SOURCE_EXTENSIONS:
            source_lines += line_count

    if sensitive_paths:
        _add_finding(
            findings,
            seen,
            rule_id="secrets.sensitive-file-name",
            severity="high",
            category="bezpieczeństwo",
            title="Znaleziono pliki mogące zawierać poświadczenia",
            evidence=sensitive_paths,
            recommendation="Nie wersjonuj sekretów. Przenieś je do bezpiecznego magazynu lub lokalnego pliku ignorowanego przez Git.",
        )

    readme = _has_top_level(paths, ("README.md", "README.rst", "README.txt"))
    if readme:
        checks.append(_check("docs.readme", "pass", "info", "Znaleziono główny README.", [readme]))
    else:
        checks.append(
            _check(
                "docs.readme",
                "warn",
                "high",
                "Brak głównego README.",
                recommendation="Dodaj krótki opis, instalację, uruchomienie i sposób testowania projektu.",
            )
        )
        _add_finding(
            findings,
            seen,
            rule_id="docs.missing-readme",
            severity="high",
            category="dokumentacja",
            title="Brak głównego README",
            evidence=[],
            recommendation="Dodaj README z opisem produktu, konfiguracją i podstawową instrukcją uruchomienia.",
        )

    for check_id, names, title, recommendation in (
        (
            "docs.license",
            ("LICENSE", "LICENSE.md", "COPYING"),
            "Brak jednoznacznej licencji",
            "Dodaj licencję lub jasno określ warunki użycia kodu.",
        ),
        (
            "docs.changelog",
            ("CHANGELOG.md", "CHANGES.md", "HISTORY.md"),
            "Brak changelogu",
            "Dodaj prosty changelog, aby klient wiedział, co zmieniło się między wydaniami.",
        ),
        (
            "docs.contributing",
            ("CONTRIBUTING.md",),
            "Brak wskazówek dla współtwórców",
            "Dodaj krótkie zasady instalacji, testów i zgłaszania zmian.",
        ),
        (
            "hygiene.gitignore",
            (".gitignore",),
            "Brak .gitignore",
            "Dodaj .gitignore dla sekretów, cache, środowisk wirtualnych i artefaktów builda.",
        ),
    ):
        match = _has_top_level(paths, names)
        if match:
            checks.append(_check(check_id, "pass", "info", "Znaleziono wymagany artefakt.", [match]))
        else:
            checks.append(_check(check_id, "warn", "low", title, recommendation=recommendation))
            _add_finding(
                findings,
                seen,
                rule_id=f"{check_id}.missing",
                severity="low" if check_id != "hygiene.gitignore" else "medium",
                category="dokumentacja" if check_id.startswith("docs") else "higiena repozytorium",
                title=title,
                evidence=[],
                recommendation=recommendation,
            )

    manifest_names = (
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "setup.cfg",
        "package.json",
    )
    manifests = [path for path in paths if Path(path).name.casefold() in manifest_names]
    if manifests:
        checks.append(_check("dependencies.manifest", "pass", "info", "Znaleziono manifest zależności.", manifests))
    else:
        checks.append(
            _check(
                "dependencies.manifest",
                "warn",
                "medium",
                "Nie znaleziono manifestu zależności.",
                recommendation="Dodaj pyproject.toml, requirements.txt lub odpowiedni manifest ekosystemu.",
            )
        )
        _add_finding(
            findings,
            seen,
            rule_id="dependencies.missing-manifest",
            severity="medium",
            category="zależności",
            title="Brak manifestu zależności",
            evidence=[],
            recommendation="Dodaj śledzony manifest zależności, aby instalacja była powtarzalna.",
        )

    lock_names = {"poetry.lock", "uv.lock", "requirements.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
    locks = [path for path in paths if Path(path).name.casefold() in lock_names]
    if manifests and not locks:
        checks.append(
            _check(
                "dependencies.lock",
                "warn",
                "low",
                "Nie znaleziono pliku blokady zależności.",
                recommendation="Tam, gdzie to możliwe, dodaj lockfile lub przypięte wersje zależności.",
            )
        )
        _add_finding(
            findings,
            seen,
            rule_id="dependencies.missing-lock",
            severity="low",
            category="zależności",
            title="Brak pliku blokady zależności",
            evidence=[],
            recommendation="Dodaj lockfile albo używaj przypiętych wersji, aby ograniczyć różnice między środowiskami.",
        )
    elif locks:
        checks.append(_check("dependencies.lock", "pass", "info", "Znaleziono lockfile zależności.", locks))

    test_paths = [entry.relative_path for entry in test_files]
    if test_paths:
        checks.append(
            _check(
                "tests.discovered",
                "not_run",
                "info",
                "Znaleziono pliki testowe; nie zostały uruchomione przez Project Doctor.",
                test_paths[:20],
                "Uruchom testy osobno w zaufanym środowisku CI lub lokalnym.",
            )
        )
    else:
        checks.append(
            _check(
                "tests.discovered",
                "warn",
                "high",
                "Nie znaleziono rozpoznawalnych plików testowych.",
                recommendation="Dodaj testy najważniejszych ścieżek działania oraz uruchamiaj je w CI.",
            )
        )
        _add_finding(
            findings,
            seen,
            rule_id="tests.none-discovered",
            severity="high",
            category="testy",
            title="Nie znaleziono testów",
            evidence=[],
            recommendation="Dodaj przynajmniej testy krytycznych funkcji i konfiguracji.",
        )

    workflow_paths = [path for path in paths if path.startswith(".github/workflows/")]
    if workflow_paths:
        checks.append(_check("ci.workflow", "pass", "info", "Znaleziono workflow CI.", workflow_paths))
    else:
        checks.append(
            _check(
                "ci.workflow",
                "warn",
                "low",
                "Nie znaleziono workflow CI.",
                recommendation="Dodaj prosty workflow uruchamiający testy i kontrolę formatowania.",
            )
        )
        _add_finding(
            findings,
            seen,
            rule_id="ci.no-workflow",
            severity="low",
            category="dostarczanie",
            title="Brak widocznego workflow CI",
            evidence=[],
            recommendation="Dodaj minimalny workflow CI, który uruchamia testy przy zmianach.",
        )

    if ".git" in lower_paths or (walk.root / ".git").exists():
        checks.append(_check("repository.git", "pass", "info", "Katalog wygląda na repozytorium Git."))
    else:
        checks.append(
            _check(
                "repository.git",
                "not_run",
                "info",
                "Nie potwierdzono metadanych Git w przekazanym katalogu.",
                recommendation="Jeśli to źródła projektu, trzymaj je w repozytorium Git.",
            )
        )

    checks.append(
        _check(
            "execution.tests",
            "not_run",
            "info",
            "Testy, instalacja zależności i kod projektu nie były uruchamiane.",
            recommendation="To świadoma granica bezpieczeństwa audytu statycznego; wykonanie dodaj tylko w izolowanym CI/sandboxie.",
        )
    )

    coverage_status = "partial" if walk.partial or text_files_omitted else "complete"
    coverage = {
        "status": coverage_status,
        "scanned_files": len(files),
        "scanned_bytes": walk.total_bytes,
        "text_files_scanned": text_files_scanned,
        "text_files_omitted": text_files_omitted,
        "skipped": dict(sorted(walk.skipped.items())),
        "limits": {
            "max_files": max_files,
            "max_total_bytes": max_total_bytes,
            "max_file_bytes": max_file_bytes,
        },
    }
    inventory = {
        "file_count": len(files),
        "source_file_count": len(source_files),
        "test_file_count": len(test_files),
        "source_line_count": source_lines,
        "languages": dict(sorted(languages.items())),
        "extensions": dict(sorted(extensions.items())),
    }
    result = AuditResult(
        audit_id=f"PD-{datetime.now(timezone.utc):%Y%m%d}-{uuid.uuid4().hex[:8].upper()}",
        generated_at=datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        repository=_safe_label(walk.root.name) or "repository",
        client=_safe_label(client),
        coverage=coverage,
        inventory=inventory,
        checks=checks,
        findings=stable_findings(findings),
        limitations=[
            "Audyt jest statyczny: nie uruchamia kodu, testów, instalatorów ani poleceń Git klienta.",
            "Raport nie jest pentestem ani gwarancją braku podatności.",
            "Zawartość plików z nazwami sugerującymi sekret nie jest odczytywana; raport zawiera wyłącznie względne ścieżki i typy znalezisk.",
            "Testy są tylko wykrywane, nigdy uruchamiane. Wynik 'not_run' nie oznacza powodzenia testów.",
        ],
    )
    result.score = _score(result.findings)
    result.score["findings_by_severity"] = _severity_summary(result.findings)
    return result
