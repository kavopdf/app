# w:vMerge blast radius — class `content-present-partly-displaced`

Date: 2026-11-19 · Read-and-measure only. No engine change, no build, no conversion.

Class = the 18 OPEN rows of `benchmarks/DEFECT-CLASSES.md` whose `problem` is
`content-present-partly-displaced`:

```
mobile-bill                                   electricity-bill
admit-card                                    very-long-single-column-table
salary-slip-corporate                         75_merged_header_cell_three_columns
374_org_chart                                 payslip-label-left-amount-right
table-of-contents-dot-leaders                 64_newspaper_uneven_columns_ad_boxes
bank-statement-horizontal-rules-only          330_cad_drawing_sheet
65_two_col_full_width_figure_caption          price-list-2col-dense-right-aligned
315_gazette_notification                      price-list-right-aligned-amounts
27_two_column_left_short_txtpos               70_magazine_drop_cap_photo_caption
```

## Q1 — HOW MANY DOCUMENTS: **1 of 18**

`75_merged_header_cell_three_columns` is the only document in the class that contains a
cell a word processor would express as a vertically merged cell. Every other document in
the class has no vertically merged cell at all.

### The measurement, and how it was validated

The corpus was not on the pod (`/scratch/work/p2w/corpus` is built by `benchmarks/p2w.py`
from the `corpus-v1` release). It was downloaded, not measured:

```
gh release download corpus-v1 --repo kavopdf/app -p '<zip>'   # 4 zips
```

213 PDFs landed; all 18 class documents are among them.

Script: `/scratch/work/vmerge_scope.py` (pure pymupdf, no conversion). For every page:

1. every drawn horizontal segment `(y,x0,x1)` and vertical segment `(x,y0,y1)` from
   `page.get_drawings()` — both `l` items and `re` rects;
2. **row edges** = the clustered `y` of the horizontals; **column edges** = the clustered
   `x` of the verticals;
3. a **drawn rectangle** = a box `(xl..xr) x (yl..yr)` with a horizontal rule at `yl` and
   at `yr` covering the full width, a vertical rule at `xl` and `xr` covering the full
   height, and **no rule of either direction crossing its interior** (a crossing rule
   splits it — that is two cells, not one merged cell);
4. **bands covered = 1 + the number of row edges strictly inside `(yl,yr)`.** Those
   interior edges exist because the page's own row grid continues in the neighbouring
   columns. `bands >= 2` ⇒ the page drew one cell where its grid has two rows.
5. the table's outer frame is excluded (no vertical rule outside it covers the same
   y-range, so it is the border, not a cell inside it).

Two mistakes were made and fixed while building it, both worth recording because each
produced a wrong answer:

* **A merged cell has no interior rule, so it never appears as a cell built from two
  *adjacent* row edges.** The first version iterated adjacent edges only and returned
  **0 of 18 and 0 of 213** — a confident, wrong answer. It has to enumerate all edge
  pairs. On `table-with-merged-cells` that changed 0 → 5.
* **Nesting both ways.** A box must have no *vertical* rule crossing its interior either.
  Without that, `admit-card` produced 9 "cells" that were really 9 nested x-combinations
  of the same box, and `330_cad_drawing_sheet` produced 45.

**Positive and negative controls** (same script, same run):

| document | known truth | measured |
|---|---|---|
| `table-with-merged-cells` | has merged cells (by name, class `content-partly-lost-and-displaced`) | **5** — largest `x 42.5–92.4, y 127.3–182.5`, 3 bands |
| `75_merged_header_cell_three_columns` | the PDF's own caption says *"The header cell marked SCHEDULED spans three columns; the depot column and the last two columns are merged vertically across the two header rows."* | **2** drawn + **3** straddled labels |
| `372_timesheet_grid` | plain ruled grid | 0 |
| `340_bill_of_lading` | plain ruled grid | 0 |
| `375_attendance_register` | plain ruled grid (455 lattice cells) | 0 |
| `320_balance_sheet_statutory` | plain ruled grid (79 lattice cells) | 0 |

A detector that finds 455 lattice cells in `375_attendance_register` and zero merges is a
detector that is looking, not one that is silent.

### The table

