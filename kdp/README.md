# KDP files

One command builds everything, in EN, FR and PL: `./build_interior.sh`. It sets the print interiors, runs
`./build_covers.py` (the print spines are sized from the interiors' page counts), then builds the Kindle EPUBs.

| | What | Upload as |
|---|---|---|
| `hardcover/*-hardcover-interior.pdf` | 5.5 x 8.5 in, black ink, no bleed. KDP needs 75 pages or more; the build fails if an edition falls short | hardcover manuscript |
| `hardcover/*-hardcover-5.5x8.5.pdf` | full case wrap | hardcover cover |
| `paperback/*-paperback-interior.pdf` | 6 x 9 in, black ink, no bleed | paperback manuscript |
| `paperback/*-paperback-6x9.pdf` | full wrap with 0.125 in bleed, no spine text (KDP allows it only from 79 pages) | paperback cover |
| `../Rakszawa-Wisconsin-{EN,FR,PL}.epub` | Kindle edition with the plates | eBook manuscript |
| `kindle/*-kindle.jpg` | 1702 x 2560 px, front only | eBook cover |

The front art is `src/front-art-remix.jpg`, with no lettering on it; the title and subtitle are set by the script.
The eight plates are in `plates/`. The lower right of each back cover is left empty for KDP's barcode.
If KDP reports a different expected cover size, the page count it used differs from the interior PDF's.
