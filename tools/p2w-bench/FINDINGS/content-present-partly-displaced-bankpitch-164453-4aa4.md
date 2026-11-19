# bank-statement-horizontal-rules-only — the +0.34 pt/row is not a table row height: no table is built, and every row the writer splits into two paragraphs leaks one 9-twip hairline

Agent A, subagent finding. Run 19 Nov 2026, 16:31–16:44 UTC.
Engine: `https://github.com/kavopdf/app` at **origin/main `3abfa85`** ("run start 21:59: claim,
handoff, archive"). Clone left clean; the only file added is this one. All engine measurements
were taken from a throwaway instrumented copy of the same tree at `/scratch/work/inst`; the
clone's `app/src/main/java` was never touched.

Document: `bank-statement-horizontal-rules-only`, class
`content-present-partly-displaced`, worst page 1, text_recall 100.00 %.

## 0. What this adds to the sibling finding, and the one thing it corrects

`content-present-partly-displaced-mergedheader-130426-4bd9.md` established the table pipeline
(`findTables` → `intersectionsToCells` → `tableFromCells` → `DocxWriter`) on a document that
*has* a table. It does not apply here, and the reason is new:

1. **This document never reaches a table at all.** Both table passes return nothing — the ruled
   pass because the page draws **zero vertical rules** (`tableFromCells` needs `ncol >= 2`,
   `PdfToWord.java:7805`), and the row pass because of a **numeric gate nobody has looked at**:
   `rowGapOk` (`PdfToWord.java:9701-9723`) caps a table's row gap at `max(size*2.4, 16)`
   = **16.0 pt**, and this page's rows are **18.400 pt** apart. Measured, engine-side:
   `rowGapOk=false gap=18.399963 size=6.5999994` on every consecutive pair.
2. **So the pitch is decided by `DocxWriter.flowRow`, not by `w:trHeight`** — and the drift is
   one hairline line-box per *two-paragraph* row, i.e. **exactly 9 twips = 0.4500 pt** per split
   row, 12 split rows of 16 data rows → mean pitch **18.7375 pt** (measured) against the page's
   **18.4000 pt**.
3. **Correction to the sibling's "accumulating without bound".** On this page the miss is
   **bounded**: it reaches +5.847 pt at row 17-09-2026 and then drops back to +0.047 pt, because
   the writer stops flowing and emits the following rows as absolutely anchored text boxes
   (`<wp:anchor><wp:positionV>` at `5566186` EMU). The same page therefore contains both a
   drifting writer and a non-drifting one — a controlled comparison inside one document.

The +5.77 pt the brief quotes is reproduced here as **+5.847 pt** at y=431.801 (the last table
row), on the current head.

## 1. The answer in one sentence

**A table with only horizontal rules has no column lattice, so the ruled pass cannot build it
(`ncol < 2`); the row pass, which exists precisely for such tables, rejects it because its row
pitch (18.400 pt) exceeds `rowGapOk`'s 16 pt ceiling — so the page's rows are written as flowed
paragraphs, and `DocxWriter.flowRow`'s gap expression `extra = pitch - (1-LINE_BASE)*lastLinePt -
LINE_BASE*linePt` (DocxWriter.java:3347) deducts **one** hairline line-box for a row that emits
**two**, leaving 9 twips (0.450 pt) of advance that the model never sees again.**

## 2. (a) The code that decides the vertical pitch, and its file:line

There are three candidate codes and the document's fate is settled by which one is reached.

| # | file:line | what it decides | reached on this document? |
|:-|:--|:--|:--|
| 1 | `PdfToWord.java:7805` `if (ncol < 2 \|\| nrow < 1) return null;` in `tableFromCells` (called from `findTables`, `PdfToWord.java:8694`) | whether the **ruled** pass makes a table at all | **No.** The page has 0 vertical rules, so `edgesToIntersections` yields nothing and `findTables` returns before `tableFromCells`. Emitted: `0 <w:tbl>`. |
| 2 | **`PdfToWord.java:9722`** `return gap <= Math.max(size * 2.4f, 16f);` in **`rowGapOk`** (`PdfToWord.java:9701`), used by the run test in **`rowTables`** (`PdfToWord.java:9158`, the loop at `9228-9231`) | whether the **row** pass — the pass built for tables with no drawn lines — may treat consecutive rows as one table | **No.** 18.400 > 16.0, so no run reaches `j - i >= 3` and `rowTables` returns an empty list. This is the line that decides that this document gets no table. |
| 3 | **`DocxWriter.java:3347`** `float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;` in **`flowRow`** (`DocxWriter.java:3298`), with `pitch` at **`DocxWriter.java:3317`** and the hairline box at **`DocxWriter.java:3316`** → `hairlinePt` (`DocxWriter.java:3821-3833`) | **the vertical pitch of every row of this document** — the code that actually places the rows | **Yes, 17 rows.** This is the answer to the brief's (a). |

For completeness, the code that *would* set the pitch if the table had been built is
`DocxWriter.java:2104` (`<w:trHeight w:val="rowTw" w:hRule="exact"/>`, `rowTw` from the tallest
cell at `2088-2089`). It was reached in the experiment in §7 and produced `trHeight 368`
= **18.400 pt exactly**, with a rendered pitch of 18.400 on every row.

### The precise condition

> **A row is written as more than one `w:p` (one per column band) while `flowRow` charges the
> row a single line box. `extra` at DocxWriter.java:3347 subtracts `(1-LINE_BASE)*lastLinePt +
> LINE_BASE*linePt` — the height of *one* hairline box — but the row emits two paragraphs, so the
> row's real advance is `pitch + hairline`. Because the next row's `before` is solved from
> `ctx.lastBaseline` (the **page's** baseline, DocxWriter.java:3317) and never from `ctx.flowY`
> (where the flow really is), the hairline already spent is never reclaimed and appears as a
> permanent extra advance.**

The two paragraphs come from the column-band split (`p.column`): the row's left fields
(Date / Value date / Narration / Ref) are one `Para` with `column=0` and the amount fields are a
second `Para` with `column=1`; `flowRow` sees `pitch > 0` for the first and `pitch == 0` for the
second, so the second is written `w:before="0"` and is charged nothing but its own line box.

## 3. (b) The arithmetic that produces 18.74 instead of 18.40

Every number below is a value printed by the engine or read out of the emitted XML.

```
hairlinePt(size) = min(0.069 * size, 0.6485)     DocxWriter.java:3821-3833
                 = 0.069 * 6.6 = 0.4554 pt  =  9.11 twips  -> w:line="9"  (0.4500 pt)

one-paragraph row:
    extra = 18.400 - (1-0.8)*0.4554 - 0.8*0.4554
          = 18.400 - 0.4554 = 17.9446 pt   -> 17.9446*20 = 358.89 -> w:before="359"
    row charge = 359 + 9 = 368 twips = 18.400 pt                       <- correct

two-paragraph row (the amount fields are the second Para):
    first  Para: w:before="359" w:line="9"      (identical - the model is unchanged)
    second Para: w:before="0"   w:line="9"      -> +9 twips = 0.4500 pt, never reclaimed
    row charge = 368 + 9 = 377 twips = 18.850 pt                       <- +0.45 too tall

16 data rows, 12 of them two-paragraph (engine trace, §5):
    (4 * 368 + 12 * 377) / 16 = 5996 / 16 = 374.75 twips = 18.7375 pt
    measured rendered mean pitch over the same 16 rows        = 18.7375 pt
    excess = 18.7375 - 18.4000 = 0.3375 pt/row  ("+0.34 pt per row")
    total  = 12 * 9 twips = 108 twips = 5.400 pt
```

The 0.0054 pt difference between the solved 17.9446 and the written 359 twips is a **constant**,
not a ramp: it appears identically on all 17 rows.

## 4. The page (`pymupdf`, page 1, 595.28 x 841.89 pt)

| quantity | value |
|---|---|
| drawing primitives | 39 stroked horizontal lines, **0 vertical**, **0 rectangles** (`re`), 0 fills |
| distinct rule y | 35, from 72.354 to 802.205 |
| rule stroke widths | 0.4 pt (body), 0.9 pt (header / table end / summary), 1.0 pt (the masthead rule) |
| rule x extent | 45.35 → 549.92 on every rule (504.57 pt wide) |
| body rule intervals | 28 intervals, **min = max = 18.4000 pt** (no jitter) |
| text baselines, date column x=48.4 | 29 baselines, 113.154 → 628.354, **pitch exactly 18.4000**, size 6.6 pt |
| fields per row | 6, all on one baseline: 48.35, 91.60, 134.85, ~351 (ref), amount, balance |

The page's own pitch is therefore exact to four decimals, and the 0.34 pt is entirely ours.

## 5. What the engine emits (measured, not reasoned)

**`document.xml` of the converted .docx** (`ConvertOne`, one document per JVM):

| quantity | value |
|---|---|
| `<w:tbl>` / `<w:tr>` / `<w:tc>` / `w:trHeight` | **0 / 0 / 0 / 0** |
| top-level `<w:p>` in `w:body` | 158 |
| `w:before="359" w:line="9"` | **17** (the 17 rows: 1 header block row + 16 data rows) |
| `w:before="0" w:line="9"` | **13** (the second paragraph of 13 split rows) |
| `w:before="387" w:line="9"` | 1 (the table's header row, pitch 19.8) |
| `w:before="0" w:line="1"` | 123 (absolutely anchored text boxes, `<wp:anchor>`) |

**The engine's own numbers** (one `System.err.println` in `flowRow`, instrumented copy, no other
change). Columns: row baseline, `pitch`, `ctx.lastBaseline`, `ctx.flowY`, written `before`,
written `line`, field count, column band:

```
FR y=113.1544 pitch=19.8000 lastBase=113.1544 flowY=93.3500  beforeTw=387 lineTw=9 ncols=4 col=0 txt=Date
FR y=113.1544 pitch=0.0000  lastBase=113.1544 flowY=113.1600 beforeTw=0   lineTw=9 ncols=3 col=1 txt=Withdrawal
FR y=131.5544 pitch=18.4000 lastBase=131.5544 flowY=113.6100 beforeTw=359 lineTw=9 ncols=4 col=0 txt=01-09-2026
FR y=131.5544 pitch=0.0000  lastBase=131.5544 flowY=132.0100 beforeTw=0   lineTw=9 ncols=2 col=1 txt=6,08,523.96
FR y=149.9543 pitch=18.4000 lastBase=149.9543 flowY=132.4600 beforeTw=359 lineTw=9 ncols=6 col=0 txt=02-09-2026
FR y=168.3544 pitch=18.4000 lastBase=168.3544 flowY=150.8600 beforeTw=359 lineTw=9 ncols=4 col=0 txt=03-09-2026
FR y=168.3544 pitch=0.0000  lastBase=168.3544 flowY=169.2600 beforeTw=0   lineTw=9 ncols=2 col=1 txt=1,19,571.31
...
FR y=425.9544 pitch=18.4000 lastBase=425.9544 flowY=413.4097 beforeTw=359 lineTw=9 ncols=4 col=0 txt=17-09-2026
```

Three facts are visible in that trace and nowhere else:

* `beforeTw` is **359 on all 17 rows** — the model never shrinks the gap, so it never pays back
  the hairline.
* `flowY` — the position the writer believes the flow is at — walks away from the page's
  baseline by **0.4554 pt per split row** (113.61 → 132.46 → 150.86 → 169.26 … 413.41). The model
  **knows** it is drifting; `extra` at 3347 just never reads `flowY`.
* The rows with `ncols=6 col=0` (02-09, 05-09, 07-09, 09-09) are the four that arrive as **one**
  paragraph and cost no hairline. They are exactly the rows whose only amount sits in the deposit
  column at x=449.59; the twelve split rows carry an amount at x=391.92 (withdrawal). Measured
  from the page's spans.

**The rendered result** (LibreOffice, `soffice --headless --convert-to pdf`), date column:

```
source   131.554 149.954 168.354 186.754 205.154 ... 425.954
ours     132.001 150.901 169.301 188.101 207.001 ... 431.801
dy         0.447   0.947   0.947   1.347   1.847 ...   5.847
increments (ours)  18.8 18.9 18.4 18.8 18.9 18.4 18.8 18.4 18.9 18.4 18.8 18.9 18.8 18.9 18.8 18.9
mean pitch ours (132.001 -> 431.801)/16 = 18.7375    source = 18.4000
```

`dy` rises monotonically to **+5.847 pt** at row 17-09-2026 and then **returns to +0.047 pt**:
the writer emits the rows after the table block as anchored text boxes, not as flowed paragraphs.

**The defect metric** (`benchmarks/p2w.py`, `measure_doc`, current head):

```
share1 26.88   share5 6.89   share10 0.93   median 1.44  p90 3.84  max 6.24
signature "displacement"   text_recall 100.0   worst_page 1
```

(The brief's "share@5px 26.88, max_pt 6.89" maps to this run's `share1 = 26.88`,
`share5 = 6.89`, `max_pt = 6.24`; the numbers are the same, the labels are one column apart.)

## 6. Why no table: the two passes, measured

Instrumented `PdfToWord.processPage` (scratch copy), printed at each stage:

```
DBG ruled=0 rowPass=0
DBG afterRowMerge=0
DBG afterNestDrop=0
```

and the row pass's own gate, printed inside `rowTables` for the first rows of the page:

```
GATE i=4 j=5 size>=2=true alignedStart=true rowGapOk=false gap=18.399963 size=6.5999994
GATE i=5 j=6 size>=2=true alignedStart=true rowGapOk=false gap=18.399963 size=6.5999994
GATE i=6 j=7 size>=2=true alignedStart=true rowGapOk=false gap=18.400024 size=6.5999994
RT   i=4 j=5 rows=38 meanCellLen=8.142858 shortCells=true
RT   i=5 j=6 rows=38 meanCellLen=14.0     shortCells=true
```

So the row pass has **38 rows** and cuts them into cells correctly (mean cell length ≈ 12.5 chars,
`shortCells` true, `alignedStart` true); the only thing that fails is
`gap <= max(6.6*2.4, 16) = 16.0` against a gap of 18.400. The run never reaches three rows, so
`if (j - i >= 3 && shortCells(...))` at `PdfToWord.java:9231` is never satisfied and no `Table`
is produced. The page therefore falls through to the paragraph writers, and
`DocxWriter.flowRow` owns the pitch.

## 7. The experiment that separates "no table" from "wrong row height"

Scratch copy only, **not committed**: one constant changed in `rowGapOk` (`16f` → `24f`,
`PdfToWord.java:9722`), nothing else.

| | origin/main | ceiling 24 pt |
|:-|:--|:--|
| `<w:tbl>` | 0 | **1** (29 rows) |
| `w:trHeight` | – | **368 twips (`atLeast`) = 18.400 pt** |
| rendered row pitch | 18.8 / 18.9 / 18.4 mixed, mean 18.7375 | **18.400 on every one of 26 intervals** |
| dy vs source | 0.047 → **5.847** | **0.016 constant** |
| share1 / share5 / max_pt | 26.88 / 6.89 / 6.24 | **10.80 / 0.14 / 3.84** |
| signature | displacement | **clean** |
| text_recall | 100.0 | 100.0 |

Same PDF, same engine, one numeric gate: the pitch becomes exact and the document goes from
`displacement` to `clean`. That is what makes the missing table, and not a row-height formula,
the thing to fix.

## 8. (c) What other corpus documents the same mechanism predicts

The mechanism is *"a row written as two or more flowed paragraphs at a pitch the writer charges
as one"*, and it needs three things at once: no table (so `flowRow` runs), a **row pitch above
`rowGapOk`'s ceiling** (`max(2.4*size, 16)`) or no vertical rules, and a **column gutter wide
enough to split the row into two `Para`s**. The `*-horizontal-rules-only` family is the obvious
set — three documents, all measured:

| document | split rows (`pitch==0` calls) | predicted excess | measured dy vs source |
|:--|:--|:--|:--|
| `bank-statement-horizontal-rules-only` | **13** (12 data + 1 header) | 12 x 0.4500 = 5.400 pt over the data rows | **+5.847** at the worst row (0.047 base + 5.800) |
| `gst-invoice-horizontal-rules-only` | **7** | 7 x 0.4968 = 3.478 pt (7.2 pt type → `lineTw=10` = 0.500 pt → 3.500) | **+3.547** step, and it does not decay |
| `boq-horizontal-rules-only` | **0** | 0 pt | **+0.016 constant**, no ramp — and it scores 0.13 / `clean` |

That is the discriminating test the mechanism predicts, and it passes on all three: the ramp
scales with the **number of two-paragraph rows** and with the **type size** (0.069 em), and is
absent exactly where there are no split rows. `boq` is the control: same family, same 18.4 pt
pitch, same absence of vertical rules, no split rows, no drift.

More generally the mechanism predicts: any flowed (non-table) page whose rows exceed the
16 pt / 2.4-em row-gap ceiling **and** carry a right-hand amount or figure block in its own column
band — bank statements, GST invoices, fee receipts, salary slips, ledger and trial-balance
exports, BOQ summaries with a totals column, ITR schedules. It does **not** predict drift on pages
whose rows are one `Para` (that is the `boq` case), nor on pages the writer anchors absolutely
(the rows after 17-09 on this very page sit at +0.047).

## 9. (d) What I ruled out, with numbers

1. **`w:trHeight` / table row height / the `max(trHeight, content)` ramp.** Ruled out by
   construction: the .docx has **0 `<w:tbl>`, 0 `<w:tr>`, 0 `w:trHeight`**. No expression in the
   table writer is reachable for this document. (And where a table *was* built in §7, the row
   height was 368 twips = 18.400 pt — correct.)
2. **The ruled table pass, `intersectionsToCells` / `tableFromCells`.** Ruled out: the page draws
   **0 vertical rules and 0 rectangles**, so there is no intersection to start a cell from;
   `tableFromCells` additionally rejects `ncol < 2` (`PdfToWord.java:7805`). Instrumented
   `findTables` returns 0 tables.
3. **`recutColumnBands`.** Unreachable — it only re-cuts tables that already exist
   (`PdfToWord.java:8685`), and none exist.
4. **Rule width / stroke thickness as the accumulating term.** Ruled out: the page's rules are
   0.4, 0.9 and 1.0 pt, and the drift is **identical** on rows whose rule is 0.4 pt (body) and
   0.9 pt (the header and table-end rules). The quantum is 9 twips = **0.450 pt**, which is
   `0.069 em` of the **6.6 pt type**, not any rule width. Changing the rule width would move
   nothing; changing the type size would move the drift linearly (§8, gst-invoice at 7.2 pt →
   0.500 pt per split row).
5. **Twip rounding of `w:before`.** 359 twips = 17.950 pt against a solved 17.9446 pt: a
   **0.0054 pt constant**, present on all 17 rows. It cannot accumulate and is 60x smaller than
   the 0.3375 pt/row measured.
6. **`LINE_BASE = 0.8`.** Contributes `(1-0.8) * 0.4554 = 0.091 pt` per line, constant; visible
   as the +0.047 pt that even the header and the anchored rows carry. Not the ramp.
7. **`fitPage` squeeze / page budget.** The engine writes `beforeTw=359 lineTw=9` on **every**
   row — nothing is squeezed, nothing is clamped, and there is only one page.
8. **Source pitch jitter.** Ruled out: 28 body rule intervals and 28 text-baseline intervals are
   **all exactly 18.4000** (min = max). The 0.34 pt is entirely ours.
9. **The row-gap ceiling as the *cause of the drift*.** Ruled out as a cause, kept as the cause of
   the *missing table*: §7 shows that raising it removes the drift, but the drift itself is the
   hairline leak — a table built at 16 pt rows with split paragraphs would drift by the same
   0.45 pt per split row. The two are separate faults that compound here.
10. **Anchoring / `ZERO_GAP_ANCHOR` masking the effect.** Partly ruled out: the anchor path is
    *clean* when it fires (the 12 rows after the table block sit at +0.047), but it does not fire
    for the table rows themselves, because each row's gap (18.4 pt) is a normal leading and its
    `extra` stays positive. So the anchor rule cannot rescue these rows.

## 10. (e) What would prove this answer wrong

* If the .docx contained a `<w:tbl>` and `w:trHeight` values for this document, the answer would
  be in the table writer, not in `flowRow`. It contains neither (0 / 0).
* If the mean pitch over the 16 data rows were **not** 18.7375, or the total excess were not
  **12 x 0.4500 = 5.400 pt**, the hairline-per-split-row arithmetic would be wrong. Both were
  measured directly from the render, to four decimals.
* If the row pass had **not** been blocked by `rowGapOk` — i.e. if the instrumented gate printed
  `rowGapOk=true` at gap 18.4 — then the 16 pt ceiling would not be the reason this document has
  no table, and the finding would have to explain the absence some other way. It printed `false`.
* If raising that one constant had **not** produced a table with an exact 18.400 pt pitch and a
  `clean` signature, the claim that the table path is the correct one for this page would be
  unsupported. It did: 368 twips, 18.400 on every interval, share5 6.89 → 0.14.
* If `beforeTw` had **varied** across the 17 rows (i.e. the model had started paying the hairline
  back), the "never reclaimed" mechanism would be wrong. It is 359 on all 17.
* If a split row had produced **no** extra advance in the render (an 18.400 increment), the
  second paragraph would not be the leak. The increments are 18.8 / 18.9 exactly on the split
  rows and 18.4 on the four unsplit ones.
* If the drift had kept growing past row 17-09 rather than resetting to +0.047, my "bounded by the
  next anchored box" correction would be wrong — it reset.

## 11. Provenance and commands

* Page geometry: `pymupdf` on `corpus/bank-statement-horizontal-rules-only.pdf` (from the
  `corpus-v1` release, asset `p2w-all-groups.zip`, entry `C/bank-statement-horizontal-rules-only.pdf`).
* Engine output: `java -cp tools/engine-verify/out:tools/engine-verify/libs/{aar/classes,bcprov,bcpkix,bcutil}.jar ConvertOne <pdf> <outdir>`, one document per JVM, engine built with
  `bash tools/p2w-bench/build-engine.sh`.
* Engine values: instrumented copy at `/scratch/work/inst` — `System.err.println` in
  `DocxWriter.flowRow` (row y, pitch, lastBaseline, lastLinePt, flowY, beforeTw, lineTw, size,
  field count, column band), in `PdfToWord.processPage` (table counts per stage) and in
  `PdfToWord.rowTables` (the three gates per candidate row pair). No engine behaviour changed in
  that copy except the single `16f` → `24f` in §7.
* Render: `soffice --headless --convert-to pdf` (LibreOffice 7.4.7.2) on the converted .docx;
  baselines read back with `pymupdf`.
* Metric: `benchmarks/p2w.py`'s `measure_doc(pdf, docx)` imported directly; `scipy` present, so
  the instrument ran on `edt`, not the dilation ladder.
* The clone's `app/src/main/java` is untouched; `git status` shows only this file (plus the
  `corpus/` directory and the two files `tools/install-gate.sh` rewrites, neither of which is
  committed).
