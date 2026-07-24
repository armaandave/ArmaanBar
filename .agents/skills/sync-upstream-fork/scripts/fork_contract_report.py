#!/usr/bin/env python3
"""Report upstream changes that require a fork-owner decision before a sync."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


CONTRACT_PATH = Path(".agents/fork-contract.md")
INFRASTRUCTURE_PREFIXES = (
    "AGENTS.md",
    ".agents/fork-contract.md",
    ".agents/skills/sync-upstream-fork/",
)


@dataclass
class ContractItem:
    name: str
    paths: list[str]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def contract_items(contract: Path) -> list[ContractItem]:
    items: list[ContractItem] = []
    current: ContractItem | None = None
    collecting_paths = False

    for line in contract.read_text().splitlines():
        if line.startswith("## "):
            if current:
                items.append(current)
            current = ContractItem(name=line.removeprefix("## "), paths=[])
            collecting_paths = False
        elif current and line == "- Paths:":
            collecting_paths = True
        elif collecting_paths and line.startswith("  - `") and line.endswith("`"):
            current.paths.append(line[5:-1])
        elif line.startswith("- "):
            collecting_paths = False

    if current:
        items.append(current)

    invalid = [item.name for item in items if not item.paths]
    if invalid:
        raise ValueError(f"Contract item missing Paths: {', '.join(invalid)}")
    return items


def changed_files(revision_range: str) -> list[str]:
    output = git("diff", "--name-only", revision_range)
    return [line for line in output.splitlines() if line]


def covers(contract_path: str, file_path: str) -> bool:
    return file_path == contract_path or (
        contract_path.endswith("/") and file_path.startswith(contract_path)
    )


def is_infrastructure(file_path: str) -> bool:
    return any(
        file_path == prefix or file_path.startswith(prefix)
        for prefix in INFRASTRUCTURE_PREFIXES
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", default="upstream/main")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 2 when a fork-owner decision is required.",
    )
    args = parser.parse_args()

    if not CONTRACT_PATH.is_file():
        print(f"Missing required fork contract: {CONTRACT_PATH}", file=sys.stderr)
        return 1

    try:
        items = contract_items(CONTRACT_PATH)
        base = git("merge-base", "HEAD", args.upstream)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"Could not create fork-contract report: {error}", file=sys.stderr)
        return 1

    upstream_files = changed_files(f"{base}..{args.upstream}")
    fork_files = changed_files(f"{base}..HEAD")
    protected_changes = [
        (item, [path for path in upstream_files if any(covers(scope, path) for scope in item.paths)])
        for item in items
    ]
    protected_changes = [(item, paths) for item, paths in protected_changes if paths]
    uncovered_fork_files = [
        path
        for path in fork_files
        if not is_infrastructure(path) and not any(covers(scope, path) for item in items for scope in item.paths)
    ]

    print(f"Fork contract base: {base}")
    print(f"Upstream changes: {len(upstream_files)} file(s)")
    print(f"Fork-only changes: {len(fork_files)} file(s)")

    if protected_changes:
        print("\nOWNER DECISION REQUIRED: upstream touches protected fork behavior")
        for item, paths in protected_changes:
            print(f"- {item.name}")
            print("  " + "\n  ".join(paths))

    if uncovered_fork_files:
        print("\nOWNER DECISION REQUIRED: fork-only paths missing from the contract")
        print("- " + "\n- ".join(uncovered_fork_files))

    if not protected_changes and not uncovered_fork_files:
        print("\nNo fork-contract decision required.")

    return 2 if args.check and (protected_changes or uncovered_fork_files) else 0


if __name__ == "__main__":
    raise SystemExit(main())
