# PDF to Word benchmark — 13 metrics

Run after any change to `PdfToWord`. Every figure comes from an independent library
(PyMuPDF for text, python-docx for structure), never from the engine's own report.

    python3 tools/p2w-bench/score.py <folder-with-.txt-and-.docx>

## Floor at KavoPDF 3.46.4 (203 files)

    char volume            97.44 %
    word recall            95.95 %
    line count match       93.86 %
    exact line hit         89.06 %   <- below 95
    global line hit        95.85 %
    line order accuracy    79.14 %   <- below 95, worst metric
    garbage rate            0.02 %   (lower is better)
    docx paragraphs        5944
    docx tables             120
    doc pass @95 %         71.92 %   (146/203)
    doc pass @98 %         65.52 %   (133/203)
    median per-file       100.00 %

## What each new metric caught

`line order accuracy` is a SequenceMatcher ratio over the whole line sequence, so it
measures ORDER, not just presence. At 79.14 % it is the worst metric, and the old
seven could not see it: `122_content_order_scrambled` scores hit 100 % but order
16.7 % — every line present, in the wrong order.

The worst order files are all multi-column:

    order 19.0   458 lines   115_newspaper_front_page
    order 23.2   180 lines   11_three_column_newsletter
    order 36.4   258 lines   362_price_list_dense
    order 45.1   120 lines   10_two_column_academic
    order 45.4   118 lines   101_latex_ieee_twocolumn

## The next fix, precisely

The XY-cut downstream works on **paragraphs**. A paragraph whose lines came from two
columns has a bounding box spanning the gutter, so no vertical cut can separate it and
the columns interleave. `toParagraphs` already sorts by `(column, y)`, so the failure is
upstream: column detection returns nothing for these pages.

Measured: relaxing the line-start clustering (`gap > 30f`, `need 5 %`, `bounds <= 3`)
made the newspaper report `bands=3` — and every metric fell slightly, because it also
fired on single-column pages and split their paragraphs. Reverted.

The real fix is to cut on **lines** before paragraphs are built, not to loosen the
detector.

## Approaches tried on the column problem, and rejected

All four were measured on the full corpus and reverted. None of them moved the
multi-column files at all, because column detection still returned nothing for them.

| Approach | Result |
|---|---|
| Relax the clustering (`gap > 30f`, `need 5 %`, `bounds <= 3`) | newspaper finally reported `bands=3`, but every metric fell — it also fired on single-column pages and split their paragraphs |
| Build paragraphs one column at a time (`toParagraphs` per column) | all metrics identical; `bands` is still 1 for the files that matter |
| Require the two sides to be balanced (ratio >= 0.45, so a 90/10 indent is not a column) | order 79.14 -> 79.18, nothing else moved |
| Vertical projection: a gutter is an x-range no line crosses | order 79.18 -> 79.53 overall, but `350_question_paper` fell 48.9 -> 47.1 and the multi-column files were unchanged — reverted |

## Why detection fails on these pages

Instrumented `115_newspaper_front_page`, 465 raw lines. Clustering line STARTS gave
ten groups, not three columns:

    [14-14 n=92] [38-38 n=8] [68-124 n=57] [150-150 n=84] [175-262 n=44]
    [287-287 n=60] [311-398 n=56] [423-423 n=32] [448-448 n=4] [478-533 n=28]

The lines begin at ten different x values, so no start-cluster and no projection
separates them cleanly. This page draws its text as fragments — the headline is one
word per line — and the geometry that works for a normal two-column paper does not
apply to it.

## The next thing to try

Not a threshold. Either:

1. Cut on the **glyph** level: project every glyph's x-extent (not every line's) and
   find the x-range with zero coverage. A fragment drawn at x=150 still crosses the
   gutter at x=300 if the other column's glyphs do not.
2. Accept that a fragmented layout cannot be linearised and detect it — if the page
   has more than three x-clusters of comparable weight, keep the original order and
   say so, rather than guessing wrong.
