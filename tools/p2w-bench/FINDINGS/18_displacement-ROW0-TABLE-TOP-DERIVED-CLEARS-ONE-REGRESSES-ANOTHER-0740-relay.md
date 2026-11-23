# 18_displacement — row 0 of a table is placed from a pitch-derived edge, not from the table's own top. The construct is real and derived; the fix is not landable, and here is the document that says so.

**23 Nov 2026 · relay slot 06:19 → 07:45 IST · engine reverted, `regress.py --check` PASS on the tree as it stands**

## Why this run went here

`classpick.py` named `18_displacement` as the class holding an open lead, and
`classpick.py --leverage` prices it at **34.2 clean documents**. The previous run
(`18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md`) had already
shown that the seven LibreOffice one-check documents are seven mechanisms — but it left
**two** of them un-diagnosed: `71_invoice_space_aligned_no_rules` (+9.52 whole table) and
`table-inside-two-column-page` (−9.06 whole table), both "one check from clean", both
whole-block placements with the internal pitch exact.

This run went after the mechanism behind the whole-block placements, on the reasoning that
a table whose rows are right and whose top is wrong is a placement bug, not a row bug.

## What was measured, and what it falsified

### The first hypothesis was wrong and the instrument said so before any build

The obvious reading of `PdfToWord.java:9502`

    t.rowTopPt = rowEdge[0] - 0.8f * lastPitch;

is that the anchor and row 0's own edge disagree by `0.8 * (firstPitch - lastPitch)`, and
that this would show up as a whole-table shift whose sign flips per document — exactly the
+9.52 / −9.06 pair. **It does not.** An env-gated print of the row model (reverted) on the
two candidates:

| document | rows | edge0 | firstPitch | lastPitch | rowTopPt | shift if firstPitch |
|:--|--:|--:|--:|--:|--:|--:|
| `71_invoice_space_aligned_no_rules` table 1 | 10 | 176.0 | 18.0 | 18.0 | 161.6 | **0.0** |
| `71_invoice_space_aligned_no_rules` table 2 | 4 | 372.0 | 16.0 | 16.0 | 359.2 | **0.0** |
| `table-inside-two-column-page` | — | — | — | — | — | **no unruled row-table at all** |

Both candidates are inert under that hypothesis, and the second document has no whitespace
table in it: its table is ruled. **The ±9 pt pair is not this construct.** The instrument
that explains it is the spacer, not the row model: on `71` the gap before the table is
`extraAbs = -1.50`, so `spacerTw = 0` and the table simply continues the flow — the flow's
cursor is 9.52 pt below where the page drew the table's top. That is D-26, still unfixed,
and it is a flow-position problem, not a table-arithmetic one.

### The construct that IS real: row 0 is placed from an edge the box never had

`DocxWriter.java:6403-6409` places every row from `rowEdge[r]`, subtracting `LINE_BASE *`
that row's own pitch for a whitespace table. Rows 1+ are placed from their own absolute
edge and land right. **Row 0's top is not `rowEdge[0] - 0.8 * firstPitch`: row 0's top is
the table's top, which the spacer put at `t.rowTopPt`.** When the two disagree the whole
first row inherits the difference.

The disagreement is computable and was measured (env-gated print, reverted):

| document | edge0 | firstPitch | lastPitch | rowTopPt | edge0 − 0.8·firstPitch | **delta** |
|:--|--:|--:|--:|--:|--:|--:|
| `balance-sheet-two-columns-of-figures` t1 | 115.354 | 16.0 | 11.6 | 106.074 | 102.554 | **+3.52** |
| `balance-sheet-two-columns-of-figures` t2 | 178.154 | 11.6 | 11.6 | 168.874 | 168.874 | 0.00 |
| `newsletter-3col-header-footer` | 693.905 | 14.0 | 10.0 | 685.905 | 682.705 | **+3.20** |
| `360_restaurant_menu` t1 | 120.0 | 22.0 | 20.0 | 104.0 | 102.4 | **+1.60** |
| `360_restaurant_menu` t2 | 420.0 | 22.0 | 20.0 | 404.0 | 402.4 | **+1.60** |
| `71_invoice_space_aligned_no_rules` (both) | — | — | — | — | — | 0.00 |
| `363_warranty_card` | 124.0 | 10.0 | 10.0 | 116.0 | 116.0 | 0.00 |
| `330_cad_drawing_sheet`, `64_newspaper…` | — | — | — | — | — | no unruled table |

