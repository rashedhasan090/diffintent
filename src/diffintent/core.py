"""Analyze a unified diff and attach intent labels."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .classify import classify_path, risk_hints, summarize_categories
from .parse import FileDiff, parse_unified_diff


@dataclass
class LabeledFile:
    path: str
    category: str
    added: int
    deleted: int
    hunks: int
    is_binary: bool
    is_new: bool
    is_deleted: bool
    risks: list[str]


@dataclass
class Analysis:
    files: list[LabeledFile]
    summary: dict[str, int]
    totals: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "totals": self.totals,
            "files": [asdict(f) for f in self.files],
        }


def analyze_diff(text: str) -> Analysis:
    parsed: list[FileDiff] = parse_unified_diff(text)
    labeled: list[LabeledFile] = []
    for fd in parsed:
        category = classify_path(fd.path)
        risks = risk_hints(fd.path, fd.added, fd.deleted, fd.is_binary)
        if fd.is_deleted and "delete-only" not in risks and fd.added == 0:
            risks = list(dict.fromkeys(risks + ["delete-only"]))
        labeled.append(
            LabeledFile(
                path=fd.path,
                category=category,
                added=fd.added,
                deleted=fd.deleted,
                hunks=len(fd.hunks),
                is_binary=fd.is_binary,
                is_new=fd.is_new,
                is_deleted=fd.is_deleted,
                risks=risks,
            )
        )

    summary = summarize_categories(f.category for f in labeled)
    totals = {
        "files": len(labeled),
        "added": sum(f.added for f in labeled),
        "deleted": sum(f.deleted for f in labeled),
        "hunks": sum(f.hunks for f in labeled),
    }
    return Analysis(files=labeled, summary=summary, totals=totals)


def filter_files(analysis: Analysis, only: list[str] | None) -> Analysis:
    if not only:
        return analysis
    wanted = {c.lower() for c in only}
    files = [f for f in analysis.files if f.category in wanted]
    summary = summarize_categories(f.category for f in files)
    totals = {
        "files": len(files),
        "added": sum(f.added for f in files),
        "deleted": sum(f.deleted for f in files),
        "hunks": sum(f.hunks for f in files),
    }
    return Analysis(files=files, summary=summary, totals=totals)
