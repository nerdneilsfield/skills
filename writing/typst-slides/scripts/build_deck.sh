#!/bin/sh
# Compile a Typst deck, render every page to PNG, and screen for overflow.
# Usage: build_deck.sh deck.typ [outdir] [typst compile options...]
# Default outdir: <deck>-pages next to the deck. The PDF is written inside outdir.
# A second argument that starts with "-" is a typst option, not the outdir.
# Needs: typst 0.15+, pdftoppm and pdftotext (poppler).
set -eu
deck=${1:?usage: build_deck.sh deck.typ [outdir] [typst options]}
shift
out=${deck%.typ}-pages
case ${1-} in
  ""|-*) ;;
  *) out=$1; shift ;;
esac
here=$(dirname "$0")
mkdir -p "$out"
rm -f "$out"/page-*.png
pdf="$out/$(basename "${deck%.typ}").pdf"
typst compile "$@" "$deck" "$pdf"
pdftoppm -r 60 -png "$pdf" "$out/page"
python3 -I "$here/check_deck.py" "$pdf"
echo "pdf: $pdf"
echo "pages: $out/page-*.png  (open them and look; the check above is only a screen)"
