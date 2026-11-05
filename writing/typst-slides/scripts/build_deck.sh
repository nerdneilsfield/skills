#!/bin/sh
# Compile a Typst deck, render every page to PNG, and screen for overflow.
# Usage: build_deck.sh deck.typ [outdir]   (default outdir: <deck>-pages next to the deck)
# Needs: typst 0.15+, pdftoppm and pdftotext (poppler). Extra args after outdir go to `typst compile`.
set -eu
deck=${1:?usage: build_deck.sh deck.typ [outdir]}
out=${2:-${deck%.typ}-pages}
[ $# -ge 2 ] && shift 2 || shift 1
here=$(dirname "$0")
mkdir -p "$out"
pdf="$out/$(basename "${deck%.typ}").pdf"
typst compile "$@" "$deck" "$pdf"
pdftoppm -r 60 -png "$pdf" "$out/page"
python3 -I "$here/check_deck.py" "$pdf"
echo "pages: $out/page-*.png  (open them and look; the check above is only a screen)"
