"""Path-based intent classification and light risk hints for diff files."""

from __future__ import annotations

import os
import re
from typing import Iterable

from . import CATEGORIES


def _norm(path: str) -> str:
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def classify_path(path: str) -> str:
    """Return the primary intent category for a repository-relative path."""
    p = _norm(path)
    lower = p.lower()
    base = os.path.basename(lower)
    parts = [seg for seg in lower.split("/") if seg]

    # CI before generic yaml/config
    if (
        (".github" in parts and "workflows" in parts)
        or ".circleci" in parts
        or base in {"jenkinsfile", ".gitlab-ci.yml"}
        or lower.endswith("/.gitlab-ci.yml")
        or lower == ".gitlab-ci.yml"
    ):
        return "ci"

    if (
        "tests" in parts
        or "__tests__" in parts
        or (len(parts) >= 1 and parts[0] == "test")
        or base.startswith("test_")
        or base.endswith("_test.py")
        or ".spec." in base
        or ".test." in base
        or base.endswith(("_spec.rb", ".test.js", ".test.ts", ".spec.ts", ".spec.js"))
    ):
        return "tests"

    doc_stems = (
        "readme",
        "changelog",
        "license",
        "contributing",
        "code_of_conduct",
        "authors",
        "history",
    )
    if (
        base.endswith((".md", ".rst", ".adoc"))
        or any(base.startswith(s) for s in doc_stems)
        or "docs" in parts
        or (len(parts) >= 1 and parts[0] == "doc")
    ):
        return "docs"

    dep_names = {
        "requirements.txt",
        "pyproject.toml",
        "poetry.lock",
        "pipfile",
        "pipfile.lock",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "cargo.toml",
        "cargo.lock",
        "go.mod",
        "go.sum",
        "gemfile",
        "gemfile.lock",
        "composer.json",
        "composer.lock",
    }
    if base in dep_names or (base.startswith("requirements") and base.endswith(".txt")):
        return "deps"
    if base.endswith(".lock"):
        return "deps"

    if (
        "dist" in parts
        or "build" in parts
        or ".min.js" in base
        or base.endswith("_pb2.py")
        or ".generated." in base
        or base.endswith((".generated.ts", ".generated.js"))
    ):
        return "generated"

    config_bases = {
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "makefile",
        "cmakelists.txt",
        ".editorconfig",
        ".gitignore",
        ".gitattributes",
        ".nvmrc",
        ".python-version",
        ".tool-versions",
    }
    if (
        base in config_bases
        or base.startswith("dockerfile")
        or base.startswith(".env")
        or base.endswith((".ini", ".cfg", ".conf"))
        or base.endswith((".yml", ".yaml", ".toml"))
        or re.fullmatch(r"\..*rc", base)
    ):
        return "config"

    return "code"


def risk_hints(path: str, added: int, deleted: int, is_binary: bool) -> list[str]:
    """Lightweight review hints (not security advisories)."""
    hints: list[str] = []
    if is_binary:
        hints.append("binary")
    if deleted > 0 and added == 0:
        hints.append("delete-only")
    elif deleted > added * 2 and deleted >= 20:
        hints.append("delete-heavy")
    if added >= 200:
        hints.append("large-add")
    lower = _norm(path).lower()
    if lower.startswith("../") or lower.startswith("/"):
        hints.append("unusual-path")
    return hints


def summarize_categories(categories: Iterable[str]) -> dict[str, int]:
    counts = {c: 0 for c in CATEGORIES}
    for cat in categories:
        if cat in counts:
            counts[cat] += 1
        else:
            counts[cat] = counts.get(cat, 0) + 1
    return {k: v for k, v in counts.items() if v}
