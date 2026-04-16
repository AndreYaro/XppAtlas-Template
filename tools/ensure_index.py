#!/usr/bin/env python3
"""
Ensure .claude/index is present and up to date.

Examples:
  python tools/ensure_index.py
  python tools/ensure_index.py --model DYSNepi
  python tools/ensure_index.py --quiet
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "Models"
INDEX_DIR = REPO_ROOT / ".claude" / "index"


def find_source_dirs(model_filter: str | None = None) -> list[Path]:
    dirs = []
    if not MODELS_DIR.is_dir():
        return dirs
    for model_dir in sorted(MODELS_DIR.iterdir()):
        if not model_dir.is_dir() or model_dir.name.startswith("_"):
            continue
        if model_filter and model_filter.lower() not in model_dir.name.lower():
            continue
        source_dir = model_dir / "Source"
        if source_dir.is_dir():
            dirs.append(source_dir)
    return dirs


def newest_xml_mtime(source_dir: Path) -> float:
    newest = 0.0
    for xml_file in source_dir.rglob("*.xml"):
        try:
            newest = max(newest, xml_file.stat().st_mtime)
        except OSError:
            continue
    return newest


def model_index_files(model_name: str) -> list[Path]:
    return [
        INDEX_DIR / f"{model_name}.json",
        INDEX_DIR / f"{model_name}_summary.json",
        INDEX_DIR / f"{model_name}_cache.json",
    ]


def model_needs_update(source_dir: Path) -> bool:
    model_name = source_dir.parent.name
    index_files = model_index_files(model_name)
    if not all(path.is_file() for path in index_files):
        return True

    try:
        oldest_index_mtime = min(path.stat().st_mtime for path in index_files)
    except OSError:
        return True

    return newest_xml_mtime(source_dir) > oldest_index_mtime


def cross_summary_needs_update(source_dirs: list[Path]) -> bool:
    cross_summary = INDEX_DIR / "_all_summary.json"
    if not cross_summary.is_file():
        return True

    try:
        cross_summary_mtime = cross_summary.stat().st_mtime
    except OSError:
        return True

    for source_dir in source_dirs:
        model_file = INDEX_DIR / f"{source_dir.parent.name}.json"
        if not model_file.is_file():
            return True
        try:
            if model_file.stat().st_mtime > cross_summary_mtime:
                return True
        except OSError:
            return True
    return False


def needs_update(source_dirs: list[Path]) -> bool:
    if not source_dirs:
        return False
    if not INDEX_DIR.is_dir():
        return True
    if any(model_needs_update(source_dir) for source_dir in source_dirs):
        return True
    return cross_summary_needs_update(source_dirs)


def run_incremental(model_filter: str | None) -> int:
    command = [sys.executable, "tools/index_all.py", "--incremental"]
    if model_filter:
        command.extend(["--model", model_filter])
    return subprocess.run(command, cwd=REPO_ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure model indexes exist and are current.")
    parser.add_argument("--model", "-m", help="Only evaluate models whose name contains this string")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    args = parser.parse_args()

    source_dirs = find_source_dirs(args.model)
    if not source_dirs:
        if not args.quiet:
            print("No Source/ directories found under Models/.")
        return 0

    if not needs_update(source_dirs):
        if not args.quiet:
            print("Indexes are already current.")
        return 0

    if not args.quiet:
        print("Refreshing indexes incrementally...")
    return run_incremental(args.model)


if __name__ == "__main__":
    raise SystemExit(main())
