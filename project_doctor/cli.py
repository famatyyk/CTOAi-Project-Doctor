"""Command-line interface for the Project Doctor MVP."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .analyzer import analyze_repository
from .policy import DEFAULT_MAX_FILES
from .reporting import validate_output_directory, write_reports


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Wartość musi być liczbą całkowitą.") from error
    if number < 1:
        raise argparse.ArgumentTypeError("Wartość musi być większa od zera.")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-doctor",
        description="Bezpieczny, statyczny przegląd repozytorium Python/AI.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="Wykonaj statyczny audyt katalogu projektu.")
    audit.add_argument("target", type=Path, help="Lokalny katalog projektu klienta.")
    audit.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Pusty katalog poza badanym repozytorium, do którego trafi raport.",
    )
    audit.add_argument("--client", default="", help="Opcjonalna nazwa klienta widoczna w raporcie.")
    audit.add_argument(
        "--max-files",
        type=_positive_int,
        default=DEFAULT_MAX_FILES,
        help=f"Maksymalna liczba plików do inwentaryzacji (domyślnie {DEFAULT_MAX_FILES}).",
    )
    audit.add_argument(
        "--force",
        action="store_true",
        help="Zezwól na zapis do istniejącego katalogu raportu i zastąpienie report.*.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "audit":  # Defensive guard for future subcommands.
        parser.error("Nieobsługiwana komenda.")

    try:
        target = args.target.resolve(strict=True)
        output = validate_output_directory(target, args.output, force=args.force)
        result = analyze_repository(target, client=args.client, max_files=args.max_files)
        files = write_reports(result, output, force=args.force)
    except (OSError, ValueError, FileExistsError) as error:
        print(f"Błąd Project Doctor: {error}", file=sys.stderr)
        return 2

    print(
        "Project Doctor zakończony: "
        f"wynik={result.score['value']}/100, "
        f"znaleziska={len(result.findings)}, "
        f"pokrycie={result.coverage['status']}"
    )
    print(f"Markdown: {files['markdown']}")
    print(f"JSON: {files['json']}")
    return 0
