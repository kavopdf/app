# A row split into two paragraphs put every continuation one hairline box low, and nothing took it back

Fixer, 19 Nov. Engine `DocxWriter.java` - `recordBaseline()`, called by `flowRow` and
`flowFromBox`. **KEPT: 13 documents improved, 0 worse across 213.**

## The one question

Why is `bank-statement-horizontal-rules-only` correct to +0.03 pt at the top of the page and
+5.77 pt low by y=421, accumulating a constant 0.34 pt per positioned row against a source pitch
of exactly 18.4 pt?

## Answer

There is no table on that page and no row height at all. The rows are flow paragraphs, and a row
with a left column and a right column is emitted as TWO paragraphs. The first is spaced to its y
by the pitch solver. The second is written `w:before="0"` - there is no gap to give it - and the
flow, which has already spent the first paragraph's line box, puts its baseline one hairline box
(0.069 em = 0.4554 pt at 6.6 pt type) BELOW the shared baseline.

The pitch solver then reads `ctx.lastBaseline` as the page's y and measures every following row
from a place the reader is never at. Twelve split rows, twelve hairline boxes, +5.85 pt.

Subagent A's numbers (finding `content-present-partly-displaced-bankpitch-133100-d68d.md`):
17 row paragraphs at `w:before="359" w:line="9"` (18.400 pt - the row advance is right) and 12
amount paragraphs at `w:before="0" w:line="9"`; dates 132.001 pt at the top, 431.801 pt at the
bottom, mean pitch 18.7375 against the page's 18.4.

## The fix

`recordBaseline()` records the baseline the box ACTUALLY landed on when the paragraph continues
a line already open:

    lastBaseline = lastBaseline + (1 - LINE_BASE) * lastLinePt + LINE_BASE * linePt

so the next row's pitch is relative to the page's next baseline again and the drift stops at that
one row. The continuation's own half-line remains - 0.46 pt at 6.6 pt type; removing it needs the
two halves in ONE paragraph, which is the layout's job, not the flow's.

## What it cost to get right - three constraints, each measured

| version | what broke | number |
|:--|:--|:--|
| tolerance = 0.25 em of the new box | a 34 pt drop cap swallowed the 9.2 pt line 7.7 pt above it | `70_magazine_drop_cap_photo_caption` 1.49 -> 4.28 |
| base = the paragraph's own y | counted one continuation of two on a three-box row | `table-of-contents-dot-leaders` 8.52 -> 10.72 |
| tolerance = 0.25 em of the smaller box | a sidebar label 0.85 pt off a body line counted as its continuation | `67_two_col_with_sidebar` 0.80 -> 7.82, `350_question_paper` 0.11 -> 19.59 |
| **exactness: 0.2 pt, accumulated from the open row's y** | nothing | **13 improved, 0 worse** |

## Corpus

    report-2col-table-spanning-both-columns   16.10 -> 0.76
    78_mixed_english_devanagari_line          13.51 -> 1.73
    66_two_col_footnotes_bottom               13.03 -> 2.92
    bank-statement-horizontal-rules-only       6.89 -> 0.10
    gst-invoice-horizontal-rules-only          6.72 -> 0.38
    table-of-contents-dot-leaders             10.72 -> 4.97
    65_two_col_full_width_figure_caption       4.91 -> 1.75
    newsletter-3col-header-footer              2.51 -> 0.20
    brochure-3col-with-sidebar-box             4.51 -> 2.30
    70_magazine_drop_cap_photo_caption         1.49 -> 1.16
    315_gazette_notification                   1.96 -> 1.91
    28_value_overflows_cell_txtpos             0.74 -> 0.72
    39_small_caps_letter_spacing               0.72 -> 0.70

## What it predicts

Any document whose rows are split into a left part and a right part - forms, bills, ledgers,
timetables, tables of contents - was drifting down the page by 0.4554 pt per split row. The count
of `flowRow` calls with `pitch == 0.0` in a document should equal its drift / 0.4554.

## Ruled out

* dropping fill-only rectangles from the table Edge list - measured 27.31 -> 46.58, and 2 pages.
* `w:vMerge` as the cause of the 22 pt shift on `75_merged_header_cell_three_columns`: it is a
  real missing feature (`spanR` is computed at `PdfToWord:7950` and read by nothing) but it
  affects **1 of the 18 documents in this class** - subagent B measured the whole class and only
  `75` has a cell a word processor would merge vertically. It cannot close this class and it is
  not what moves these numbers.
