#!/usr/bin/env python3
"""Validate a walkthrough JSON against a repository and write one offline HTML file."""
import argparse
import json
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "template.html"


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
    return [e for e in errors if e]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    errors = validate(data, args.repo)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    blob = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    title = data["title"].replace("&", "&amp;").replace("<", "&lt;")
    html = TEMPLATE.read_text(encoding="utf-8").replace("__TITLE__", title).replace("__DATA__", blob)
    args.output.write_text(html, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
