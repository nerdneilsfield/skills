#!/usr/bin/env python3
"""Validate walkthrough data against a repository, then build one HTML page from the app template."""
import argparse
import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "assets" / "app"


def location_error(repo, where, file, line):
    path = repo / file
    if not path.is_file():
        return f"{where}: file not found: {file}"
    if line is not None:
        count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        if not 1 <= int(line) <= count:
            return f"{where}: {file}:{line} is outside 1..{count}"
    return None


def validate(data, repo):
    errors = []
    for key in ("title", "summary", "nodes", "edges", "flows"):
        if not data.get(key):
            errors.append(f"missing or empty: {key}")
    if errors:
        return errors
    ids = [n["id"] for n in data["nodes"]]
    errors += [f"duplicate node id: {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    known = set(ids)
    edges = {(e["from"], e["to"]) for e in data["edges"]}
    for edge in data["edges"]:
        for end in (edge["from"], edge["to"]):
            if end not in known:
                errors.append(f"edge uses unknown node: {end}")
    for node in data["nodes"]:
        if "layer" not in node:
            errors.append(f"node {node['id']}: missing layer")
        if node.get("file"):
            errors.append(location_error(repo, f"node {node['id']}", node["file"], node.get("line")))
    for flow in data["flows"]:
        if not flow.get("steps"):
            errors.append(f"flow {flow.get('title')}: no steps")
        for i, step in enumerate(flow.get("steps", []), 1):
            where = f"flow {flow.get('title')} step {i}"
            if step.get("to") not in known or step.get("from") not in known | {None}:
                errors.append(f"{where}: unknown node")
            elif step.get("from") and (step["from"], step["to"]) not in edges:
                errors.append(f"{where}: no edge {step['from']} -> {step['to']}")
            if step.get("verified", True) and not step.get("file"):
                errors.append(f"{where}: claimed verified without a file")
            if step.get("file"):
                errors.append(location_error(repo, where, step["file"], step.get("line")))
    graph = data.get("graph")
    if graph:
        graph_ids = [n["id"] for n in graph.get("nodes", [])]
        errors += [f"duplicate graph node: {i}" for i in sorted({i for i in graph_ids if graph_ids.count(i) > 1})]
        for edge in graph.get("edges", []):
            for end in (edge["from"], edge["to"]):
                if end not in graph_ids:
                    errors.append(f"graph edge uses unknown node: {end}")
        for node in graph.get("nodes", []):
            if node.get("file"):
                errors.append(location_error(repo, f"graph node {node['id']}", node["file"], node.get("line")))
    return [e for e in errors if e]


def build_page(data, output, offline, keep):
    workdir = Path(tempfile.mkdtemp(prefix="walkthrough-"))
    project = workdir / "app"
    try:
        shutil.copytree(APP, project)
        (project / "src" / "data.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["npm", "install", "--silent", "--no-audit", "--no-fund"], cwd=project, check=True)
        script = "build:offline" if offline else "build"
        subprocess.run(["npm", "run", "--silent", script], cwd=project, check=True)
        page = (project / "dist" / "index.html").read_text(encoding="utf-8")
        title = html.escape(data["title"])
        output.write_text(page.replace("<title>Code walkthrough</title>", f"<title>{title}</title>"), encoding="utf-8")
    finally:
        if keep:
            print(f"project kept at {project}")
        else:
            shutil.rmtree(workdir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--offline", action="store_true", help="bundle libraries into the page instead of using a CDN")
    parser.add_argument("--check", action="store_true", help="validate only, do not build")
    parser.add_argument("--keep", action="store_true", help="keep the temporary project for further edits")
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    errors = validate(data, args.repo)
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
