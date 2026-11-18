# The ~1.44 pt displacement is a ladder, not a constant: one uncharged table BOTTOM RULE per table

Run: 18 Nov 2026. Documents: `mobile-bill`, `salary-slip-factory-wages`, `electricity-bill`
(all single page, all with three tables, all with 0.45 pt table rules).

**Answer in one sentence.** On these three pages the vertical error is not a constant and it is
not per line: it is a **four-rung ladder of +0.50 pt steps, one step per table**, and the missing
term is the table's own **bottom rule width**, which the renderer draws *outside* the last row's
box and which `DocxWriter.table()` never charges to the flow that follows the table
(`DocxWriter.java:6547-6554`, with the discarded rule term at `DocxWriter.java:6020` and the
flow charge at `DocxWriter.java:6508-6512`). The engine already knows about this residual and
names it as 0.20 pt and "left unmodelled" in its own comment at `DocxWriter.java:6539-6541`; the
measured value on these pages is the whole rule, **0.50 pt**, not 0.20.

## 1. What the shift actually is

Matching every source line to the line the render drew, by its text, and comparing **baselines**
(pymupdf `span.origin[1]`) on the source PDF and on the LibreOffice render of the `.docx`:

`mobile-bill`, all 112 lines, dy = our baseline − the page's baseline, in page order:

| source y | dy | what starts here |
|---|---|---|
| 52.52 – 62.52 | **−0.02** | the two header flow lines (`VISTARA TELECOM`, the address line) |
| 85.12 – 182.52 | **+0.48** | table 1 (info grid, 5 rows) and its trailing caption |
| 198.92 – 349.72 | **+0.98** | table 2 (usage, 7 rows) and its trailing caption |
| 366.32 – 596.12 | **+1.48** | table 3 (bill details, 10 rows) and the three lines under it |
| 816.38 | **+1.52** | the footer line |

Per-line histogram: 4 lines at 0.00, 21 at +0.48, 35 at +0.98, 35 at +1.48, 2 at +1.52.
`salary-slip-factory-wages` (102 lines) and `electricity-bill` (125 lines) give the identical
four rungs with identical values. Nothing is 1.44: **1.44 is the ink-weighted median of a
mixture whose top rung is +1.48 and whose largest rung is +1.48** (35 of 97 distinct lines on
`mobile-bill`; 42 % of source ink on `salary-slip` sits on the +1.48 rung, 88 % of it on
rungs 1–3).

The steps are exactly 0.500 pt = **10 twips** = 1.04 px at the bench's 150 dpi. So every rung
except the header is more than 1 px out, which is why `share@1px` reads 47–51 % while
`share@5px` (2.4 pt) reads 16–18 %: the ladder alone does not exceed 5 px.

## 2. The mechanism, isolated by surgery on the .docx

I did not touch the engine. I rewrote only the table properties of the converted `.docx`,
re-rendered, and re-measured the same baselines. `w:sz="4"` is 4 eighths of a point = 0.5 pt,
and that is what `szOf(0.45f)` produces for the page's 0.45 pt rules (`DocxWriter.java:5437`).