| document | vertically merged cell? | how many | largest example — drawn rectangle `(x0,y0,x1,y1)` |
|---|---|---|---|
| `75_merged_header_cell_three_columns` | **yes** | 2 drawn rectangles (2 bands each) + 3 header labels centred across the two stacked header rows | **`(56.0, 126.0, 196.0, 160.0)`** — the "Depot" cell, 140.0 × 34.0 pt, 2 row bands |
| `mobile-bill` | no | 0 | — |
| `electricity-bill` | no | 0 | — |
| `admit-card` | no | 0 | — |
| `very-long-single-column-table` | no | 0 (3 pages) | — |
| `salary-slip-corporate` | no | 0 | — |
| `374_org_chart` | no | 0 | — |
| `payslip-label-left-amount-right` | no | 0 | — |
| `table-of-contents-dot-leaders` | no | 0 | — |
| `64_newspaper_uneven_columns_ad_boxes` | no | 0 | — |
| `bank-statement-horizontal-rules-only` | no | 0 | — |
| `330_cad_drawing_sheet` | no | 0 | — |
| `65_two_col_full_width_figure_caption` | no | 0 | — |
| `price-list-2col-dense-right-aligned` | no | 0 | — |
| `315_gazette_notification` | no | 0 | — |
| `price-list-right-aligned-amounts` | no | 0 | — |
| `27_two_column_left_short_txtpos` | no | 0 | — |
| `70_magazine_drop_cap_photo_caption` | no | 0 | — |

The second drawn rectangle in `75` is `(328.0, 143.0, 394.0, 177.0)`, 2 bands. The three
labels centred across the header rule at `y = 143.0` are `Depot` (bbox 61.0,139.3,85.1,148.8),
`Fleet held` (399.0,139.8,436.3,148.7) and `Breakdowns` (461.0,139.8,508.5,148.7) — the
page draws the two-row header and centres the label on the boundary, which is the second
form of vertical merge in the brief.

### The near-misses, named so nobody re-opens them

Four class documents have text whose bbox a row edge passes through. Only one of them is a
merge; the other three are page furniture crossing a rule:

* `75_merged_header_cell_three_columns` — `Depot`, `Fleet held`, `Breakdowns` straddling
  `y=143.0`. **Real**: the header labels of a two-row header band.
* `64_newspaper_uneven_columns_ad_boxes` — 5 straddles, all ordinary body copy
  (`"scheme for Vinayaka Nagar will be taken"` at `y=136.0`) crossing rules that belong to
  the ad boxes above them. Not a merge.
* `65_two_col_full_width_figure_caption` — 6 straddles, all chart axis tick labels
  (`"70"`, `"80"`, `"90"`, `"100"`, `"110"`, `"120"`) crossing the chart's own gridlines.
  Not a merge.
* `330_cad_drawing_sheet` — 2 straddles, title-block labels (`"DRAWING NO."`) with the
  block's rule running through the middle of the glyph box. Not a merge.

**Conclusion for Q1: the blast radius of `w:vMerge` on this class is one document out of
eighteen.** Fifteen of the eighteen are `content-present-partly-displaced` for reasons that
have nothing to do with merged cells — no table at all, or a grid with no rule-drawn
merge in it. If `w:vMerge` is built and measured against this class, the class-movement
bar `moved >= max(2, 25 % of the class)` = **2 documents cannot be met by this change
alone**: the change can move at most `75_merged_header_cell_three_columns`.

---

## Q2 — WHAT THE CODE CHANGE IS

### What the model already carries

`PdfToWord.tableFromCells` (`app/src/main/java/com/kavopdf/app/engine/PdfToWord.java`,
7800-7961) records, per grid slot, the page's own rectangle in grid coordinates:

```java
7891            int[][] sc = new int[nrow][ncol];
7892            int[][] sr = new int[nrow][ncol];
7893            for (float[] cell : group) {
7894                int c0 = edgeIdx(CE, cell[0]), c1 = edgeIdx(CE, cell[2]);
7895                int r0 = edgeIdx(RE, cell[1]), r1 = edgeIdx(RE, cell[3]);
...
7911                for (int r = r0; r < r1; r++) {
7912                    if (sc[r][c0] != 0) continue;   // a second rectangle claiming the same slot
7913                    sc[r][c0] = Math.max(1, c1 - c0);
7914                    sr[r][c0] = Math.max(1, r1 - r0);
7915                }
7916            }
```

and writes both onto the Table at 7946-7950:

