#!/bin/sh
# First look at a PDF or image template before rebuilding it in Typst.
# Usage: pdf_spec.sh template.pdf [outdir]. Writes page PNGs and embedded images to outdir,
# prints page size, fonts and image list. Needs poppler (pdfinfo, pdffonts, pdfimages, pdftoppm).
set -eu
pdf=${1:?usage: pdf_spec.sh template.pdf [outdir]}
out=${2:-${pdf%.pdf}-spec}
mkdir -p "$out"
pdfinfo "$pdf" | grep -E 'Pages|Page size'
echo "--- fonts (name, embedded) ---"
pdffonts "$pdf"
echo "--- images (a repeated image on every page is a logo or background) ---"
pdfimages -list "$pdf" | head -30
pdfimages -png "$pdf" "$out/img" >/dev/null 2>&1 || true
pdftoppm -r 50 -png "$pdf" "$out/page"
echo "wrote $out/page-*.png and $out/img-*.png"
