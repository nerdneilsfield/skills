#!/usr/bin/env python3
"""Re-grade Part A runs from the preserved post-run workspaces.

Every non-git Part A run keeps runs/<case>/<arm>-t<trial>/workspace_after, so
the checks can be re-applied to the real artifacts without re-running the
agents. Git cases keep only workdirs/<case>/workspace (the last arm), so they
are reported as not re-gradable here.

Writes results/partA.regraded.json and prints every verdict that moved.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import text_checks
import git_checks

ROOT = Path("/tmp/behavior-eval")
RUNS = ROOT / "runs"
FIX = ROOT / "fixtures"


def snapshot(d):
    out = {}
    for p in Path(d).rglob("*"):
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts:
            out[str(p.relative_to(d))] = p.read_bytes()
    return out


def fixture_files(case):
    out = {}
    for f in case.get("files") or ([case["fixture"]] if case.get("fixture") else []):
        rel = f[len("fixtures/"):] if f.startswith("fixtures/") else f
        src = FIX / rel
        if src.is_file():
            out[f"fixtures/{rel}"] = src.read_bytes()
        elif src.is_dir():
            for q in src.rglob("*"):
                if q.is_file():
                    out[f"fixtures/{q.relative_to(src)}"] = q.read_bytes()
    return out


def main():
    results = json.loads((ROOT / "results" / "partA.json").read_text())
    specs = {}
    for skill in ("deai", "co-commit", "qi-read-paper", "technical-writing"):
        spec = json.loads((ROOT / "evals" / f"{skill}.json").read_text())
        for c in spec["evals"]:
            specs[c["id"]] = c

    out, moves, skipped = [], [], set()
    for rec in results:
        case = specs[rec["case"]]
        is_git = bool(case.get("fixture", "").startswith("git/"))
        adir = RUNS / rec["case"] / f"{rec['arm']}-t{rec['trial']}"
        snapdir = adir / "workspace_after"
        if is_git or not snapdir.exists():
            skipped.add(rec["case"])
            out.append({"case": rec["case"], "arm": rec["arm"], "trial": rec["trial"],
                        "regraded": False, "grading": rec["grading"]})
            continue

        before = fixture_files(case)
        after = snapshot(snapdir)
        changed = sorted(k for k in after if before.get(k) != after[k])
        removed = sorted(k for k in before if k not in after)
        unchanged = sorted(k for k in before if before.get(k) == after.get(k))
        files_after = {k: v.decode("utf-8", "replace") for k, v in after.items()
                       if k.endswith((".md", ".txt", ".py"))}
        tools = json.loads((adir / "tools.json").read_text()) \
            if (adir / "tools.json").exists() else []
        ctx = {
            "assertion": None, "prompt": case["prompt"],
            "answer_blob": rec.get("result") or "",
            "file_blob": "\n".join(files_after[k] for k in changed if k in files_after),
            "files_after": files_after,
            "fixture_spans": sorted(text_checks.spans_in(
                "\n".join(b.decode("utf-8", "replace") for b in before.values()))),
            "fixture_text": "\n".join(b.decode("utf-8", "replace")
                                      for b in before.values()),
            "changed_paths": changed, "unchanged_paths": unchanged,
            "removed_paths": removed, "repo": str(snapdir), "baseline": None,
            "seen_commands": [c["input"]["command"] for c in tools
                              if c.get("name") == "Bash"
                              and isinstance(c.get("input"), dict)
                              and "command" in c["input"]],
            "expected_paths": [],
        }
        grading = []
        for a in case["assertions"]:
            fn = text_checks.CHECKS.get(a["check"])
            if fn is None:
                grading.append({"id": a["id"], "passed": None,
                                "detail": f"NO CHECK {a['check']}"})
                continue
            ctx["assertion"] = a
            try:
                ok, detail = fn(ctx)
            except Exception as e:
                ok, detail = None, f"CHECK ERROR {type(e).__name__}: {e}"
            grading.append({"id": a["id"], "passed": ok, "detail": detail})
        out.append({"case": rec["case"], "arm": rec["arm"], "trial": rec["trial"],
                    "regraded": True, "grading": grading})
        for o, n in zip(rec["grading"], grading):
            if o["passed"] != n["passed"]:
                moves.append(f"{rec['case']}/{rec['arm']}/t{rec['trial']} {n['id']}: "
                             f"{o['passed']} -> {n['passed']}  (old: {o['detail'][:70]}) "
                             f"(new: {n['detail'][:70]})")

    (ROOT / "results" / "partA.regraded.json").write_text(json.dumps(out, indent=2))
    for m in moves:
        print("MOVED", m)
    print(f"\nre-graded {sum(1 for r in out if r['regraded'])} runs, "
          f"{len(moves)} verdicts moved; not re-gradable: {sorted(skipped)}")


if __name__ == "__main__":
    main()
