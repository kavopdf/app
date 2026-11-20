# t13_amount_columns: the misaligned amounts ARE the table path, and the guard throws the right edge away

20 Nov 2026, by a read of `TxtWriter.java` plus a real build and a real run. The source PDF is
not in the repository (only 5 PDFs travel with the repo), so it was fetched from the corpus
release that `benchmarks/p2w.py:corpus()` uses:

    gh release download corpus-v1 --repo kavopdf/app -p 'p2w-all-groups.zip' ...
    -> x/C/gst-invoice-3line-items.pdf

Engine built with `tools/p2w-bench/build-engine.sh` (41-58 s per build, JDK 17 fetched from
Adoptium because the image has no javac). Converted with `ConvertOne` / `ConvertAll` from
`tools/engine-verify`. Everything below was measured, not inferred.

---

## The answer in one paragraph

The amounts are emitted by the **table path**, `TxtWriter.appendTable()` (line 355), and
`cellRight()` is **not** NaN for them (it is `552.5905` on every row). The right-align branch
at lines 373-377 does fire, computes `startCol`, and then line 375 —

    if (startCol > col) col = startCol;      // TxtWriter.java:375

— **discards it**, because `startCol` is 1-2 columns *left* of the cell's own left edge. The
cell therefore falls back to its left edge, and the amount's end column becomes
`baseCol + text.length()`, which is 134 for a 9-character amount and 133 for an 8-character
one. That is exactly the 133/134/134 the check reports. Candidate **(d)** is the mechanism;
(a), (b) and (c) are each falsified below.

---

## The code path, with line numbers (HEAD = 4282bea)

| line | code |
|---|---|
| 355 | `private static void appendTable(StringBuilder sb, PdfToWord.Table t, float charW)` — the table path |
| 363 | `int baseCol = column(cellLeft(t, ri, ci), charW);` |
| 364 | `float right = cellRight(t, ri, ci);` |
| 373 | `if (isNumeric(c) && !Float.isNaN(right)) {` |
| 374 | `int startCol = column(right, charW) - c.length();` |
| 375 | `if (startCol > col) col = startCol;`  ← **the line that loses the alignment** |
| 377-378 | pad to `col`, append the cell, newline |
| 408-414 | `cellRight()` — returns `Float.NaN` only when `cellR` is absent/short/null |
| 418-432 | `isNumeric()` — true for digits with `, . - + ( ) % / : space ₹ $` |
| 434-440 | `column(float x, float charW)` — `Math.round(x / charW)` |
| 48 | `CELL_RATIO = 0.6f` → `charW = 0.6 × 7 pt = 4.2` for this document |
| 342 | the paragraph path's only positioning: `int pad = column(lx, charW);` — left edge, never a right edge |

## The exact arithmetic that produces 133 vs 134

Measured by instrumenting lines 373-378 (a temporary `System.err` print, reverted; the diff is
kept out of the commit) and converting `gst-invoice-3line-items.pdf`:

    DBG  RIGHT  charW=4.2000003  colR=132  startCol=123  baseCol=125  len=9   32,745.00
    DBG  RIGHT  charW=4.2000003  colR=132  startCol=124  baseCol=125  len=8   7,522.50
    DBG  RIGHT  charW=4.2000003  colR=132  startCol=123  baseCol=125  len=9   13,806.00
    DBG  RIGHT  charW=4.2000003  colR=132  startCol=121  baseCol=123  len=11  1,68,150.00
    DBG  TABLE  r=1 c=9  baseCol=125  right=552.5905  col=125  num=true  32,745.00
    DBG  TABLE  r=2 c=9  baseCol=125  right=552.5905  col=125  num=true  7,522.50
    DBG  TABLE  r=3 c=9  baseCol=125  right=552.5905  col=125  num=true  13,806.00

* `column(cellRight) = round(552.5905 / 4.2) = 132`.
* `column(cellLeft) = 125` for rows 1-3, `123` for the two total rows.
* So the cell is **132 − 125 = 7 columns wide in the writer's ruler**, while its own content is
  **8 or 9 characters**. The right-align target `132 − len` is therefore 123 or 124 — to the
  *left* of the cell's left edge.
* `startCol > col` is false in every case, `col` stays `125`, and the amount is emitted
  left-aligned. End = `125 + len` = **134** for the two 9-character amounts and **133** for the
  8-character one. One line per cell is preserved; only the end column diverges.

**Why the cell is "too narrow":** `c.length()` counts characters while `charW` is one value for
the whole document (`documentCharWidth`, line 452, = 0.6 × the weighted-median font size). In
the source the amount column is drawn in a 7 pt face whose digits and commas are narrower than
0.6 em, so 9 characters occupy ~8.3 ruler columns, not 9. The ruler systematically
over-estimates a numeric token's width by about one column, which is precisely the one column
that puts `startCol` below `baseCol`.

## Candidates (a)-(c), each falsified by the run

* **(a) the paragraph path** — false. The `DBG TABLE` lines above are the emitter for all
  three amounts; `appendPara` (line 342) never sees them. The .txt shape (one cell per line,
  increasing indents) is the table path's own shape, not a paragraph with nine lines.
