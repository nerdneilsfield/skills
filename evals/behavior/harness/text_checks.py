#!/usr/bin/env python3
"""Scripted assertions for Part A output evals.

Each check returns (passed: bool, detail: str). Checks operate on the agent's
final text answer and on the files left in the trial workspace.
"""

import re

PROTECTED = {
    "numeric": ["2.4.0", "2.3.x", "10000", "500", "250ms", "30s", "8080"],
    "identifiers": ["--batch-size", "TELEMETRY_INGEST_LEGACY_MODE",
                    "ghcr.io/acme/telemetry-ingest:2.4.0", "ingest-worker",
                    "TELEMETRY_INGEST_ENDPOINT", "/healthz"],
    "academic": ["96 KB", "12-hour", "1.4 billion", "3.1%", "11.7%",
                 "99th percentile", "count-min sketch"],
}


def norm(s):
    return re.sub(r"\s+", " ", s or "")


def present(span, text):
    """Lenient on whitespace and thousands separators, strict on the token."""
    t = norm(text)
    if norm(span) in t:
        return True
    return span.replace(",", "") in t.replace(",", "")


def all_numbers(text):
    return set(re.findall(r"\d+(?:[.,]\d+)?", text or ""))


# ---------- deai ----------

def required_spans(ctx):
    """Only spans the case input actually carries are at stake.

    PROTECTED is the union of every fixture's facts; a case whose input never
    contained a span cannot require it to survive. Deriving the set from
    prompt + fixture text keeps one check usable across cases.
    """
    source = (ctx.get("prompt") or "") + "\n" + (ctx.get("fixture_text") or "")
    return sorted(s for group in PROTECTED.values() for s in group
                  if present(s, source))


def check_protected_spans(ctx):
    blob = ctx["answer_blob"] + "\n" + ctx.get("file_blob", "")
    missing = [s for s in required_spans(ctx) if not present(s, blob)]
    return (not missing, f"missing={missing}")


def check_span_count(ctx):
    blob = ctx["answer_blob"] + "\n" + ctx.get("file_blob", "")
    need = ctx["assertion"].get("min", 1)
    found = sorted({s for g in PROTECTED.values() for s in g if present(s, blob)})
    return (len(found) >= need, f"found={len(found)} need>={need}: {found}")


def check_slop_reduced(ctx):
    """Judge the rewritten file only.

    The answer text legitimately quotes the phrases it removed, so scanning it
    would punish a correct report.
    """
    a = ctx["assertion"]
    blob = norm((ctx.get("file_blob") or "")).lower()
    if not blob.strip():
        return (None, "no rewritten file available to judge")
    remaining = [m for m in a["markers"] if m.lower() in blob]
    return (len(remaining) <= a["max_remaining"], f"remaining={remaining}")


def check_no_new_numbers(ctx):
    """Only the rewritten artifact can introduce facts; a report may cite counts.

    Numbers appearing only in the answer (e.g. "0 candidates, down from 8")
    are quotes of tool output and are not new claims about the document.
    """
    # The input may be the prompt itself (no fixture file), so both count as
    # known facts. Otherwise a prompt-only case allows no number at all.
    allowed = all_numbers((ctx.get("prompt") or "") + "\n"
                          + (ctx.get("fixture_text") or ""))
    blob = ctx.get("file_blob") or ""
    if not blob.strip():
        return (None, "no rewritten file available to judge")
    extra = {n for n in all_numbers(blob) if n not in allowed}
    return (not extra, f"extra_numbers_in_file={sorted(extra)}")


def check_file_written(ctx):
    return (len(ctx["changed_paths"]) > 0, f"changed={ctx['changed_paths']}")


def check_file_unchanged(ctx):
    path = ctx["assertion"]["path"]
    if path in ctx["unchanged_paths"]:
        return (True, f"{path} unchanged")
    if path in ctx["changed_paths"]:
        return (False, f"{path} WAS MODIFIED")
    return (False, f"{path} missing")


