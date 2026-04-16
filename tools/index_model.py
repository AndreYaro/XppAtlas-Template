#!/usr/bin/env python3
"""
X++ Model Indexer — parses AOT XML source files and produces a compact JSON index.

Outputs two files alongside the full index:
  <model>_index.json   — full structured index (classes, tables, enums, EDTs, ...)
  <model>_summary.json — compact overview (~2-3k tokens) for quick agent orientation

Usage:
  python tools/index_model.py Models/DYSBillingIntegration/Source
  python tools/index_model.py Models/DYSBillingIntegration/Source --out .claude/index/DYSBillingIntegration.json
  python tools/index_model.py Models/DYSBillingIntegration/Source --out ... --incremental
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


# ── helpers ───────────────────────────────────────────────────────────────────

def text(node) -> str:
    return (node.text or "").strip() if node is not None else ""


def extract_summary(source: str) -> str:
    """Pull the first /// <summary> block."""
    m = re.search(r'///\s*<summary>(.*?)///\s*</summary>', source, re.DOTALL)
    if not m:
        return ""
    lines = [ln.lstrip("/ ").strip() for ln in m.group(1).splitlines()]
    return " ".join(ln for ln in lines if ln)


_MODIFIERS = r'(?:public|protected|private|static|final|server|client|abstract|display|edit)'

def extract_method_sig(source: str) -> dict:
    sig = re.search(rf'(?:{_MODIFIERS}\s+)+(\S+)\s+(\w+)\s*\(([^)]*)\)', source)
    if not sig:
        return {}
    params = []
    for p in sig.group(3).strip().split(","):
        p = p.strip()
        if not p:
            continue
        parts = p.rsplit(None, 1)
        if len(parts) == 2:
            params.append({"type": parts[0].strip(), "name": parts[1].lstrip("_")})
        else:
            params.append({"raw": p})
    return {"returnType": sig.group(1), "params": params}


def extract_method_attrs(source: str) -> list[str]:
    pre = source.split("{", 1)[0] if "{" in source else source
    return [a.strip() for a in re.findall(r'\[([^\]]+)\]', pre)]


def infer_role(name: str, attrs: list[str]) -> str:
    """Classify a class by naming convention and attributes."""
    for a in attrs:
        if "ExtensionOf" in a:
            return "extension"
    if name.endswith("_Cls_Extension"):
        return "extension"
    if name.endswith("_Tab_Extension"):
        return "tableExtension"
    if name.endswith("_Form_Extension"):
        return "formExtension"
    lower = name.lower()
    for suffix, role in [
        ("contract", "contract"), ("requestcontract", "contract"), ("responsecontract", "contract"),
        ("service", "service"), ("handler", "handler"), ("orchestrator", "orchestrator"),
        ("provider", "provider"), ("helper", "helper"), ("builder", "builder"),
        ("factory", "factory"), ("validator", "validator"), ("processor", "processor"),
        ("controller", "controller"), ("dp", "dataProvider"), ("eventhandler", "eventHandler"),
    ]:
        if lower.endswith(suffix):
            return role
    return "class"


def extract_coc_target(attrs: list[str]) -> dict | None:
    """Parse [ExtensionOf(classStr(X))] → {name: X, kind: class/table/form}."""
    for a in attrs:
        m = re.search(r'ExtensionOf\(\s*(classStr|tableStr|formStr|enumStr)\s*\(\s*(\w+)\s*\)', a)
        if m:
            kind_map = {"classStr": "class", "tableStr": "table", "formStr": "form", "enumStr": "enum"}
            return {"name": m.group(2), "kind": kind_map[m.group(1)]}
    return None


def extract_references(all_sources: str, known_names: set[str]) -> list[str]:
    """
    Find references to known AOT objects within source code.
    Looks for: new ClassName(  |  ClassName::  |  classStr(ClassName)  |  tableStr(...)
    """
    found: set[str] = set()
    # instantiation: new Foo(  or static call: Foo::
    for m in re.finditer(r'\bnew\s+(\w+)\s*\(', all_sources):
        if m.group(1) in known_names:
            found.add(m.group(1))
    for m in re.finditer(r'\b(\w+)::', all_sources):
        if m.group(1) in known_names:
            found.add(m.group(1))
    # metadata references
    for m in re.finditer(r'(?:classStr|tableStr|formStr|enumStr)\s*\(\s*(\w+)\s*\)', all_sources):
        if m.group(1) in known_names:
            found.add(m.group(1))
    return sorted(found)


# ── parsers ───────────────────────────────────────────────────────────────────

