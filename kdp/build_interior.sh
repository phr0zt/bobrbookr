#!/usr/bin/env bash
# Build the KDP hardcover interiors (5.5 x 8.5 in, black ink) as print PDFs, in EN, FR and PL.
# Usage: kdp/build_interior.sh      (needs pandoc, weasyprint, pdfinfo)
# KDP hardcovers need 75 to 550 pages; the script fails if an edition falls short.
# Run kdp/build_covers.py afterwards: the spine width is taken from these PDFs' page counts.
set -euo pipefail
cd "$(dirname "$0")/.."
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

declare -A TOC=([EN]="Contents" [FR]="Table des matières" [PL]="Spis treści")
declare -A RIGHTS=(
  [EN]="All rights reserved. Illustrations and cover made with AI image tools, directed by the author."
  [FR]="Tous droits réservés. Illustrations et couverture réalisées avec des outils d’image IA, sous la direction de l’auteur."
  [PL]="Wszelkie prawa zastrzeżone. Ilustracje i okładka wykonane narzędziami AI pod kierunkiem autora.")
declare -A CREDIT=(
  [EN]="Research and writing by Claude ‘Opus’ Five. Guided by Jason ‘phr0zt’ Moss."
  [FR]="Recherche et écriture : Claude « Opus » Five. Sous la direction de Jason « phr0zt » Moss."
  [PL]="Badania i tekst: Claude „Opus” Five. Prowadzenie: Jason „phr0zt” Moss.")

for L in EN FR PL; do
  l=${L,,}
  {
    echo '<div class="half">Rakszawa, Wisconsin</div>'
    echo "<div class=\"plate\"><img src=\"$PWD/kdp/plates/frontispiece.jpg\" alt=\"\"></div>"
    echo '<div class="titlepage">'; pandoc -f markdown -t html "$l/title-page.md"; echo '</div>'
    echo "<div class=\"copyright\"><p>Rakszawa, Wisconsin</p><p>© 2026 Jason ’phr0zt’ Moss</p><p>${CREDIT[$L]}</p><p>${RIGHTS[$L]}</p></div>"
  } > "$tmp/front.html"
  : > "$tmp/body.md"
  for n in 1 2 3 4 5; do
    printf '\n\n::: plate\n![](%s/kdp/plates/ch%s.jpg)\n:::\n\n' "$PWD" "$n" >> "$tmp/body.md"
    cat "$l/ch$n.md" >> "$tmp/body.md"
  done
  # after the last chapter: the lift at dusk, then the author and his subject
  printf '\n\n::: {.plate .tail}\n![](%s/kdp/plates/tail-dusk.jpg)\n:::\n\n::: {.plate .tail}\n![](%s/kdp/plates/tail-riverbank.jpg)\n:::\n' "$PWD" "$PWD" >> "$tmp/body.md"
  out="kdp/hardcover/Rakszawa-Wisconsin-$L-hardcover-interior.pdf"
  pandoc "$tmp/body.md" -f markdown -t html5 -s --toc --toc-depth=1 \
    -M lang="$l" -M title="Rakszawa, Wisconsin" -M pagetitle="Rakszawa, Wisconsin" -M toc-title="${TOC[$L]}" \
    -V title= --include-before-body="$tmp/front.html" --css="$PWD/build/print-hardcover.css" -o "$tmp/$L.html"
  weasyprint -q "$tmp/$L.html" "$out"
  pages=$(pdfinfo "$out" | awk '/^Pages/ {print $2}')
  echo "$out: $pages pages"
  [ "$pages" -ge 75 ] && [ "$pages" -le 550 ] || { echo "KDP hardcover needs 75-550 pages" >&2; exit 1; }
done