def check_no_full_rewrite(ctx):
    text = ctx["answer_blob"]
    long_answer = len(text.split()) > 600
    fenced = text.count("```") >= 4
    return (not (long_answer and fenced),
            f"words={len(text.split())} fences={text.count('```')}")


def check_mentions_markers(ctx):
    a = ctx["assertion"]
    blob = norm((ctx["answer_blob"] + "\n" + ctx.get("file_blob", "")).lower())
    hits = [m for m in a["markers"] if m.lower() in blob]
    return (len(hits) >= a.get("min_hits", 1), f"hits={hits}")


def check_no_human_verdict_promise(ctx):
    text = norm(ctx["answer_blob"]).lower()
    bad = ["is 100% human", "definitely human", "guaranteed to pass",
           "this will pass ai detection", "zero ai probability"]
    return (not [b for b in bad if b in text], "no score promise")


def check_no_hedge_injection(ctx):
    a = ctx["assertion"]
    blob = norm((ctx["answer_blob"] + "\n" + ctx.get("file_blob", "")).lower())
    return (not [h for h in a["hedges"] if h in blob], f"hedges={a['hedges']}")


def check_minimal_edit_posture(ctx):
    text = norm(ctx["answer_blob"]).lower()
    cues = ["no change", "minimal", "already appropriate", "不需要修改", "无需修改",
            "最小", "keep as is", "leave as is", "technical", "academic", "学术"]
    hits = [c for c in cues if c in text]
    return (bool(hits), f"cues={hits}")


# ---------- qi-read-paper ----------

def check_single_round_pacing(ctx):
    text = ctx["answer_blob"].lower()
    round_headers = len(re.findall(r"(第一轮|第二轮|第三轮|round 1|round 2|round 3)", text))
    deep = any(k in text for k in ["第三轮", "round 3", "复现路径", "limitations and reproduction"])
    return (round_headers <= 2 and not deep,
            f"round_headers={round_headers} deep={deep}")


def check_no_round_pacing(ctx):
    text = ctx["answer_blob"].lower()
    hits = re.findall(r"(第一轮|第二轮|第三轮|round 1|round 2|round 3|next round|继续.*轮)", text)
    return (not hits, f"round_cues={hits}")


def check_max_words(ctx):
    a = ctx["assertion"]
    n = len(ctx["answer_blob"].split())
    return (n <= a["max"], f"words={n} max={a['max']}")


def check_no_reproduction_claim(ctx):
    text = norm(ctx["answer_blob"]).lower()
    bad = ["i reproduced", "we reproduced", "reproduction complete", "已经复现",
           "复现成功", "reproduced the results"]
    return (not [b for b in bad if b in text], "no false reproduction claim")


def check_cites_locations(ctx):
    text = ctx["answer_blob"].lower()
    hits = re.findall(r"(section \d+|§\s?\d+|第\s?\d+\s?节|table \d+|图\s?\d+)", text)
    return (len(hits) >= 1, f"citations={hits[:8]}")


# ---------- technical-writing ----------

def check_has_commands(ctx):
    """Commands must appear in the deliverable.

    A guide is written to a file; the chat answer only reports on it. Judging
    the answer alone marked a file full of kubectl blocks as having no steps.
    """
    blob = ctx["answer_blob"] + "\n" + (ctx.get("file_blob") or "")
    return (blob.count("```") >= 2 or "kubectl" in blob.lower(),
            f"fences={blob.count('```')}")


def check_no_confident_invention(ctx):
    blob = norm((ctx["answer_blob"] + "\n" + ctx.get("file_blob", "")).lower())
    suspects = ["3 replicas", "replicas: 3", "requests: cpu", "limits: cpu"]
    hits = [s for s in suspects if s in blob]
    flagged = any(k in blob for k in ["confirm", "待确认", "未知", "unknown", "needs confirmation"])
    return (not hits or flagged, f"invented={hits} flagged={flagged}")


def check_declines_out_of_scope(ctx):
    text = norm(ctx["answer_blob"]).lower()
    cues = ["outside", "not within", "scope", "academic", "paper", "论文", "学术",
            "qi-read-paper", "deai", "超出", "不属于"]
    hits = [c for c in cues if c in text]
    return (len(hits) >= 2, f"scope_cues={hits}")