def parse_class(xml_file: Path) -> dict:
    root = ET.parse(xml_file).getroot()
    name = root.findtext("Name", "")
    decl_node = root.find(".//Declaration")
    decl = text(decl_node)
    summary = extract_summary(decl)

    # class-level attributes
    cls_attrs = [a.strip() for a in re.findall(r'\[([^\]]+)\]', decl)]

    # class signature
    modifiers, extends, implements = [], None, []
    sig = re.search(
        r'((?:(?:public|internal|final|abstract|static)\s+)*)class\s+\w+'
        r'(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?',
        decl
    )
    if sig:
        modifiers = sig.group(1).split() if sig.group(1) else []
        extends = sig.group(2)
        implements = [s.strip() for s in sig.group(3).split(",")] if sig.group(3) else []

    # private fields
    fields = []
    for fld in re.finditer(
        r'(?:private|protected|public)\s+([\w<>]+)\s+(\w+)\s*(?:=\s*[^;]+)?;', decl
    ):
        fields.append({"type": fld.group(1), "name": fld.group(2)})

    # methods — collect all source for dependency extraction later
    methods = []
    all_method_src = []
    for mn in root.findall(".//Method"):
        mname = mn.findtext("Name", "")
        src_node = mn.find("Source")
        src = text(src_node)
        all_method_src.append(src)
        msig = extract_method_sig(src)
        mattrs = extract_method_attrs(src)
        msummary = extract_summary(src)
        m: dict[str, Any] = {"name": mname}
        if mattrs:
            m["attributes"] = mattrs
        if msig:
            m.update(msig)
        if msummary:
            m["summary"] = msummary
        methods.append(m)

    role = infer_role(name, cls_attrs)
    coc_target = extract_coc_target(cls_attrs)

    obj: dict[str, Any] = {
        "type": "class",
        "role": role,
        "name": name,
        "_allSrc": decl + "\n".join(all_method_src),  # temporary, removed after dep extraction
    }
    if summary:
        obj["summary"] = summary
    if cls_attrs:
        obj["attributes"] = cls_attrs
    if modifiers:
        obj["modifiers"] = modifiers
    if extends:
        obj["extends"] = extends
    if implements:
        obj["implements"] = implements
    if fields:
        obj["fields"] = fields
    if methods:
        obj["methods"] = methods
    if coc_target:
        obj["cocTarget"] = coc_target
    return obj


def parse_table(xml_file: Path) -> dict:
    root = ET.parse(xml_file).getroot()
    name = root.findtext("Name", "")
    is_ext = root.tag == "AxTableExtension"

    fields = []
    for f in root.findall(".//AxTableField"):
        fname = f.findtext("Name", "")
        ftype = f.get("{http://www.w3.org/2001/XMLSchema-instance}type", "")
        edt = f.findtext("ExtendedDataType", "")
        enum_ = f.findtext("EnumType", "")
        entry: dict[str, Any] = {"name": fname, "itype": ftype}
        if edt:
            entry["edt"] = edt
        if enum_:
            entry["enum"] = enum_
        fields.append(entry)

    relations = []
    for r in root.findall(".//AxTableRelation"):
        rname = r.findtext("Name", "")
        rtable = r.findtext("RelatedTable", "")
        if rname or rtable:
            relations.append({"name": rname, "relatedTable": rtable})

    indexes = []
    for idx in root.findall(".//AxTableIndex"):
        iname = idx.findtext("Name", "")
        unique = idx.findtext("AlternateKey", "No") == "Yes"
        fnames = [fi.findtext("DataField", "") for fi in idx.findall(".//AxTableIndexField")]
        indexes.append({"name": iname, "unique": unique, "fields": fnames})

    obj_type = "tableExtension" if is_ext else "table"
    obj: dict[str, Any] = {"type": obj_type, "name": name}

    # For extensions: base table is first segment of "Base.Model" name
    if is_ext and "." in name:
        obj["extendsTable"] = name.split(".")[0]

    if fields:
        obj["fields"] = fields
    if relations:
        obj["relations"] = relations
    if indexes:
        obj["indexes"] = indexes
    return obj


def parse_enum(xml_file: Path) -> dict:
    root = ET.parse(xml_file).getroot()
    name = root.findtext("Name", "")
    values = []
    for ev in root.findall(".//AxEnumValue"):
        entry: dict[str, Any] = {"name": ev.findtext("Name", "")}
        lbl = ev.findtext("Label", "")
        if lbl:
            entry["label"] = lbl
        values.append(entry)
    return {"type": "enum", "name": name, "values": values}


def parse_edt(xml_file: Path) -> dict:
    root = ET.parse(xml_file).getroot()
    name = root.findtext("Name", "")
    obj: dict[str, Any] = {"type": "edt", "name": name}
    ext = root.findtext("Extends", "")
    lbl = root.findtext("Label", "")
    if ext:
        obj["extends"] = ext
    if lbl:
        obj["label"] = lbl
    return obj


