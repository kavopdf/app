# 75_merged_header_cell_three_columns - the table is built from cell RECTANGLES, not from the row lattice

Agent B, subagent finding. Engine: `app/src/main/java/com/kavopdf/app/engine/` at origin/main
(engine head at the time of this run). Document: `75_merged_header_cell_three_columns`,
class `content-present-partly-displaced`, share5 27.31.

## The one question

Which code decides (a) how many table rows the header occupies, (b) which sub-row within a
merged/stacked header a cell's text belongs to, and (c) whether a vertically merged source cell
becomes `w:vMerge` or a separate cell per row? And what is the exact condition that is wrong.

## Short answer

There is no "header row count" in the engine at all - and that is not the fault. The fault is
that the table's cells are cut from **the page's drawing primitives** rather than from the
table's own row lattice, and that a glyph's row is then inherited from **the top edge of the
cell it fell into** instead of from the glyph's own y. Three lines do the damage:

| # | file:line | what it does | why it is wrong |
|:-|:--|:--|:--|
| 1 | `PdfToWord.java:6245` `RuleCollector.appendRectangle`, edges recorded at `6262-6267` | every `re` path contributes four table RULES, whether it is stroked with `S`, filled with `f`, or both | a **shading fill** is a paint region, not a cell outline. One fill that covers two header cells supplies the edges that close ONE cell across both |
| 2 | `PdfToWord.java:7800` `tableFromCells`, row index at `7846-7847` | `int ri = R.indexOf(hit[1])` - the row is the row the **cell rectangle starts on** | any glyph lower down inside a cell that is taller than one row is emitted in the cell's FIRST row |
| 3 | `PdfToWord.java:7912-7916` span loop, `7950` `t.spanR.add(...)`, `DocxWriter.java:6201` + `6277` | `spanC` is written on **every** row the rectangle covers; `spanR` is recorded and read by nothing | a real vertical merge becomes one cell per row with the text in the top one; `w:vMerge` is never emitted anywhere in the engine (`grep -rn spanR` finds no reader outside `PdfToWord`) |

The engine's own comment at `PdfToWord.java:421` says it: *"{@code DocxWriter} does not yet emit
{@code w:vMerge}"*. The comment at `7904-7910` already names **this document** - a previous run
saw the 2-row, 2-column header rectangle and worked around it by repeating `spanC` on every row
instead of emitting the merge.

## What I measured

### The page (`pymupdf`, one page, 595.28 x 841.89 pt)

Column edges `C = [56, 196, 262, 328, 394, 456, 518]` (6 columns).
Row edges `R = [126, 143, 160, 177, 194, 211, 228, 245, 262]` (8 rows: 2 header + 6 data).

The drawing primitives are, in the content stream (`xref 29`):

    q 0 0 0 RG .7 w 56 681.89 140 34 re S Q          <- Depot cell outline, 56..196 x 126..160
    q 0 0 0 RG .7 w 196 698.89 198 17 re S Q         <- SCHEDULED cell outline, 196..394 x 126..143
    q .9 .92 .96 rg 196 698.89 198 17 re f Q         <- its shading
    q .9 .92 .96 rg 394 681.89 124 34 re f Q         <- ONE shading fill, 394..518 x 126..160
    q 0 0 0 RG .5 w 196 698.89 m 394 698.89 l S Q    <- the y=143 rule, x 196..394 ONLY
    ...  rules at y=177,194,211,228,245,262 spanning 56..518
    ...  vertical rules at x=196 (160..262), 262,328,394,456 (143..262)

Two separators the page never draws, and both matter:

* **x = 456 between y=126 and y=143** - "Fleet held" and "Breakdowns" are each merged vertically
  across both header rows, so their own separator only exists from y=143 down. Above it the only
  geometry is the single fill.
* **y = 160 between x=196 and x=394** - the bottom of header row 2 under Services / Km operated /
  Revenue. The page draws that edge only where a cell ends: under Depot (x 56..196, the `re`)
  and under the two shaded cells (x 394..518, the fill). Nothing separates "Services" from
  "1,842".