def check_no_doc_restructure(ctx):
    blob = norm((ctx["answer_blob"] + "\n" + ctx.get("file_blob", "")).lower())
    bad = ["## prerequisites", "## quick start", "## installation", "deployment guide",
           "troubleshooting section"]
    hits = [b for b in bad if b in blob]
    return (not hits, f"doc_shapes={hits}")


# ---------- technical-writing review fixture ----------

def check_catches_retention_contradiction(ctx):
    blob = norm((ctx["answer_blob"]).lower())
    seven = ("7 day" in blob) or ("7 天" in blob)
    fourteen = ("14 day" in blob) or ("14 天" in blob)
    return (seven and fourteen, f"seven={seven} fourteen={fourteen}")


# ---------- protected-span survival (diff based) ----------
#
# Stronger than "present in answer": we compare the set of protected spans in
# the pre-run fixture against the same set in the post-run workspace files.
# A span that was present and is now gone has been destroyed by the edit.

PROTECTED_PATTERNS = [
    r"\b\d+\.\d+\.\d+\b",                 # versions like 2.4.0
    r"\b\d+\.\d+\.x\b",                   # 2.3.x
    r"--[a-z][a-z0-9-]+",                 # long flags
    r"\b[A-Z][A-Z0-9_]{6,}\b",            # env vars / constants
    r"ghcr\.io/[A-Za-z0-9._\-/]+:[A-Za-z0-9._-]+",  # image tags
    r"/[a-zA-Z0-9._-]+(?:/[a-zA-Z0-9._-]+)*",       # paths
    r"\b\d+\.\d+%",                       # percentages
    r"\b\d+\s?(?:KB|MB|GB|ms|s)\b",       # units
    r"\b\d+(?:,\d{3})+\b",                # thousands-separated numbers
]


def spans_in(text):
    out = set()
    for pat in PROTECTED_PATTERNS:
        out |= set(re.findall(pat, text or ""))
    return out


def check_protected_span_survival(ctx):
    """Every protected span present before the run must still be present after."""
    before = set(ctx.get("fixture_spans") or [])
    after_files = set()
    for name, blob in (ctx.get("files_after") or {}).items():
        after_files |= spans_in(blob)
    after_files |= spans_in(ctx["answer_blob"])
    lost = sorted(s for s in before if s not in after_files)
    return (not lost, f"lost_spans={lost}")


def check_span_count_preserved(ctx):
    before = set(ctx.get("fixture_spans") or [])
    after = set()
    for blob in (ctx.get("files_after") or {}).values():
        after |= spans_in(blob)
    after |= spans_in(ctx["answer_blob"])
    return (len(after) >= len(before),
            f"before={len(before)} after={len(after)}")


CHECKS = {
    "protected_span_survival": check_protected_span_survival,
    "span_count_preserved": check_span_count_preserved,
    "protected_spans": check_protected_spans,
    "span_count": check_span_count,
    "slop_reduced": check_slop_reduced,
    "no_new_numbers": check_no_new_numbers,
    "file_written": check_file_written,
    "file_unchanged": check_file_unchanged,
    "no_full_rewrite": check_no_full_rewrite,
    "mentions_markers": check_mentions_markers,
    "no_human_verdict_promise": check_no_human_verdict_promise,
    "no_hedge_injection": check_no_hedge_injection,
    "minimal_edit_posture": check_minimal_edit_posture,
    "single_round_pacing": check_single_round_pacing,
    "no_round_pacing": check_no_round_pacing,
    "max_words": check_max_words,
    "no_reproduction_claim": check_no_reproduction_claim,
    "cites_locations": check_cites_locations,
    "has_commands": check_has_commands,
    "no_confident_invention": check_no_confident_invention,
    "declines_out_of_scope": check_declines_out_of_scope,
    "no_doc_restructure": check_no_doc_restructure,
    "catches_retention_contradiction": check_catches_retention_contradiction,
}