def parse_data_entity(xml_file: Path) -> dict:
    root = ET.parse(xml_file).getroot()
    name = root.findtext("Name", "")
    obj: dict[str, Any] = {"type": "dataEntity", "name": name}
    pub = root.findtext("PublicEntityName", "")
    pri = root.findtext("PrimaryDataSourceName", "")
    fields = [f.findtext("Name", "") for f in root.findall(".//AxDataEntityViewField")]
    if pub:
        obj["publicName"] = pub
    if pri:
        obj["primaryTable"] = pri
    if fields:
        obj["fields"] = fields
    return obj


def parse_service(xml_file: Path) -> dict:
    root = ET.parse(xml_file).getroot()
    name = root.findtext("Name", "")
    class_name = root.findtext("ServiceContract", "")
    ops = [op.findtext("Name", "") for op in root.findall(".//AxServiceOperation")]
    return {"type": "service", "name": name, "serviceClass": class_name, "operations": ops}


def parse_query(xml_file: Path) -> dict:
    root = ET.parse(xml_file).getroot()
    name = root.findtext("Name", "")
    ds = [d.findtext("Table", "") for d in root.findall(".//AxQuerySimpleRootDataSource")]
    return {"type": "query", "name": name, "dataSources": [d for d in ds if d]}


# ── folder dispatch ───────────────────────────────────────────────────────────

FOLDER_PARSERS = {
    "AxClass":                  ("class",        parse_class),
    "AxTable":                  ("table",        parse_table),
    "AxTableExtension":         ("tableExt",     parse_table),
    "AxEnum":                   ("enum",         parse_enum),
    "AxEnumExtension":          ("enumExt",      parse_enum),
    "AxEdt":                    ("edt",          parse_edt),
    "AxEdtExtension":           ("edtExt",       parse_edt),
    "AxDataEntityView":         ("entity",       parse_data_entity),
    "AxDataEntityViewExtension":("entityExt",    parse_data_entity),
    "AxService":                ("service",      parse_service),
    "AxQuery":                  ("query",        parse_query),
}


# ── post-processing ───────────────────────────────────────────────────────────

def build_dependencies(objects: list[dict]) -> None:
    """
    For each class, scan its source for references to other known AOT objects.
    Adds a 'references' list in-place. Removes the temporary '_allSrc' key.
    """
    known_names: set[str] = {o["name"] for o in objects}

    for obj in objects:
        src = obj.pop("_allSrc", "")
        if obj["type"] != "class" or not src:
            continue
        refs = extract_references(src, known_names - {obj["name"]})
        if refs:
            obj["references"] = refs


def build_coc_map(objects: list[dict]) -> dict:
    """
    Build a lookup: extensionClass → {extends: BaseClass, kind: class|table|...}
    """
    coc_map = {}
    for obj in objects:
        if obj.get("cocTarget"):
            coc_map[obj["name"]] = obj["cocTarget"]
    return coc_map


# ── compact summary ───────────────────────────────────────────────────────────

def build_summary(index: dict) -> dict:
    objects = index["objects"]
    stats = index["stats"]

    overview_parts = []
    for k, v in stats.items():
        overview_parts.append(f"{v} {k}")
    overview = f"{sum(stats.values())} objects: " + ", ".join(overview_parts)

    classes = [
        {k: v for k, v in {
            "n": o["name"],
            "role": o.get("role"),
            "s": o.get("summary", ""),
            "extends": o.get("extends"),
            "cocTarget": o.get("cocTarget"),
            "methods": [m["name"] for m in o.get("methods", [])],
        }.items() if v}
        for o in objects if o["type"] == "class"
    ]

    tables = [
        {"n": o["name"], "fields": [f["name"] for f in o.get("fields", [])]}
        for o in objects if o["type"] == "table"
    ]

    table_exts = [
        {"n": o["name"], "extendsTable": o.get("extendsTable"), "addedFields": [f["name"] for f in o.get("fields", [])]}
        for o in objects if o["type"] == "tableExtension"
    ]

    enums = [
        {"n": o["name"], "values": [v["name"] for v in o.get("values", [])]}
        for o in objects if o["type"] in ("enum", "enumExt")
    ]

    edts = [
        {"n": o["name"], "extends": o.get("extends", ""), "label": o.get("label", "")}
        for o in objects if o["type"] == "edt"
    ]

    services = [
        {"n": o["name"], "serviceClass": o.get("serviceClass"), "operations": o.get("operations", [])}
        for o in objects if o["type"] == "service"
    ]

    coc_extensions = [
        {"extension": o["name"], **o["cocTarget"]}
        for o in objects if o.get("cocTarget")
    ]

    return {
        "model": index["model"],
        "indexedAt": index["indexedAt"],
        "overview": overview,
        "classes": classes,
        "tables": tables,
        "tableExtensions": table_exts,
        "enums": enums,
        "edts": edts,
        "services": services,
        "cocExtensions": coc_extensions,
    }


