#!/usr/bin/env python3
"""Validate guide data, inline its images, and build one HTML page from the app template."""
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
BLOCKS = {"text", "callout", "code", "figure", "compare", "steps", "terms", "quiz", "formula", "mermaid", "flow", "graph"}
REQUIRED = {"text": ["md"], "callout": ["md"], "code": ["code"], "figure": ["src", "alt"], "compare": ["headers", "rows"],
            "steps": ["items"], "terms": ["items"], "quiz": ["question", "options", "answer"], "formula": ["tex"],
            "mermaid": ["code"], "flow": ["nodes", "edges", "flows"], "graph": ["nodes", "edges"]}


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
    errors = [f"missing or empty: {k}" for k in ("title", "summary", "pages") if not data.get(k)]
    if errors:
        return errors
    ids = [p.get("id") for p in data["pages"]]
    if len(set(ids)) != len(ids) or not all(ids):
        errors.append("every page needs a unique id")
    for page in data["pages"]:
        for i, block in enumerate(page.get("blocks", []), 1):
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
            elif kind == "quiz" and not 0 <= block["answer"] < len(block["options"]):
                errors.append(f"{where}: answer out of range")
    return [e for e in errors if e]


def inline_images(data, base):
    """Every image becomes a data URI: a page must never depend on a sibling file or remote host."""
    errors = []
    for page in data["pages"]:
        for block in page.get("blocks", []):
            if block.get("type") != "figure" or str(block.get("src", "")).startswith("data:"):
                continue
            src = block["src"]
            path = base / src
            mime = mimetypes.guess_type(src)[0]
            if "://" in src:
                errors.append(f"remote image: {src}; save it locally first")
            elif not path.is_file() or not (mime or "").startswith("image/"):
                errors.append(f"image not found or not an image: {src}")
            else:
                block["src"] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
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
        output.write_text(page.replace("<title>Interactive guide</title>", f"<title>{html.escape(data['title'])}</title>"), encoding="utf-8")
    finally:
        if keep:
            print(f"project kept at {project}")
        else:
            shutil.rmtree(workdir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo", type=Path, help="check file:line claims against this repository")
    parser.add_argument("--offline", action="store_true", help="bundle libraries into the page instead of using a CDN")
    parser.add_argument("--check", action="store_true", help="validate only, do not build")
    parser.add_argument("--keep", action="store_true", help="keep the temporary project for further edits")
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    errors = validate(data, args.repo) or inline_images(data, args.data.resolve().parent)
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
