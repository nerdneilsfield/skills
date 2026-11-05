#!/usr/bin/env python3
"""Behavioural eval harness for nerdneilsfield skills.

Design notes / deviations are recorded in REPORT.md. This harness only runs
agents; grading lives in grade.py.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT = Path("/tmp/behavior-eval/skills")
RUNS = Path("/tmp/behavior-eval/runs")
MODEL = os.environ.get("EVAL_MODEL", "claude-sonnet-5-5")

# Isolation: --setting-sources '' hides the user's ~/.claude/skills so the
# without-skill arm really has no skill. --plugin-dir injects exactly one
# skill directory for the with-skill arm. --strict-mcp-config drops MCP.
#
# Transport: EVAL_TRANSPORT=direct uses the Claude subscription; =proxy routes
# to the local opencodex proxy on 127.0.0.1:10100, which serves the same
# claude-sonnet-5-5 model. Both are metered with independent 5-hour windows;
# run_full.py picks whichever answers and waits out a limit. See REPORT.md.
PROXY = "http://127.0.0.1:10100"
PROXY_ENV = {"ANTHROPIC_BASE_URL": PROXY, "ANTHROPIC_API_KEY": "dummy"}
TRANSPORT = os.environ.get("EVAL_TRANSPORT", "direct")

BASE_ARGS = [
    "--model", MODEL,
    "--setting-sources", "",
    "--strict-mcp-config",
    # stream-json is the only format that carries tool calls; --output-format
    # json returns just the final text, which cannot prove the skill was read.
    "--output-format", "stream-json",
    "--verbose",
    "--no-session-persistence",
]

TOOLS = "Bash,Read,Write,Edit,Glob,Grep"

# "You've reached your 5-hour usage limit ... resets at 2026-11-05T11:26:16.841Z"
RESET_RE = re.compile(r"resets at (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z)")


def parse_stream(raw: str):
    """Split a stream-json transcript into (events, result payload, tool calls)."""
    events = []
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    payload = None
    limits = None
    for e in events:
        if e.get("type") == "result":
            payload = e
        elif e.get("type") == "rate_limit_event":
            limits = e.get("rate_limit_info")
    calls = []
    for e in events:
        if e.get("type") != "assistant":
            continue
        for b in (e.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                calls.append({"name": b.get("name"), "input": b.get("input")})
    return events, payload, calls, limits


def rate_limited_until(record: dict) -> float | None:
    """Epoch seconds when a rate limit lifts, if the run hit one.

    The subscription reports quota state directly in the stream, which is
    exact; the 429 message is the fallback for the proxy.
    """
    for window in ((record.get("rate_limit") or {}).get("unifiedWindows") or {}).values():
        if window.get("status") == "rejected" and window.get("resetsAt"):
            return float(window["resetsAt"])
    if (record.get("rate_limit") or {}).get("status") == "rejected":
        reset = (record["rate_limit"] or {}).get("resetsAt")
        if reset:
            return float(reset)
    blob = " ".join(str(record.get(k) or "") for k in ("result", "stderr"))
    m = RESET_RE.search(blob)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1).split(".")[0], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc).timestamp()
    except Exception:
        return time.time() + 3600


def make_plugin(dest: Path, skill_name: str, skill_src: Path) -> Path:
    """Wrap one skill dir as a single-skill plugin so it is the only skill."""
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "skills").mkdir(parents=True)
    (dest / ".claude-plugin").mkdir(parents=True)
    shutil.copytree(skill_src, dest / "skills" / skill_name)
    (dest / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": "evalplug",
        "version": "1.0.0",
        "description": "isolated single-skill plugin for evaluation",
    }))
    return dest


def run_failed(record: dict) -> str | None:
    """Why a run did not produce a gradeable result, or None if it did.

    An empty answer or a zero-token run means the agent never completed the
    task. Grading such a run would let a crash look like a correct no-op.
    """
    if not (record.get("result") or "").strip():
        return "empty answer"
    if record.get("total_tokens_modelusage") == 0:
        return "zero tokens"
    return None


def wait_out_limit(record: dict, cap: float = 6 * 3600) -> bool:
    """Sleep past a 5-hour quota reset so the caller's retry can succeed.

    Both transports are metered. A trial that dies on the limit is not a
    result; waiting is the only way a 100-trial run finishes.
    """
    until = rate_limited_until(record)
    if until is None:
        return False
    wait = until - time.time() + 30
    if wait <= 0 or wait > cap:
        return False
    print(f"[{record['case']}/{record['arm']}/t{record['trial']}] rate limited; "
          f"sleeping {wait / 3600:.2f}h until "
          f"{datetime.fromtimestamp(until, timezone.utc).isoformat()}", flush=True)
    time.sleep(wait)
    return True


def run_one(*, case_id: str, arm: str, prompt: str, workdir: Path,
            plugin_dir: Path | None, timeout: int, trial: int = 1,
            extra_env=None) -> dict:
    outdir = RUNS / case_id / f"{arm}-t{trial}"
    if outdir.exists():
        shutil.rmtree(outdir)
    (outdir / "outputs").mkdir(parents=True)

    cmd = ["claude", "-p", prompt] + BASE_ARGS
    if plugin_dir is not None:
        cmd += ["--plugin-dir", str(plugin_dir)]
    cmd += ["--allowedTools", TOOLS, "--permission-mode", "acceptEdits"]
    cmd += ["--add-dir", str(workdir)]

    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    if TRANSPORT == "proxy":
        env.update(PROXY_ENV)
    else:
        env.pop("ANTHROPIC_BASE_URL", None)
        env.pop("ANTHROPIC_API_KEY", None)
    env.pop("CLAUDE_CODE_SAFE_MODE", None)

    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(workdir), capture_output=True,
                              text=True, timeout=timeout, env=env)
        stdout, stderr, returncode = proc.stdout or "", proc.stderr or "", proc.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        returncode = -1
    duration_ms = int((time.time() - started) * 1000)

    record = {"case": case_id, "arm": arm, "trial": trial, "prompt": prompt,
              "plugin_dir": str(plugin_dir) if plugin_dir else None,
              "workdir": str(workdir), "duration_ms": duration_ms,
              "returncode": returncode, "transport": TRANSPORT, "model": MODEL}

    raw = stdout
    (outdir / "stdout.raw").write_text(raw)
    if stderr:
        (outdir / "stderr.txt").write_text(stderr)
    record["stderr"] = stderr[-2000:]

    events, payload, calls, limits = parse_stream(raw)
    (outdir / "tools.json").write_text(json.dumps(calls, indent=2))
    record["tool_calls"] = calls
    record["rate_limit"] = limits

    if payload:
        usage = payload.get("usage") or {}
        mu = payload.get("modelUsage") or {}
        record.update({
            "result": payload.get("result", ""),
            "is_error": payload.get("is_error"),
            "num_turns": payload.get("num_turns"),
            "stop_reason": payload.get("stop_reason"),
            "tokens_input": usage.get("input_tokens"),
            "tokens_output": usage.get("output_tokens"),
            "tokens_cache_read": usage.get("cache_read_input_tokens"),
            "tokens_cache_create": usage.get("cache_creation_input_tokens"),
            "cost_usd": payload.get("total_cost_usd"),
            "models": list(mu.keys()),
        })
        tu = sum(v.get("inputTokens", 0) + v.get("outputTokens", 0)
                 + v.get("cacheReadInputTokens", 0)
                 + v.get("cacheCreationInputTokens", 0) for v in mu.values())
        record["total_tokens_modelusage"] = tu
    else:
        record["result"] = raw
        record["is_error"] = True

    # The raw event stream is the transcript: it carries tool calls, which the
    # final-text payload alone does not.
    (outdir / "transcript.json").write_text(raw)
    (outdir / "timing.json").write_text(json.dumps({
        "duration_ms": duration_ms,
        "total_tokens": record.get("total_tokens_modelusage"),
        "model": MODEL,
        "run_failed": run_failed(record),
    }, indent=2))
    wait_out_limit(record)
    return record