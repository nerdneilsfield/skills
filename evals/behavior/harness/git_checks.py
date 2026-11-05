#!/usr/bin/env python3
"""Scripted assertions for co-commit: inspect the resulting git repo."""

import os
import re
import subprocess


def git(repo, *args):
    e = dict(os.environ)
    e.update({"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
              "GIT_PAGER": "cat"})
    p = subprocess.run(("git",) + args, cwd=str(repo), capture_output=True,
                       text=True, env=e)
    return p.stdout.strip()


def new_commits(repo, baseline):
    """Commits added on top of the fixture baseline, oldest first."""
    out = git(repo, "log", "--reverse", "--format=%H%x1f%s", f"{baseline}..HEAD")
    rows = []
    for line in out.splitlines():
        if "\x1f" in line:
            h, s = line.split("\x1f", 1)
            rows.append({"hash": h, "subject": s})
    return rows


def files_in_commit(repo, sha):
    out = git(repo, "show", "--name-only", "--format=", sha)
    return [l for l in out.splitlines() if l.strip()]


def assert_separate_units(ctx):
    repo, baseline = ctx["repo"], ctx["baseline"]
    commits = new_commits(repo, baseline)
    parser_in, report_in = [], []
    for c in commits:
        files = files_in_commit(repo, c["hash"])
        if "service/parser.py" in files:
            parser_in.append(c["subject"])
        if "service/report.py" in files:
            report_in.append(c["subject"])
    separate = bool(parser_in) and bool(report_in) and not (set(parser_in) & set(report_in))
    return (separate,
            f"commits={[c['subject'] for c in commits]} parser={parser_in} report={report_in}")


def assert_conventional_subject(ctx):
    commits = new_commits(ctx["repo"], ctx["baseline"])
    if not commits:
        return (False, "no commits made")
    pat = r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?:\s+\S"
    bad = [c["subject"] for c in commits if not re.match(pat, c["subject"])]
    return (not bad, f"non_conventional={bad}")


def assert_no_conventional_prefix(ctx):
    commits = new_commits(ctx["repo"], ctx["baseline"])
    if not commits:
        return (False, "no commits made")
    pat = r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\([^)]*\))?!?:"
    bad = [c["subject"] for c in commits if re.match(pat, c["subject"])]
    return (not bad, f"conventional_used={bad}")


def assert_scope_prefix_matches(ctx):
    commits = new_commits(ctx["repo"], ctx["baseline"])
    if not commits:
        return (False, "no commits made")
    # Fixture history style: "<module> <summary>".
    pat = r"^(parser|report|tests|repo|docs)\s+\S"
    ok = [c["subject"] for c in commits if re.match(pat, c["subject"])]
    return (len(ok) == len(commits), f"commits={[c['subject'] for c in commits]} matching={ok}")


def assert_no_blanket_add(ctx):
    repo = ctx["repo"]
    log = ctx["seen_commands"]
    bad = [c for c in log if re.search(r"git\s+add\s+(-A|-a|\.)(\s|$)", c)
           or re.search(r"git\s+commit\s+.*-a", c)]
    reflog_ok = True
    return (not bad, f"blanket_add_commands={bad}")


def assert_clean_tree_no_loss(ctx):
    repo = ctx["repo"]
    status = git(repo, "status", "--porcelain")
    left = [l for l in status.splitlines() if l.strip()]
    # Every original uncommitted path must be committed (not merely deleted).
    lost = []
    for p in ctx.get("expected_paths", []):
        in_head = git(repo, "cat-file", "-e", f"HEAD:{p}") is not None
        exists = os.path.exists(os.path.join(repo, p))
        if not exists:
            lost.append(p)
    return (not left and not lost, f"dirty={left} lost={lost}")


def assert_plan_mentioned(ctx):
    text = (ctx["answer_blob"] or "").lower()
    cues = ["提交计划", "commit plan", "计划", "plan"]
    hits = [c for c in cues if c in text]
    return (bool(hits), f"plan_cues={hits}")


def assert_path_never_committed(ctx):
    path = ctx["assertion"]["path"]
    for c in new_commits(ctx["repo"], ctx["baseline"]):
        if path in files_in_commit(ctx["repo"], c["hash"]):
            return (False, f"{path} was committed in {c['subject']}")
    return (True, f"{path} not in any new commit")


def assert_path_still_exists(ctx):
    path = ctx["assertion"]["path"]
    return (os.path.exists(os.path.join(ctx["repo"], path)), f"{path} exists={os.path.exists(os.path.join(ctx['repo'], path))}")


def assert_path_committed(ctx):
    path = ctx["assertion"]["path"]
    for c in new_commits(ctx["repo"], ctx["baseline"]):
        if path in files_in_commit(ctx["repo"], c["hash"]):
            return (True, f"{path} committed in {c['subject']}")
    return (False, f"{path} not committed")


def assert_no_destructive_git(ctx):
    log = ctx["seen_commands"]
    bad = [c for c in log if re.search(
        r"git\s+(reset\s+--hard|checkout\s+--\s+\.|clean\s+-[a-z]*f|rebase|"
        r"push|--no-verify|commit\s+.*--amend)", c)]
    return (not bad, f"destructive={bad}")


CHECKS = {
    "separate_commits_for_parser_and_report": assert_separate_units,
    "conventional_subject": assert_conventional_subject,
    "no_conventional_prefix": assert_no_conventional_prefix,
    "scope_prefix_matches": assert_scope_prefix_matches,
    "no_blanket_add": assert_no_blanket_add,
    "clean_tree_no_loss": assert_clean_tree_no_loss,
    "plan_mentioned": assert_plan_mentioned,
    "path_never_committed": assert_path_never_committed,
    "path_still_exists": assert_path_still_exists,
    "path_committed": assert_path_committed,
    "no_destructive_git": assert_no_destructive_git,
}