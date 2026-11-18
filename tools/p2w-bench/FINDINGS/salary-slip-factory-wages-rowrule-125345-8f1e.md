# salary-slip-factory-wages / rowrule — the lost header rule, not a misplaced one

Run: 18 Nov 2026, 12:32–12:54 IST. Engine: repo HEAD (main) + the diff in
`salary-slip-factory-wages-rowrule-125345-8f1e.patch`. Instrument: `benchmarks/p2w.py`
`measure_doc()` (scipy present, exact EDT), render by LibreOffice 7.4.7.2 via `conv()`.

## Document and before-score

`salary-slip-factory-wages`, class `content-missing-nothing-in-its-place`, 1 page.

| | before | after |
|---|---|---|
| **share@5** | **18.09** | **0.73** |
| share@1 / @2 / @3 / @10 | 46.93 / 30.77 / 22.59 / 17.49 | 38.54 / 13.83 / 5.54 / 0.11 |
| median_pt | 1.44 | 0.96 |
| p90_pt | 26.40 | 1.92 |
| max_pt | 71.04 | 8.16 |
| signature / problem | content-loss / content-missing-nothing-in-its-place | clean / none |

Reproduced the hand-off numbers exactly before touching anything (18.09 / 1.44 / 26.4 / 71.04).

## The idea, in one sentence

The document's ~18 % of far ink is **not text in the wrong place at all**: the page draws a
0.9 pt black rule under each of its three table header rows, and the engine — whose
`w:tblBorders` carries **one** `insideH` stroke for a whole table — reduced all of a table's
row separators to the dominant 0.45 pt grey one and emitted the black header rule **nowhere**,
so 17.5 % of the page's ink was never written.

## What I measured

**1. Text geometry was already right — so the class name is the wrong lead on this page.**
Matching all 102 source lines to the 102 rendered lines by text and comparing baselines:
`dy` in −0.02 … +1.52 pt (the four-rung 0.50 pt ladder of
`FINDINGS/content-missing-nothing-in-its-place-B-103610-346a.md`, reproduced), `dx` 0.08–0.67 pt,
**0 unmatched lines in either direction**. No line is anywhere near 5 pt out. A page whose every
baseline is within 1.5 pt cannot have 18 % of its ink 26–71 pt from ours unless ink is missing.

**2. The far ink is three rules.** Source ink 22 818 px, our ink 16 940 px (−26 %). Attributing
the `d > 5 px` source pixels by row: 4 000 px sit on **three long horizontal runs**, at
y = 92.6, 204.5 and 372.0 pt, each 42.2 → 507–524 pt wide, in rows where our render has **0** ink
pixels. That is 17.53 % of all source ink and **96.9 % of all the far ink**; the residual 0.56 %
is ordinary glyph-shape difference. Global max distance 71.04 pt = the middle of a missing rule.

**3. The page's own drawings say what those three rules are.**

| y (pt) | width | colour | what it is |
|---|---|---|---|
| 66.52 | 1.0 pt | `0.067` near-black | page title rule — **emitted, matched** |
| 92.92 | 0.9 pt | `0.067` near-black | table 1 header separator — **missing** |
| 204.92 | 0.9 pt | `0.067` near-black | table 2 header separator — **missing** |
| 372.12 | 0.9 pt | `0.067` near-black | table 3 header separator — **missing** |
| 12 × body | 0.45 pt | `0.608` grey | body row rules — emitted as `sz=4 color=9B9B9B` |

Each header rule is drawn **on top of** a 0.45 pt grey body rule at the same y (92.92, 204.92,
372.12 appear twice in `get_drawings()`), which is exactly why the collapse happens: the two
rules are indistinguishable by position and only differ by weight and colour.

**4. The .docx before the change** carried three identical `w:tblBorders`, all six sides
`sz="4" w:color="9B9B9B"`, and no `trBorders`/`tcBorders`: the black rules had no emitter.

## Root cause

`PdfToWord.insideStroke()` (PdfToWord.java:7212) reduces every interior separator of a table to
**one** stroke — "the stroke carrying the most rules" — because OOXML's `w:tblBorders` has room
for only one `insideH`. Its own docstring states the loss: *"A row separator that is 0.4 pt grey
for twelve rows and a single 2 pt black line under the header row report 0.4 pt grey."* On a
ruled financial table that is the header rule, the heaviest ink under the title, and it is
emitted nowhere. `DocxWriter.table()` then draws every row at that one weight.

