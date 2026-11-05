#!/usr/bin/env python3
"""Measure which skill a description routes each query to.

Usage: run_trigger.py <git-rev|WORK> <tag> [queries.json] [--parallel N]
Builds stub skills from one revision in a throwaway project, runs `claude -p`
per query, and writes results-<tag>.json. Built-in skills can still appear in
`loaded`; report them instead of filtering them out.
"""
import argparse
import json
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODEL = "sonnet"
CLAUDE_ARGS = ["--model", MODEL, "--output-format", "stream-json", "--verbose",
               "--setting-sources", "project", "--strict-mcp-config",
               "--tools", "Skill", "--allowedTools", "Skill", "--max-turns", "4"]


def skill_text(path, rev):
    rel = path.relative_to(ROOT).as_posix()
    if rev == "WORK":
        return path.read_text(encoding="utf-8")
    shown = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{rel}"],
                           capture_output=True, text=True)
    return shown.stdout if shown.returncode == 0 else None


def build(rev, root, names):
    for path in sorted(ROOT.glob("*/*/SKILL.md")):
        name = path.parent.name
        text = skill_text(path, rev)
        if name not in names or text is None:
            continue
        head = re.match(r"---\n(.*?)\n---", text, re.S)[1]
        desc = re.search(r"^description:\s*(.*)$", head, re.M)[1].strip()
        desc = desc if desc.startswith('"') else json.dumps(desc)
        skill = root / ".claude" / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {desc}\n---\n\n"
            f"Skill loaded. Reply with exactly: LOADED {name}. "
            "Load any other skill you need first.\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True)


def run_query(root, query):
    try:
        run = subprocess.run(["claude", "-p", query["query"], *CLAUDE_ARGS], cwd=root,
                             capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {**query, "loaded": None, "error": "timeout"}
    seen = []
    for line in run.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in event["message"].get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                skill = block["input"].get("skill", "")
                if skill not in seen:
                    seen.append(skill)
    return {**query, "loaded": seen, "rc": run.returncode}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rev")
    parser.add_argument("tag")
    parser.add_argument("queries", nargs="?", default=HERE / "queries.json")
    parser.add_argument("--parallel", type=int, default=8)
    args = parser.parse_args()
    queries = json.loads(Path(args.queries).read_text(encoding="utf-8"))
    names = {q["expected"] for q in queries}
    root = Path(tempfile.mkdtemp(prefix=f"trigger-{args.tag}-"))
    try:
        build(args.rev, root, names)
        with ThreadPoolExecutor(args.parallel) as pool:
            results = list(pool.map(lambda q: run_query(root, q), queries))
    finally:
        shutil.rmtree(root)
    Path(f"results-{args.tag}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=0), encoding="utf-8")
    print(sum(r["expected"] in (r["loaded"] or []) for r in results), "of", len(results))


if __name__ == "__main__":
    main()
