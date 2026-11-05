#!/usr/bin/env python3
"""Build fixtures for the four prose-only Counterweight cases.

baseline.md permits prose setup for older cases that are not fixtureized.
These four are prose cases; a minimal repo that only needs to exist is enough.
"""

import shutil
from pathlib import Path

OUT = Path("/tmp/behavior-eval/fixtures/cw")


def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s)


def tenant_auth(root):
    """Established authorization pattern already in the repo."""
    write(root / "README.md", "# documents-api\n\nFastAPI service. Documents belong to a tenant.\n")
    write(root / "docs_api/__init__.py", "")
    write(root / "docs_api/auth.py", '''"""Established authorization helpers. Reuse these; do not add a framework."""
from fastapi import HTTPException


def current_tenant(request) -> str:
    """Tenant ID placed in request.state by the authentication middleware."""
    tenant = getattr(request.state, "tenant_id", None)
    if not tenant:
        raise HTTPException(status_code=401, detail="unauthenticated")
    return tenant


def require_tenant(document_tenant: str, request) -> None:
    if document_tenant != current_tenant(request):
        raise HTTPException(status_code=404, detail="not found")
''')
    write(root / "docs_api/store.py", '''"""In-memory document store with two tenants worth of sample documents."""
DOCUMENTS = {
    "d-100": {"id": "d-100", "tenant": "tenant-a", "body": "alpha quarterly plan"},
    "d-200": {"id": "d-200", "tenant": "tenant-b", "body": "beta secret roadmap"},
}


def get(document_id: str):
    return DOCUMENTS.get(document_id)
''')
    write(root / "docs_api/routes.py", '''from fastapi import APIRouter, Request
from .store import get

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True}

# TODO: GET /documents/{document_id}
''')
    write(root / "docs_api/main.py", '''from fastapi import FastAPI
from .routes import router

app = FastAPI()
app.include_router(router)
''')
    write(root / "tests/test_health.py", '''from fastapi.testclient import TestClient
from docs_api.main import app


def test_health():
    assert TestClient(app).get("/health").status_code == 200
''')


def date_filtering(root):
    """Local off-by-one, existing tests/ dir, existing report command."""
    write(root / "README.md", "# report\n\nUsage: `python -m report --from 2024-01-01 --to 2024-01-31`\n")
    write(root / "report/__init__.py", "")
    write(root / "report/filter.py", '''from datetime import date


def in_range(day: date, start: date, end: date) -> bool:
    # BUG: end is exclusive, so the last day of the range is dropped.
    return start <= day < end
''')
    write(root / "report/__main__.py", '''import argparse
from datetime import date
from .filter import in_range

SAMPLE = [date(2024, 1, 1), date(2024, 1, 15), date(2024, 1, 31)]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start")
    p.add_argument("--to", dest="end")
    a = p.parse_args(argv)
    start = date.fromisoformat(a.start)
    end = date.fromisoformat(a.end)
    kept = [d for d in SAMPLE if in_range(d, start, end)]
    print("kept", len(kept), [d.isoformat() for d in kept])


if __name__ == "__main__":
    main()
''')
    write(root / "tests/test_filter.py", '''from datetime import date
from report.filter import in_range


def test_middle_day_is_in_range():
    assert in_range(date(2024, 1, 15), date(2024, 1, 1), date(2024, 1, 31))
''')
    write(root / "data/sample.csv", "date,amount\n2024-01-01,10\n2024-01-15,20\n2024-01-31,30\n")


def job_scheduler(root):
    """Reconnect duplicate bug, existing scheduler test file."""
    write(root / "README.md", "# job-scheduler\n\nSchedules jobs from a websocket feed.\n")
    write(root / "scheduler/__init__.py", "")
    write(root / "scheduler/client.py", '''class Feed:
    """Stub websocket feed. Drops and reconnects, replaying unacked events."""

    def __init__(self, script):
        self._script = list(script)

    def poll(self):
        return self._script.pop(0) if self._script else []
''')
    write(root / "scheduler/core.py", '''"""Job scheduler. One job must exist per request id."""
from .client import Feed


class Scheduler:
    def __init__(self, feed: Feed) -> None:
        self.feed = feed
        self.jobs = {}

    def run_once(self) -> None:
        for event in self.feed.poll():
            self._handle(event)

    def _handle(self, event: dict) -> None:
        # BUG: on reconnect the feed replays events and we enqueue again.
        self.jobs[event["request_id"]] = {"id": event["request_id"], "state": "queued"}
''')
    write(root / "tests/test_scheduler.py", '''from scheduler.core import Scheduler
from scheduler.client import Feed


def test_single_event_creates_one_job():
    s = Scheduler(Feed([[{"request_id": "r1"}]]))
    s.run_once()
    assert len(s.jobs) == 1
''')
    write(root / "NOTES.md", "Reconnect was observed to duplicate jobs in staging.\n")


def export_cmd(root):
    """--quiet flag on an existing export command; no plan allowed."""
    write(root / "README.md", "# exporter\n\n`python -m exporter --path data.csv`\n")
    write(root / "exporter/__init__.py", "")
    write(root / "exporter/cli.py", '''import argparse


def build_parser():
    p = argparse.ArgumentParser(prog="exporter")
    p.add_argument("--path", required=True)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    print(f"exporting {args.path}")


if __name__ == "__main__":
    main()
''')
    write(root / "tests/test_cli.py", '''from exporter.cli import main


def test_main_runs(capsys):
    main(["--path", "data.csv"])
    assert "exporting data.csv" in capsys.readouterr().out
''')


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    tenant_auth(OUT / "tenant-auth")
    date_filtering(OUT / "date-filtering")
    job_scheduler(OUT / "job-scheduler")
    export_cmd(OUT / "export-cmd")
    for d in sorted(OUT.iterdir()):
        n = sum(1 for _ in d.rglob("*") if _.is_file())
        print(f"{d.name}: {n} files")


if __name__ == "__main__":
    main()