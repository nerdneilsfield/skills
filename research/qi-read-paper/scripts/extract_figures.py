#!/usr/bin/env python3
"""Extract paper figures from a PDF with poppler.

List embedded images:    extract_figures.py paper.pdf --list
Save embedded images:    extract_figures.py paper.pdf --images out/
Render whole pages:      extract_figures.py paper.pdf --pages 3,7 out/   (ranges too: 2-5,9)
Crop a region of a page: extract_figures.py paper.pdf --crop 3 10 20 80 40 out/fig3.png
Crop values are percentages of the page as displayed (rotation applied): left, top, width, height.
Errors (bad page, missing poppler) print one line and exit 2.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

DPI = 220  # keeps small labels readable without producing huge pages


class FigureError(Exception):
    pass


def run(*cmd):
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    except FileNotFoundError:
        raise FigureError(f"{cmd[0]} not found; install poppler-utils")
    except subprocess.CalledProcessError as e:
        raise FigureError(f"{cmd[0]} failed: {e.stderr.strip()[:200]}")


def page_count(pdf):
    match = re.search(r"^Pages:\s+(\d+)", run("pdfinfo", str(pdf)), re.M)
    if not match:
        raise FigureError(f"cannot read the page count of {pdf}")
    return int(match[1])


def parse_pages(spec, total):
    """'3,7' or '2-5,9' -> sorted page numbers; pages outside 1..total are an error."""
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", part)
        if not m:
            raise FigureError(f"bad page list item: {part!r} (use 3, 2-5, or 1,4-6)")
        lo, hi = int(m[1]), int(m[2] or m[1])
        if lo > hi:
            raise FigureError(f"empty page range: {part}")
        pages.update(range(lo, hi + 1))
    bad = sorted(p for p in pages if not 1 <= p <= total)
    if bad:
        raise FigureError(f"page(s) {', '.join(map(str, bad))} outside 1..{total}")
    return sorted(pages)


def page_size(pdf, page):
    """Size in points of the page as displayed: width and height swap when /Rotate is 90 or 270."""
    info = run("pdfinfo", "-f", str(page), "-l", str(page), str(pdf))
    match = re.search(r"Page\s+\d+\s+size:\s+([\d.]+) x ([\d.]+) pts", info)
    if not match:
        raise FigureError(f"page {page} not found in {pdf}")
    width, height = float(match[1]), float(match[2])
    rot = re.search(r"Page\s+\d+\s+rot:\s+(-?\d+)", info)
    if rot and int(rot[1]) % 180 == 90:
        width, height = height, width
    return width, height


def crop(pdf, page, box, output):
    total = page_count(pdf)
    if not 1 <= page <= total:
        raise FigureError(f"page {page} outside 1..{total}")
    width, height = page_size(pdf, page)
    scale = DPI / 72
    left, top, wide, tall = (value / 100 for value in box)
    args = ["-x", round(left * width * scale), "-y", round(top * height * scale),
            "-W", round(wide * width * scale), "-H", round(tall * height * scale)]
    output.parent.mkdir(parents=True, exist_ok=True)
    run("pdftoppm", "-r", str(DPI), "-f", str(page), "-l", str(page), "-png", "-singlefile",
        *map(str, args), str(pdf), str(output.with_suffix("")))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--images", type=Path)
    parser.add_argument("--pages", nargs=2, metavar=("LIST", "DIR"))
    parser.add_argument("--crop", nargs=6, metavar=("PAGE", "LEFT", "TOP", "WIDTH", "HEIGHT", "OUT"))
    args = parser.parse_args()
    try:
        return dispatch(args, parser)
    except FigureError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def dispatch(args, parser):
    if args.list:
        print(run("pdfimages", "-list", str(args.pdf)))
    elif args.images:
        args.images.mkdir(parents=True, exist_ok=True)
        run("pdfimages", "-png", str(args.pdf), str(args.images / "img"))
    elif args.pages:
        out = Path(args.pages[1])
        out.mkdir(parents=True, exist_ok=True)
        for page in parse_pages(args.pages[0], page_count(args.pdf)):
            run("pdftoppm", "-r", str(DPI), "-f", str(page), "-l", str(page), "-png", "-singlefile",
                str(args.pdf), str(out / f"page-{page}"))
    elif args.crop:
        page, *box, out = args.crop
        crop(args.pdf, int(page), [float(v) for v in box], Path(out))
    else:
        parser.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
