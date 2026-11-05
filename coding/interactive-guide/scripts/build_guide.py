#!/usr/bin/env python3
"""Validate guide data, inline its images, and build one HTML page from the app template.

The data is one JSON file, or a guide directory whose guide.json lists pages/NN-*.json.
"""
import argparse
import base64
import html
import json
import mimetypes
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "assets" / "app"
BLOCKS = {"text", "callout", "code", "figure", "compare", "steps", "terms", "quiz", "formula", "mermaid", "flow", "graph", "claim", "figuretour", "papercode"}
# REQUIRED fields hold the structure; a block cannot render without them, so a missing one stops the build.
REQUIRED = {"text": [], "callout": [], "code": ["code"], "figure": ["src"], "compare": ["headers", "rows"],
            "steps": ["items"], "terms": ["items"], "quiz": ["options", "answer"], "formula": ["tex"],
            "mermaid": ["code"], "claim": ["kind"], "papercode": ["items"], "figuretour": ["src", "stops"], "flow": ["nodes", "edges", "flows"], "graph": ["nodes", "edges"]}
# DISPLAY fields are facts for the reader. A missing one shows a marker on the page and a warning here.
DISPLAY = {"text": ["md"], "callout": ["md"], "figure": ["alt"], "figuretour": ["alt"], "quiz": ["question"], "claim": ["md"]}
MODES = {None, "answer"}
ANSWER_BLOCKS = range(2, 5)
IMAGE_WARN_KB = 800
TOTAL_WARN_MB = 8
PNG_TOOLS = {
    "pngquant": lambda src, out: ["pngquant", "--quality=65-90", "--skip-if-larger", "--output", str(out), "--", str(src)],
    "oxipng": lambda src, out: ["oxipng", "-o", "3", "--strip", "safe", "--out", str(out), str(src)],
    "optipng": lambda src, out: ["optipng", "-quiet", "-o2", "-out", str(out), str(src)],
}


class GuideError(Exception):
    """The data cannot be read at all."""


def blank(value):
    return value is None or str(value).strip() == ""


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise GuideError(f"cannot read {path}: {e.strerror}") from e
    except ValueError as e:
        raise GuideError(f"bad JSON in {path}: {e}") from e


def load_guide(path):
    """Return (data, base directory for images, notes), merging any page files listed in guide.json."""
    path = path.resolve()
    index = path / "guide.json" if path.is_dir() else path
    data = read_json(index)
    if not isinstance(data, dict):
        raise GuideError(f"{index}: expected an object")
    base = index.parent
    if data.get("mode") == "answer" and "pages" not in data and "blocks" in data:
        data["pages"] = [{"id": "answer", "title": data.get("title"), "blocks": data.pop("blocks")}]
    entries = data.get("pages") or []
    if not isinstance(entries, list):
        raise GuideError(f"{index}: pages must be a list")
    data["pages"] = [read_json(base / e) if isinstance(e, str) else e for e in entries]
    notes = []
    listed = {(base / e).resolve() for e in entries if isinstance(e, str)}
    if listed:
        notes = [f"page file not listed in guide.json: {f.relative_to(base)}"
                 for f in sorted((base / "pages").glob("*.json")) if f.resolve() not in listed]
    return data, base, notes


def location_error(repo, where, file, line):
    if repo is None:
        return None
    path = repo / file
    if not path.is_file():
        return f"{where}: file not found: {file}"
    if line is not None:
        count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        if not 1 <= int(line) <= count:
            return f"{where}: {file}:{line} is outside 1..{count}"
    return None


def check_located(items, repo, where):
    return [location_error(repo, f"{where} {i.get('id', i.get('title'))}", i["file"], i.get("line"))
            for i in items if i.get("file")]


def check_flow(block, repo, where):
    errors = check_located(block["nodes"], repo, where)
    known = {n["id"] for n in block["nodes"]}
    if len(known) != len(block["nodes"]):
        errors.append(f"{where}: duplicate node id")
    if len(block["nodes"]) > 12:
        errors.append(f"{where}: more than 12 nodes; split the flow or use a graph block")
    edges = {(e["from"], e["to"]) for e in block["edges"]}
    errors += [f"{where}: edge uses unknown node: {end}" for e in block["edges"] for end in (e["from"], e["to"]) if end not in known]
    errors += [f"{where}: node {n['id']} has no layer" for n in block["nodes"] if "layer" not in n]
    for flow in block["flows"]:
        name = f"{where} flow {flow.get('title')}"
        if not flow.get("steps"):
            errors.append(f"{name}: no steps")
        for i, step in enumerate(flow.get("steps", []), 1):
            if step.get("to") not in known or step.get("from") not in known | {None}:
                errors.append(f"{name} step {i}: unknown node")
            elif step.get("from") and (step["from"], step["to"]) not in edges:
                errors.append(f"{name} step {i}: no edge {step['from']} -> {step['to']}")
            if step.get("verified", True) and repo is not None and not step.get("file"):
                errors.append(f"{name} step {i}: claimed verified without a file")
        errors += check_located(flow.get("steps", []), repo, name)
    return errors