`balance-sheet`'s measured first-row error is **+3.69 pt** and the derived delta is
**+3.52 pt** — the same number the 06:30 run found empirically as "74 twips" (−3.70 pt),
now **derived from the source rather than tuned**. Everything else on that page was
already within 0.40.

## The change, and the measurement that killed it

The change tried: in `DocxWriter`'s `exactRows` branch, use the table's own top for row 0 —

    if (r == 0 && !Float.isNaN(t.rowTopPt)) edgePt = t.rowTopPt;

Two variants were built and measured; a third guard was added and it did not help.

| measurement | baseline | with the change |
|:--|--:|--:|
| `balance-sheet` runs out of 94 (`dy.py`, LibreOffice) | **6** | **0** — span 4.18 → 0.89 |
| `balance-sheet` first row dy | +3.69 | +0.40 |
| `balance-sheet` share@5 | 0.57 | 0.57 (unchanged — the 3.5 pt is under the 5 px pixel bar) |
| `newsletter-3col-header-footer` runs out of 129 | 8 | **4** |
| `71_invoice_space_aligned_no_rules` | 29/72 out | unchanged (delta 0.0) |
| `table-inside-two-column-page` | 44/64 out | unchanged (ruled table, delta n/a) |
| **`360_restaurant_menu` share@5** | **34.43** | **35.66** |

`balance-sheet` would have gone 41/42 → **42/42 in the measurable renderer** — a clean
document, and the first one this construct has ever produced.

`360_restaurant_menu` is the reason it cannot land. **`regress.py --check` refused the
commit** on `360_restaurant_menu 34.43 -> 35.66 share@5`. The number reproduces: 35.66 on
a fresh measure of the same `.docx`, 34.43 on the same document rebuilt from the reverted
engine. It is not renderer noise.

### Why the two documents disagree, and why that is the finding

For `360`, `edge0 − 0.8·firstPitch = 102.4` and `rowTopPt = 104.0`: the pitch-derived edge
is the **right** answer and the table's own top is 1.6 pt low. For `balance-sheet`,
`edge0 − 0.8·firstPitch = 102.55` and `rowTopPt = 106.07`: the table's own top is the
**right** answer and the pitch-derived edge is 3.5 pt high.

**The sign of the correct answer differs between the two documents.** So no constant rule
at row 0 can be right for both, and the thing that decides it is not in the row model at
all — it is whether the box actually landed where the spacer's arithmetic says it did.
`balance-sheet`'s rows 1+ are correct while the box top is 3.5 pt from the derived edge,
which is only possible if the box top is *not* `rowTopPt` there; `360`'s rows 1+ are
correct and its box top *is* consistent with `rowTopPt`. Guarding the change on
`spacerTw > 0` does not separate them — `360` spends a spacer too.

**This is the same D-26 defect the whole-block candidates sit on.** Row 0 is where the
disagreement becomes visible, not where it is caused. A run that fixes row 0 for one
document breaks another, which is exactly what a symptom-level fix does.

## What a run should try next, and what would overturn this

The measurement that separates `360` from `balance-sheet` is the **rendered** position of
the table's top edge versus `t.rowTopPt` and versus `flowTopPt + spacerTw / 20`. If those
agree on `360` and disagree on `balance-sheet`, then the spacer is not placing the box where
its own arithmetic says, and the fix belongs in the spacer's split (`spendable`, the
`w:line` under-read, `squeeze`) — not in the row model.

**What would overturn this finding:** a rule that places row 0 from the *rendered* box top
rather than from either page coordinate. Nothing in the writer knows that number today; the
spacer computes a distance and never checks where it landed. That is the missing term.

## Cost of the negative

A full corpus pass was run to test this: **212 of 212 documents measured** with the changed
engine (`benchmarks/p2w.py --force`, `P2W_ENGINE_SRC=/scratch/work/CS`), census
`content-loss 16 · displacement 32 · mixed 11 · clean 153`. The pass is what found
`360_restaurant_menu`; a screen on the two target documents would have shipped the
regression. The table was then restored to the committed one, because it describes an
engine that was reverted.

**Nothing was committed to `app/`. `regress.py --check` PASSes on the tree as it stands.**
