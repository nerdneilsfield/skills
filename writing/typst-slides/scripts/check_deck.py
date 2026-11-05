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


def main(pdf):
    seen = []
    for i, text in enumerate(pages(pdf), 1):
        m = re.findall(r"(\d+)\s*/\s*(\d+)\s*$", text.strip(), re.M)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        seen.append((i, int(m[-1][0]) if m else None, lines[0][:60] if lines else "(blank)"))
    flagged = 0
    prev = (None, None)
    for i, n, first in seen:
        mark = ""
        if n is not None and n == prev[0]:
            # Same slide number again: an animation step repeats the title, an overflow page does not.
            mark = "step" if first == prev[1] else "OVERFLOW?"
            flagged += mark != "step"
        print(f"page {i:2d} slide {n if n else '-':>2} {mark:9} {first}")
        prev = (n, first)
    print(f"{len(seen)} pages, {flagged} suspected overflow page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]) if len(sys.argv) == 2 else print(__doc__) or 2)
