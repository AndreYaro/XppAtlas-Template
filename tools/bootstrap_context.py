#!/usr/bin/env python3
"""
Resolve the active D365 task/model/project context and surface relevant index files.

Examples:
  python tools/bootstrap_context.py
  python tools/bootstrap_context.py Models/DYSNepi/Tasks/22822_UpdateInvoiceWIthKSeFFields
  python tools/bootstrap_context.py --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import re
import subprocess


REPO_ROOT = Path(__file__).resolve().parent.parent


def ensure_indexes(model_name: str | None) -> None:
    command = [sys.executable, "tools/ensure_index.py", "--quiet"]
    if model_name:
        command.extend(["--model", model_name])
    subprocess.run(command, cwd=REPO_ROOT, check=False)


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_scalar(value: str):
    value = strip_quotes(value)
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    return value


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_multiline_text(block_lines: list[str]) -> str:
    parts = []
    for line in block_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            parts.append(stripped)
    return " ".join(parts)


def next_content_line(lines: list[str], start: int) -> tuple[int | None, str | None]:
    i = start
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith("#"):
            return i, lines[i]
        i += 1
    return None, None


def parse_multiline(lines: list[str], start: int, parent_indent: int) -> tuple[str, int]:
    block = []
    i = start
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if stripped and indent_of(raw) <= parent_indent:
            break
        block.append(raw)
        i += 1
    return parse_multiline_text(block), i


def parse_list(lines: list[str], start: int, indent: int) -> tuple[list, int]:
    items = []
    i = start
    current = None

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        current_indent = indent_of(raw)

        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if current_indent < indent:
            break
        if current_indent == indent and stripped.startswith("- "):
            payload = stripped[2:].strip()
            if not payload:
                current = {}
                items.append(current)
                i += 1
                continue

            if ":" in payload:
                key, value = payload.split(":", 1)
                key = key.strip()
                value = value.strip()
                current = {}
                items.append(current)
                if value == ">":
                    current[key], i = parse_multiline(lines, i + 1, indent)
                    continue
                if value:
                    current[key] = parse_scalar(value)
                    i += 1
                    continue

                next_i, next_line = next_content_line(lines, i + 1)
                if next_i is None or indent_of(next_line) <= indent:
                    current[key] = {}
                    i += 1
                    continue
                child_indent = indent_of(next_line)
                if next_line.strip().startswith("- "):
                    current[key], i = parse_list(lines, next_i, child_indent)
                else:
                    current[key], i = parse_dict(lines, next_i, child_indent)
                continue

            current = parse_scalar(payload)
            items.append(current)
            i += 1
            continue

        if current_indent > indent and isinstance(current, dict) and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == ">":
                current[key], i = parse_multiline(lines, i + 1, current_indent)
                continue
            if value:
                current[key] = parse_scalar(value)
                i += 1
                continue

            next_i, next_line = next_content_line(lines, i + 1)
            if next_i is None or indent_of(next_line) <= current_indent:
                current[key] = {}
                i += 1
                continue
            child_indent = indent_of(next_line)
            if next_line.strip().startswith("- "):
                current[key], i = parse_list(lines, next_i, child_indent)
            else:
                current[key], i = parse_dict(lines, next_i, child_indent)
            continue

        break

    return items, i


def parse_dict(lines: list[str], start: int, indent: int = 0) -> tuple[dict, int]:
    data = {}
    i = start

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        current_indent = indent_of(raw)

        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if current_indent < indent:
            break
        if current_indent > indent:
            i += 1
            continue
        if stripped.startswith("- ") or ":" not in stripped:
            break

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == ">":
            data[key], i = parse_multiline(lines, i + 1, indent)
            continue
        if value:
            data[key] = parse_scalar(value)
            i += 1
            continue

        next_i, next_line = next_content_line(lines, i + 1)
        if next_i is None or indent_of(next_line) <= indent:
            data[key] = {}
            i += 1
            continue

        child_indent = indent_of(next_line)
        if next_line.strip().startswith("- "):
            data[key], i = parse_list(lines, next_i, child_indent)
        else:
            data[key], i = parse_dict(lines, next_i, child_indent)

    return data, i


def parse_context_file(path: Path) -> dict:
    parsed, _ = parse_dict(path.read_text(encoding="utf-8").splitlines(), 0, 0)
    return parsed


def find_context_chain(start_path: Path) -> list[Path]:
    current = start_path.resolve()
    if current.is_file():
        current = current.parent

    candidates = []
    for directory in [current, *current.parents]:
        context_file = directory / "context_setup.md"
        if context_file.is_file():
            candidates.append(context_file)
        if directory == REPO_ROOT:
            break

    # Order from project -> model -> task so later files override earlier ones.
    return list(reversed(candidates))


def merge_contexts(paths: list[Path]) -> tuple[dict, list[dict]]:
    merged: dict = {}
    layers: list[dict] = []
    for path in paths:
        parsed = parse_context_file(path)
        parsed["_path"] = str(path.relative_to(REPO_ROOT))
        layers.append(parsed)
        for key, value in parsed.items():
            if key.startswith("_"):
                continue
            merged[key] = value
    return merged, layers


def infer_model_name(paths: list[Path]) -> str | None:
    pattern = re.compile(r"Models[\\/](?P<model>[^\\/]+)[\\/]")
    for path in reversed(paths):
        match = pattern.search(str(path))
        if match:
            return match.group("model")
    return None


def build_index_info(model_name: str | None) -> dict:
    index_dir = REPO_ROOT / ".claude" / "index"
    info = {
        "cross_model": index_dir / "_all_summary.json",
        "per_model_summary": None,
        "per_model_full": None,
        "search_command": "python tools/search_index.py <query> [--type class] [--model ModelName]",
        "rebuild_command": "python tools/index_all.py --incremental",
    }
    if model_name:
        info["per_model_summary"] = index_dir / f"{model_name}_summary.json"
        info["per_model_full"] = index_dir / f"{model_name}.json"
    return info


def relativize(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def make_output(start_path: Path) -> dict:
    chain = find_context_chain(start_path)
    merged, layers = merge_contexts(chain)
    model_name = infer_model_name(chain)
    ensure_indexes(model_name)
    indexes = build_index_info(model_name)

    output = {
        "startPath": relativize(start_path.resolve()),
        "repoRoot": str(REPO_ROOT),
        "contextChain": [layer["_path"] for layer in layers],
        "effectiveContext": merged,
        "modelName": model_name,
        "indexFiles": {
            "crossModel": relativize(indexes["cross_model"]),
            "perModelSummary": relativize(indexes["per_model_summary"]),
            "perModelFull": relativize(indexes["per_model_full"]),
        },
        "recommendedFlow": [
            "Read the nearest context_setup.md chain project -> model -> task.",
            "Read the per-model summary first when a model is known.",
            "Use the full model index when method, field, reference, or dependency detail is needed.",
            "Use the cross-model summary when the model is unknown or the task spans multiple models.",
            "Verify any code or XML edits against the real source files before changing anything.",
        ],
        "commands": {
            "rebuild": indexes["rebuild_command"],
            "search": indexes["search_command"],
        },
    }
    return output


def print_human(output: dict) -> None:
    print("Bootstrap context")
    print(f"  Start path:      {output['startPath']}")
    print(f"  Model:           {output['modelName'] or '-'}")
    print("  Context chain:")
    for path in output["contextChain"]:
        print(f"    - {path}")

    ctx = output["effectiveContext"]
    print("  Effective values:")
    for key in ("ProjectPrefix", "LabelFile", "LabelLanguages", "UserVISA", "TaskID", "TaskName"):
        if key in ctx:
            print(f"    - {key}: {ctx[key]}")

    refs = ctx.get("reference_paths", [])
    if refs:
        print("  Reference paths:")
        for item in refs:
            if isinstance(item, dict):
                print(f"    - {item.get('path', '')}  ({item.get('description', '')})")
            else:
                print(f"    - {item}")

    print("  Index files:")
    print(f"    - Cross-model:      {output['indexFiles']['crossModel']}")
    print(f"    - Per-model summary:{' ' if output['indexFiles']['perModelSummary'] else ''} {output['indexFiles']['perModelSummary'] or '-'}")
    print(f"    - Per-model full:   {output['indexFiles']['perModelFull'] or '-'}")

    print("  Recommended flow:")
    for step in output["recommendedFlow"]:
        print(f"    - {step}")

    print("  Commands:")
    print(f"    - Rebuild: {output['commands']['rebuild']}")
    print(f"    - Search:  {output['commands']['search']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Show the active context chain and recommended model indexes.")
    parser.add_argument("path", nargs="?", default=".", help="Task, model, file, or repo path to resolve from")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    start_path = (REPO_ROOT / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
    if not start_path.exists():
        print(f"ERROR: path not found: {start_path}", file=sys.stderr)
        return 1

    output = make_output(start_path)
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_human(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