# ── incremental support ───────────────────────────────────────────────────────

def cache_path(out_path: Path) -> Path:
    return out_path.parent / (out_path.stem + "_cache.json")


def load_cache(out_path: Path) -> tuple[dict[str, float], dict[str, dict]]:
    """Returns (timestamps, objectsByFile) from the cache file."""
    cp = cache_path(out_path)
    if cp.exists():
        try:
            with open(cp, encoding="utf-8") as f:
                c = json.load(f)
            return c.get("fileTimestamps", {}), c.get("objectsByFile", {})
        except Exception:
            pass
    return {}, {}


def write_cache(out_path: Path, file_timestamps: dict, objects_by_file: dict) -> None:
    cp = cache_path(out_path)
    with open(cp, "w", encoding="utf-8") as f:
        json.dump({"fileTimestamps": file_timestamps, "objectsByFile": objects_by_file},
                  f, ensure_ascii=False, separators=(",", ":"))


# ── main indexer ──────────────────────────────────────────────────────────────

def index_source(source_path: Path, incremental: bool = False, existing_out: Path | None = None) -> dict:
    model_name = source_path.parent.name
    now = datetime.now(timezone.utc).isoformat()

    old_timestamps: dict[str, float] = {}
    old_objects_by_file: dict[str, dict] = {}
    if incremental and existing_out:
        old_timestamps, old_objects_by_file = load_cache(existing_out)

    file_timestamps: dict[str, float] = {}
    objects: list[dict] = []
    stats: dict[str, int] = {}
    skipped = 0

    for folder_name, (_, parser) in FOLDER_PARSERS.items():
        folder = source_path / folder_name
        if not folder.is_dir():
            continue
        count = 0
        for xml_file in sorted(folder.glob("*.xml")):
            rel = f"{folder_name}/{xml_file.name}"
            mtime = xml_file.stat().st_mtime
            file_timestamps[rel] = mtime

            if incremental and old_timestamps.get(rel) == mtime and rel in old_objects_by_file:
                cached = dict(old_objects_by_file[rel])
                cached["_file"] = rel
                objects.append(cached)
                count += 1
                skipped += 1
                continue

            try:
                obj = parser(xml_file)
                obj["_file"] = rel
                objects.append(obj)
                count += 1
            except Exception as e:
                print(f"  WARN: failed to parse {xml_file.name}: {e}", file=sys.stderr)
        if count:
            stats[folder_name] = count

    if skipped:
        print(f"  Incremental: {skipped} files unchanged, skipped.")

    # Post-processing
    build_dependencies(objects)
    coc_map = build_coc_map(objects)

    # Build a lookup by file for incremental storage
    objects_by_file = {o.pop("_file", ""): o for o in objects}
    objects_list = list(objects_by_file.values())

    return {
        "model": model_name,
        "indexedAt": now,
        "sourceRoot": str(source_path),
        "stats": stats,
        "cocMap": coc_map,
        "fileTimestamps": file_timestamps,
        "_objectsByFile": objects_by_file,
        "objects": objects_list,
    }


def write_outputs(index: dict, out_path: Path) -> Path:
    """Write full index, compact summary, and cache. Returns summary path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write cache for incremental support
    write_cache(out_path, index["fileTimestamps"], index["_objectsByFile"])

    # Write full index (without internal keys)
    export = {k: v for k, v in index.items() if not k.startswith("_")}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)

    # Write compact summary
    summary = build_summary(index)
    stem = out_path.stem.replace("_index", "")
    summary_path = out_path.parent / f"{stem}_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Index a D365 F&O X++ Source folder to JSON.")
    parser.add_argument("source", help="Path to the model Source/ directory")
    parser.add_argument("--out", help="Output JSON path (default: .claude/index/<Model>.json)")
    parser.add_argument("--incremental", action="store_true",
                        help="Skip re-parsing files whose mtime is unchanged")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    if not source_path.is_dir():
        print(f"ERROR: not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    model_name = source_path.parent.name
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = Path(f".claude/index/{model_name}.json")

    print(f"Indexing: {source_path}")
    index = index_source(source_path, incremental=args.incremental, existing_out=out_path)
    summary_path = write_outputs(index, out_path)

    total = len(index["objects"])
    print(f"Index:   {out_path}  ({total} objects)")
    print(f"Summary: {summary_path}")
    print("Stats:")
    for k, v in index["stats"].items():
        print(f"  {k}: {v}")
    if index["cocMap"]:
        print(f"  CoC extensions: {len(index['cocMap'])}")


if __name__ == "__main__":
    main()
