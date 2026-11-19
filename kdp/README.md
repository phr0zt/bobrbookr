# KDP covers

Nine JPGs, 300 DPI, sRGB, built by `./build_covers.py` from `src/front-art-clean-4x.jpg`.

| | Size | Built for |
|---|---|---|
| `kindle/` | 1911 x 2560 px | eBook cover, front only |
| `paperback/` | A5 trim (5.83 x 8.27 in), full wrap with 0.125 in bleed | 48 / 54 / 50 pages (EN / FR / PL), white paper |
| `hardcover/` | 5.5 x 8.5 in trim, full case wrap | 76 pages, white paper |

Page counts live in `PAGES` at the top of the script. Spine width depends on them, so change
them and rebuild if the interior changes. The lower right of each back cover is left empty for
KDP's barcode.