Rung 0 is the two header flow lines; rung *k* is the cell text of table *k* plus the caption
that follows it (captions are flow lines and follow the table, so they sit on the rung *below*
their own table's cells — the asymmetry is the leak itself).

| variant (mobile-bill) | rung 0 | rung 1 | rung 2 | rung 3 | footer |
|---|---|---|---|---|---|
| as converted | −0.02 | +0.48 | +0.98 | +1.48 | +1.52 |
| **all six sides of every table → `w:val="nil"`** | **−0.02** | **−0.02** | **−0.02** | **−0.02** | **+0.02** |
| only the **bottom** rule of every table → nil | −0.02 | +0.48 | +0.48 | +0.48 | +0.02 |
| bottom rule of table 1 → nil | −0.02 | +0.48 | +0.48 | +0.98 | +1.02 |
| bottom rule of table 2 → nil | −0.02 | +0.48 | +0.98 | +0.98 | +1.02 |
| bottom rule of table 3 → nil | −0.02 | +0.48 | +0.98 | +1.48 | +1.02 |
| **every bottom rule at `w:sz="16"` (2.0 pt)** | −0.02 | +1.98 | +2.98 | +4.48 | +6.02 |
| only the **top** rule of table 1 → nil | −0.02 | row 1 → 0.00, rows 2+ +0.48 | +0.98 | +1.48 | +1.52 |

Read the columns:

* **Kill every rule and the whole ladder vanishes** — every line lands within 0.02 pt. The
  displacement is made entirely of table-rule width; there is no other vertical term on these
  pages.
* **Kill only the bottom rules and the accumulation stops**: every rung collapses to +0.48 — the
  table's own cell text keeps a single, non-cumulative +0.5 (its own top rule) and the flow lines
  *between* tables go to −0.02, so the page no longer drifts as it descends.
* **One table's bottom rule, one rung**: taking table 1's bottom rule away lifts exactly the
  rungs below it by 0.50; table 2's lifts rungs 2–3; table 3's lifts only the last.
* **Widen the bottom rules and the step is the new width**: 2.0 pt rules give steps of exactly
  **2.00 pt** per table (+1.98, +2.98, +4.48, +6.02), i.e. the step is `w:sz / 8` pt, not a
  constant. The 0.5 is not magic — it is `round(0.45 * 8) / 8`.
* **The top rule is charged, and it does not accumulate**: removing it moves only that table's
  *first row's* text, by 0.50, and nothing below. So the engine's per-row half-rule arithmetic
  does model the top rule; it is the *bottom* rule that escapes.

## 3. Where the code loses it

`DocxWriter.table(StringBuilder sb, PdfToWord.Table t, Ctx ctx)`, `DocxWriter.java:5592`.

1. **The rule is written but never charged when the pitch binds** — `DocxWriter.java:6020`:

   ```java
   writtenRowsTw += Math.max(0, Math.max(pitchTwHere,
           Math.max(rowTwHere, rowLineTw) + ruleTwHere));
   ```

   The intent is right ("the content plus the rule - not the content alone"). But on these three
   documents `pitchTwHere` binds: the rows are written `w:trHeight` 360/380 tw (18.0/19.0 pt,
   averaging the page's 18.4 pt pitch) and the cell content is `w:before` ≈ 195–207 tw plus
   `w:line` 10 tw ≈ 10.3 pt, far below the floor. So `max(pitch, content + rule) = pitch` and
   `ruleTwHere` is thrown away on every row. The table is charged 5 × 18.4 = 92.0 pt for
   `mobile-bill`'s 5-row grid; the renderer occupies 92.0 + the bottom rule.

2. **The anchor the next paragraph is spaced from is the last row's box bottom, without the
   rule** — `DocxWriter.java:6547-6554`:

   ```java
   float rowBottomPt = t.bottom;
   if (!Float.isNaN(lastRowTopPagePt) && lastRowHeightTw > 0) {
       rowBottomPt = lastRowTopPagePt + lastRowHeightTw / (float) TWIPS_PER_PT;
   } else { ... }
   ctx.lastBaseline = rowBottomPt;
   ```

   `ctx.lastBaseline` is what the following paragraph's `w:before` is computed against
   (`ctx.flowY` at 6564, and the same number charged to `ctx.flowTw` at 6508–6512). The
   renderer, meanwhile, draws the table's bottom rule *below* that box, so every paragraph after
   a table starts `w:sz/8` pt lower than the engine believes — and because each table then hands
   the next band a position that is 0.5 pt low, the error is **cumulative down the page**, which
   is the ladder.

3. **The engine says so itself** — `DocxWriter.java:6539-6541`:

   > "The borders the writer emits add a further 0.20 pt (the bottom rule less the top rule),
   > which is left unmodelled and is the residual quoted in the patch note."

   That sentence is the bug, with the wrong magnitude: on a page whose six sides are all the
   page's own 0.45 pt stroke, the unmodelled term is the **full bottom rule, 0.50 pt per table**,
   not "bottom less top" and not 0.20.

The one-term fix (not applied — this run writes findings only): add
`(hRuleBottom ? sideSz[2] / 8f : 0f)` to `rowBottomPt` and `(hRuleBottom ? sideSz[2] * 20 / 8 : 0)`
to the `ctx.flowTw` charge at 6508, i.e. charge the bottom rule the renderer draws. `sideSz[2]`
and `hRuleBottom` are both already in scope at 5903–5911.

## 4. It predicts documents I did not tune on

The prediction is: **a page with N ruled tables is displaced by k·(szBottom/8) pt in the band
after the k-th table**, independent of row count, font, size and pitch. Converted one-per-JVM
with the same engine:

| document | `w:tbl` | bottom `w:sz` | predicted step | measured rungs |
|---|---|---|---|---|
| `mobile-bill` | 3 | 4 | 0.50 / table | 0.00, +0.48, +0.98, +1.48 |
| `salary-slip-factory-wages` | 3 | 4 | 0.50 / table | 0.00, +0.48, +0.98, +1.48 |
| `electricity-bill` | 3 | 4 | 0.50 / table | 0.00, +0.48, +0.98, +1.48 |
| `marksheet-university-consolidated` | 3 | 4 | 0.50 / table | +0.02, +0.52, +1.02, +1.52 |
| `two-tables-stacked-with-no-gap` | **1** (the two tables merge into one `w:tbl`) | 4 | 0.50, **once** | −0.02, then +0.48 for the rest of the page — no second rung |
| `405_sheet_music_lyrics` | **0** | — | no ladder | flat +0.10 everywhere, no rung |

`two-tables-stacked-with-no-gap` is the sharpest control: it has two tables on the page but only
one `w:tbl` element, and it shows **one** rung of 0.5 and no more — the ladder counts emitted
tables, not drawn ones. (Its `median_pt` 6.24 in RANKING is a different, larger defect; the
0.5 rung rides on top of it.) `405_sheet_music_lyrics` has no tables and no ladder at all.

## 5. What I ruled out

* **A constant per-line shift.** No: 4 lines are at 0.00, and the rungs change only at table
  boundaries — 0.48 is flat across all 21 lines of table 1, 0.98 flat across all 35 of table 2.
  A per-line term would ramp within a band; this does not move at all inside a band.
* **The hairline line box (`w:line = 1.38·size`, `lineRule="exact"`, `LINE_BASE = 0.8`).** The
  flow lines *above* the first table are placed to 0.02 pt, and the ladder's rungs are 0.5 pt
  whatever the type size (13 pt heading and 6.4 pt footer share the same rung). The
  hairline/`LINE_BASE` model is doing its job here.
* **Row pitch / `w:trHeight`.** The rows inside every table land at the page's own pitch (18.4 pt
  on all three; the 360/380 alternation averages it), so no error accrues *within* a table. The
  table's total height is right; only the rule below it is missing.
* **`w:tblCellMar`.** It is 0 on all four sides in all three files — not the 0.5.
* **The top rule.** Charged: removing it moves only the table's first row and nothing below.
* **A per-row rule charge** (the other way the same omission could show). On
  `itr-computation-with-slab-table` there *is* a −0.5 step per row, but rewriting its rules to
  nil leaves the per-row step bit-identical (−0.5 × 16 rows either way, only a −1.0 global
  move), so that document's ramp is a row-height defect, **not** this one. The two must not be
  conflated.
* **Text boxes / table-cell widths** (`carry-ceiling-span-1900.md`). Not involved: this is a
  vertical gap between the table's box and the flow below it, and it survives every change to
  widths. The width finding is not re-derived here and is not contradicted.
* **The DeviceGray/alpha finding.** Untouched; these pages' ink is present, just displaced
  (text_recall 100.0, chars_missing 0).

## 6. A second, smaller, horizontal member of the same family

Not asked for, and not part of the 1.44, but it is the same 10-twip constant and it is worth one
line: table text is also **+0.58 pt to the right** (flow text is +0.08), because `w:tblInd` is
written 860 twips = 43.0 pt (`DocxWriter.java:5770-5772`, `tw(x0)`) against the page's table left
edge at 42.52 pt. That is 1.2 px at 150 dpi and it contributes to `share@1px` on every cell.
I did not localise it to a line and am not claiming a mechanism for it.

## 7. What would prove me wrong

* A document with ruled tables whose lines below the k-th table are **not** displaced by
  `k · szBottom/8` — in particular a three-table page with 0.5 pt rules whose median dy is not
  ~1.5, or whose rungs are not 0/0.5/1.0/1.5.
* A page with tables whose `w:tblBorders` bottom is `nil` in the converted `.docx` and which
  still shows a rung per table.
* A `share@1px` that does not fall when the bottom rules are set to `nil` on all three documents
  (I measured the geometry, not the score: with the bottom rules nil the p90 dy goes
  1.481 → 0.481 on all three, which should move `share@1px` sharply; I did not run the bench on
  the mutated files, so the *score* consequence is predicted, not measured).
* Any case where adding `sideSz[2]/8` to `rowBottomPt` makes a document worse — the term is the
  renderer's own geometry, so it should be sign-uniform, but a `w:tblBorders` bottom that the
  page did not draw (`hRuleBottom` false) must stay 0, and a table that is the last thing on the
  page must not be charged for a rule it does not have.