### What the engine computes (instrumented build of the same tree, not committed)

`findTables` -> `intersectionsToCells` -> `tableFromCells` produced **39 cell rectangles** and
the lattice:

    C = [56.0, 196.0, 262.0, 328.0, 394.0, 456.0]
    R = [126.0, 143.0, 160.0, 177.0, 194.0, 211.0, 228.0, 245.0]

C and R are **right**. The cells are not. The three that matter:

    cell 394,126 -> 518,160     (one rectangle: cols 4-5, rows 0-1)
    cell 196,143 -> 262,177     (one rectangle: rows 1-2)
    cell 262,143 -> 328,177     (one rectangle: rows 1-2)
    cell 328,143 -> 394,177     (one rectangle: rows 1-2)

and the resulting buckets:

    [0][0] = Depot
    [0][1] = SCHEDULED
    [0][4] = "Fleet held\nBreakdowns"      <- two columns welded into one cell
    [1][1] = "Services\n1,842"             <- two rows welded into one cell
    [1][2] = "Km operated\n6,42,180"
    [1][3] = "Revenue (Rs. lakh)\n1,284.42"
    [2][0] = Yeshwanthpur   [2][4] = 184   [2][5] = 42
    [3..7] = correct

so `spanC=[1,3,0,0,2,0] spanR=[2,1,0,0,2,0]` on row 0 and
`spanC=[1,1,1,1,2,0] spanR=[2,2,2,2,2,0]` on row 1.

### The .docx (the artifact under test)

One table, 8 `<w:tr>`, 6 `<w:gridCol>`, **44 `<w:tc>`**, **3 `<w:gridSpan>`** (3, 2, 2),
**0 `w:vMerge`** - matches the brief exactly. Per row:

    0  [Depot]                [SCHEDULED span3]  [Fleet held\nBreakdowns span2]
    1  []                     [Services|1,842]   [Km operated|6,42,180]  [Revenue...|1,284.42]  [ span2]
    2  [Yeshwanthpur]         []                 []                      []                      [184] [42]
    3-7 correct

Two paragraphs in row 0's third cell and in row 1's second/third/fourth cells. Every row is
`trHeight 340 atLeast` (17 pt), so each of the two header rows grows to two lines. That is the
22.07 pt: **two extra lines above the body, not a pitch or row-height error.**

### The source needs

    46 <w:tc>, 1 <w:gridSpan> (SCHEDULED = 3), 3 <w:vMerge> (Depot, Fleet held, Breakdowns)
    r0: Depot(vMerge restart) | SCHEDULED(gridSpan 3) | Fleet held(vMerge restart) | Breakdowns(vMerge restart)
    r1: (vMerge continue)     | Services | Km operated | Revenue (Rs. lakh) | (continue) | (continue)
    r2: Yeshwanthpur | 1,842 | 6,42,180 | 1,284.42 | 184 | 42      <- one row, six cells

The engine emits 44 cells and 0 merges: the two cells it did merge are the two the page never
merged, and the three the page did merge it did not.

## The mechanism, step by step

1. `RuleCollector.appendRectangle` (`PdfToWord.java:6245`) is called for **every** `re`, and
   unconditionally records `{minY,minX,maxX}` / `{maxY,minX,maxX}` as horizontal rules and
   `{minX,minY,maxY}` / `{maxX,minY,maxY}` as vertical rules (`6262-6267`). The comment there
   admits it does not know the paint operator: *"A `re` that is only filled, never stroked,
   records the fill-only stroke it did not use"*. So `q .9 .92 .96 rg 394 681.89 124 34 re f Q`
   enters the rule list as four rules, at x=394 (y 126..160), x=518 (y 126..160), y=126 and
   y=160 (x 394..518).
