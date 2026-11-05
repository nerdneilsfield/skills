#!/usr/bin/env python3
"""Extract paper figures from a PDF with poppler.

List embedded images:    extract_figures.py paper.pdf --list
Save embedded images:    extract_figures.py paper.pdf --images out/
Render whole pages:      extract_figures.py paper.pdf --pages 3,7 out/
Crop a region of a page: extract_figures.py paper.pdf --crop 3 10 20 80 40 out/fig3.png
Crop values are page percentages: left, top, width, height.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

DPI = 220  # keeps small labels readable without producing huge pages


def run(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def page_size(pdf, page):
    info = run("pdfinfo", "-f", str(page), "-l", str(page), str(pdf))
    match = re.search(r"Page\s+\d+\s+size:\s+([\d.]+) x ([\d.]+) pts", info)
    return float(match[1]), float(match[2])


def crop(pdf, page, box, output):
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
    if args.list:
        print(run("pdfimages", "-list", str(args.pdf)))
    elif args.images:
        args.images.mkdir(parents=True, exist_ok=True)
        run("pdfimages", "-png", str(args.pdf), str(args.images / "img"))
    elif args.pages:
        out = Path(args.pages[1])
        out.mkdir(parents=True, exist_ok=True)
        for page in args.pages[0].split(","):
            run("pdftoppm", "-r", str(DPI), "-f", page, "-l", page, "-png", "-singlefile",
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
