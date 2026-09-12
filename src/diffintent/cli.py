"""Command-line interface for diffintent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import CATEGORIES, __version__
from .core import analyze_diff, filter_files


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _format_human(analysis, list_hunks: bool) -> str:
    lines: list[str] = []
    lines.append(
        f"files={analysis.totals['files']}  "
        f"+{analysis.totals['added']}/-{analysis.totals['deleted']}  "
        f"hunks={analysis.totals['hunks']}"
    )
    if analysis.summary:
        parts = [f"{k}:{v}" for k, v in analysis.summary.items()]
        lines.append("by intent: " + "  ".join(parts))
    lines.append("")
    for f in analysis.files:
        risk = f"  [{', '.join(f.risks)}]" if f.risks else ""
        flags = []
        if f.is_new:
            flags.append("new")
        if f.is_deleted:
            flags.append("deleted")
        if f.is_binary:
            flags.append("binary")
        flag_s = f" ({', '.join(flags)})" if flags else ""
        lines.append(
            f"  [{f.category:9}] +{f.added:<4}/-{f.deleted:<4}  "
            f"{f.path}{flag_s}{risk}"
        )
        if list_hunks and f.hunks:
            lines.append(f"               hunks={f.hunks}")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="diffintent",
        description=(
            "Classify unified-diff files by intent "
            "(tests, docs, deps, config, ci, generated, code). "
            "Reads a patch; never applies it."
        ),
    )
    p.add_argument(
        "diff",
        nargs="?",
        default="-",
        help="Path to a unified diff, or '-' for stdin (default)",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON")
    p.add_argument(
        "--only",
        action="append",
        metavar="CATEGORY",
        choices=list(CATEGORIES),
        help="Keep only this category (repeatable)",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=True,
        help="Human summary (default)",
    )
    p.add_argument(
        "--list-hunks",
        action="store_true",
        help="Include hunk counts per file in human output",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = _read_input(args.diff)
    except OSError as exc:
        print(f"diffintent: cannot read input: {exc}", file=sys.stderr)
        return 2

    if not text.strip():
        print("diffintent: empty diff", file=sys.stderr)
        return 2

    analysis = analyze_diff(text)
    analysis = filter_files(analysis, args.only)

    if args.json:
        json.dump(analysis.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_human(analysis, args.list_hunks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
