#!/usr/bin/env python3
"""
X++ Multi-Model Indexer — indexes all models found under Models/ in one pass.

Usage:
  python tools/index_all.py                     # full re-index of all models
  python tools/index_all.py --incremental       # skip unchanged files
  python tools/index_all.py --model DYSBilling  # index only matching model(s)

Output:
  .claude/index/<ModelName>.json         full index per model
  .claude/index/<ModelName>_summary.json compact summary per model
  .claude/index/_all_summary.json        cross-model overview (names + summaries)
"""

import argparse
import json
import sys
from pathlib import Path

# Allow importing sibling module
sys.path.insert(0, str(Path(__file__).parent))
from index_model import index_source, write_outputs  # noqa: E402


MODELS_DIR = Path("Models")
INDEX_DIR = Path(".claude/index")


def find_source_dirs(model_filter: str | None = None) -> list[Path]:
    """Return all Source/ directories under Models/, optionally filtered by name."""
    dirs = []
    if not MODELS_DIR.is_dir():
        return dirs
    for model_dir in sorted(MODELS_DIR.iterdir()):
        if not model_dir.is_dir() or model_dir.name.startswith("_"):
            continue
        if model_filter and model_filter.lower() not in model_dir.name.lower():
            continue
        source = model_dir / "Source"
        if source.is_dir():
            dirs.append(source)
    return dirs


def build_cross_model_summary(all_indexes: list[dict]) -> dict:
    """
    Compact cross-model overview: per model, just class/table names + summaries.
    Used to give an agent a bird's-eye view of ALL models at once.
    """
    models = []
    for idx in all_indexes:
        objects = idx["objects"]
        classes = [
            {k: v for k, v in {
                "n": o["name"],
                "role": o.get("role"),
                "s": o.get("summary", ""),
                "cocTarget": o.get("cocTarget"),
            }.items() if v}
            for o in objects if o["type"] == "class"
        ]
        tables = [o["name"] for o in objects if o["type"] == "table"]
        services = [
            {"n": o["name"], "ops": o.get("operations", [])}
            for o in objects if o["type"] == "service"
        ]
        models.append({
            "model": idx["model"],
            "indexedAt": idx["indexedAt"],
            "stats": idx["stats"],
            "cocMap": idx.get("cocMap", {}),
            "classes": classes,
            "tables": tables,
            "services": services,
        })
    return {"models": models}


def main():
    parser = argparse.ArgumentParser(description="Index all D365 F&O models.")
    parser.add_argument("--incremental", action="store_true",
                        help="Skip files whose mtime is unchanged since last index")
    parser.add_argument("--model", "-m", help="Only index models whose name contains this string")
    args = parser.parse_args()

    source_dirs = find_source_dirs(args.model)
    if not source_dirs:
        print("No Source/ directories found under Models/", file=sys.stderr)
        sys.exit(1)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    all_indexes = []
    total_objects = 0

    for source_path in source_dirs:
        model_name = source_path.parent.name
        out_path = INDEX_DIR / f"{model_name}.json"
        print(f"\n[{model_name}]")
        index = index_source(source_path, incremental=args.incremental, existing_out=out_path)
        summary_path = write_outputs(index, out_path)
        n = len(index["objects"])
        total_objects += n
        all_indexes.append(index)
        print(f"  -> {n} objects  |  index: {out_path}  |  summary: {summary_path}")
        if index.get("cocMap"):
            for ext, target in index["cocMap"].items():
                print(f"     CoC: {ext} -> {target['kind']}:{target['name']}")

    # Cross-model summary
    cross = build_cross_model_summary(all_indexes)
    cross_path = INDEX_DIR / "_all_summary.json"
    with open(cross_path, "w", encoding="utf-8") as f:
        json.dump(cross, f, ensure_ascii=False, indent=2)

    cross_size = cross_path.stat().st_size
    compact_size = len(json.dumps(cross, separators=(",", ":")))

    print(f"\n{'-'*60}")
    print(f"Models indexed:  {len(all_indexes)}")
    print(f"Total objects:   {total_objects}")
    print(f"Cross-model:     {cross_path}  ({cross_size:,} bytes, ~{compact_size//4:,} tokens)")
    print(f"{'-'*60}")
    print("\nTo search: python tools/search_index.py <query> [--type class] [--model X]")
    print("Stats:     python tools/search_index.py --stats")


if __name__ == "__main__":
    main()
