#!/usr/bin/env bash
# Build every interior and cover, in EN, FR and PL:
#   kdp/hardcover/*-hardcover-interior.pdf   5.5 x 8.5 in, black ink (KDP needs 75 to 550 pages)
#   kdp/paperback/*-paperback-interior.pdf   6 x 9 in, black ink     (KDP needs 24 or more)
#   kdp/{kindle,paperback,hardcover}/        covers, via build_covers.py (spines from the page counts)
#   Rakszawa-Wisconsin-{EN,FR,PL}.epub       Kindle edition, with the plates and the Kindle cover
# Usage: kdp/build_interior.sh      (needs pandoc, weasyprint, pdfinfo, magick, and build_covers.py's needs)
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
declare -A META=([EN]=book/metadata.yaml [FR]=build/metadata-fr.yaml [PL]=build/metadata-pl.yaml)
declare -A MIN=([hardcover]=75 [paperback]=24)
P=$PWD/kdp/plates

# --- print interiors: a plate on the left page, the chapter opening on the right page facing it
for L in EN FR PL; do
  l=${L,,}
  {
    echo '<div class="half">Rakszawa, Wisconsin</div>'
    echo "<div class=\"plate\"><img src=\"$P/frontispiece.jpg\" alt=\"\"></div>"
    echo '<div class="titlepage">'; pandoc -f markdown-smart -t html "$l/title-page.md"; echo '</div>'
    echo "<div class=\"copyright\"><p>Rakszawa, Wisconsin</p><p>© 2026 Jason ’phr0zt’ Moss</p><p>${CREDIT[$L]}</p><p>${RIGHTS[$L]}</p></div>"
  } > "$tmp/front.html"
  : > "$tmp/body.md"
  for n in 1 2 3 4 5; do
    printf '\n\n::: plate\n![](%s/ch%s.jpg)\n:::\n\n' "$P" "$n" >> "$tmp/body.md"
    cat "$l/ch$n.md" >> "$tmp/body.md"
  done
  # after the last chapter: the lift at dusk, then the author and his subject
  printf '\n\n::: {.plate .tail}\n![](%s/tail-dusk.jpg)\n:::\n\n::: {.plate .tail}\n![](%s/tail-riverbank.jpg)\n:::\n' "$P" "$P" >> "$tmp/body.md"
  for fmt in hardcover paperback; do
    css=(--css="$PWD/build/print-hardcover.css")
    [ "$fmt" = paperback ] && css+=(--css="$PWD/build/print-paperback.css")
    out="kdp/$fmt/Rakszawa-Wisconsin-$L-$fmt-interior.pdf"
    pandoc "$tmp/body.md" -f markdown-smart -t html5 -s --toc --toc-depth=1 \
      -M lang="$l" -M title="Rakszawa, Wisconsin" -M pagetitle="Rakszawa, Wisconsin" -M toc-title="${TOC[$L]}" \
      -V title= --include-before-body="$tmp/front.html" "${css[@]}" -o "$tmp/$L.html"
    weasyprint -q "$tmp/$L.html" "$out"
    pages=$(pdfinfo "$out" | awk '/^Pages/ {print $2}')
    echo "$out: $pages pages"
    [ "$pages" -ge "${MIN[$fmt]}" ] && [ "$pages" -le 550 ] || { echo "KDP $fmt needs ${MIN[$fmt]}-550 pages" >&2; exit 1; }
  done
done

# --- covers (the print spines depend on the page counts above)
kdp/build_covers.py

# --- Kindle EPUBs: smaller plates, each one just under its chapter heading
mkdir "$tmp/p"
for f in "$P"/*.jpg; do magick "$f" -resize 1000x -quality 82 "$tmp/p/$(basename "$f")"; done
plate() { printf '\n\n![](%s/%s.jpg){.plate}\n\n' "$tmp/p" "$1"; }
for L in EN FR PL; do
  l=${L,,}
  { cat "$l/title-page.md"; plate frontispiece
    for n in 1 2 3 4 5; do head -n 1 "$l/ch$n.md"; plate "ch$n"; tail -n +2 "$l/ch$n.md"; echo; done
    plate tail-dusk; plate tail-riverbank; } > "$tmp/$L.md"
  pandoc "${META[$L]}" "$tmp/$L.md" -f markdown-smart -o "Rakszawa-Wisconsin-$L.epub" --toc --toc-depth=1 \
    --css=build/epub.css --epub-cover-image="kdp/kindle/Rakszawa-Wisconsin-$L-kindle.jpg"
  echo "Rakszawa-Wisconsin-$L.epub: $(du -h "Rakszawa-Wisconsin-$L.epub" | cut -f1)"
done
