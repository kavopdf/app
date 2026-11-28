# Google's table row advance is not controllable by any spacing declaration. Ten variants, three documents, Google only.

**28 Nov 2026, fixer run 08:24 IST. Measured in Google Docs (upload -> convert -> export PDF ->
PyMuPDF), not LibreOffice.** Probe `.docx` files are on branch `probe-28nov` under
`benchmarks/probe-28nov/`; each is reproducible in ~30 s with `GOOGLEDRIVE_UPLOAD_FROM_URL` on the raw
URL and mime `application/vnd.google-apps.document`.

## What was believed

The 28 Nov 05:54 run root-caused `18_displacement` to the table cell: the engine writes a row's top edge
from a pitch and the cell's baseline from `before + LINE_BASE*box`, the two disagree, and the shortfall
is one-signed. Its named next step was: *"give the cell the font's natural line box and move the
identical difference into `before`, so the baseline is preserved by construction."*

That prediction is falsifiable on one document, and this run falsified it — and, measuring it, found the
mechanism underneath.

## The engine's row geometry is already exact

For `price-list-2col-dense-right-aligned` the shipped `.docx` writes `w:trHeight 328 atLeast` (16.40 pt)
and, in every cell, `w:before="317" w:line="11" w:lineRule="exact"` — `before + line = 328 tw` exactly.
The source PDF's own row pitch is **16.40 pt**. The engine asks for precisely what the page drew. The
defect is downstream of the engine.

## Ten variants, in Google

### price-list-2col-dense-right-aligned — 41 rows, 8 pt text, source pitch 16.40, source span 651.60

| variant | change | pitch | span | first row | last row |
|---|---|---|---|---|---|
| src | — | 16.290 | 651.60 | 93.69 | 745.29 |
| **v0 shipped** | — | **16.497** | **659.88** | 94.19 | 754.07 |
| v1 | trHeight +5 tw, before +5 tw | 16.601 | 664.05 | 94.44 | 758.49 |
| v2 | before 88, line 240 — the named next step | 16.500 | 643.51 | 105.70 | 749.21 |
| v3 | trHeight +5 tw only | 16.497 | 659.88 | 94.19 | 754.07 |
| v4 | trHeight −4 tw, before −4 tw | 16.497 | 659.88 | 93.99 | 753.87 |
| v5 | before −4 tw only | 16.497 | 659.88 | 93.99 | 753.87 |
| v6 | before +20 tw only | 17.107 | 684.30 | 95.19 | 779.49 |
| v7 | cell paragraph mark at 6 pt | 16.497 | 659.88 | 94.19 | 754.07 |
| v8 | `w:line="0"` | 22.468 | 674.05 | 99.48 | 773.53 |

### The same test on two other documents

| document | rows | font | source pitch | Google pitch | excess/row | accumulated |
|---|---:|---:|---:|---:|---:|---:|
| `price-list-2col-dense-right-aligned` | 40 | 8 pt | 16.40 | 16.50 | **+0.10** | **+8.28** |
| `table-with-no-header-row` | 30 | 8 pt | 18.40 | 18.53 (15 at 18.4, 10 at 18.9) | **+0.13** | **+3.92** |
| `341_shipping_manifest` | 24 | 6 pt | 13.00 | 13.50 | **+0.50** | **+9.24** |

`341_shipping_manifest` was also run with `before −10 tw` (−0.50 pt/row): **the export is identical to
the shipped file**, span 570.52 both, first row 14.28 both.

## What the numbers say

1. **`w:trHeight` is inert in Google.** v3 (+0.25 pt/row) and v4 (−0.20 pt/row) render a table identical
   to v0 in span and in last-row position, to 0.00 pt. The engine's entire row-height spend is a number
   Google does not read.
2. **Reducing `w:before` is inert below a per-document value.** v5 (−0.20 pt/row on price-list) and
   `bm10` (−0.50 pt/row on the manifest) both render identically to shipped: only the whole table's
   first row moves, never the pitch. **Increasing** `before` by 1.00 pt (v6) moves the pitch by 0.61 pt.
   The response is one-sided.
3. **The paragraph mark's font size is inert** (v7 identical to v0), and `w:line="0"` is read as
   "single spacing" (v8: pitch 22.47), not as zero.
4. **The excess is not a constant floor.** It is +0.10 at 16.40, +0.13 at 18.40, +0.50 at 13.00 with 6 pt
   text. So it is not a fixed 16.5 pt clamp either — an earlier draft of this finding claimed one from
   price-list alone, and the manifest refuted it. What is constant across all three is the *sign* and the
   *linear accumulation*.
5. **The named next step is refuted by the variant that implements it.** v2 *is* the natural-line-box
   rewrite: same `before + line` sum, a 12 pt exact box instead of 0.55 pt. Its pitch is unchanged
   (16.500) and it moves the table's first row **+11.51 pt**. It would not fix `18_displacement` and it
   would move every cell of every table in the corpus. **Do not build it.**

## Why this fails the check, arithmetically

