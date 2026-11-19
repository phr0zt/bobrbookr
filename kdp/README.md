# KDP covers

Nine JPGs (300 DPI, sRGB) plus a PDF of each print cover for KDP's print uploader, built by `./build_covers.py` from `src/front-art-clean-4x.jpg`.

| | Size | Built for |
|---|---|---|
| `kindle/` | 1911 x 2560 px | eBook cover, front only |
| `paperback/` | 6 x 9 in trim, full wrap with 0.125 in bleed | EN 12.384 in wide, as KDP expects; FR and PL estimated |
| `hardcover/` | 5.5 x 8.5 in trim, full case wrap | 76 pages, white paper |

Paperback widths live in `PB_WIDTH` at the top of the script: paste in the width from KDP's
"expected cover size" message and rebuild. Hardcover page counts live in `PAGES`. The lower right of each back cover is left empty for
KDP's barcode.