def check_graph(block, repo, where):
    ids = [n["id"] for n in block["nodes"]]
    errors = [f"{where}: duplicate node id: {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    errors += [f"{where}: edge uses unknown node: {end}" for e in block["edges"] for end in (e["from"], e["to"]) if end not in ids]
    return errors + check_located(block["nodes"], repo, where)


def validate(data, repo):
    if not data.get("pages"):
        return ["missing or empty: pages"]
    if not all(isinstance(p, dict) for p in data["pages"]):
        return ["every page must be an object"]
    errors = []
    if data.get("mode") not in MODES:
        errors.append(f"unknown mode: {data['mode']}")
    if data.get("mode") == "answer":
        count = len(data["pages"][0].get("blocks") or [])
        if len(data["pages"]) != 1 or count not in ANSWER_BLOCKS:
            errors.append(f"answer mode needs one page of {ANSWER_BLOCKS[0]} to {ANSWER_BLOCKS[-1]} blocks")
    assumptions = data.get("assumptions", [])
    if not isinstance(assumptions, list) or not all(isinstance(a, str) for a in assumptions):
        errors.append("assumptions must be a list of strings")
    ids = [p.get("id") for p in data["pages"]]
    if len(set(ids)) != len(ids) or not all(ids):
        errors.append("every page needs a unique id")
    for page in data["pages"]:
        if not page.get("blocks"):
            errors.append(f"page {page.get('id')}: no blocks")
        for i, block in enumerate(page.get("blocks") or [], 1):
            where = f"page {page.get('id')} block {i}"
            kind = block.get("type")
            if kind not in BLOCKS:
                errors.append(f"{where}: unknown type {kind}")
                continue
            missing = [k for k in REQUIRED[kind] if k not in block]
            if missing:
                errors.append(f"{where}: {kind} needs {', '.join(missing)}")
            elif kind == "flow":
                errors += check_flow(block, repo, where)
            elif kind == "graph":
                errors += check_graph(block, repo, where)
            elif kind == "code" and block.get("file"):
                errors.append(location_error(repo, where, block["file"], block.get("line")))
            elif kind == "claim" and block["kind"] not in {"author", "evidence", "inference", "unknown"}:
                errors.append(f"{where}: unknown claim kind {block['kind']}")
            elif kind == "papercode":
                errors += [f"{where}: item {n} has bad status" for n, x in enumerate(block["items"], 1)
                           if x.get("status") not in {"match", "differs", "unstated"}]
                errors += check_located(block["items"], repo, where)
            elif kind == "figuretour":
                errors += [f"{where}: stop {n} leaves the image" for n, s in enumerate(block["stops"], 1)
                           if s["x"] < 0 or s["y"] < 0 or s["x"] + s["w"] > 100 or s["y"] + s["h"] > 100]
            elif kind == "quiz" and not 0 <= block["answer"] < len(block["options"]):
                errors.append(f"{where}: answer out of range")
    return [e for e in errors if e]


def display_gaps(data):
    """List the facts the page will mark as missing, so the author can fill or accept each one."""
    found = [f"guide: {k}" for k in ("title", "summary") if blank(data.get(k))]
    if data.get("repo") and blank(data.get("commit")):
        found.append("guide: commit")
    for page in data["pages"]:
        if blank(page.get("title")):
            found.append(f"page {page.get('id')}: title")
        for i, block in enumerate(page["blocks"], 1):
            where, kind = f"page {page.get('id')} block {i} {block['type']}", block["type"]
            found += [f"{where}: {k}" for k in DISPLAY.get(kind, []) if blank(block.get(k))]
            if kind == "compare":
                width = len(block["headers"])
                found += [f"{where}: row {n}" for n, row in enumerate(block["rows"], 1)
                          if len(row) != width or any(blank(c) for c in row)]
            elif kind == "steps":
                found += [f"{where}: item {n}" for n, x in enumerate(block["items"], 1) if blank(x)]
            elif kind == "terms":
                found += [f"{where}: item {n}" for n, x in enumerate(block["items"], 1) if blank(x.get("term")) or blank(x.get("meaning"))]
            elif kind == "papercode":
                found += [f"{where}: item {n}" for n, x in enumerate(block["items"], 1) if blank(x.get("paper"))]
            elif kind == "figuretour":
                found += [f"{where}: stop {n}" for n, x in enumerate(block["stops"], 1) if blank(x.get("title")) or blank(x.get("md"))]
            elif kind in {"flow", "graph"}:
                found += [f"{where}: node {n['id']} label" for n in block["nodes"] if blank(n.get("label"))]
                found += [f"{where}: flow {f.get('title')} step {n} title" for f in block.get("flows", [])
                          for n, s in enumerate(f.get("steps", []), 1) if blank(s.get("title"))]
    return found


def compress_png(path, raw, warnings):
    """Return smaller bytes from the first tool installed, or the original; the source file is left alone."""
    tool = next((t for t in PNG_TOOLS if shutil.which(t)), None)
    if tool is None:
        warnings.append(f"{path.name}: no PNG compressor found (tried {', '.join(PNG_TOOLS)})")
        return raw
    with tempfile.TemporaryDirectory(prefix="guide-png-") as tmp:
        out = Path(tmp) / "out.png"
        try:
            subprocess.run(PNG_TOOLS[tool](path, out), capture_output=True, timeout=120)
            smaller = out.read_bytes() if out.is_file() else raw
        except (OSError, subprocess.TimeoutExpired):
            warnings.append(f"{path.name}: {tool} failed; embedding the original")
            return raw
    if len(smaller) >= len(raw):
        return raw
    print(f"{path.name}: {len(raw) // 1024} KB -> {len(smaller) // 1024} KB with {tool}")
    return smaller


def inline_images(data, base, warnings=None, compress=False):
    """Every image becomes a data URI: a page must never depend on a sibling file or remote host."""
    errors, total = [], 0
    warnings = [] if warnings is None else warnings
    for page in data["pages"]:
        for block in page.get("blocks", []):
            if block.get("type") not in {"figure", "figuretour"} or str(block.get("src", "")).startswith("data:"):
                continue
            src = block["src"]
            path = base / src
            mime = mimetypes.guess_type(src)[0]
            if "://" in src:
                errors.append(f"remote image: {src}; save it locally first")
            elif not path.is_file() or not (mime or "").startswith("image/"):
                errors.append(f"image not found or not an image: {src}")
            else:
                raw = path.read_bytes()
                if compress and mime == "image/png" and len(raw) > IMAGE_WARN_KB * 1024:
                    raw = compress_png(path, raw, warnings)
                if len(raw) > IMAGE_WARN_KB * 1024:
                    warnings.append(f"large image: {src} is {len(raw) // 1024} KB (limit {IMAGE_WARN_KB}); shrink it or redraw as SVG")
                total += len(raw)
                block["src"] = f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")
    if total > TOTAL_WARN_MB * 1024 * 1024:
        warnings.append(f"images total {total // 1024 // 1024} MB (limit {TOTAL_WARN_MB}); the page will load slowly")
    return errors


def build_page(data, output, offline, keep):
    workdir = Path(tempfile.mkdtemp(prefix="guide-"))
    project = workdir / "app"
    try:
        shutil.copytree(APP, project)
        (project / "src" / "data.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["npm", "install", "--silent", "--no-audit", "--no-fund"], cwd=project, check=True)
        subprocess.run(["npm", "run", "--silent", "build:offline" if offline else "build"], cwd=project, check=True)
        page = (project / "dist" / "index.html").read_text(encoding="utf-8")
        output.write_text(page.replace("<title>Interactive guide</title>", f"<title>{html.escape(data.get('title') or '⚠ 未指定')}</title>"), encoding="utf-8")
    finally:
        if keep:
            print(f"project kept at {project}")
        else:
            shutil.rmtree(workdir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="a JSON file, or a guide directory holding guide.json")
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo", type=Path, help="check file:line claims against this repository")
    parser.add_argument("--offline", action="store_true", help="bundle libraries into the page instead of using a CDN")
    parser.add_argument("--check", action="store_true", help="validate only, do not build")
    parser.add_argument("--keep", action="store_true", help="keep the temporary project for further edits")
    parser.add_argument("--no-compress", action="store_true", help="embed large PNGs unchanged, for exact colours")
    args = parser.parse_args()
    try:
        data, base, warnings = load_guide(args.data)
    except GuideError as e:
        print(e, file=sys.stderr)
        return 1
    errors = validate(data, args.repo)
    if not errors:
        warnings += [f"shown as ⚠ 未指定: {gap}" for gap in display_gaps(data)]
        errors = inline_images(data, base, warnings, compress=not (args.check or args.no_compress))
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if args.check:
        return 0
    build_page(data, args.output.resolve(), args.offline, args.keep)
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