2. `intersectionsToCells` (`7730-7756`) then finds, from the intersection (394,126), the nearest
   *connected* corner below that closes a rectangle. (394,143) fails because there is no
   horizontal edge at y=143 past x=394; (394,160) closes against (518,160), which the fill's own
   bottom edge supplies. **The only closed rectangle there is 394..518 x 126..160** - two
   columns wide, two rows tall, and no such cell exists on the page.
3. `tableFromCells` reads that width as a merge: `sc[r][c0] = Math.max(1, c1 - c0)` (`7914`),
   i.e. `gridSpan=2`, and `sr[r][c0] = Math.max(1, r1 - r0)` (`7915`), i.e. `spanR=2`.
   `DocxWriter` consumes only `spanC` (`6201`, written at `6277`), so row 0 writes one 2-column
   cell holding both header words and row 1 writes an empty 2-column cell where the merge
   continues.
4. Independently, the missing y=160 rule under Services/Km operated/Revenue leaves the only
   closed rectangle there as `196..262 x 143..177` etc. - header row 2 plus data row 1 in one
   cell, `spanR=2`.
5. `tableFromCells` then buckets glyphs by the cell they fall in and uses **the cell's top edge**
   as the row: `int ri = R.indexOf(hit[1])` (`7846`). "Services" (baseline ~157.6) and "1,842"
   (baseline ~174.8) are both inside the rectangle that starts at y=143, so both get `ri=1`.
   The row that should carry 1,842 - r2 - is emitted with that slot empty. This is the
   "numbers in the row above the depot name" symptom, exactly.
6. The vertical merges the page really has (Depot's stroked `re` 56..196 x 126..160, the two
   shaded cells) are also recorded as `spanR=2`, and `spanR` has **no reader anywhere in the
   engine** (`grep -rn spanR app/ tools/` -> declaration `425`, the comment `7909`, the write
   `7950`, nothing else). So no `w:vMerge` is written, the merge is expressed as "the same
   `gridSpan` cell on each covered row", and the text stays in the top one.

So the answers to the brief's three questions:

* **(a) header row count** - there is none. Rows are `nrow = |R|`, the distinct **cell tops**
  (`7801-7804`), and `t.header = nrow > 1` (`7917`) is only a boolean. On this document that
  gives the correct 8 rows / 2 header rows. Not the fault.
* **(b) which sub-row a cell's text belongs to** - `PdfToWord.java:7846`, the cell's top edge.
  That is the line that hoists 1,842 / 6,42,180 / 1,284.42 into the header row.
* **(c) vMerge** - never. `PdfToWord.java:7912-7916` + `7950` record `spanR`; nothing reads it;
  `DocxWriter` writes `gridSpan` only. A vertical merge becomes one cell per row.

## What I ruled out, with the numbers

1. **LibreOffice's rendering of gridSpan/vMerge.** Ruled out: the fault is in `document.xml`
   before any renderer sees it - 0 `w:vMerge`, 44 `w:tc`, and "Services" and "1,842" in the
   same `<w:tc>` as two `<w:p>`. Nothing a renderer could do would recover it.
2. **The row count being wrong (3 header rows, or a missing/extra row).** Ruled out: `R` has 8
   entries and the docx has 8 `<w:tr>`; the page has 9 horizontal rules from 126 to 262. The
   row *grid* is right; only the cells and their text are.
3. **`recutColumnBands` (the band re-cut).** Ruled out: the final table carries `recut=false`,
   and the function rejects this table at `8385` (`cols < 2 || cols > 4` - this table has 6) and
   at `8382` (`rows > 12`).
4. **`buildTables` / `rowTables` (the other two table passes).** Ruled out: the final table has
   populated `spanC`/`spanR` and cells joined with `"\n"`; `buildTables` never fills `spanC` or
   `spanR` and joins lines with `" "` (`8921`). `findTables` returned non-empty, so the
   `1284-1287` fallback never ran.
