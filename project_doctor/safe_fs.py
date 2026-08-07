"""Bounded file-system access for untrusted customer repositories.

The scanner never executes target code, follows no symlinks/reparse points, and
reads only regular files with size limits. This is intentionally conservative:
an omitted file is preferable to accidentally following a link outside the
customer's submitted repository.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass, field
from pathlib import Path

from .policy import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_FILE_BYTES,
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_TEXT_BYTES,
    DEFAULT_MAX_TOTAL_BYTES,
    is_excluded_directory,
)


@dataclass(frozen=True, slots=True)
class FileEntry:
    path: Path
    relative_path: str
    size: int
    device: int
    inode: int


@dataclass(slots=True)
class WalkResult:
    root: Path
    files: list[FileEntry] = field(default_factory=list)
    skipped: dict[str, int] = field(default_factory=dict)
    total_bytes: int = 0
    partial: bool = False

    def skip(self, reason: str) -> None:
        self.skipped[reason] = self.skipped.get(reason, 0) + 1


def _is_reparse_point(file_stat: os.stat_result) -> bool:
    """Detect Windows junctions/reparse points without assuming Windows."""

    attributes = getattr(file_stat, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def _is_regular_file(file_stat: os.stat_result) -> bool:
    return stat.S_ISREG(file_stat.st_mode) and not _is_reparse_point(file_stat)


def _same_file(left: os.stat_result, right: os.stat_result) -> bool:
    """Avoid a basic time-of-check/time-of-use file replacement race."""

    return (
        left.st_dev == right.st_dev
        and left.st_ino == right.st_ino
        and stat.S_IFMT(left.st_mode) == stat.S_IFMT(right.st_mode)
    )


def walk_repository(
    target: Path,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> WalkResult:
    """Inventory safe regular files below ``target`` without following links."""

    root = target.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("The audit target must be an existing directory.")

    result = WalkResult(root=root)
    stack: list[tuple[Path, int]] = [(root, 0)]

    while stack:
        current, depth = stack.pop()
        if depth > max_depth:
            result.partial = True
            result.skip("depth_limit")
            continue

        try:
            with os.scandir(current) as iterator:
                entries = sorted(iterator, key=lambda item: item.name.casefold())
        except OSError:
            result.partial = True
            result.skip("unreadable_directory")
            continue

        for entry in entries:
            path = Path(entry.path)
            try:
                # DirEntry.stat(follow_symlinks=False) can expose zeroed device/
                # inode fields on Windows. lstat provides the identity used again
                # immediately before a bounded read.
                entry_stat = os.lstat(path)
            except OSError:
                result.partial = True
                result.skip("unstatable_entry")
                continue

            if stat.S_ISLNK(entry_stat.st_mode) or _is_reparse_point(entry_stat):
                result.skip("link_or_reparse_point")
                continue

            if stat.S_ISDIR(entry_stat.st_mode):
                if is_excluded_directory(path):
                    result.skip("excluded_directory")
                else:
                    stack.append((path, depth + 1))
                continue

            if not _is_regular_file(entry_stat):
                result.skip("non_regular_file")
                continue

            if entry_stat.st_size > max_file_bytes:
                result.partial = True
                result.skip("file_size_limit")
                continue
            if len(result.files) >= max_files:
                result.partial = True
                result.skip("file_count_limit")
                continue
            if result.total_bytes + entry_stat.st_size > max_total_bytes:
                result.partial = True
                result.skip("total_size_limit")
                continue

            relative = path.relative_to(root).as_posix()
            result.files.append(
                FileEntry(
                    path=path,
                    relative_path=relative,
                    size=entry_stat.st_size,
                    device=entry_stat.st_dev,
                    inode=entry_stat.st_ino,
                )
            )
            result.total_bytes += entry_stat.st_size

    return result


def read_text_bounded(entry: FileEntry, *, max_bytes: int = DEFAULT_MAX_TEXT_BYTES) -> str | None:
    """Read a UTF-8 file only when it remains the same safe regular file.

    A return value of ``None`` means that the file was not safe/readable text;
    callers should report a bounded omission instead of raising or guessing.
    """

    if entry.size > max_bytes:
        return None
    try:
        before = os.lstat(entry.path)
        if not _is_regular_file(before):
            return None
        if before.st_dev != entry.device or before.st_ino != entry.inode:
            return None
        with entry.path.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            if not _same_file(before, opened) or opened.st_size > max_bytes:
                return None
            content = handle.read(max_bytes + 1)
    except OSError:
        return None

    if len(content) > max_bytes:
        return None
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return None
