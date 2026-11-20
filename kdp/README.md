# KDP covers

Nine JPGs (300 DPI, sRGB) plus a PDF of each print cover for KDP's print uploader, built by `./build_covers.py` from `src/front-art-clean-4x.jpg`.

| | Size | Built for |
|---|---|---|
| `kindle/` | 1911 x 2560 px | eBook cover, front only |
| `paperback/` | 6 x 9 in trim, full wrap with 0.125 in bleed | EN 12.384 in wide, as KDP expects; FR and PL estimated |
| `hardcover/` | 5.5 x 8.5 in trim, full case wrap | remixed art (`src/front-art-remix.jpg`); spine sized from the interior PDF's page count, white paper |

## Hardcover interiors

`./build_interior.sh` sets the three hardcover interiors as print PDFs (`hardcover/*-hardcover-interior.pdf`, 5.5 x 8.5 in,
black ink, no bleed) from the chapter markdown, with the eight plates in `plates/`. KDP hardcovers need at least 75 pages and
the script fails if an edition falls short. Upload these PDFs as the interior, not the EPUB. Run `./build_covers.py` after it,
since the hardcover spine is taken from the page count.

Paperback widths live in `PB_WIDTH` at the top of the script: paste in the width from KDP's
"expected cover size" message and rebuild. The lower right of each back cover is left empty for
KDP's barcode.
