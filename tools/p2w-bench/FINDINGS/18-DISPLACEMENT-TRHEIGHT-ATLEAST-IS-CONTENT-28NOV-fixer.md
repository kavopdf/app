# 18_displacement: in Google, `hRule="atLeast"` lays the row at CONTENT height, and `exact` is not the number you wrote

**28 Nov 2026, fixer slot 08:24 IST. Measured in Google, on the real renderer, five Drive round-trips.
No engine change. This file supersedes the reading of `18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md`
for documents whose cells carry a sub-glyph exact line box.**

## What was measured, and how

`35_four_typefaces_one_page`, the document the 05:54 run proved its patch on. Its seven table rows are
written identically:

    <w:trHeight w:val="380" w:hRule="atLeast"/>     380 tw = 19.00 pt, the page's own row pitch
    <w:spacing w:before="1150" w:line="13" w:lineRule="exact"/>   (first cell of a row)

Three builds of the same `.docx`, differing in one attribute, each uploaded to the KavoPDF-Verify folder,
converted to a Google Doc and exported as PDF:

| build | `w:trHeight` | rows |
|:--|:--|:--|
| A (shipped) | `380 atLeast` | 7 |
| B | `380 exact` | 7 |
| C | `377 exact` | 7 |

Row baselines read from each exported PDF with PyMuPDF (`line.bbox[1]`), against the source PDF:

| row | source | A `380 atLeast` | B `380 exact` | C `377 exact` |
|:--|--:|--:|--:|--:|
| header | 139.18 | 137.22 (**−1.96**) | 140.92 (**+1.74**) | 140.92 (**+1.74**) |
| BCO-401 | 158.18 | 155.97 (−2.21) | 160.06 (+1.88) | 160.06 (+1.88) |
| BCO-402 | 177.18 | 174.72 (−2.46) | 179.19 (+2.01) | 179.19 (+2.01) |
| BCO-403 | 196.18 | 193.47 (−2.71) | 198.33 (+2.15) | 198.33 (+2.15) |
| BCO-404 | 215.18 | 212.22 (−2.96) | 217.46 (+2.28) | 217.46 (+2.28) |
| BCO-405 | 234.18 | 230.97 (−3.21) | 236.60 (+2.42) | 236.60 (+2.42) |
| BCO-406 | 253.18 | 250.47 (−3.71) | 256.49 (+3.31) | 256.49 (+3.31) |
| **row pitch** | **19.00** | **18.75** | **19.14** | **19.14** |

## What is now true

1. **`atLeast` is not a floor in Google.** The engine asks for at least 19.00 pt and Google lays 18.75 —
   *less* than the floor it was given. What Google lays is the row's content height, so the value in
   `w:trHeight` is not read at all under this rule. Every row of this table is 0.25 pt short, which is
   the ramp: −1.96 on the first row, −3.71 on the seventh, one-signed, ≈ −0.25/row.
2. **`exact` is honoured, but not as the number written.** 19.00 pt exact lays 19.14; 18.85 pt exact
   lays 19.14 as well. So the exact height is quantised — two values 0.15 pt apart land on the same
   row — and the quantised step is not the requested pitch either. `exact` therefore converts a −0.25/row
   undershoot into a +0.13/row overshoot; it does not fix the document, it flips the sign of the error.
3. **This contradicts the 22 Nov mobile-bill result that `hRule="exact"` is inert**, and the difference
   is the cell, not the row: mobile-bill's rows carry ordinary line spacing, this document's cells carry
   `w:line="11..13"` (0.55–0.65 pt) `exact` under a 12 pt face with `w:before` ≈ 1150 tw. A row whose
   content height is governed by a sub-glyph exact line box is exactly the case where the two rules
   diverge. Neither finding is wrong; the construct is document-dependent, and any patch that assumes
   one answer for both will be refuted by the other document.

## What this means for the class, and what would prove it wrong

The pitch is not settable through `w:trHeight` on this document: `atLeast` gives content height, `exact`
gives a quantised height that is 0.14 pt over, and the two probe values 377/380 both landed on the same
19.14. **So the remaining lever is the cell's own line box, not the row's height** — give the cell a
natural `w:line` (so the content height Google computes is the page's 19.00) and move the difference into
`w:before`, which is the 05:54 run's candidate; that candidate is only worth building if the content
height is what Google uses, and this measurement says it is.

## The falsifier was run: five builds, and the row height is QUANTISED, not computed

Two more builds of the same document, both changing only the cells' `w:spacing` (35 cell paragraphs):

| build | cell `w:spacing` | content asked | row pitch laid by Google | first row dy vs source |
|:--|:--|--:|--:|--:|
| A | `before=368 line=12 exact` (shipped) | 19.00 pt | **18.75** | −1.96 |
| D | `before=173 line=207 atLeast` (natural box) | 19.00 pt | **20.90** | +1.04 |
| E | `before=373 line=12 exact` | 19.25 pt | **19.39** | +1.99 |
| B | `380 exact` rows | — | 19.14 | +1.74 |

Reading the four rows together: Google's line height is not the `w:line` it is given (0.60 pt asked, 0.35 pt
contributed at `before=368`; 0.74 pt at `before=373`; ~12.25 pt for an `atLeast` natural box under a 9 pt
face), and the row height is **quantised**: **+5 twips (0.25 pt) of `before` moved the row by 0.64 pt**,
and 0.15 pt of requested exact height landed on the same row. There is no value of `before` and `line` you
can *compute* to land on 19.00 pt, because the map from what is written to what Google lays is a step
function of unknown step, measured here at four points.

**So the class cannot be fixed by writing better numbers into the cell.** It needs either (a) a sweep of
`before` in ~2-twip steps to find the interval that lays 19.00 — a per-document measurement, which the
"one rule true of every document" test forbids as a fix — or (b) a construct Google lays exactly, which
four probes have not found. That is the honest state of `18_displacement`'s row half, and it is why the
class has survived every attempt: the instrument (our `.docx`) cannot express the target exactly, and the
renderer quantises what it is given.

What would prove this wrong: a `before` value in the 368–373 twip band whose Google export lays 19.00 on
all seven rows. The band is 5 twips wide and the map moves 0.64 pt across it, so a value that lands
exactly on 19.00 is possible only if the quantisation has a step at 19.00 — worth one probe, not a patch.

Evidence kept: the three exported PDFs were compared line by line; the probe `.docx` files are
reproducible from the recipe above (one attribute changed, nothing else). The two probe Google Docs were
deleted after the export, per VERIFY-GOOGLE's rule; the verify folder holds nothing from this run.
