#!/usr/bin/env python3
"""Drive Part A output evals: each case x {with_skill, without_skill}."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import run_eval
import text_checks
import git_checks

ROOT = Path("/tmp/behavior-eval")
SNAP = ROOT / "skills"
FIX = ROOT / "fixtures"
WORK = ROOT / "workdirs"
RUNS = ROOT / "runs"


def snapshot_files(d):
    out = {}
    for p in Path(d).rglob("*"):
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts:
            rel = str(p.relative_to(d))
            out[rel] = p.read_bytes()
    return out


def prepare_text_case(case, fixture_paths):
    """Copy the case's fixtures into a fresh workdir under fixtures/."""
    d = WORK / case["id"] / "workspace"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for fp in fixture_paths or []:
        fp = Path(fp)
        if not fp.exists():
            raise FileNotFoundError(f"fixture missing for {case['id']}: {fp}")
        rel = fp.relative_to(FIX)
        dest = d / "fixtures" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if fp.is_dir():
            shutil.copytree(fp, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(fp, dest)
    return d


def prepare_git_case(case):
    d = WORK / case["id"] / "workspace"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(FIX / case["fixture"], d)
    baseline = git_checks.git(d, "rev-parse", "HEAD")
    return d, baseline


def prepare_case(case):
    """Fresh workspace for one trial. Returns (workdir, git baseline)."""
    if case.get("fixture", "").startswith("git/"):
        return prepare_git_case(case)
    case_files = case.get("files") or ([case["fixture"]] if case.get("fixture") else [])
    resolved = []
    for f in case_files:
        p = Path(f)
        # prompts reference paths as "fixtures/<x>" inside the workspace;
        # fixtures/ holds that same prefix
        rel = p.relative_to("fixtures") if str(p).startswith("fixtures/") else p
        resolved.append(FIX / rel)
    return prepare_text_case(case, resolved), None


def seen_commands(rec):
    """Bash commands the agent actually ran, taken from the event stream."""
    out = []
    for c in rec.get("tool_calls") or []:
        if c.get("name") == "Bash" and isinstance(c.get("input"), dict):
            cmd = c["input"].get("command")
            if cmd:
                out.append(cmd)
    return out


def run_trial(skill, case, arm, trial, plugin, timeout):
    """Run one trial and grade it. Returns the result record."""
    is_git = bool(case.get("fixture", "").startswith("git/"))
    prompt = case["prompt"]

    for attempt in (1, 2):
        wd, baseline = prepare_case(case)
        before = snapshot_files(wd)
        rec = run_eval.run_one(
            case_id=case["id"], arm=arm, prompt=prompt, workdir=wd,
            plugin_dir=plugin, timeout=timeout, trial=trial)
        why = run_eval.run_failed(rec)
        if why is None:
            break
        print(f"[{skill}/{case['id']}/{arm}/t{trial}] attempt {attempt} "
              f"failed ({why}), retrying", flush=True)
    rec["attempts"] = attempt
    rec["run_failed"] = why
    after = snapshot_files(wd)
    changed = sorted(k for k in after if before.get(k) != after[k])
    removed = sorted(k for k in before if k not in after)
    unchanged = sorted(k for k in before if before.get(k) == after.get(k))

    table = git_checks.CHECKS if is_git else text_checks.CHECKS
    files_after = {k: v.decode("utf-8", "replace") for k, v in after.items()
                   if k.endswith((".md", ".txt", ".py"))}
    fixture_spans = sorted(text_checks.spans_in(
        "\n".join(b.decode("utf-8", "replace") for b in before.values())))
    ctx = {
        "assertion": None, "prompt": prompt,
        "answer_blob": rec.get("result") or "",
        "file_blob": "\n".join(files_after[k] for k in changed if k in files_after),
        "files_after": files_after,
        "fixture_spans": fixture_spans,
        "fixture_text": "\n".join(b.decode("utf-8", "replace")
                                  for b in before.values()),
        "changed_paths": changed, "unchanged_paths": unchanged,
        "removed_paths": removed, "repo": wd, "baseline": baseline,
        "seen_commands": seen_commands(rec),
        "expected_paths": ["service/parser.py"] if is_git else [],
    }

    grading = []
    for a in case["assertions"]:
        if why is not None:
            grading.append({"id": a["id"], "passed": False,
                            "detail": f"RUN FAILED: {why}"})
            continue
        fn = table.get(a["check"])
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

    outdir = RUNS / case["id"] / f"{arm}-t{trial}"
    (outdir / "grading.json").write_text(json.dumps(grading, indent=2))
    # preserve the arm's post-run workspace so grading stays reproducible
    if not is_git:
        snapdir = outdir / "workspace_after"
        if snapdir.exists():
            shutil.rmtree(snapdir)
        shutil.copytree(wd, snapdir)
    rec.update({"skill": skill, "case": case["id"], "arm": arm,
                "changed_paths": changed, "removed_paths": removed,
                "grading": grading,
                "passed": sum(1 for g in grading if g["passed"] is True),
                "failed": sum(1 for g in grading if g["passed"] is False),
                "errors": sum(1 for g in grading if g["passed"] is None)})
    print(f"[{skill}/{case['id']}/{arm}/t{trial}] "
          f"{rec['passed']}P {rec['failed']}F {rec['errors']}E "
          f"tok={rec.get('total_tokens_modelusage')} "
          f"attempts={attempt} run_failed={why} changed={changed}", flush=True)
    return rec


def run_part_a(skills, only=None, timeout=900, repeats=1):
    results = []
    for skill in skills:
        spec = json.loads((ROOT / "evals" / f"{skill}.json").read_text())
        skill_src = SNAP / spec["skill_path"].split("skills/", 1)[1]
        plug = run_eval.make_plugin(WORK / f"plugin-{skill}", skill, skill_src)

        for case in spec["evals"]:
            if only and case["id"] not in only:
                continue
            for trial in range(1, repeats + 1):
                for arm in ("with_skill", "without_skill"):
                    plugin = plug if arm == "with_skill" else None
                    rec = run_trial(skill, case, arm, trial, plugin, timeout)
                    results.append(rec)
                    (ROOT / "results" / "partA.json").write_text(
                        json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", nargs="*",
                    default=["deai", "co-commit", "qi-read-paper", "technical-writing"])
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--repeats", type=int, default=1)
    a = ap.parse_args()
    run_part_a(a.skills, only=a.only, timeout=a.timeout, repeats=a.repeats)