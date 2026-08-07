"""Customer-safe JSON and Markdown report generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AuditResult


def _is_within(candidate: Path, container: Path) -> bool:
    try:
        candidate.relative_to(container)
    except ValueError:
        return False
    return True


def validate_output_directory(target: Path, output: Path, *, force: bool = False) -> Path:
    """Validate that reports cannot modify the audited repository itself."""

    resolved_target = target.resolve(strict=True)
    resolved_output = output.resolve(strict=False)
    if _is_within(resolved_output, resolved_target):
        raise ValueError("Katalog raportu nie może znajdować się wewnątrz audytowanego repozytorium.")
    if resolved_output.exists() and not resolved_output.is_dir():
        raise ValueError("Ścieżka wyjściowa istnieje, ale nie jest katalogiem.")
    if resolved_output.exists() and any(resolved_output.iterdir()) and not force:
        raise FileExistsError(
            "Katalog raportu nie jest pusty. Użyj nowego katalogu albo podaj --force."
        )
    return resolved_output


def _escape(value: object) -> str:
    """Avoid Markdown/HTML injection through hostile file names or labels."""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("|", "\\|")
        .replace("`", "\\`")
        .replace("\n", " ")
    )


def render_markdown(result: AuditResult) -> str:
    """Render a concise Polish customer report from the canonical result."""

    payload = result.as_dict()
    coverage = payload["coverage"]
    inventory = payload["inventory"]
    score = payload["score"]
    findings: list[dict[str, Any]] = payload["findings"]
    severity_counts: dict[str, int] = score["findings_by_severity"]

    lines = [
        "# Project Doctor — raport statyczny",
        "",
        f"- **Projekt:** {_escape(payload['repository'])}",
        f"- **Klient:** {_escape(payload['client'] or 'nie podano')}",
        f"- **ID audytu:** `{_escape(payload['audit_id'])}`",
        f"- **Wygenerowano:** {_escape(payload['generated_at'])}",
        f"- **Pokrycie:** {_escape(coverage['status'])}",
        "",
        "## Wynik",
        "",
        f"**{_escape(score['value'])}/100 — {_escape(score['label'])}**",
        "",
        _escape(score["method"]),
        "",
        "| Krytyczne | Wysokie | Średnie | Niskie | Informacyjne |",
        "| ---: | ---: | ---: | ---: | ---: |",
        "| "
        + " | ".join(
            str(severity_counts[level])
            for level in ("critical", "high", "medium", "low", "info")
        )
        + " |",
        "",
        "## Zakres skanu",
        "",
        f"- Pliki: {coverage['scanned_files']} ({coverage['scanned_bytes']} bajtów)",
        f"- Tekstowo przeanalizowane pliki: {coverage['text_files_scanned']}",
        f"- Pliki tekstowe pominięte z powodu limitu lub odczytu: {coverage['text_files_omitted']}",
        f"- Limit plików: {coverage['limits']['max_files']}; limit łączny: {coverage['limits']['max_total_bytes']} bajtów; limit pliku: {coverage['limits']['max_file_bytes']} bajtów.",
    ]
    if coverage["skipped"]:
        lines.extend(["", "Pominięte elementy:"])
        for reason, count in coverage["skipped"].items():
            lines.append(f"- {_escape(reason)}: {count}")

    lines.extend(
        [
            "",
            "## Inwentaryzacja",
            "",
            f"- Pliki źródłowe: {inventory['source_file_count']}",
            f"- Wykryte pliki testowe: {inventory['test_file_count']} (nie uruchamiano)",
            f"- Linie kodu źródłowego: {inventory['source_line_count']}",
            f"- Języki: {_escape(', '.join(f'{name}: {count}' for name, count in inventory['languages'].items()) or 'nie wykryto')}",
            "",
            "## Priorytety naprawy",
            "",
        ]
    )
    actionable = [item for item in findings if item["severity"] != "info"][:5]
    if actionable:
        for index, finding in enumerate(actionable, start=1):
            lines.append(
                f"{index}. **{_escape(finding['severity'].upper())}: {_escape(finding['title'])}** — {_escape(finding['recommendation'])}"
            )
    else:
        lines.append("Brak pilnych statycznych znalezisk w zdefiniowanym zakresie.")

    lines.extend(["", "## Wszystkie znaleziska", ""])
    if findings:
        lines.extend(
            [
                "| Priorytet | Kategoria | Znalezisko | Dowód | Zalecenie |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for finding in findings:
            evidence = ", ".join(_escape(item) for item in finding["evidence"]) or "—"
            lines.append(
                "| "
                + " | ".join(
                    [
                        _escape(finding["severity"]),
                        _escape(finding["category"]),
                        _escape(finding["title"]),
                        evidence,
                        _escape(finding["recommendation"]),
                    ]
                )
                + " |"
            )
    else:
        lines.append("Brak znalezisk statycznych w przeanalizowanym zakresie.")

    lines.extend(["", "## Kontrole", ""])
    for check in payload["checks"]:
        evidence = ", ".join(_escape(item) for item in check["evidence"]) or "—"
        lines.append(
            f"- **{_escape(check['id'])}** ({_escape(check['status'])}): {_escape(check['message'])} Dowód: {evidence}"
        )

    lines.extend(["", "## Ograniczenia", ""])
    lines.extend(f"- {_escape(item)}" for item in payload["limitations"])
    lines.append("")
    return "\n".join(lines)


def write_reports(result: AuditResult, output: Path, *, force: bool = False) -> dict[str, Path]:
    """Write canonical JSON and customer-friendly Markdown into ``output``."""

    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "report.json"
    markdown_path = output / "report.md"
    if not force and (json_path.exists() or markdown_path.exists()):
        raise FileExistsError("Raport już istnieje w katalogu wyjściowym. Użyj --force, aby go zastąpić.")
    json_path.write_text(
        json.dumps(result.as_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(result), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}