```java
7946                rowSpanC.add(sc[r][c]);
7947                rowSpanR.add(sr[r][c]);
...
7949            t.spanC.add(rowSpanC);
7950            t.spanR.add(rowSpanR);
```

**`spanR` is a rectangle size, not a restart marker.** Line 7914 writes `sr[r][c0] = r1 - r0`
for **every** row `r` in `r0 .. r1-1`, so on a 2-band merge the value `2` sits at
`spanR[r0][c]` **and** at `spanR[r0+1][c]`. Any emitter that reads `spanR[r][c] > 1` as
"this slot restarts a merge" will put `<w:vMerge w:val="restart"/>` on the continuation row
too, produce two restarts and no continuation, and Word will close the merge on the second
row. The writer has to *derive* which row is the restart; the model does not store it.

### The exact emission change

`DocxWriter.java` writes one row's cells in a `while (c < cols)` loop that starts at 6197:

```java
6197            int c = 0;
6198            while (c < cols) {
6199                // A slot the page's own rectangle handed to the cell on its left is not a
6200                // cell: writing a w:tc for it would split the merge the page drew.
6201                int mspan = hasSpans(t) ? spanCAt(t, r, c) : 1;
6202                if (mspan == 0) { c++; continue; }
6203                String cell = c < row.size() ? row.get(c) : "";
```

and the cell's properties are opened at 6275, `w:gridSpan` written at 6277, borders at 6279:

```java
6275                inner.append("<w:tc><w:tcPr><w:tcW w:w=\"").append(spanTw)
6276                        .append("\" w:type=\"dxa\"/>");
6277                if (span > 1) inner.append("<w:gridSpan w:val=\"").append(span).append("\"/>");
6278                // tcBorders comes after gridSpan and before noWrap in the OOXML tcPr order.
6279                if (sepSz > 0 && sepColour != null) {
6280                    inner.append("<w:tcBorders><w:bottom w:val=\"single\" w:sz=\"").append(sepSz)
6281                            .append("\" w:color=\"").append(sepColour).append("\"/></w:tcBorders>");
6282                }
```

**The insertion point is between line 6277 and line 6278** — after `w:gridSpan`, before
`w:tcBorders`, which is where the OOXML `tcPr` child order (`tcW, gridSpan, hMerge,
vMerge, tcBorders, shd, noWrap, ...`) puts it. Nothing else in the method moves.

The accessor pair the new code has to sit beside is at 5631-5640:

```java
5631    private static int spanCAt(PdfToWord.Table t, int r, int c) {
5632        if (t == null || t.spanC == null || r < 0 || r >= t.spanC.size()) return 1;
5633        List<Integer> row = t.spanC.get(r);
...
5639    private static boolean hasSpans(PdfToWord.Table t) {
5640        return t != null && t.spanC != null && t.spanC.size() == t.rows.size();
5641    }
```

Given `spanR[r][c] = n > 1` for the cell whose rectangle starts at row `r`, the writer must
emit, in the `tcPr` of grid slot `(r, c)`:

```xml
<w:vMerge w:val="restart"/>
```

and in the `tcPr` of each grid slot `(r+1, c) … (r+n-1, c)`:

```xml
<w:vMerge/>
```

with the cell's content empty and **the same `w:gridSpan` as the restart cell** — which the
existing code already produces, because `sc[r][c0]` is written on every covered row at 7913
and `span` is computed from it at 6239, so `spanCAt(t, r+1, c)` returns the same number as
`spanCAt(t, r, c)`. The row therefore keeps its full tiling; no `w:tc` is added or removed
and line 6202's `mspan == 0` skip is untouched.

The restart/continuation decision has to be derived, e.g.:

```java
int rspan = hasSpansR(t) ? spanRAt(t, r, c) : 1;
boolean cont = false;
for (int k = 1; k < rspan; k++)
    if (spanRAt(t, r - k, c) > k) { cont = true; break; }
if (rspan > 1 && !cont) inner.append("<w:vMerge w:val=\"restart\"/>");
else if (cont)           inner.append("<w:vMerge/>");
```

`hasSpansR` must mirror `hasSpans` exactly (`t.spanR != null && t.spanR.size() ==
t.rows.size()`, else `1`). That guard is not cosmetic — see the risk below.

### What must NOT change

