#!/usr/bin/env python3
"""Build throwaway git fixtures for the co-commit evals.

Each fixture is a repo with an ESTABLISHED commit convention in its history
and a working tree containing several separable, uncommitted changes.
"""

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path("/tmp/behavior-eval/fixtures/git")

PARSER_WITH_TAGS = '''"""Parse raw metric lines into records."""


def parse_line(line):
    name, _, value = line.partition("=")
    return {"name": name.strip(), "value": float(value)}


def parse_stream(lines):
    return [parse_line(l) for l in lines if l.strip()]


def parse_tags(line):
    """Parse the optional trailing tag list: cpu=1.5 #env=prod #host=web1"""
    body, _, tag_part = line.partition("#")
    record = parse_line(body)
    tags = {}
    for tok in tag_part.split("#"):
        if "=" in tok:
            k, _, v = tok.partition("=")
            tags[k.strip()] = v.strip()
    record["tags"] = tags
    return record
'''

REPORT_WITH_GROUPED = '''"""Render parsed records for the status page."""


def render(records):
    total = sum(r["value"] for r in records)
    return f"{len(records)} records, total={total:.2f}"


def render_grouped(records, key="name"):
    """Group records by a field and render one line per group."""
    groups = {}
    for r in records:
        groups.setdefault(r.get(key, "unknown"), []).append(r["value"])
    return "\\n".join(f"{k}: n={len(v)} total={sum(v):.2f}" for k, v in sorted(groups.items()))
'''

README_AFTER = ("# metrics-service\n\nInternal metrics parsing service.\n\n"
                "See `service/parser.py` for line syntax.\n")


def sh(cwd, *args, env=None):
    e = dict(os.environ)
    e.update({
        "GIT_AUTHOR_NAME": "Fixture Author",
        "GIT_AUTHOR_EMAIL": "author@example.invalid",
        "GIT_COMMITTER_NAME": "Fixture Author",
        "GIT_COMMITTER_EMAIL": "author@example.invalid",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
    })
    if env:
        e.update(env)
    return subprocess.run(args, cwd=str(cwd), check=True, capture_output=True,
                          text=True, env=e)


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def commit(repo, msg, date):
    env = {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    sh(repo, "git", "add", "-A", env=env)
    sh(repo, "git", "commit", "-m", msg, env=env)


def touch_note(repo: Path, n: int):
    """Give each history commit real content so git accepts it."""
    write(repo / "CHANGELOG.md", f"# Changelog\n\n- entry {n}: {n}\n")


def init(repo: Path):
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    sh(repo, "git", "init", "-q", "-b", "main")
    sh(repo, "git", "config", "user.name", "Fixture Author")
    sh(repo, "git", "config", "user.email", "author@example.invalid")
    sh(repo, "git", "config", "commit.gpgsign", "false")


def scaffold(repo: Path):
    """A small service with two independent modules: parser and report."""
    write(repo / "README.md", "# metrics-service\n\nInternal metrics parsing service.\n")
    write(repo / "service/__init__.py", "")
    write(repo / "service/parser.py", '''"""Parse raw metric lines into records."""


def parse_line(line):
    name, _, value = line.partition("=")
    return {"name": name.strip(), "value": float(value)}


def parse_stream(lines):
    return [parse_line(l) for l in lines if l.strip()]
''')
    write(repo / "service/report.py", '''"""Render parsed records for the status page."""


def render(records):
    total = sum(r["value"] for r in records)
    return f"{len(records)} records, total={total:.2f}"
''')
    write(repo / "tests/test_parser.py", '''from service.parser import parse_line


def test_parse_line_basic():
    assert parse_line("cpu=1.5") == {"name": "cpu", "value": 1.5}
''')
    write(repo / ".gitignore", "__pycache__/\n*.pyc\n")


CONV_HISTORY = [
    "feat(parser): add parse_stream for multi-line input",
    "fix(parser): strip whitespace around metric names",
    "test(parser): cover parse_line basics",
    "chore: ignore python bytecode",
    "feat(report): render record count and total",
    "docs: describe the metrics service",
    "fix(report): format totals to two decimals",
    "refactor(parser): use partition instead of split",
]

NONCONV_HISTORY = [
    "parser add stream parsing",
    "parser trim metric names",
    "tests cover parse_line",
    "repo ignore bytecode",
    "report render count and total",
    "docs describe service",
    "report two decimal totals",
    "parser use partition",
]


def build_conventional(repo: Path):
    """History where Conventional Commits clearly dominate."""
    init(repo)
    scaffold(repo)
    for i, msg in enumerate(CONV_HISTORY):
        touch_note(repo, i)
        commit(repo, msg, f"2024-01-{8 + i:02d}T10:00:00")

    # Uncommitted work: TWO independent logical units + one doc tweak.
    write(repo / "service/parser.py", PARSER_WITH_TAGS)
    write(repo / "service/report.py", REPORT_WITH_GROUPED)
    write(repo / "README.md", README_AFTER)


def build_nonconventional(repo: Path):
    """History where a bare '<scope> <summary>' style dominates."""
    init(repo)
    scaffold(repo)
    for i, msg in enumerate(NONCONV_HISTORY):
        touch_note(repo, i)
        commit(repo, msg, f"2024-01-{8 + i:02d}T10:00:00")
    write(repo / "service/parser.py", PARSER_WITH_TAGS)
    write(repo / "service/report.py", REPORT_WITH_GROUPED)
    write(repo / "README.md", README_AFTER)


def build_unrelated_staged(repo: Path):
    """Boundary: the user already has an unrelated change staged.

    The agent must not sweep the pre-existing staged file into its commits.
    """
    init(repo)
    scaffold(repo)
    for i, msg in enumerate(CONV_HISTORY[:6]):
        touch_note(repo, i)
        commit(repo, msg, f"2024-01-{8 + i:02d}T10:00:00")

    # Uncommitted: one feature change in parser.py ...
    write(repo / "service/parser.py", PARSER_WITH_TAGS)
    # ... plus a scratch note the user staged themselves and never mentioned.
    write(repo / "NOTES-scratch.txt", "reminder: ask dana about the retention policy\n")
    sh(repo, "git", "add", "NOTES-scratch.txt")


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    build_conventional(ROOT / "conventional")
    build_nonconventional(ROOT / "nonconventional")
    build_unrelated_staged(ROOT / "unrelated-staged")
    for name in ("conventional", "nonconventional", "unrelated-staged"):
        r = ROOT / name
        print(f"--- {name} ---")
        print("BASELINE_HEAD:", sh(r, "git", "rev-parse", "HEAD").stdout.strip()[:8])
        print("LOG:", sh(r, "git", "log", "--format=%s", "-3").stdout.strip().replace("\n", " | "))
        print("STATUS:", sh(r, "git", "status", "--short").stdout.strip().replace("\n", " | "))


if __name__ == "__main__":
    main()