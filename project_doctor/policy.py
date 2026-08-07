"""Policy constants for a bounded, read-only Project Doctor audit."""

from __future__ import annotations

from pathlib import Path


DEFAULT_MAX_FILES = 10_000
DEFAULT_MAX_TOTAL_BYTES = 250 * 1024 * 1024
DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_TEXT_BYTES = 512 * 1024
DEFAULT_MAX_DEPTH = 32
MAX_FINDINGS = 200

# These trees are either metadata, dependency caches, generated outputs, or
# likely to make an inexpensive customer audit slow and noisy.
EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".idea",
        ".vscode",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".nox",
        ".next",
        ".nuxt",
        "coverage",
        "htmlcov",
        "site-packages",
    }
)

TEXT_EXTENSIONS = frozenset(
    {
        ".cfg",
        ".cjs",
        ".css",
        ".csv",
        ".c",
        ".cpp",
        ".cc",
        ".cxx",
        ".h",
        ".hpp",
        ".hxx",
        ".html",
        ".ini",
        ".js",
        ".json",
        ".jsx",
        ".lua",
        ".md",
        ".mjs",
        ".py",
        ".pyi",
        ".rst",
        ".sh",
        ".toml",
        ".ts",
        ".tsx",
        ".txt",
        ".yaml",
        ".yml",
    }
)

TEXT_FILENAMES = frozenset(
    {
        "dockerfile",
        "makefile",
        "procfile",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-test.txt",
    }
)

SOURCE_EXTENSIONS = frozenset(
    {".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx", ".lua"}
)

SENSITIVE_FILE_NAMES = frozenset(
    {
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "credentials.json",
        "service-account.json",
    }
)


def is_excluded_directory(path: Path) -> bool:
    return path.name.lower() in EXCLUDED_DIRECTORIES


def is_sensitive_file_name(path: Path) -> bool:
    """Return true for files whose contents must never be read by this tool."""

    name = path.name.lower()
    suffix = path.suffix.lower()
    if name in {".env.example", ".env.sample", ".env.template"}:
        return False
    return (
        name in SENSITIVE_FILE_NAMES
        or name == ".env"
        or name.startswith(".env.")
        or suffix in {".pem", ".p12", ".pfx", ".key"}
    )


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name.lower() in TEXT_FILENAMES