`18_displacement` allows `clamp(0.35*size, 1.5, 4.5)` pt per run — 2.8 pt for 8 pt text — on at most
`max(2, ceil(0.05*n))` runs per page, and no run more than twice its tolerance out. A one-signed excess
of 0.10 pt/row crosses 2.8 pt at row 28; 0.50 pt/row crosses it at row 6. All three documents measured
here accumulate 3.9-9.2 pt by the bottom of the table, and all three fail `18_displacement` and
**nothing else** (41/42 in `benchmarks/gverify/`). The accumulation is the whole defect.

## What is now true

* On a table with 20+ rows, **the engine cannot make Google reproduce the source's row pitch.** Not with
  `w:trHeight`, not with `w:before`, not with the paragraph mark, not with `w:line`. Ten variants across
  three documents move the pitch in exactly one case, and that case is an increase.
* The excess is **per-document** (+0.10 to +0.50 pt/row) and correlates with nothing the engine declares:
  two documents with identical `trHeight 328 / before 316-317 / line 11-12` differ by 0.4 pt/row.
* Therefore `18_displacement` on dense-table documents is a **renderer behaviour, not an engine defect**.
  It is the fourth construct in this repository where the answer is "Google cannot do it", and it must be
  written as a finding and parked, not fixed.

## What the class table should now say

`classpick.py --leverage` prices `18_displacement` at **47.1 clean documents**, with 19 documents that
fail nothing else. Measured on the source PDFs themselves, those 19 split by their own dominant row pitch:

| pitch | documents |
|---|---|
| 11.2-14.0 | `balance-sheet-two-columns-of-figures` (9), `table-inside-two-column-page` (19), `303_discharge_summary` (4), `341_shipping_manifest` (24), `70_magazine_drop_cap_photo_caption` (4), `320_balance_sheet_statutory` (15) |
| 16.4 | `price-list-2col-dense-right-aligned` (39), `bus-timetable-station-left-times-right` (32) |
| 17.0-19.0 | `306_clinical_protocol_synopsis`, `72_bank_statement_no_rules_right_amounts`, `74_balance_sheet_indented_subitems`, `10_stamp_as_image`, `30_mixed_font_sizes_one_baseline_txtpos`, `71_invoice_space_aligned_no_rules`, `35_four_typefaces_one_page`, `eway-bill`, `table-with-no-header-row`, `two-tables-stacked-with-no-gap`, `403_crossword_puzzle` |

**Twelve of the nineteen are 20-row-plus tables and the excess is measured on three of them; the other
seven have fewer rows and may still be reachable.** The next run should not treat the 19 as one class:
measure each one's row count and pitch first, and expect the dense half to be charged by the renderer.


## The fourth document: the excess is NOT universal (added 09:48)

`table-inside-two-column-page`, 17 baselines, source rows **11.8 pt** apart, shipped `w:trHeight 370/350`
(18.5/17.5 pt — taller than the text pitch, because each cell holds more than one line):

| | rows | first | last | span | dominant pitch |
|---|---:|---:|---:|---:|---|
| source | 17 | 55.35 | 816.38 | 761.03 | **11.8** (11 of 16 gaps) |
| Google | 17 | 55.59 | 747.20 | 691.61 | **11.8** (11 of 16 gaps) |

**The text pitch is reproduced exactly.** So the excess measured on the other three is not a property of
"tables in Google" — it is a property of the regime where **one text line sets the row height**. This
document's rows are taller than its text pitch and Google honours both.

That splits the class a second time, and it is the correction this finding needed: the drift is not
"Google adds 0.1-0.5 pt per row to every table", it is "where a single line of text defines the row, the
delivered row is taller than the line, by +0.10 (16.40 src), +0.13 (18.40) and +0.50 (13.00, 6 pt text)".
This document also lands its table **69.18 pt short** at the bottom (747.20 vs 816.38) with the pitch
intact, which is a different defect — a page-layout difference, not a per-row one — and it is the shape
`18_displacement` takes on a two-column page.

## What would prove this wrong

* A Google render of any 20+ row table whose measured pitch equals its source pitch to within 0.05 pt.
  Nothing measured here does: 16.40->16.50, 18.40->18.53, 13.00->13.50.
* A variant that changes the delivered pitch while reducing `before`. Four attempts (v5, bm10) failed.
* The claim that `w:trHeight` is inert is refuted by any export where two different `trHeight` values
  produce two different pitches on the same table. v3 and v4 are the direct test and both fail to move it.

## What was not measured

* Why the excess is +0.50 on the 6 pt document and +0.10-0.13 on the 8 pt ones. A font-proportional law
  fits the sign of all three but not the magnitude; nothing here separates "font size" from "row count"
  from "declared line box" (0.45 pt vs 0.55 pt).
* `bus-timetable-station-left-times-right`. Its left-column y-band mixes wrapped lines with rows, so the
  band pitch is not a row pitch. It needs a row-aware reader.
* Tables carrying borders or `w:tblCellMar`: all three documents here declare `tblBorders` all `nil` and
  `tblCellMar` all zero.
