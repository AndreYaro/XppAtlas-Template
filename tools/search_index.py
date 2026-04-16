#!/usr/bin/env python3
"""
X++ Index Search — queries .claude/index/*.json files.

Examples:
  python tools/search_index.py invoice                         # name contains "invoice" (all models)
  python tools/search_index.py staging --type table            # tables whose name contains "staging"
  python tools/search_index.py DataContract --attr             # objects with [DataContract] attribute
  python tools/search_index.py ExtensionOf --attr              # all CoC extensions
  python tools/search_index.py legalEntity --field             # objects with a field named "legalEntity"
  python tools/search_index.py ImportInvoices --method         # objects with method "ImportInvoices"
  python tools/search_index.py DYSBillingImportService --refs  # what references this class
  python tools/search_index.py "" --model DYSBilling           # all objects in model
  python tools/search_index.py "" --role contract              # all contracts
  python tools/search_index.py "" --coc                        # list all CoC extensions
  python tools/search_index.py "" --deps DYSBillingOrchestrator # show deps of a class
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


INDEX_DIR = Path(".claude/index")


def ensure_indexes(model_filter: str | None = None) -> None:
    command = [sys.executable, "tools/ensure_index.py", "--quiet"]
    if model_filter:
        command.extend(["--model", model_filter])
    subprocess.run(command, check=False)


def load_indexes(model_filter: str | None = None) -> list[tuple[str, dict]]:
    """Load all *_index*.json (not summary/cache) from INDEX_DIR."""
    indexes = []
    pattern = "*.json"
    for f in sorted(INDEX_DIR.glob(pattern)):
        if "_summary" in f.name or "_cache" in f.name:
            continue
        if model_filter and model_filter.lower() not in f.stem.lower():
            continue
        try:
            with open(f, encoding="utf-8") as fp:
                indexes.append((f.stem, json.load(fp)))
        except Exception as e:
            print(f"WARN: could not load {f}: {e}", file=sys.stderr)
    return indexes


def match(value: str, query: str) -> bool:
    return query.lower() in value.lower()


def fmt_obj(model: str, obj: dict, verbose: bool = False) -> str:
    name = obj.get("name", "?")
    otype = obj.get("type", "")
    role = obj.get("role", "")
    summary = obj.get("summary", "")
    coc = obj.get("cocTarget")

    tag = f"[{otype}]" if not role or role == otype else f"[{otype}/{role}]"
    line = f"  {model:<30} {tag:<22} {name}"
    if coc:
        line += f"  ->CoC-> {coc['kind']}:{coc['name']}"
    if summary and verbose:
        line += f"\n    {summary}"
    elif summary:
        short = summary[:80] + ("…" if len(summary) > 80 else "")
        line += f"\n    {short}"
    return line


def search(query: str, indexes: list, args) -> None:
    results = []

    for model, idx in indexes:
        objects = idx.get("objects", [])

        for obj in objects:
            name = obj.get("name", "")
            matched = False

            # Filter by type
            if args.type and args.type.lower() not in obj.get("type", "").lower():
                continue

            # Filter by role
            if args.role and args.role.lower() not in obj.get("role", "").lower():
                continue

            # --attr: match against attributes list
            if args.attr:
                if any(match(a, query) for a in obj.get("attributes", [])):
                    matched = True
                for m in obj.get("methods", []):
                    if any(match(a, query) for a in m.get("attributes", [])):
                        matched = True
                        break

            # --field: match against field names
            elif args.field:
                if any(match(f.get("name", ""), query) for f in obj.get("fields", [])):
                    matched = True

            # --method: match against method names
            elif args.method:
                if any(match(m.get("name", ""), query) for m in obj.get("methods", [])):
                    matched = True

            # --refs: who references this name (query IS the target name)
            elif args.refs:
                if query.lower() in [r.lower() for r in obj.get("references", [])]:
                    matched = True

            # --coc: list all CoC extensions
            elif args.coc:
                if obj.get("cocTarget"):
                    matched = not query or match(name, query)

            # --deps: show dependencies of a specific object
            elif args.deps:
                if name.lower() == args.deps.lower():
                    refs = obj.get("references", [])
                    print(f"\n{model} / {name}")
                    print(f"  Dependencies ({len(refs)}):")
                    for r in refs:
                        # Try to find the type of the referenced object
                        ref_obj = next((o for o in objects if o["name"] == r), None)
                        if ref_obj:
                            print(f"    [{ref_obj.get('type','?')}/{ref_obj.get('role','?')}] {r}")
                        else:
                            print(f"    {r}")
                    return

            # Default: match name
            else:
                if not query or match(name, query):
                    matched = True

            if matched:
                results.append((model, obj))

    if not results:
        print("No matches found.")
        return

    print(f"\n{len(results)} match(es):\n")
    for model, obj in results:
        print(fmt_obj(model, obj, verbose=args.verbose))
    print()


def show_coc_map(indexes: list) -> None:
    """Print a formatted CoC extension table."""
    print(f"\n{'Extension':<50} {'Extends':<35} Kind")
    print("-" * 100)
    for model, idx in indexes:
        coc_map = idx.get("cocMap", {})
        for ext, target in sorted(coc_map.items()):
            print(f"  {ext:<48} {target['name']:<35} {target['kind']}")
    print()


def show_stats(indexes: list) -> None:
    """Print per-model stats."""
    print(f"\n{'Model':<35} {'Objects':>8}  Stats")
    print("-" * 90)
    for model, idx in indexes:
        stats = idx.get("stats", {})
        total = sum(stats.values())
        detail = "  ".join(f"{k.replace('Ax','')}: {v}" for k, v in stats.items())
        print(f"  {model:<33} {total:>8}  {detail}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Search X++ model indexes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("query", nargs="?", default="", help="Search term")
    parser.add_argument("--model", "-m", help="Filter by model name (partial match)")
    parser.add_argument("--type", "-t", help="Filter by object type (class, table, enum, edt, ...)")
    parser.add_argument("--role", "-r", help="Filter by class role (contract, service, handler, ...)")
    parser.add_argument("--attr", "-a", action="store_true", help="Search in attributes")
    parser.add_argument("--field", "-f", action="store_true", help="Search in field names")
    parser.add_argument("--method", help="Find objects with a method matching this name")
    parser.add_argument("--refs", action="store_true", help="Find objects that reference <query>")
    parser.add_argument("--coc", action="store_true", help="List all CoC extensions")
    parser.add_argument("--deps", metavar="CLASS", help="Show dependencies of a class")
    parser.add_argument("--stats", action="store_true", help="Show per-model stats and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full summaries")
    args = parser.parse_args()

    ensure_indexes(args.model)

    if not INDEX_DIR.exists():
        print(f"ERROR: index directory not found: {INDEX_DIR}", file=sys.stderr)
        print("Run: python tools/index_all.py", file=sys.stderr)
        sys.exit(1)

    indexes = load_indexes(args.model)
    if not indexes:
        print("No index files found. Run: python tools/index_all.py")
        sys.exit(1)

    if args.stats:
        show_stats(indexes)
        return

    if args.coc and not args.query:
        show_coc_map(indexes)
        return

    # --method is actually a search filter, merge into args namespace
    if args.method:
        args_query = args.method
        args.method = True
        query = args_query
    else:
        query = args.query

    search(query, indexes, args)


if __name__ == "__main__":
    main()