1. **`spanC` must keep being written on every covered row** (7911-7915). The comment at
   7902-7910 records what happened when it was zeroed below the first row:
   *"on 75_merged_header_cell_three_columns: a header cell spanning rows 0-2 and columns 4-5
   zeroed row 1 and row 2 at column 4, so those rows wrote 3 cells across a 6-column grid
   and the whole row lost its right-hand pair."* The vMerge work must not "fix" that by
   moving the ownership of the slot into `spanR`.
2. **The continuation `w:tc` must still be written.** Skipping it (the obvious reading of
   "the cell above owns this slot") is the same failure — the row falls short of the grid
   and `w:tblGrid` no longer matches the row's cells.
3. **The row a glyph lands in must not change.** `PdfToWord.java:7846`:

```java
7846                int ri = R.indexOf(hit[1]);
7847                int ci = C.indexOf(hit[0]);
7848                if (ri >= 0 && ci >= 0) buckets.get(ri).get(ci).add(g);
```

   `hit` is the cell rectangle that contains the glyph centre (7832-7835), and `hit[1]` is
   that rectangle's **top** edge. So every glyph drawn anywhere inside a 2-band rectangle
   is bucketed at `ri = r0`, the rectangle's first row, column `c0`. A vertically merged
   cell's text already lives, in the model, in its top row and nowhere else. **That is why
   the change is additive: the continuation slots are already empty, and nothing has to be
   emptied.**

### The risk, concretely

**Is there a case where emptying the continuation cells would lose text?** For cells the
ruled path emits: **no, and here is the proof rather than the assertion.**

`intersectionsToCells` (7730-7758) emits, for each top-left point, the **nearest** closing
corner — `below` and `right` are built in ascending order from the sorted point list and the
loop `break`s on the first closed rectangle (7744-7756). So no two emitted cells share a
top-left point, and a cell whose top edge is at row `r` cannot extend past the next rule
crossing its own column, because that rule is the nearest connected bottom point. Two
rectangles therefore cannot overlap inside one column, so a slot `(r>r0, c)` can never hold
a *different* rectangle's text while `spanR[r0][c] > 1`. Combined with 7846 (all glyphs of
the rectangle bucket to `r0`), the continuation slots of a genuine merge are empty strings
already — `String cell = c < row.size() ? row.get(c) : ""` at 6203 is `""` there, and
`glyphText(buckets.get(r).get(c))` at 7935 was `""` when the row was built.

**The one real hazard is a table whose rows were re-cut, and it is a hazard of *adding*
`w:vMerge` too eagerly, not of emptying anything.** `recutColumnBands`
(`PdfToWord.java:8379`) builds a fresh `Table u = new Table()` (line 8448) and copies
`recut, ruled, innerH, innerV, header, rtl, top, …` onto it — it does **not** copy `spanC`
or `spanR`, and `t.spanC.add` occurs at exactly one place in the file (7949). That is why
`hasSpans(u)` is false for a re-cut table and `spanCAt` returns `1`: gridSpan is not
emitted for re-cut tables at all. A `spanRAt` without the same guard, or one that reads
`spanR` off a table whose rows no longer correspond to the page's rectangles, would emit
`w:vMerge` on a re-cut table's spanning band (`DocxWriter.java:6139-6145`, `t.recut`) —
where row 0 is a spanning band and row 1 is the whole of the columns — and merge cells that
the page never merged. Guard on `spanR.size() == t.rows.size()`, exactly as 5640 does.

Second-order, worth knowing before measuring: `DocxWriter` reads `spanC` only through
`hasSpans`, so on every document where the grid came from the whitespace pass rather than
the ruled pass, `spanC` and `spanR` are both empty and this change is a no-op by
construction. That is 15 of the 18 class documents, and it is the mechanical reason Q1's
answer is one.

---

## What this does not say

* It does not say `w:vMerge` will move `75_merged_header_cell_three_columns` by any
  particular number. That needs a conversion and a measurement, neither of which was run.
* It does not audit the other 195 corpus documents. The controls in the Q1 table were run
  to validate the detector, not to size a corpus-wide change. A corpus-wide count is the
  obvious next question and is one command away:
  `python3 /scratch/work/vmerge_scope.py /scratch/work/p2w/corpus <name>…`.
* `spanR` at a continuation slot is recorded as the *rectangle's* height, not the
  remaining height. `spanR[1][c]` is `2` on a 2-band merge, so it is not a usable
  "rows still to go" count either. Only the restart row's value means what it looks like.