* **(b) `cellR` is NaN** — false. `right = 552.5905` for every amount cell, and `num=true`.
  `cellRight()` returned a number, so the `isNumeric && !isNaN(right)` guard at 373 passed.
* **(c) `cellR` differs per row** — false for the amounts: `cellR` is `552.5905` on rows 1-5.
  `cellLeft` *does* differ (125 on rows 1-3, 123 on the total rows) and that is why the two
  source "columns" t13 sees are 133 and 134 apart, but it is not what splits 133 from 134
  inside one column.
* **(d) the clamp** — **true**, line 375.

---

## Before / after, on `gst-invoice-3line-items`

`verify_txt.py <pdf> <txt>`, before:

    10/12 applicable, 9 passed, 2 abstained  FAIL
        t13_amount_columns         source=6          txt=5

after (the fix below):

    10/12 applicable, 10 passed, 2 abstained  PASS

The three lines of the failing column, `.txt` before (end column 134 / 133 / 134):

    len=134  '...125 spaces...32,745.00'
    len=133  '...125 spaces...7,522.50'
    len=134  '...125 spaces...13,806.00'

and after (all three end at 134):

    len=134  '...125 spaces...32,745.00'
    len=134  '...126 spaces...7,522.50'      <- one extra space, nothing else moved
    len=134  '...125 spaces...13,806.00'

Line count is **142 before and 142 after** — unchanged, so `t04_structure` cannot drift.

---

## The smallest change that converges

### Variant 1 — one token (fixes this document, and is NOT the one to ship)

    if (startCol > col) col = startCol;      // line 375
    ->
    col = startCol;                          // or: if (startCol >= 0) col = startCol;

Measured over a 60-document sample (below): **9 improved, 2 worse, 49 same**; failing-t13
documents 13 -> 6. It fixes `gst-invoice-3line-items` and breaks
`04_stamp_180deg_upside_down` (t13 1/1 -> 0/1) and
`600_reviewed_invoice_with_annotations` (2/2 -> 1/2), because in those documents `cellR`
genuinely is ragged — the total row's cell is wider — so a per-cell right edge splits a column
that used to line up by luck at the left edge. That is candidate (c) in the wild, and it is
why the guard existed.

### Variant 2 — one end column per table column (measured 0 worse)

Right-align to the **widest numeric cell in the same table column** instead of to each cell's
own right edge. Inserted in `appendTable()` (before the emit loop) and applied at the emit
point; it never moves text left, so it cannot make anything worse by construction:

    // before the emit loop
    int[] endCol = new int[ncol];
    for each row ri, each cell ci:
        int baseCol = column(cellLeft(t, ri, ci), charW);
        for each non-empty numeric part c of the cell:
            endCol[ci] = Math.max(endCol[ci], baseCol + c.length());

    // at the emit point, replacing lines 373-376
    if (isNumeric(c) && ci < ncol && endCol[ci] > 0) {
        int startCol = endCol[ci] - c.length();
        if (startCol > col) col = startCol;   // startCol >= baseCol always
    }

On `gst-invoice-3line-items` this puts `7,522.50` one space further right; all five rows of
that column end at 134; t13 goes 5/6 -> 6/6, verdict FAIL -> PASS, line count 142 -> 142.

**Measurement, 60 documents** (the table/invoice/amount-named subset of the corpus, all under
3 MB; `java ConvertAll` in one JVM, `verify_txt.compare()` per document, before and after):

| variant | improved | worse | same | t13-failing docs | line counts changed |
|---|---|---|---|---|---|
| 1 (drop the guard) | 9 | 2 | 49 | 13 -> 6 | none |
| 2 (end column per table column) | 6 | 0 | 54 | 13 -> 7 | none |

Variant 2 is the one worth a full-corpus run. Variant 1 must not be shipped: it is the smaller
diff and the worse patch, and it is the same trap as `PATCH-t13-table-row-per-line.patch` —
obvious reasoning, 0 measured benefit.

## What this does NOT claim

* **Not measured on all 211 documents.** `ConvertAll` over the whole corpus was not attempted
  inside a single 300 s call (`416_many_tiny_pages` alone is ~4m40s, and a per-document JVM is
  7.7 s). The sample is 60 documents selected by name pattern
  (`invoice|table|amount|marksheet|balance|grid|statement|bill|receipt|quote|form|price|...`)
  and capped at 3 MB, so it is biased toward the documents this defect lives in. The
  improvement figures above describe that sample and nothing wider.
* **No patch is committed.** Only this file. The instrumented build and the two fix variants
  were local, reverted before the commit, and the tree was rebuilt from HEAD afterwards so the
  commit gate (`tools/install-gate.sh`, installed in this clone) sees the engine it measured.
* **`.docx` untouched.** The change is inside `TxtWriter` only, which the `.docx` path does not
  read.
* `verify_txt.py` was not modified. It was run, and read, and its `t13` code is what the
  numbers above are judged by.
