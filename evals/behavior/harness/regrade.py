#!/usr/bin/env python3
"""Re-grade already-finished runs with the current checks.

run_part_a prepares the workspace fresh per arm, so only the arm that ran last
for a case is still on disk. This script finds that arm from the artifact
timestamps, rebuilds the pre-run fixture set from the pristine fixture, and
re-grades. It exists to show that the old grading.json errors and
misjudgements came from the checks, not from the agent runs.
results/partA.json is untouched.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import text_checks
import git_checks

ROOT = Path("/tmp/behavior-eval")
RUNS = ROOT / "runs"
WORK = ROOT / "workdirs"
FIX = ROOT / "fixtures"


def snapshot(d):
    out = {}
    for p in Path(d).rglob("*"):
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts:
            out[str(p.relative_to(d))] = p.read_bytes()
    return out


def owning_arm(case_id):
    """The arm whose run last touched the shared workspace."""
    best = None
    for arm in ("with_skill", "without_skill"):
        t = RUNS / case_id / arm / "transcript.json"
        if t.exists() and (best is None or t.stat().st_mtime > best[1]):
            best = (arm, t.stat().st_mtime)
    return best[0] if best else None


def fixture_files(case):
    """Pre-run workspace contents, keyed the way run_part_a keys them."""
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
    out = {}
    for skill in ("deai", "co-commit", "qi-read-paper", "technical-writing"):
        spec = json.loads((ROOT / "evals" / f"{skill}.json").read_text())
        for case in spec["evals"]:
            wd = WORK / case["id"] / "workspace"
            arm = owning_arm(case["id"])
            if not wd.exists() or arm is None:
                print(f"SKIP {case['id']}: no workspace")
                continue
            is_git = bool(case.get("fixture", "").startswith("git/"))
            table = git_checks.CHECKS if is_git else text_checks.CHECKS
            adir = RUNS / case["id"] / arm
            rec = json.loads((adir / "transcript.json").read_text())
            before = {} if is_git else fixture_files(case)
            baseline = None
            if is_git:
                baseline = git_checks.git(FIX / case["fixture"], "rev-parse", "HEAD")

            after = snapshot(wd)
            changed = sorted(k for k in after if before.get(k) != after[k])
            removed = sorted(k for k in before if k not in after)
            unchanged = sorted(k for k in before if before.get(k) == after.get(k))
            files_after = {k: v.decode("utf-8", "replace") for k, v in after.items()
                           if k.endswith((".md", ".txt", ".py"))}
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
                "removed_paths": removed, "repo": wd, "baseline": baseline,
                "seen_commands": [], "expected_paths": ["service/parser.py"] if is_git else [],
            }

            old = json.loads((adir / "grading.json").read_text())
            new = []
            for a in case["assertions"]:
                fn = table.get(a["check"])
                if fn is None:
                    new.append({"id": a["id"], "passed": None,
                                "detail": f"NO CHECK {a['check']}"})
                    continue
                ctx["assertion"] = a
                try:
                    ok, detail = fn(ctx)
                except Exception as e:
                    ok, detail = None, f"CHECK ERROR {type(e).__name__}: {e}"
                new.append({"id": a["id"], "passed": ok, "detail": detail})

            key = f"{case['id']}/{arm}"
            out[key] = {"old": old, "new": new, "changed_paths": changed}
            for o, n in zip(old, new):
                if o["passed"] is None:
                    print(f"E-FIXED {key} {n['id']}: None -> {n['passed']}")
                    print(f"   old: {o['detail'][:140]}")
                    print(f"   new: {n['detail'][:140]}")
                elif o["passed"] != n["passed"]:
                    print(f"CHANGED {key} {n['id']}: {o['passed']} -> {n['passed']}")
                    print(f"   old: {o['detail'][:140]}")
                    print(f"   new: {n['detail'][:140]}")
    (ROOT / "results" / "regrade.json").write_text(json.dumps(out, indent=2))
    print(f"\nregraded {len(out)} arm-runs -> results/regrade.json")


if __name__ == "__main__":
    main()
