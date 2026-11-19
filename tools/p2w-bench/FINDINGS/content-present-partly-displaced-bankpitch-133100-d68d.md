# bank-statement-horizontal-rules-only — the 0.34 pt/row ramp is one un-reclaimed hairline box per row, not a row height

Run: 19 Nov 2026, 13:24–13:31 UTC. Engine: repo HEAD (7083db2), tree left clean.
Instrument: `ConvertOne` on the corpus PDF, `pymupdf` for the page geometry, LibreOffice
`soffice --headless --convert-to pdf` once for the render, and a throwaway instrumented copy
of the tree at `/scratch/work/CS-inst` (a `System.err.println` in `DocxWriter.flowRow`; the
clone's `app/src/main/java` was not touched).

## The answer in one sentence

**There is no table and no row height.** `bank-statement-horizontal-rules-only` emits **zero**
`<w:tbl>` elements — with horizontal rules only there is no vertical edge, so no lattice, so
no `Table` — and its 18.4 pt rows are rebuilt as **positioned flow paragraphs**. The pitch is
decided by `DocxWriter.flowRow`'s **incremental** gap expression
`float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;`
(DocxWriter.java:3347), which measures the next row's `w:before` from the **page's** baseline
distance (`pitch = first.y - ctx.lastBaseline`, DocxWriter.java:3317) instead of from where
the flow actually is (`ctx.flowY`). When a row is written as **two** paragraphs — the left
columns and the right amount columns, because the page's gutter between them splits the row
into two `Para`s — the second paragraph is written with `w:before="0"` and a hairline
`w:line`, and the reader advances one whole hairline box (0.069 em = **0.4554 pt** at 6.6 pt)
below the row's baseline. The next row's `before` is still 359 twips, because the model never
looked at `flowY`, so **that box is never reclaimed: +0.4554 pt per split row, always down,
accumulating without bound.**

## 1. Root-cause chain, with file:line

| # | where | what happens |
|---|---|---|
| 1 | `PdfToWord.tableFromCells` — PdfToWord.java:7819 `if (ncol < 2 \|\| nrow < 1) return null;` (called from the ruled pass at PdfToWord.java:7797-7802) | Columns come from the **vertical** rule intersections. This page draws 30 horizontal rules at x 45.4→550.0 and **no vertical rule at all**, so `ncol == 0`, no `Table` is built, and the ruled block is handed back as positioned text. Confirmed: the emitted `document.xml` contains `tbl count 0`. |
| 2 | `DocxWriter.flowRow` — DocxWriter.java:3302 | Each page row arrives as one or more `Para`s. `flowRow` writes one `Para` as one paragraph with a tab stop at each field's x: the row's whole pitch rides in `w:before`. |
| 3 | DocxWriter.java:3317 `float pitch = !ctx.newPage && ctx.lastBaseline >= 0f ? first.y - ctx.lastBaseline : -1f;` | The pitch is the **page's** baseline distance. It is right (18.4), and it is the wrong quantity to place from. |
| 4 | DocxWriter.java:3316 `float linePt = hairlinePt(size);` → DocxWriter.java:3821-3832 `Math.min(HAIRLINE_EM * max(1,size), 0.6485f)` | The line box is a hairline, `w:line = 1.38*size` twips. At 6.6 pt: **9 twips = 0.45 pt**. |
| 5 | **DocxWriter.java:3347** `float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;` | **THE WRONG EXPRESSION.** `18.4 − 0.2×0.4554 − 0.8×0.4554 = 17.9446` → `w:before="359"`. It is a *modelled* advance: it assumes the previous thing in the flow is the previous row's box. |
| 6 | DocxWriter.java:3332 `int beforeTw = 0;` + DocxWriter.java:3346 `} else if (pitch > 0f) {` | For the **second** `Para` of the same row, `pitch == 0` (same `y`), so the branch is not taken at all: `beforeTw` stays 0 and the paragraph is written `w:before="0" w:line="9"`. |
| 7 | DocxWriter.java:3364-3377 (`ctx.zeroGap++`, `zeroGapPt += miss`) | The engine **sees** this miss and only counts it. Nothing corrects the position. |
| 8 | DocxWriter.java:3454 `resync(ctx, placeTopPt, beforeTw, lineTw);` | `ctx.flowY` becomes the *written* position — one hairline below the row's baseline — while `ctx.lastBaseline` stays the page's `y`. The two disagree by exactly one hairline from here on. |
| 9 | DocxWriter.java:3347 again, next row | `before` is recomputed from `lastBaseline` (still 18.4), so it is 359 twips again. The 0.4554 the reader has already consumed is never subtracted. **+0.4554 per split row, forever.** |

`DocxWriter.place()` (DocxWriter.java:3883-3925) is the **absolute** positioner that this file
already uses for ordinary lines, and its own javadoc (DocxWriter.java:3844-3862) describes
exactly this failure mode of the incremental model ("the gap only exists when it is positive …
the error was never seen again by the model, but the reader kept it, and each line added its
own … On 16_right_aligned_amounts 0.3 pt per line became 10.5 pt"). `flowRow` was never
converted to it: it still uses the `extra = pitch - …` form (DocxWriter.java:3347 for rows,
DocxWriter.java:4200 for the single-box twin `flowFromBox`).

## 2. The exact wrong expression, and what it should be

Wrong (DocxWriter.java:3347):

```java
float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;
```

The gap must be solved from the position the reader is really at, not from the page's baseline
pitch — the same form `place()` already uses at DocxWriter.java:3897-3920:

```java
float topPt = ctx.flowY + (1f - LINE_BASE) * ctx.flowBoxPt;   // where this paragraph starts
float d = first.y - topPt;                                   // what is left to spend
float before = d - LINE_BASE * linePt;                       // the gap
if (before < 0f) before = 0f;
```

and the row must then `resync` on the twips actually written (as it already does at
DocxWriter.java:3454). With `flowY` as the input, the second `Para` of a row leaves
`d = −0.4554` (before = 0, as now, which is correct — a flow cannot go backwards), but the
**next** row's `d` becomes `18.4 − 0.4554 = 17.9446`, `before = 17.4892` → **349 twips**, and
the row lands back on the page's own baseline. The miss stays bounded inside the row that
caused it instead of compounding.

This is a diagnosis, not a patch proposal: the defect is that `flowRow` asks the *page* where
the next line goes when only the *flow* knows where the current one ended.

## 3. What I measured

**The page's own geometry** (`pymupdf`, page 1, 595.28 × 841.89):

| quantity | value |
|---|---|
| horizontal rules | y = 103.354, 121.754, 140.154, 158.554 … 636.954, then 654.954, 673.354, 691.754 |
| rule pitch | **exactly 18.400 pt**, 30 intervals, no jitter |
| rule width / x | 504.6 pt, x 45.4 → 550.0; **no vertical rule anywhere on the sheet** |
| rule strokes | 0.4 pt `0.608` grey body rules; 0.9 pt `0.067` black header/table-end rules |
| text baselines | 113.154, 131.554, 149.954 … 628.354 — **pitch 18.400**, size 6.6 pt, one baseline per row (all columns share it) |

**What the engine emitted** (`document.xml` of the converted .docx):

| quantity | value |
|---|---|
| `<w:tbl>` | **0** (158 paragraphs; this document has no table at all) |
| row paragraphs | 17 × `w:before="359" w:line="9" w:lineRule="exact"` |
| the amount paragraphs of those rows | 12 × `w:before="0" w:line="9" w:lineRule="exact"` |
| 359 + 9 | = 368 twips = **18.400 pt** — the emitted row advance is exactly the page's pitch |
| 9 twips | = `1.38 × 6.6` = the hairline = 0.069 em = 0.4554 pt |

So the row height is right. The **row occupies 18.4 + 0.4554 = 18.855** because it is two
paragraphs.

**What the render does** (LibreOffice 7.4.7.2, one page):

| quantity | measured |
|---|---|
| date baselines, ours | 132.001, 150.901, 169.301, 188.101 … 431.801 |
| source date baselines | 131.554, 149.954, 168.354, 186.754 … 425.954 |
| dy, first row → last row | **+0.447 → +5.847** (the prior run's "+5.77 at y=421" reproduced) |
| mean pitch, ours | (431.801 − 132.001) / 16 = **18.7375** |
| predicted from the counts | (4 × 18.400 + 12 × 18.855) / 16 = **18.7375** |
| total excess | 5.400 pt = **12 × 0.450** (the 12 split rows, each one hairline) |

The two numbers agree to four decimals, which is the whole proof: 12 of 16 rows were written as
two paragraphs and each cost one hairline.

**What the engine's own values say** (instrumented `DocxWriter.flowRow`, one line per call —
`y`, `pitch`, `beforeTw`, `lastBaseline`, `flowY`):

```
FLOWROW y=113.15442 pitch=19.800049 beforeTw=387  lastBase=93.35437  flowY=93.35    cols=4 txt=Date
FLOWROW y=113.15442 pitch=0.0        beforeTw=0    lastBase=113.15442 flowY=113.16   cols=3 txt=Withdrawal
FLOWROW y=131.55438 pitch=18.399963  beforeTw=359  lastBase=113.15442 flowY=113.61   cols=4 txt=01-09-2026
FLOWROW y=131.55438 pitch=0.0        beforeTw=0    lastBase=131.55438 flowY=132.01   cols=2 txt=6,08,523.96
FLOWROW y=149.95435 pitch=18.399963  beforeTw=359  lastBase=131.55438 flowY=132.46   cols=6 txt=02-09-2026
FLOWROW y=168.35437 pitch=18.400024  beforeTw=359  lastBase=149.95435 flowY=150.86   cols=4 txt=03-09-2026
FLOWROW y=168.35437 pitch=0.0        beforeTw=0    lastBase=168.35437 flowY=169.26   cols=2 txt=1,19,571.31
```

Read the `flowY` column: it enters each row **0.4554 lower than the row's own `y`** and that
offset grows by 0.4554 for every split row (113.61 → 132.46 → 150.86 → 169.26 …), while
`beforeTw` never leaves **359**. `pitch` is 18.4 on every left half and **0.0** on every right
half. The row that was one `Para` (`02-09-2026`, `cols=6`) costs no extra hairline — which is
why 12 and not 16.

## 4. What I ruled out, and how

* **Table row height (`w:trHeight`), the `max(trHeight, content + rule)` ramp of
  DocxWriter.java:5960-6035, `rowEdge`/`rowTopPt` of PdfToWord.java:7865-7876 and
  9384-9393.** Ruled out by construction: the .docx has **zero** `<w:tbl>`. Every expression
  in that chain is unreachable for this document. (The 404_sudoku_grid "+2 pt a row" mechanism
  documented there is a different defect on a different document and is not this ramp.)
* **Font metrics / `LINE_FACTOR` (1.15 em) / the face's line height.** The row's `w:line` is 9
  twips = 0.45 pt at 6.6 pt type, and 359 + 9 is exactly 368 = the page's 18.4. Nothing in the
  emission is font-sized except the hairline, and the hairline is what is missing from the
  accounting — so the drift *is* font-sized (0.069 em), but it is not the face's line height.
* **Rounding of `w:before` to twips.** 359 twips is 17.95 pt against a solved 17.9446 — 0.0054
  pt, a constant, not accumulating; the rendered first-row dy is +0.447, an order of magnitude
  larger, and it comes from the split, not from the rounding.
* **`LINE_BASE = 0.8` vs the renderer putting the baseline at the foot of an exact line box.**
  That is a real constant offset of `0.2 × hairline = 0.09 pt` per line, and it is visible in
  the first row (+0.047 on the header block, +0.447 after one split) — but it is constant, so it
  cannot produce a ramp; it is not the accumulating term.
* **`fitPage` squeeze / page-budget accounting.** One page, nothing squeezed: `beforeTw` and
  `lineTw` come out of `fitPage` unchanged on every row (359 / 9).
* **`place()` / the absolute positioner.** Not the culprit — `flowRow` does not use it; the
  absolute model is what would fix this.
* **Dropping fill-only rules from the Edge list.** Not touched; SETTLED already measures it as
  worse (27.31 → 46.58), and nothing here depends on it.

## 5. Falsifiable prediction

The charge is **0.069 em per split row**, and only for rows the model splits into more than one
`Para` (a gutter wider than the row-splitting gap, typically a narration column and a
right-hand amount block). So:

1. **`gst-invoice-horizontal-rules-only`** (same generator, same "horizontal rules only"
   family, `content-present-wholly-displaced`) should show the **same down-only ramp at the
   same 0.4554 pt/row**, with the excess equal to `0.4554 × (number of two-paragraph rows)`.
   If its rows are all single `Para`s it will show no ramp at all — that is the discriminating
   measurement, and it distinguishes this cause from anything about rules or pitch.
2. **`boq-horizontal-rules-only`** scores 0.13 and is `clean`; this cause predicts it has
   **zero or one** split row, i.e. excess ≤ 0.46 pt. If it had 12 split rows it could not score
   0.13.
3. **The drift must scale with the row's type size and not with the rule width.** Re-rendering
   the same document with the row type at 10 pt must give **0.69 pt/row** (0.069 em) while the
   rules stay 0.4 pt; a rule-width cause would stay near 0.45.
4. **Any other document whose rows are split into two `Para`s on a flow-paragraph (not table)
   page has the same ramp**, with the same sign, whatever its pitch — so a search of the corpus
   for `flowRow` calls with `pitch == 0.0` should return exactly the documents with this defect,
   and the count of those calls per document should equal `excess_pt / 0.4554`.

## 6. Provenance

* Page geometry and render comparison: `pymupdf` on
  `corpus/bank-statement-horizontal-rules-only.pdf` and on the `soffice` render of the
  converted .docx.
* Engine values: instrumented copy of the tree at `/scratch/work/CS-inst` (one
  `System.err.println` added to `DocxWriter.flowRow`); `app/src/main/java` in the clone is
  unmodified and `git status` is clean apart from this file.
* No corpus measurement was run; no engine change was committed.
