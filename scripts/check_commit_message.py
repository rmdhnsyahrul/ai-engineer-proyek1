#!/usr/bin/env python3
"""Validate documentation-grade Git commit messages using only the stdlib."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_TYPES = (
    "feat",
    "fix",
    "refactor",
    "perf",
    "docs",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
)
SUBJECT_PATTERN = re.compile(
    rf"^(?:{'|'.join(ALLOWED_TYPES)})(?:\([a-z0-9][a-z0-9-]*\))?!?: .+$"
)
REQUIRED_SECTIONS = ("Why:", "What changed:", "How to verify:")
OPTIONAL_SECTIONS = ("Notes / Tradeoffs:",)
ALL_SECTIONS = REQUIRED_SECTIONS + OPTIONAL_SECTIONS
TRAILER_PATTERN = re.compile(
    r"^(?:Roadmap|Refs|Co-authored-by|Signed-off-by):\s+\S.+$",
    re.IGNORECASE,
)
EXEMPT_PREFIXES = ("Merge ", "Revert ", "fixup! ", "squash! ")


def _clean_lines(message: str) -> list[str]:
    """Remove Git template comments while preserving meaningful blank lines."""
    lines = [line.rstrip() for line in message.splitlines()]
    return [line for line in lines if not line.lstrip().startswith("#")]


def _section_content(lines: list[str], section_index: int) -> list[str]:
    content: list[str] = []
    for line in lines[section_index + 1 :]:
        if line in ALL_SECTIONS or TRAILER_PATTERN.match(line):
            break
        if line.strip():
            content.append(line.strip())
    return content


def validate_commit_message(message: str) -> list[str]:
    """Return validation errors; an empty list means the message is valid."""
    lines = _clean_lines(message)
    while lines and not lines[-1]:
        lines.pop()

    if not lines:
        return ["commit message is empty"]

    subject = lines[0]
    if subject.startswith(EXEMPT_PREFIXES):
        return []

    errors: list[str] = []
    if len(subject) > 72:
        errors.append(f"subject is {len(subject)} characters; maximum is 72")
    if not SUBJECT_PATTERN.fullmatch(subject):
        errors.append(
            "subject must match '<type>(<scope>): <summary>' using an allowed type"
        )
    if subject.endswith("."):
        errors.append("subject must not end with a period")

    if len(lines) < 2 or lines[1] != "":
        errors.append("add one blank line between the subject and body")

    section_positions: dict[str, int] = {}
    for section in REQUIRED_SECTIONS:
        try:
            section_positions[section] = lines.index(section)
        except ValueError:
            errors.append(f"missing required section '{section}'")

    if len(section_positions) == len(REQUIRED_SECTIONS):
        positions = [section_positions[name] for name in REQUIRED_SECTIONS]
        if positions != sorted(positions):
            errors.append(
                "required sections must appear in order: "
                + ", ".join(REQUIRED_SECTIONS)
            )

        for section, index in section_positions.items():
            if not _section_content(lines, index):
                errors.append(f"section '{section}' must contain documentation")

    return errors


def _read_commit(commit: str) -> str:
    result = subprocess.run(
        ["git", "show", "-s", "--format=%B", commit],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _commits_in_range(commit_range: str) -> list[str]:
    result = subprocess.run(
        ["git", "rev-list", "--reverse", commit_range],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.split()


def _report(label: str, errors: list[str]) -> bool:
    if not errors:
        print(f"commit message OK: {label}")
        return True

    print(f"invalid commit message: {label}", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    print(
        "See docs/commit-convention.md for the required format.",
        file=sys.stderr,
    )
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message_file", nargs="?", type=Path)
    parser.add_argument(
        "--commit-range",
        help="validate every commit in a Git revision range, for example main..HEAD",
    )
    args = parser.parse_args()

    if bool(args.message_file) == bool(args.commit_range):
        parser.error("provide either MESSAGE_FILE or --commit-range, not both")

    if args.message_file:
        errors = validate_commit_message(args.message_file.read_text(encoding="utf-8"))
        return 0 if _report(str(args.message_file), errors) else 1

    success = True
    try:
        commits = _commits_in_range(args.commit_range)
        if not commits:
            print(f"no commits to validate in range: {args.commit_range}")
            return 0
        for commit in commits:
            errors = validate_commit_message(_read_commit(commit))
            success = _report(commit, errors) and success
    except subprocess.CalledProcessError as exc:
        print(exc.stderr or str(exc), file=sys.stderr)
        return 2
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())