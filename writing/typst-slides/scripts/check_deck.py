#!/usr/bin/env python3
"""Flag likely overflow in a compiled deck. Usage: check_deck.py deck.pdf

Needs pdftotext (poppler). Touying prints "n / N" in the footer, where n counts
slides, not pages. Consecutive pages with the same n are animation steps when
the first line (the title) repeats, and suspected overflow when it does not.
It is a screen, not a proof: always look at the rendered PNGs too.
"""
import re
import subprocess
import sys


def pages(pdf):
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return out.split("\f")[:-1] if out.endswith("\f") else out.split("\f")


def analyze(texts):
    """Return [(page, n, N, label, first line)]; label is '', 'step', 'frozen?' or 'OVERFLOW?'."""
    rows, prev = [], (None, None)
    for i, text in enumerate(texts, 1):
        m = re.findall(r"(\d+)\s*/\s*(\d+)\s*$", text.strip(), re.M)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        n, total = (int(m[-1][0]), int(m[-1][1])) if m else (None, None)
        first = lines[0][:60] if lines else "(blank)"
        label = ""
        if n is not None and n == prev[0]:
            if first == prev[1]:
                label = "step"
            elif n == total:
                # `#show: appendix` freezes the counter at the last slide, so every appendix
                # page repeats "N / N". Indistinguishable from overflow of the last slide.
                label = "frozen?"
            else:
                label = "OVERFLOW?"
        rows.append((i, n, total, label, first))
        prev = (n, first)
    return rows


def main(pdf):
    rows = analyze(pages(pdf))
    for i, n, _, label, first in rows:
        print(f"page {i:2d} slide {n if n else '-':>2} {label:9} {first}")
    over = sum(r[3] == "OVERFLOW?" for r in rows)
    frozen = sum(r[3] == "frozen?" for r in rows)
    print(f"{len(rows)} pages, {over} suspected overflow page(s)")
    if frozen:
        print(f"{frozen} page(s) repeat the final slide number with a new title: appendix pages "
              "(frozen counter), or overflow of the last slide. Look at them.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]) if len(sys.argv) == 2 else print(__doc__) or 2)
