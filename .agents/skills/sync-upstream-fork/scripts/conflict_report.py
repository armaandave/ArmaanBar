#!/usr/bin/env python3
"""Print a compact Markdown report for Git conflict markers."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def conflicted_files() -> list[Path]:
    out = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        text=True,
    )
    return [Path(line) for line in out.splitlines() if line.strip()]


def clip(lines: list[str], limit: int) -> str:
    if len(lines) <= limit:
        return "\n".join(lines)
    head = "\n".join(lines[:limit])
    return f"{head}\n... ({len(lines) - limit} more lines)"


def parse_conflicts(text: str) -> list[tuple[list[str], list[str], str, str]]:
    conflicts: list[tuple[list[str], list[str], str, str]] = []
    ours: list[str] = []
    theirs: list[str] = []
    state = "normal"
    ours_label = "ours"
    theirs_label = "theirs"

    for raw in text.splitlines():
        if raw.startswith("<<<<<<<"):
            state = "ours"
            ours = []
            theirs = []
            ours_label = raw.removeprefix("<<<<<<<").strip() or "ours"
        elif raw.startswith("=======") and state in {"ours", "base"}:
            state = "theirs"
        elif raw.startswith("|||||||") and state == "ours":
            state = "base"
        elif raw.startswith(">>>>>>>") and state == "theirs":
            theirs_label = raw.removeprefix(">>>>>>>").strip() or "theirs"
            conflicts.append((ours, theirs, ours_label, theirs_label))
            state = "normal"
        elif state == "ours":
            ours.append(raw)
        elif state == "theirs":
            theirs.append(raw)

    return conflicts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context-lines", type=int, default=24)
    args = parser.parse_args()

    files = conflicted_files()
    if not files:
        print("No conflicted files.")
        return 0

    print(f"# Conflict Report\n\nConflicted files: {len(files)}")
    for path in files:
        print(f"\n## {path}")
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            print("\nBinary or non-UTF-8 conflict; inspect with Git directly.")
            continue

        conflicts = parse_conflicts(text)
        if not conflicts:
            print("\nNo conflict markers found; inspect unmerged stages with Git.")
            continue

        for index, (ours, theirs, ours_label, theirs_label) in enumerate(conflicts, 1):
            print(f"\n### Hunk {index}")
            print(f"\nOurs ({ours_label}):\n```")
            print(clip(ours, args.context_lines))
            print("```")
            print(f"\nUpstream ({theirs_label}):\n```")
            print(clip(theirs, args.context_lines))
            print("```")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
