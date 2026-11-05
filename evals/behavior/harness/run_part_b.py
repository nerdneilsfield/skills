#!/usr/bin/env python3
"""Part B: Counterweight 0.6.0 vs the one-line YAGNI arm."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import run_eval
import cw_checks

ROOT = Path("/tmp/behavior-eval")
SNAP = ROOT / "skills"
CW_SRC = SNAP / "coding" / "counterweight"
FIX = ROOT / "fixtures"
WORK = ROOT / "work" / "counterweight"
RUNS = ROOT / "runs" / "counterweight"
RESULTS = ROOT / "results" / "counterweight.json"

# Both arms carry this file so the only difference is the skill itself.
YAGNI = "YAGNI. Do not over-engineer. Keep changes minimal.\n"


def snapshot(d):
    out = {}
    for p in Path(d).rglob("*"):
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts:
            out[str(p.relative_to(d))] = p.read_bytes()
    return out


def prepare(case):
    d = WORK / case["id"]
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(FIX / case["fixture"], d)
    (d / "AGENTS.md").write_text(YAGNI)
    return d


def skill_loaded(rec, skill_name, plugin_dir):
    """Prove the agent actually opened the offered skill, from the event stream.

    A plugin skill is loaded on demand: either the Skill tool names
    evalplug:<skill>, or a read/search tool points inside the injected
    skills/<skill>/ directory. The answer text mentioning the name proves
    nothing, which is what the previous substring test did.
    """
    tag = f"evalplug:{skill_name}"
    for c in rec.get("tool_calls") or []:
        inp = c.get("input") if isinstance(c.get("input"), dict) else {}
        if c.get("name") == "Skill" and tag in json.dumps(inp):
            return True, f"Skill({tag})"
        for v in inp.values():
            if isinstance(v, str) and f"skills/{skill_name}" in v \
                    and str(plugin_dir) in v:
                return True, f"{c.get('name')} -> {v}"
    return False, "no skill invocation or read in transcript"


def run_arm(case, arm, trial, plugin):
    wd = prepare(case)
    before = snapshot(wd)
    rec = run_eval.run_one(
        case_id=f"cw-{case['id']}", arm=arm, prompt=case["prompt"],
        workdir=wd, plugin_dir=plugin if arm == "counterweight" else None,
        timeout=1200, trial=trial)
    why = run_eval.run_failed(rec)
    after = snapshot(wd)
    changed = sorted(k for k in after if before.get(k) != after[k])
    removed = sorted(k for k in before if k not in after)

    if arm == "counterweight":
        loaded, how = skill_loaded(rec, "counterweight", plugin)
    else:
        loaded, how = None, "baseline arm has no skill"

    ctx = {"assertion": None, "repo": wd, "prompt": case["prompt"],
           "answer_blob": rec.get("result") or "",
           "changed_paths": changed, "removed_paths": removed,
           "files_before": sorted(before)}

    grading = []
    for a in case["assertions"]:
        if why is not None:
            grading.append({"id": a["id"], "passed": False,
                            "detail": f"RUN FAILED: {why}"})
            continue
        fn = cw_checks.CHECKS.get(a["check"])
        if fn is None:
            grading.append({"id": a["id"], "passed": None, "detail": f"NO CHECK {a['check']}"})
            continue
        ctx["assertion"] = a
        try:
            ok, detail = fn(ctx)
        except Exception as e:
            ok, detail = None, f"CHECK ERROR {type(e).__name__}: {e}"
        grading.append({"id": a["id"], "passed": ok, "detail": detail})

    return {"case": case["id"], "arm": arm, "trial": trial,
            "fixture": case["fixture"],
            "transport": rec.get("transport"), "model": rec.get("model"),
            "tokens": rec.get("total_tokens_modelusage"),
            "tokens_input": rec.get("tokens_input"),
            "tokens_output": rec.get("tokens_output"),
            "cache_read": rec.get("tokens_cache_read"),
            "cache_create": rec.get("tokens_cache_create"),
            "cost_usd": rec.get("cost_usd"),
            "duration_ms": rec.get("duration_ms"),
            "num_turns": rec.get("num_turns"),
            "is_error": rec.get("is_error"),
            "run_failed": why,
            "skill_loaded": loaded, "skill_load_evidence": how,
            "changed_paths": changed, "removed_paths": removed,
            "answer": (rec.get("result") or "")[:4000],
            "grading": grading,
            "passed": sum(1 for g in grading if g["passed"] is True),
            "failed": sum(1 for g in grading if g["passed"] is False),
            "na": sum(1 for g in grading if g["passed"] is None)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--repeats", type=int, default=1)
    args = ap.parse_args()

    spec = json.loads((ROOT / "evals" / "counterweight.json").read_text())
    plug = run_eval.make_plugin(WORK / "plugin-counterweight", "counterweight", CW_SRC)
    results = []
    if RESULTS.exists():
        results = json.loads(RESULTS.read_text())

    for case in spec["cases"]:
        if args.only and case["id"] not in args.only:
            continue
        for trial in range(1, args.repeats + 1):
            for arm in ("yagni", "counterweight"):
                r = run_arm(case, arm, trial, plug)
                results = [x for x in results
                           if not (x["case"] == r["case"] and x["arm"] == r["arm"]
                                   and x["trial"] == r["trial"])]
                results.append(r)
                RESULTS.write_text(json.dumps(results, indent=2))
                print(f"[{case['id']}/{arm}/t{trial}] "
                      f"{r['passed']}P {r['failed']}F {r['na']}NA "
                      f"tok={r['tokens']} turns={r['num_turns']} "
                      f"failed={r['run_failed']} "
                      f"changed={r['changed_paths']} skill_loaded={r['skill_loaded']}",
                      flush=True)


if __name__ == "__main__":
    main()
