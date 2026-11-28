# 18_displacement — the row top and the cell baseline are derived by two pieces of arithmetic that are not inverses. Fix measured on the emitted bytes; NOT landed (no slot to re-measure 214).

**28 Nov 2026, fixer slot 05:54.** Engine at HEAD `782a290c`, fingerprint `a05b20eb05fe0fc8`.
Corpus 214 converted on that engine. The change is carried as
`18_displacement-ROWTOP-CELL-BASELINE-NOT-INVERSES-PATCH-28NOV.patch`, **not applied** — the tree is
clean and no claim is made about it.

## The mechanism

`DocxWriter.java:6662` invents a row's top edge from the page's own row rule:

    rowTopPagePt = rowEdge[r] - LINE_BASE * pitchHere      (when the table is not ruled)

and the cell's baseline is then written at `rowTopPagePt + before + LINE_BASE * box`. So the baseline
the page actually drew lands at

    rowEdge[r] - LINE_BASE*pitch + before + LINE_BASE*box

which is `rowEdge[r]` **only if** `before + LINE_BASE*box == LINE_BASE*pitch`. Nothing in the cell
emission enforces that: the placed branch sets `before` from the measured baseline and caps it with
`min(rowHeightTw, contentTwHere) - boxTw`, and the fallback sets
`before = LINE_BASE*(rowLineTw - box)`. Both can leave `before + LINE_BASE*box` short of
`LINE_BASE*pitch`, and the shortfall is one-signed and identical on every row of the same geometry.

## The measurement, made before the change and independently of it

I did not trust the edit. I took the **shipped .docx** for `35_four_typefaces_one_page`, rewrote
nothing but the spacing declarations of paragraphs inside table rows (`w:before -> 0`,
`w:line -> the row's own w:trHeight`, `lineRule=exact`), rendered **both** files with `soffice`, and
read the baselines with PyMuPDF. Three independent columns: the source PDF, the shipped docx, the
rewritten docx.

| line | source PDF | shipped docx | dy | rewritten docx | dy |
|---|---:|---:|---:|---:|---:|
| masthead | 58.00 | 58.00 | 0.00 | 58.00 | 0.00 |
| sub-head | 72.00 | 72.00 | 0.00 | 72.00 | 0.00 |
| title | 104.00 | 104.00 | 0.00 | 104.00 | 0.00 |
| programme | 122.00 | 122.00 | 0.00 | 122.00 | 0.00 |
| **table row 1** | **148.80** | **152.50** | **+3.70** | **148.80** | **0.00** |
| row 2 | 167.80 | 171.50 | +3.70 | 167.80 | 0.00 |

The four body lines above the table are unmoved, so the change moves the table and nothing else. The
+3.70 is `0.2 * 18.5`, the 18.5 pt being the row pitch: the shortfall is exactly the part of the pitch
the two pieces of arithmetic disagree about, which is why it is the same number on every row.

## Then the same rewrite, in the engine

The patch applies the inverse on both cell branches, gated to a row where **every cell holds exactly
one line** (`rowParts == 1 && wrapParts == 1`) and the row is exact (`exactRows`), so a wrapped or
newline-broken cell keeps its own line height and cannot be squeezed:

    cellBoxTw = rowHeightTw;  cellBeforeTw = 0;   // before + LINE_BASE*box == LINE_BASE*pitch

Built and converted through the real engine (`ConvertOne`), `35_four_typefaces_one_page` renders at
**dy 0.00 for all six table rows** and 0.61-0.80 pt for everything below the table, against +3.70 for
every line from the table down on the shipped engine.

## Why it is not landed

Landing it needs a corpus-wide re-measurement, and this slot could not fit one: converting 214
documents took 19 minutes of the slot, and rendering them to PDF for the LibreOffice table runs at
about 5.9 s/document even at 6 workers (~21 minutes), before any scoring. The commit gate is right to
refuse a change measured on one document, so the change is a patch and this file, not a commit.

**The next run should start here.** `corpus-slice.py` converts; then render `p2w/out/*.docx` to PDF
with `soffice -env:UserInstallation=file:///tmp/lo-prof-N` per worker (a shared profile makes every
worker but the first fail silently — measured this slot: 24 of 40 "converted" files were missing),
then `pixel-score.py --corpus /scratch/work/p2w/corpus --renders <dir> --csv benchmarks/RANKING.csv`.
Budget 21 min render + 6 min score and start it in the first half hour, not the last.

**What becomes CLEAN if it works:** the rows of the 40 documents still failing `18_displacement` that
are single-line table cells — 19 of them fail nothing else. `35_four_typefaces_one_page` is proven; the
other 39 are a prediction, not a result, and the corpus table is what decides.
