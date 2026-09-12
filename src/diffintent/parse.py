"""Parse unified diffs into per-file change records. Never applies the patch."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class Hunk:
    header: str
    added: int = 0
    deleted: int = 0


@dataclass
class FileDiff:
    path: str
    old_path: str | None = None
    is_binary: bool = False
    is_new: bool = False
    is_deleted: bool = False
    added: int = 0
    deleted: int = 0
    hunks: list[Hunk] = field(default_factory=list)


def _strip_prefix(path: str) -> str:
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def parse_unified_diff(text: str) -> list[FileDiff]:
    """Parse a unified diff string into FileDiff records."""
    files: list[FileDiff] = []
    current: FileDiff | None = None
    hunk: Hunk | None = None

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("diff --git "):
            if current is not None:
                files.append(current)
            parts = line.split()
            right = parts[-1] if len(parts) >= 4 else "unknown"
            path = _strip_prefix(right)
            current = FileDiff(path=path)
            hunk = None
            i += 1
            continue

        if current is None:
            if line.startswith("--- "):
                current = FileDiff(path="unknown")
            else:
                i += 1
                continue

        if line.startswith("Binary files ") and " differ" in line:
            current.is_binary = True
            i += 1
            continue

        if line.startswith("new file mode"):
            current.is_new = True
            i += 1
            continue

        if line.startswith("deleted file mode"):
            current.is_deleted = True
            i += 1
            continue

        if line.startswith("--- "):
            old = line[4:].strip()
            if old != "/dev/null":
                old_path = old.split("\t", 1)[0]
                current.old_path = _strip_prefix(old_path)
            else:
                current.is_new = True
            i += 1
            continue

        if line.startswith("+++ "):
            new = line[4:].strip()
            if new == "/dev/null":
                current.is_deleted = True
            else:
                new_path = new.split("\t", 1)[0]
                current.path = _strip_prefix(new_path)
            i += 1
            continue

        if line.startswith("@@"):
            hunk = Hunk(header=line)
            current.hunks.append(hunk)
            i += 1
            continue

        if hunk is not None:
            if line.startswith("+") and not line.startswith("+++"):
                hunk.added += 1
                current.added += 1
            elif line.startswith("-") and not line.startswith("---"):
                hunk.deleted += 1
                current.deleted += 1
            i += 1
            continue

        i += 1

    if current is not None:
        files.append(current)

    return files


def iter_file_paths(files: list[FileDiff]) -> Iterator[str]:
    for f in files:
        yield f.path
