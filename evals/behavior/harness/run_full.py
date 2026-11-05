#!/usr/bin/env python3
"""Run the whole evaluation: Part A rerun, then Part B, then write FULL_DONE.

Both parts share one model and one transport, chosen here after a preflight,
so the two parts stay comparable. If every transport is rate-limited the
script waits for the earliest reset instead of burning trials on 429s.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/tmp/behavior-eval")
HARNESS = ROOT / "harness"
RESULTS = ROOT / "results"
sys.path.insert(0, str(HARNESS))
import run_eval

REPEATS = os.environ.get("EVAL_REPEATS", "2")
SKILLS = ["deai", "co-commit", "qi-read-paper", "technical-writing"]


def log(msg):
    print(f"{datetime.now().isoformat(timespec='seconds')} {msg}", flush=True)


def try_transport(name):
    """One cheap real call. Returns (usable, reset_epoch)."""
    run_eval.TRANSPORT = name
    wd = ROOT / "work" / "_preflight"
    wd.mkdir(parents=True, exist_ok=True)
    try:
        rec = run_eval.run_one(case_id="_preflight", arm=name,
                               prompt="Reply with exactly: OK", workdir=wd,
                               plugin_dir=None, timeout=300, trial=1)
    except Exception as e:
        log(f"preflight {name}: {type(e).__name__}: {e}")
        return False, None
    why = run_eval.run_failed(rec)
    if why is None:
        log(f"preflight {name}: usable (tok={rec.get('total_tokens_modelusage')})")
        return True, None
    reset = run_eval.rate_limited_until(rec)
    log(f"preflight {name}: unusable ({why}, reset={reset})")
    return False, reset


def pick_transport():
    preferred = os.environ.get("EVAL_TRANSPORT", "direct")
    order = [preferred] + [t for t in ("proxy", "direct") if t != preferred]
    while True:
        resets = []
        for name in order:
            ok, reset = try_transport(name)
            if ok:
                return name
            if reset:
                resets.append(reset)
        if not resets:
            log("no transport answers and no reset time reported; giving up")
            return None
        wait = min(resets) - time.time() + 60
        if wait <= 0:
            wait = 60
        log(f"all transports limited; sleeping {wait / 3600:.2f}h")
        time.sleep(wait)


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    log(f"model={run_eval.MODEL} repeats={REPEATS} snapshot={ROOT / 'skills'}")
    transport = pick_transport()
    if transport is None:
        return 2
    env = dict(os.environ)
    env["EVAL_TRANSPORT"] = transport
    log(f"using transport={transport}")

    rc_a = subprocess.run(
        [sys.executable, str(HARNESS / "run_part_a.py"),
         "--skills", *SKILLS, "--repeats", REPEATS],
        cwd=str(ROOT), env=env).returncode
    log(f"part A exit {rc_a}")
    rc_b = subprocess.run(
        [sys.executable, str(HARNESS / "run_part_b.py"), "--repeats", REPEATS],
        cwd=str(ROOT), env=env).returncode
    log(f"part B exit {rc_b}")
    return 0 if (rc_a == 0 and rc_b == 0) else 1


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        code = 3
    finally:
        (RESULTS / "FULL_DONE").write_text(
            f"exit={code}\nfinished={datetime.now(timezone.utc).isoformat()}\n"
            f"transport={run_eval.TRANSPORT}\nrepeats={REPEATS}\n")
        log(f"FULL_DONE written exit={code}")
