"""Render parsed records for the status page."""


def render(records):
    total = sum(r["value"] for r in records)
    return f"{len(records)} records, total={total:.2f}"


def render_grouped(records, key="name"):
    """Group records by a field and render one line per group."""
    groups = {}
    for r in records:
        groups.setdefault(r.get(key, "unknown"), []).append(r["value"])
    return "\n".join(f"{k}: n={len(v)} total={sum(v):.2f}" for k, v in sorted(groups.items()))