5. **A threshold or tolerance swallowing edges** (`EDGE_MIN`, `mergeEdges`, the 2 pt slack in
   the hit test). Ruled out: every rule on the page is 0.5-0.7 pt wide and at least 140 pt long,
   and no glyph inside the table band is dropped - I logged every glyph that misses every cell
   and there are **zero** misses with y in 120..185 (all misses are the masthead/heading glyphs
   at y=60..110). Nothing was filtered; the two missing separators are missing from the PDF.
6. **The 22.07 pt body displacement being its own defect** (row pitch, `LINE_BASE`, `trHeight`).
   Ruled out: every row is `trHeight 340 atLeast` = 17 pt, which is the page's own pitch
   (126->143->160...). The displacement is the *sum of two extra lines* in the two header rows
   - row 0 stacks "Fleet held"/"Breakdowns", row 1 stacks "Services"/"1,842" - roughly
   2 x 11 pt, which is the 22.07 pt measured. Fix the structure and the displacement goes.
7. **The `cy = g.y + size*0.35` hit test** putting glyphs in the wrong cell. Ruled out: the
   buckets are right at the glyph level; the error is the row *index* derived from the cell, not
   the cell lookup.

### The two experiments that separate the two mechanisms

Both were run in a scratch copy of the tree; **no engine code was changed in this commit**.

* **Split the shading fill** in a copy of the PDF (`394 681.89 124 34 re f` -> two `62 34`
  fills) and run the unmodified engine: row 0 becomes
  `[Depot][SCHEDULED span3][Fleet held span1][Breakdowns span1]` - **four cells, no gridSpan 2**.
  So the welding of "Fleet held"/"Breakdowns" is caused by the fill rectangle being read as a
  cell, not by anything about the text or the columns.
* **Bucket by the glyph's own row band** instead of the cell's top (`ri` from `cy` against `R`)
  in the scratch build: row 2 becomes
  `[Yeshwanthpur][1,842][6,42,180][1,284.42][184][42]` - **the body is correct**. It also moves
  "Depot" from r0 to r1, which is the useful negative result: a band test alone is not the fix,
  because the top row of a real vertical merge must keep its text. The two must be solved
  together (see below).

## What the root cause is, stated as a condition

> **A cell's vertical and horizontal extent is taken from the closed rectangle the page's drawn
> primitives happen to enclose, instead of being cut at the table's own row and column edges -
> and a glyph's row is then taken from that rectangle's top edge rather than from the glyph.**

A root cause, not a patch, because it predicts the class:

* any table whose merged cell is shaded with a fill that spans two cells gets a spurious
  horizontal merge (and the same for a fill spanning two rows);
* any table whose row separator is not drawn under every column - which is the *normal* shape of
  a table with a vertically merged cell, and also of a header whose second row is narrower -
  gets a spurious vertical merge, and every line of it is emitted one row too high;
* no document anywhere gets `w:vMerge`, because `spanR` has no reader.

The fix that follows from it (for the fixer, not made here): cut cells at the row lattice, keep a
rectangle only as the *evidence* that a merge is real (`Depot`'s `re` is; the leftover closed
region under Services is not), assign each glyph to the band its own baseline falls in, and give
the cell `(r0, c0, spanR, spanC)` the text of its first row while emitting `w:vMerge`
`restart`/`continue` for the rows below.

## What would prove this wrong

* If the .docx already contained `w:vMerge` and the numbers in the correct rows, the fault would
  be elsewhere - it contains neither.
* If splitting the shading fill had **not** separated "Fleet held" from "Breakdowns", the fill
  would not be the cause of the horizontal merge. It did separate them.
* If re-bucketing by the glyph's own band had **not** put 1,842 back in the Yeshwanthpur row,
  `7846` would not be the cause of the vertical one. It did put it back.
* If the page's cells were all fully outlined (a rule at x=456 above y=143, and a rule at y=160
  under Services) the engine would have got both right, and the defect would be a *missing
  rule* rather than a modelling one. The page does not draw them, and it should not have to:
  the row and column lattices are stated by the rest of the table.
