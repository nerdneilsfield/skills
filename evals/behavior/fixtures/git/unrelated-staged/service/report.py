"""Render parsed records for the status page."""


def render(records):
    total = sum(r["value"] for r in records)
    return f"{len(records)} records, total={total:.2f}"
