#!/usr/bin/env python3
"""Export documented commits as compact Markdown context for future work."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def _git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def export_context(commit_range: str) -> str:
    commits = _git("rev-list", "--reverse", commit_range).splitlines()
    sections = ["# Development Context", "", f"Commit range: `{commit_range}`"]

    if not commits:
        sections.extend(["", "No documented commits in this range."])
        return "\n".join(sections) + "\n"

    for commit in commits:
        short_hash = _git("rev-parse", "--short", commit)
        subject = _git("show", "-s", "--format=%s", commit)
        body = _git("show", "-s", "--format=%b", commit)
        sections.extend(["", f"## {short_hash} — {subject}"])
        if body:
            sections.extend(["", body])

    return "\n".join(sections) + "\n"


def default_range() -> str:
    baseline_path = Path(".commit-documentation-baseline")
    if baseline_path.exists():
        baseline = baseline_path.read_text(encoding="utf-8").strip()
        if baseline:
            return f"{baseline}..HEAD"
    return "HEAD"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit-range", default=default_range())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    content = export_context(args.commit_range)
    if args.output:
        args.output.write_text(content, encoding="utf-8")
        print(f"wrote commit context to {args.output}")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())