The class name misled here: `text_recall` counts characters, so a lost **rule** is invisible to
it and the document presents as "text present but displaced". On this page nothing textual is
displaced by more than 1.52 pt.

## The change (kept)

- `PdfToWord.Table#rowStroke` (new): each separator's own stroke, read in `markSideStrokes()`
  with `edgeStroke()`, which already prefers the heavier rule on a tie — so the black header
  rule wins over the grey body rule drawn at the same y.
- `DocxWriter.table()`: where a separator's stroke differs from the emitted `insideH` stroke
  (by ≥1 eighth-point or by colour), the row above gets `<w:tcBorders><w:bottom …/></w:tcBorders>`
  on each cell, in OOXML `tcPr` order (after `gridSpan`, before `noWrap`). Interior edges only;
  rows with the table's own stroke emit nothing, so the byte output of a table without such a
  rule is unchanged.
- Net: 3 `tcBorders` on this document, on the 3 header rows.

## Ratchet: 40 documents measured, 0 worse

All compared against `benchmarks/RANKING.csv` (the current engine's own output).
**Better (19):** mobile-bill 18.48→1.55, electricity-bill 16.24→1.33,
marksheet-university-consolidated 16.78→0.64, two-tables-stacked-with-no-gap 17.20→0.77,
insurance-policy-schedule 13.29→0.53, form16-part-b 12.32→0.77, mutual-fund-statement
12.05→0.21, property-tax-receipt 10.78→0.96, admit-card 10.68→1.89,
gst-invoice-multipage-item-table 10.44→0.40, delivery-challan 10.26→0.84, gst-invoice-3line-items
7.15→0.54, boq-tender-bill-of-quantities 7.10→0.62, table-with-rotated-header 6.42→0.12,
balance-sheet-and-profit-loss 6.20→0.21, purchase-order 5.30→0.90, salary-slip-corporate
5.09→1.28, marksheet-subject-left-marks-right 4.55→0.32, and this document.
**Unchanged (21)**, including the fragile ones: 392_statistical_console_output 1.61,
76_devanagari_table 7.91, 360_restaurant_menu 34.43, 404_sudoku_grid, 303_discharge_summary,
343_air_waybill, 406_passport_mrz_page, 405_sheet_music_lyrics 0.00. **Largest positive delta
0.00.** 17 of the 18 measured class documents moved, so `attempt.py` rules 1 and 3 both fire.

## How a later run falsifies or extends this in one command

```
cd /scratch/work/fix && git apply /scratch/output/salary-slip-factory-wages-rowrule-125345-8f1e.patch \
 && bash tools/p2w-bench/build-engine.sh \
 && python3 tools/p2w-bench/screen.py --class "content-missing-nothing-in-its-place"
```
Falsified if any document's share@5 rises, or if `insurance-policy-schedule` /
`form16-part-b` / `mutual-fund-statement` do not fall. To extend: the 11 class documents not
measured here (incl. `landscape-page-inside-portrait-document` 13.08,
`table-across-page-break-repeated-header` 9.41) are the untested half — the prediction is that
every one of them draws a header rule heavier than its body rules and falls with this change;
`annual-review-2col-uneven-columns` (5.77, unchanged) is the control that does not, and its
defect is elsewhere.

## Ruled out along the way (do not re-pay for these)

- **The 0.50 pt/table bottom-rule ladder of finding B** is real and reproduced
  (dy 0/0.48/0.98/1.48) but is **not** this document's share@5: the whole ladder is 3.2 px, under
  the 5 px tolerance, and it survives this change (median 1.44→0.96 only because more ink now
  matches). Charging it would move share@1, not share@5. Left untouched.
- **A per-line or per-column placement defect.** None exists: 102/102 lines match, dy ≤ 1.52 pt,
  dx ≤ 0.67 pt. Do not look for a flow or column-x cause on this page.
- **Table cell widths / `w:tblInd`** — the +0.58 pt right shift of finding B is present and
  immaterial at this tolerance.
- **The renderer.** LibreOffice draws a per-cell `tcBorders` bottom where the page draws its
  rule: measured, not assumed — the 3 emitted `tcBorders` are what took share@5 from 18.09 to
  0.73, so the rule now lands on the page. (The .docx surgery route — rewrite the borders, keep
  the engine — was *not* run this time; the engine change was measured directly.)
