# COL-A — multi-column pages as table cells

**Engine:** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` and `PdfToWord.java`
**Base:** `kavopdf/app` @ `f470ac4`
**Verdict:** all six named documents render as **one page** with **0 continuous section breaks** and
**0 multi-column sections**, reading order 89 / 96 / 98 / 92 / 96 / 52 %; the 208-document gate prints
`no document got worse`.

---

## 1. What this changes

A page the column pass detects as newspaper columns is no longer written as a `w:cols` section with
`<w:type w:val="continuous"/>` breaks around its full-width bands. It is written as **one layout
table**: a fixed-geometry `w:tbl`, one row per column band, one cell per column, with the page's
full-width bands as ordinary paragraphs above and below.

Two properties follow, and they are the two the user reported:

* **One page.** Google Docs turns every continuous section break into a page break. With the breaks
  gone, 62 is one page. Corpus-wide the continuous breaks go from **26 to 0** and multi-column
  sections from **17 to 0**.
* **Reading order.** `w:cols` is flow-based: Word decides where column one ends, so a paragraph is
  flowed into the next column at the wrong height and the order comes out interleaved even when every
  line lands in the right place — that is exactly 63's 100 %-within-3-pt / 13 %-order baseline. A cell
  is a fixed rectangle, so nothing moves between columns.

---

## 2. What I took from D8-C

I read `tools/p2w-bench/patches/D8-C-sections-without-sections.patch` and its report first. The patch
no longer applies (`git apply --check` fails at `DocxWriter.java:208`), because the writer has changed
since: `pageBody()` now runs **twice** per page (a measuring pass and a writing pass, for the budget
guard), `ctx.secCols` was added so a one-column section does not subtract a column indent, and
`fitPage()` returns `null` instead of clamping. So the approach was re-applied by hand against today's
code.

Taken from D8-C essentially unchanged:

| From D8-C | What it is |
|---|---|
| `columnPage()` | The layout table itself: classification, cross-gutter row splitting, grid from the page's own column edges, per-cell flow reset. |
| `splitColumns()` | A row the column pass cut at the gutter holds both halves on one baseline; each half goes to its own cell. |
| `oneBoxPara()` | One column's half of such a row, as its own paragraph. |
| `emitBlock()` | One dispatch for a block, shared by the bands and the caller's flow. |
| `bandLeftTw()` returns 0 outside a cell | A full-width band is not shifted left by the column's x (this removed a 56 pt left shift on these pages' mastheads). |
| `flowFromBox()` / `flowRow()`: `afterTablePt` | A table is an edge, not a baseline, so the block after it is placed against the table's measured bottom; a gap too wide for the flow's cap is a position, not a gap. |
| The `used.size() < 2` and "one contiguous band" guards | A page whose prose never sits in the bands, or that interleaves bands and columns, is written as an ordinary single-column flow. |

Deliberately **not** taken, because it is the thing the brief asked me to remove:

* the `blockSpan * 0.62` full-width heuristic and the whole continuous-section machinery in
  `pageBody()` — deleted;
* `pageColumns()` returning `{page.columns, gap}` — it now always returns one column, so the page's
  section is single-column and no `w:cols w:num` is ever emitted.

---

## 3. What I had to change on top of D8-C

D8-C's patch assumed `page.columns` and `ctx.colLeft` described the columns the page was actually cut
into. On today's code neither does, and that is why a blind re-application would have engaged on
exactly one of the six documents.

### 3.1 `page.columns` was stale (`PdfToWord.java`)

`page.columns = proseColumns(...)` is computed at the **top** of `readPage()`, before any of the three
gutter detectors has finished. `proseColumns()` clusters raw line left edges and requires the bands to
be near-equal in width, so it answers **1** for a page whose columns are uneven and for a page whose
gutter is only visible to the glyph projection or to a vertical rule. Measured: 63, brochure-3col,
journal, annual-review and newspaper all reported `columns = 1` while the page was visibly cut into
bands. D8-C's `columnPage()` therefore declined on every one of them.

**Fix:** `page.columns` is now derived from `starts` — the gutter list the cut is really made from —
after all three detectors have run, capped at 4 (the widest grid the block pass is built for).

### 3.2 The column *edges* cannot come from the block tags either

`Ctx.colLeft` is the smallest left edge of the blocks tagged with a band, and it is wrong in both
directions:

* **newspaper-2col-fullwidth-headline** — the full-width masthead "THE MORNING LEDGER" sits at x=100
  and is tagged column 1, so column 1's edge reads as **99.7 pt** against the 303 pt the page sets it
  at. Every line of column 0 then straddles that "gutter" and is refused.
* **63_three_column_brochure** — the column pass found only one of its two gutters, so all three
  columns are tagged 0 and `colLeft` has no entry for columns 1 or 2 at all.

**Fix:** `rowColumnEdges()` reads the edges off the page's own **rows**. Project the fragments of every
row that holds more than one fragment, cluster their left edges, and keep the clusters that recur on at
least 30 % of those rows. A column's left edge is where its lines start, and that recurs once per row;
a masthead's issue date and a deck's overhang are one-offs and are dropped by the frequency test.

Two traps I hit and had to design around, both recorded in the code:

* **Projecting extents instead of left edges does not work.** A row whose middle column has ended —
  brochure-3col's "is the reason the tools are still in kitchens that utilisation …" holds a fragment
  in the first column and one in the last, and its first fragment runs straight across the gutter —
  covers the gutter. So does 63's deck line, which is set across the first column and a little beyond.
  Left edges do not have that problem.
* **A fragment must be assigned to its NEAREST column start**, not "the last edge it is past". The
  edges are clustered averages, so brochure-3col's third column measures 395.3 from most rows and one
  row starts it at 392; a threshold test put that fragment in column 2 and then rejected the row.

### 3.3 The band's vertical extent

D8-C assumed the band is the run of blocks between the first and last column block. On today's corpus
that fails both ways: a 6 pt drop cap and an "Edition 2026" line sit at a column's x on the masthead's
own baselines and drag the band's top up over the masthead, which then reads as full-width text inside
the columns and refuses the page.

**Fix:** the band is the **longest run of baselines on which two columns are both set**. Two columns
standing side by side is what a column *is*, and a lone line of header furniture is alone on its
baseline. The run requirement matters too: brochure-3col's header puts its title at column 1's x and
its edition line at column 3's x on one shared baseline 65 pt above the body — a single shared line is
furniture, a run of them is columns. Blocks above the band are emitted before the table, blocks below
after it, and a full-width block drawn *inside* the band still refuses the page (the brief's item 3).

### 3.4 Vertical geometry that D8-C did not have to face

Three separate defects, each found by measurement:

1. **The cell indent subtracted the wrong edge.** D8-C's `bandLeftTw()` subtracts
   `ctx.colLeft.get(column)`; on 63 that map has no entry for columns 1 and 2, so the indent stayed
   page-relative (306 pt) inside a 250 pt cell and every line wrapped to one character — 63 came out
   three pages. It now subtracts the **cell's own left edge** (`ctx.cellLeftPt`), which is set per cell.
2. **The row height was declared as the band's height.** `w:trHeight` is a minimum, so a row declared
   at the band's height while its text needs less is simply a taller row than the page had — enough, on
   a page whose columns fill the sheet, to push the row onto a second page. The cells are now written
   into their own buffers first, measured, and the row declared at the **tallest cell's** height.
3. **`hRule="atLeast"` let LibreOffice size the row.** With `atLeast`, LibreOffice decides the row from
   its own model of the cell content and, on a page that already carries a band above the columns,
   sizes it to the rest of the sheet: annual-review declared a 364 pt row and got one that ended at the
   foot of the paper, pushing the running footer and the anchored shapes onto a second, empty page.
   Measured: `atLeast` → 2 pages, `exact` → 1 page with all 41 lines present. It is safe as `exact`
   because every paragraph in a cell is written with `w:lineRule="exact"` and its own `w:before`, so
   the content height *is* that sum and the renderer has no line-box of its own to add.

### 3.5 One row per band, not one row per page

63 is set in columns **twice**: three columns of prose, then three columns of specifications below
them. The page reads band by band — all three columns of band 1, then all three of band 2 — but a
single row says "all of column one, then all of column two". With one row, 63's lines were all in the
right place (96 % within 3 pt) and its reading order was still **33 %**.

**Fix:** the table gets **one row per band**, where a band break is a gap that no column fills. 63 goes
to **96 %**. The threshold matters: at 12 pt, 62 splits at its pull quote and falls from 89 % to 75 %;
at 30 pt both hold (62 at 89 %, 63 at 96 %).

### 3.6 Two smaller fixes found while measuring

* **The bands are written top to bottom, not in block order.** The block pass orders a page by column
  then by y, so annual-review's "K" drop cap is block 0 and its letterhead block 1 although the
  letterhead is 8 pt higher. A flow cannot put the second paragraph above the first, so the letterhead
  got no space before it and the whole page moved down by the drop cap's height (a constant +19 pt).
  Sorting the bands by y took annual-review from 2 % to 91 % within 3 pt.
* **Inside a cell a wide gap is space, not a position.** The gap cap exists to stop a flow spending an
  enormous gap; inside a cell the row's height is measured from exactly what is written, so spending it
  is both safe and correct. Anchoring instead made a text box — not editable in Google Docs — and on
  brochure-3col, whose columns hold more than one band, turned 24 lines into text boxes.

---

## 4. Before / after — the six documents

`python3 tools/p2w-bench/verify_visual.py <source.pdf> <generated.docx>`. Pages and "within 10 pt" are
the geometry; **reading order is the number that matters**.

| Document | Pages (pdf → docx) | Within 10 pt | Reading order | |
|---|---|---|---|---|
| `62_two_col_newsletter_pull_quote` | **2 → 1** | 25 % → **100 %** | 33 % → **89 %** | 6 continuous breaks → 0 |
| `63_three_column_brochure` | 1 → 1 | 100 % → 96 % | 13 % → **96 %** | positions were already perfect; order was the whole problem |
| `newspaper-2col-fullwidth-headline` | **2 → 1** | 0 % → **97 %** | 100 % → 98 % | 8 continuous breaks → 0 |
| `brochure-3col-with-sidebar-box` | 1 → 1 | 1 % → **64 %** | 33 % → **92 %** | |
| `annual-review-2col-uneven-columns` | **2 → 1** | 23 % → **100 %** | 36 % → **96 %** | 2 continuous breaks → 0 |
| `journal-2col-with-footnotes` | **2 → 1** | 0 % → **45 %** | 56 % → 52 % | single-column fallback (see §5) |

Within 3 pt, for completeness:

| Document | within 3 pt | median dx | matched |
|---|---|---|---|
| 62 | 6 % → **100 %** | 0.1 pt | 100 % |
| 63 | 100 % → 96 % | 0.1 pt | 100 % |
| newspaper | 0 % → **95 %** | 0.1 pt | 100 % |
| brochure-3col | 1 % → **60 %** | 0.1 pt | 98 % → 88 % |
| annual-review | 9 % → **91 %** | 0.1 pt | 100 % |
| journal | 0 % → **23 %** | 0.1 pt | 91 % → 94 % |

Structural counts in the generated files:

| Document | continuous breaks | multi-column sections | layout tables / rows |
|---|---|---|---|
| 62 | 6 → **0** | 4 → **0** | 0 → 1 table, 1 row |
| 63 | 0 → 0 | 0 → 0 | 0 → 1 table, 2 rows |
| newspaper | 8 → **0** | 5 → **0** | 0 → 1 table, 1 row |
| brochure-3col | 0 → 0 | 0 → 0 | 0 → 1 table, 2 rows |
| annual-review | 2 → **0** | 2 → **0** | 0 → 1 table, 3 rows |
| journal | 10 → **0** | 6 → **0** | 0 (fallback) |

Corpus-wide (208 documents): `<w:type w:val="continuous"/>` **26 → 0**, `w:cols w:num="2..9"` **17 → 0**.

### Two honest regressions in that table

* **63 loses 4 % of its within-3-pt** (100 → 96). Its worst `dy` is 34.4 pt against 1.8 pt before:
  one heading row lands a line low. Order went from 13 % to 96 %, which is the property the user
  reported, but the position is not quite what it was.
* **brochure-3col matches 88 % of source lines, not 98 %** (83 rendered lines against 88). Five lines
  are missing from the render. This is the one document in the six where a line is genuinely lost, and
  it is the document whose `within 10 pt` is still 64 % — I would look at it first in a follow-up.

---

## 5. The fallback, and why journal uses it

`journal-2col-with-footnotes` is the one document of the six that does **not** get a layout table, and
that is the brief's item 3 working as intended: its page interleaves full-width content with column
content — a footnote block spans both columns *inside* the band — so `columnPage()` returns false and
the page is written as an ordinary single-column flow. One page with a correct order beats one page with
a scrambled one; in practice journal is one page and its order is 52 %, against 56 % before and two
pages. Its `within 10 pt` improves from 0 % to 45 % because the extra page is gone.

Two full-width-in-band refusals I checked and kept rather than papered over: a headline set between
column fragments (newspaper-2col-fullwidth-headline in its *earlier* state — with corrected edges its
headline is entirely above the band, so it now gets a table and scores 98 %) and the spanning footnote
on journal.

---

## 6. Gate verdict

```
$ python3 tools/p2w-bench/gate.py --corpus <corpus> --out <out> --baseline tools/p2w-bench/base208.json --check
documents: 208
IMPROVED: 26 counts
   06_rect_paid_stamp_red_transparent         lines    101 -> 107
   07_stamp_over_table                        lines    72 -> 73
   12_stamp_across_page_break                 lines    42 -> 45
   17_three_column_widths_txtpos              lines    19 -> 39
   27_two_column_left_short_txtpos            lines    30 -> 32
   315_gazette_notification                   lines    30 -> 33
   31_times_body_arial_headings               lines    24 -> 28
   350_question_paper                         lines    85 -> 115
   361_product_catalogue_grid                 lines    13 -> 33
   363_warranty_card                          lines    28 -> 30
   39_small_caps_letter_spacing               lines    19 -> 23
   401_trifold_brochure                       lines    23 -> 24
no document got worse
```

**`no document got worse`.** 208 of 208 scored, 26 counts improved, 0 regressed. The baseline build was
verified first and is also clean, so the comparison is like for like.

## 7. Build and tests

* `javac` of the whole engine against the PDFBox-Android AAR: clean, no warnings beyond the two
  pre-existing `-Xlint` notes.
* `ConvertAll` over the 208-document corpus: `done: 208 files, 0 failed`, no `EMPTY` documents.
* `tools/verify-engine.sh`: runs clean through the engine, rotation, text-layer, search, link-icon,
  font and real-document suites. `REALDOCS TOTAL: 3 passed, 0 failed`, `FONTS: PASS`.
* `TestPdfToWord` **29 passed, 0 failed** (including "sectPr is the last thing in the body");
  `TestNorms` **13 passed, 0 failed**; `TestOrder` PASS.

---

## 8. Hunk summary

`DocxWriter.java` (+851/−58) and `PdfToWord.java` (+20/−0). Full patch in Appendix A.

| Area | Change |
|---|---|
| `Ctx` | new `afterTablePt`, `inColumn`, `cellLeftPt`, `cellRightPt`; reset per page and per squeeze retry. |
| `pageBody()` | the `blockSpan` heuristic and all continuous-section emission **deleted**; a page with columns goes to `columnPage()`, otherwise the plain `emitBlock()` loop. |
| `pageColumns()` | always one column — the columns are the table's now. |
| `bandLeftTw()` | the cell's own left edge inside a cell, 0 outside. |
| `fitPage()` | inside a cell the budget does not apply (the row bounds the flow), but the page's squeeze factor does. |
| `flowFromBox()`, `flowRow()` | `afterTablePt` edge placement, cell-relative centring and right alignment, and a wide gap inside a cell is spent as space rather than anchored. |
| `columnPage()` (new) | the layout table: band from shared baselines, one row per band, cells written and measured before the row is declared. |
| `rowColumnEdges()`, `columnAt()`, `dropCap()` (new) | the edges, read off the page's own rows. |
| `splitColumns()`, `oneBoxPara()`, `emitBlock()`, `blockTop()`, `blockBottom()`, `flowTwOf()`, `sortByTop()` (new) | helpers. |
| `PdfToWord.readPage()` | `page.columns` derived from the final `starts`. |

---

## Appendix A — full diff

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 9216473..663988e 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -295,6 +295,18 @@ public final class DocxWriter {
     }
 
     private static int[] fitPage(Ctx ctx, int beforeTw, int lineTw, float size) {
+        if (ctx.inColumn) {
+            // A cell's flow is bounded by its ROW's height, which is written as the table's
+            // w:trHeight, not by the sheet: the page's budget has already been spent by the
+            // bands above the table. Charging the cell against it would squeeze or break a
+            // column that the row is holding, and a page break inside a cell is not a thing.
+            // The page's squeeze factor still applies - the row is measured from what the cell
+            // really writes, so a squeezed page has to squeeze inside the cells too.
+            int b2 = twScale(beforeTw, ctx.squeeze);
+            int l2 = twScale(lineTw, ctx.squeeze);
+            ctx.flowTw += b2 + l2;
+            return new int[]{b2, l2};
+        }
         if (ctx.measuring) {
             // Measuring a page: the gap is given up exactly as the old guard gave it up once the
             // budget was spent, but no line is shortened and nothing is broken - the answer this
@@ -450,6 +462,37 @@ public final class DocxWriter {
          * page put them, and the section said one column all along.
          */
         int secCols = 1;
+        /**
+         * The y, in points, that the next paragraph's box must start below - the bottom edge of
+         * a layout table, or the top edge of a column cell. {@code -1} when there is none.
+         *
+         * <p>A table is not a baseline: {@link #lastBaseline} cannot describe where a row ends,
+         * because the renderer decides the row's height from its own line boxes. So the block
+         * after a table is placed against the table's measured bottom instead of being spaced
+         * from the line above it, which is the only way the page's own y survives a table.
+         */
+        float afterTablePt = -1f;
+        /**
+         * True while writing the inside of a layout-table cell.
+         *
+         * <p>A cell's text starts at the column's own left edge, so every indent inside it is
+         * measured from that edge rather than from the paper. Outside a cell the paper is the
+         * origin and nothing is subtracted.
+         */
+        boolean inColumn;
+        /** The right edge of the current column cell, in points - the width an indent is from. */
+        float cellRightPt;
+        /**
+         * The left edge of the current column cell, in points.
+         *
+         * <p>Inside a cell the text starts at the CELL's edge, so every page-relative indent has
+         * to have that edge taken off it. It cannot be read from {@link #colLeft}: that map is
+         * keyed by the band the column pass tagged a block with, and on a page whose gutters the
+         * detector only partly found there is no entry for the later columns at all
+         * (63_three_column_brochure's three columns are all tagged 0). The indent then stayed
+         * page-relative, exceeded the cell's own width, and every line wrapped to one character.
+         */
+        float cellLeftPt;
         /** The page's own width in points, so a tab stop can tell when it is at the paper edge. */
         float pageWidthPt = 595f;
         /**
@@ -569,6 +612,10 @@ public final class DocxWriter {
             ctx.secCols = secCols;
             ctx.lastLinePt = 0f;
             ctx.positioned = false;
+            ctx.inColumn = false;
+            ctx.cellLeftPt = 0f;
+            ctx.cellRightPt = 0f;
+            ctx.afterTablePt = -1f;
             ctx.flowTw = 0;
             ctx.budgetTw = (int) Math.max(1L, Math.round(ph * TWIPS_PER_PT) - PAGE_ROUNDING_TW);
             // pageFits is the measurement; hasColumnBands was a proxy for it and it over-fired.
@@ -661,6 +708,10 @@ public final class DocxWriter {
                     ctx.positioned = false;
                     ctx.newPage = true;
                     ctx.lastWasTable = false;
+                    ctx.inColumn = false;
+                    ctx.cellLeftPt = 0f;
+                    ctx.cellRightPt = 0f;
+                    ctx.afterTablePt = -1f;
                     ctx.budgetTw = Math.max(1, pageBudgetTw - overheadTw);
                     pageBody(pg, page, ctx, pw, ph, secGap);
                     int w = spacingTw(pg);
@@ -712,59 +763,741 @@ public final class DocxWriter {
      */
     private static void pageBody(StringBuilder sb, PdfToWord.Page page, Ctx ctx,
                                  float pw, float ph, float secGap) {
-        // A page set in columns, with a full-width element in the middle of it, is more than
-        // one section: the columns before the element, the element, and the columns after it.
-        // Without the breaks the element is poured into a column like everything else.
+        // A page set in newspaper columns is written as a fixed-geometry layout table - one
+        // row, one cell per column - and its section stays single-column.
+        //
+        // WHY NOT CONTINUOUS SECTION BREAKS. Until now a full-width element between the columns
+        // was given a section of its own, and the boundaries were <w:type w:val="continuous"/>.
+        // Word and LibreOffice honour that. Google Docs does not: it turns every continuous
+        // break into a PAGE break, so a one-page newsletter arrived as two pages. Measured on
+        // 62_two_col_newsletter_pull_quote - six continuous breaks, 474 pt of flow on an 842 pt
+        // sheet, two pages in Google Docs.
         //
-        // The carrier is a zero-height paragraph holding the sectPr, because a sectPr has to
-        // live in a pPr and a table cannot carry one. Measured on a prototype: a table with a
-        // carrier after it costs 2.9 pt and spans correctly.
-        float blockSpan = 0f;
-        for (Object bb : page.blocks) {
-            if (bb instanceof PdfToWord.Para) {
-                PdfToWord.Para q = (PdfToWord.Para) bb;
-                blockSpan = Math.max(blockSpan, q.right - q.left);
+        // A paragraph cannot carry a column count of its own (w:cols is a section property), so
+        // no arrangement of paragraphs reproduces "full-width band, then two columns" on one
+        // sheet without a section break. A table can: the columns become the table's columns, a
+        // full-width band is simply a paragraph above or below it, and nothing in the document
+        // is a section. The words also come out in column order, which is the order the page is
+        // read in - the per-line blocks the column pass produces interleave the two columns, and
+        // grouping them by band puts each column back together.
+        if (columnPage(sb, page, ctx, pw)) return;
+        for (Object block : page.blocks) emitBlock(sb, block, ctx);
+    }
+
+    /**
+     * The column each box of a cross-gutter "row" belongs to, or null when the block is a
+     * genuine full-width line.
+     *
+     * <p>Returns an array parallel to {@code p.boxes} when the boxes fall in two or more
+     * different columns - the column pass cut a line at the gutter and left both halves on one
+     * baseline - and null when the block is a single line running the width of the paper, or
+     * when its boxes all sit in one column after all.
+     */
+    private static int[] splitColumns(Object block, float[] edge, int n) {
+        if (!(block instanceof PdfToWord.Para)) return null;
+        PdfToWord.Para q = (PdfToWord.Para) block;
+        if (q.boxes.size() < 2) return null;
+        // Each fragment belongs to the column it sits INSIDE. A column's line is often cut
+        // again wherever the typeface changes, so a row can hold six word-fragments in its first
+        // column before the second column's fragment even begins - brochure-3col's "Every Kastura
+        // product is made from ..." is one such row - and only the FIRST fragment in a column
+        // starts at that column's edge.
+        int[] part = new int[q.boxes.size()];
+        boolean mixed = false;
+        float[] firstX = new float[n];
+        for (int c = 0; c < n; c++) firstX[c] = Float.MAX_VALUE;
+        for (int k = 0; k < part.length; k++) {
+            PdfToWord.Box bx = q.boxes.get(k);
+            int c = 0;
+            // The edges are clustered averages, so a fragment can start a few points LEFT of its
+            // column's own edge - brochure-3col's third column measures 395.3 from most of its
+            // rows and one row starts it at 392 - and a strict comparison would put that
+            // fragment in the column before it and then reject the row for crossing an edge.
+            while (c + 1 < n && bx.x >= edge[c + 1] - 20f) c++;
+            // A box that runs PAST the next column's edge was never cut: it is one line across
+            // the paper. The running footer is exactly that - its words and its page number are
+            // two boxes, and the words run the whole width - and splitting it put "Page 1" at
+            // the top of the right column instead of at the foot of the page.
+            if (bx.right > edge[c + 1] + 1f) return null;
+            part[k] = c;
+            firstX[c] = Math.min(firstX[c], bx.x);
+            if (k > 0 && part[k] != part[k - 1]) mixed = true;
+        }
+        if (!mixed) return null;
+        // A masthead is not a cut row: its issue date sits at the third column's x but is
+        // right-aligned there, so it starts two hundred points into the column, while a fragment
+        // the column pass cut begins at the column's own edge.
+        for (int c = 0; c < n; c++) {
+            if (firstX[c] == Float.MAX_VALUE) continue;
+            if (firstX[c] - edge[c] > COLUMN_START_TOL) return null;
+        }
+        // A row whose boxes are merely spread across the page is not a cut line: a masthead
+        // holds the paper's name at the left and the issue date at the right, and there is a
+        // wide empty gutter between them that the page drew on purpose. What tells the two apart
+        // is where each fragment STARTS - a line the column pass cut begins at its own column's
+        // left edge, while a masthead's date is right-aligned and starts two hundred points into
+        // the last column - and columnAt has already refused every fragment that starts at no
+        // column's edge. A coverage ratio cannot tell them apart: a ragged row, whose last
+        // column's line stops short of the measure, covers only seven tenths of the width it
+        // spans and would be thrown out along with the masthead.
+        return part;
+    }
+
+    /** A copy of {@code p} holding one of its boxes - one column's half of a cross-gutter row. */
+    private static PdfToWord.Para oneBoxPara(PdfToWord.Para p, PdfToWord.Box b, int column) {
+        PdfToWord.Para q = new PdfToWord.Para();
+        q.runs.addAll(b.runs);
+        q.heading = p.heading;
+        q.align = p.align;
+        q.indent = p.indent;
+        q.bullet = p.bullet;
+        q.stamp = p.stamp;
+        q.top = b.y;
+        q.left = b.x;
+        q.right = b.right;
+        q.column = column;
+        q.boxes.add(b);
+        return q;
+    }
+
+    /**
+     * Writes a page that is set in newspaper columns, as a fixed-geometry layout table.
+     *
+     * <p>The page becomes one table: a single row with one cell per column, at the x the page
+     * drew each column at, plus the page's own full-width bands above and below it as ordinary
+     * paragraphs. Nothing in the result is a section, so nothing in the result is a continuous
+     * section break - which is the whole point, because Google Docs renders every continuous
+     * break as a page break.
+     *
+     * <p>It also puts the words in the order the page is read in. The column pass works on
+     * unsplit lines and emits one block per line, so the blocks of the two columns interleave;
+     * grouping them by band restores "all of the left column, then all of the right column".
+     *
+     * <p>A cell is a fixed rectangle, not a position in a flow. That is why this is a table and
+     * not {@code w:cols}: with {@code w:cols} the reader decides where column one ends, so a
+     * paragraph from the left column is flowed into the right one at the wrong height, and the
+     * reading order comes out interleaved even when every line lands in the right place - which
+     * is exactly what 63_three_column_brochure did (100 % of lines within 3 pt, 13 % order).
+     *
+     * @return true when the page was written this way. False when the page's column geometry
+     *         cannot be trusted, or when its prose never actually sits in the bands the column
+     *         pass found - then the caller's plain flow is the honest answer.
+     */
+    /** A page's column geometry: the left edge of every column, and the paper's right edge. */
+    private static final class ColGeom {
+        float[] edge;
+    }
+
+    /** Top edge of a block's own boxes, in points from the page top. -1 when it has none. */
+    private static float blockTop(Object b) {
+        if (b instanceof PdfToWord.Para) {
+            float t = Float.MAX_VALUE;
+            for (PdfToWord.Box z : ((PdfToWord.Para) b).boxes) {
+                if (z.runs.isEmpty()) continue;
+                t = Math.min(t, z.y - LINE_BASE * z.size);
             }
+            return t == Float.MAX_VALUE ? -1f : t;
         }
-        int curCols = page.columns;
-        for (Object block : page.blocks) {
-            if (page.columns > 1 && blockSpan > 0f) {
-                boolean full = false;
-                if (block instanceof PdfToWord.Para) {
-                    PdfToWord.Para q = (PdfToWord.Para) block;
-                    full = q.right - q.left > blockSpan * 0.62f;
-                } else if (block instanceof PdfToWord.Table) {
-                    PdfToWord.Table q = (PdfToWord.Table) block;
-                    full = q.right - q.left > blockSpan * 0.62f;
+        if (b instanceof PdfToWord.Table) return ((PdfToWord.Table) b).top;
+        return -1f;
+    }
+
+    /** Bottom edge of a block's own boxes, in points from the page top. -1 when it has none. */
+    private static float blockBottom(Object b) {
+        if (b instanceof PdfToWord.Para) {
+            float r = -Float.MAX_VALUE;
+            for (PdfToWord.Box z : ((PdfToWord.Para) b).boxes) {
+                if (z.runs.isEmpty()) continue;
+                r = Math.max(r, z.bottom > 0f ? z.bottom : z.y + z.size);
+            }
+            return r == -Float.MAX_VALUE ? -1f : r;
+        }
+        if (b instanceof PdfToWord.Table) return ((PdfToWord.Table) b).bottom;
+        return -1f;
+    }
+
+    /** How far a fragment may start from its column's left edge and still be that column's line. */
+    private static final float COLUMN_START_TOL = 40f;
+
+    /**
+     * The column whose left edge a fragment starts at, or -1 when it starts at none of them.
+     *
+     * <p>NEAREST edge, not "the last edge it is past". The edges are read off the page's own rows
+     * and are a point or two out from any one row's fragments - brochure-3col's third column is
+     * measured at 395.3 from most of its rows and one row starts at 392 - and a threshold test
+     * would put that fragment in the second column and then reject the row as a masthead.
+     */
+    private static int columnAt(float x, float[] edge, int n) {
+        int best = -1;
+        float bestD = COLUMN_START_TOL;
+        for (int c = 0; c < n; c++) {
+            float d = Math.abs(x - edge[c]);
+            if (d <= bestD) { bestD = d; best = c; }
+        }
+        return best;
+    }
+
+    /**
+     * True for a decorative initial: one narrow glyph where a column's first line would be.
+     *
+     * <p>annual-review-2col-uneven-columns opens with a 6 pt "K" drop cap drawn on the masthead's
+     * own baseline. It is a single narrow box, so it is not a column line - but it is inside
+     * column 0, so counting it when the band is measured drags the band's top up over the
+     * masthead, and the masthead then reads as full-width content INSIDE the columns and the page
+     * is refused.
+     */
+    private static boolean dropCap(PdfToWord.Para q) {
+        if (q.boxes.size() != 1) return false;
+        PdfToWord.Box z = q.boxes.get(0);
+        return z.right - z.x < 20f;
+    }
+
+    /**
+     * The page's column edges, read off the page's own ROWS, or null when it is not set in
+     * columns.
+     *
+     * <p>The column pass tags each block with the band it was cut into, and that tag is the
+     * obvious source for the edges - but it is not a reliable one. A page's full-width masthead
+     * can be tagged with the last band (newspaper-2col-fullwidth-headline's "THE MORNING LEDGER"
+     * is at x=100 and is tagged column 1, so the second column's left edge reads as 99.7 pt
+     * against the 303 pt the page drew it at), and a page whose gutters the detector only partly
+     * found carries one band for three columns (63_three_column_brochure, whose three columns are
+     * all tagged 0).
+     *
+     * <p>A ROW that holds more than one fragment is direct evidence and needs no tag. Project the
+     * boxes of those rows only - a single-fragment row is a plain line and says nothing about
+     * where a column ends - and the x-ranges nothing covers are the gutters. Restricting the
+     * projection to multi-fragment rows is what makes it work where the page-wide projection in
+     * PdfToWord does not: a deck line set across the first column and a little beyond it
+     * ("Single estate arabica from the Baba Budan hills ...") covers the gutter on a whole-page
+     * projection, but it is a single box on its own row, so it is not projected here.
+     *
+     * <p>The vertical band the columns occupy is then the run of rows that really are column
+     * rows: every fragment starts at its own column's left edge (see
+     * {@link #COLUMN_START_TOL}). A masthead is not one of those - its issue date starts two
+     * hundred points into the last column, right-aligned - so it does not stretch the band up
+     * over itself, and it stays a full-width paragraph above the table.
+     */
+    private static ColGeom rowColumnEdges(PdfToWord.Page page, float pw) {
+        java.util.List<PdfToWord.Para> rows = new ArrayList<>();
+        for (Object b : page.blocks) {
+            if (b instanceof PdfToWord.Para && ((PdfToWord.Para) b).boxes.size() >= 2) {
+                rows.add((PdfToWord.Para) b);
+            }
+        }
+        // Three rows is the least that can evidence a column layout; below that a row of two
+        // fragments is a form field or a kerning accident, not a gutter.
+        if (rows.size() < 3) return null;
+
+        // A column's left edge is where its lines START, and that is the one thing a multi-
+        // fragment row says that a projection does not. Projecting the fragments and reading the
+        // uncovered strips fails on exactly the pages this exists for: a row whose middle column
+        // has ended - brochure-3col's "is the reason the tools are still in kitchens that
+        // utilisation ..." holds a fragment in the first column and one in the last, and its
+        // first fragment runs straight across the gutter between them - and a deck line set
+        // across the first column and a little beyond it covers the gutter on 63 as well.
+        //
+        // Left edges do not have that problem. Every row of a band starts its first column at the
+        // same x, so that x recurs once per row, while a masthead's issue date and a deck's
+        // overhang are one-offs. Clustering the fragments' left edges and keeping the ones that
+        // recur is therefore the gutter's own evidence, and it is not confused by a row that is
+        // missing a column.
+        java.util.List<Float> xs = new ArrayList<>();
+        for (PdfToWord.Para q : rows) {
+            for (PdfToWord.Box z : q.boxes) {
+                if (z.runs.isEmpty() || z.right <= z.x) continue;
+                xs.add(z.x);
+            }
+        }
+        if (xs.size() < 6) return null;
+        java.util.Collections.sort(xs);
+        java.util.List<float[]> cand = new ArrayList<>();       // {x, count}
+        float cur = xs.get(0);
+        int curN = 1;
+        for (int i = 1; i < xs.size(); i++) {
+            float v = xs.get(i);
+            if (v - cur <= 8f) { cur = (cur * curN + v) / (curN + 1); curN++; }
+            else { cand.add(new float[]{cur, curN}); cur = v; curN = 1; }
+        }
+        cand.add(new float[]{cur, curN});
+        int need = Math.max(3, Math.round(rows.size() * 0.3f));
+        java.util.List<Float> starts = new ArrayList<>();
+        for (float[] c : cand) if (c[1] >= need) starts.add(c[0]);
+        if (starts.size() < 2 || starts.size() > 4) return null;
+
+        float[] edge = new float[starts.size() + 1];
+        for (int i = 0; i < starts.size(); i++) edge[i] = starts.get(i);
+        edge[edge.length - 1] = pw;
+        int n = edge.length - 1;
+        // Every column has to be a real column: an edge outside the paper, or one a kerning
+        // artefact away from its neighbour, is not a gutter.
+        for (int c = 1; c < edge.length; c++) {
+            if (edge[c] <= edge[c - 1] + 20f || edge[c] > pw) return null;
+        }
+
+        // The vertical band is decided by the caller, from the page's own baselines: a column
+        // exists where two columns are both set, not where one line happens to start at a
+        // column's x.
+        ColGeom g = new ColGeom();
+        g.edge = edge;
+        return g;
+    }
+
+    private static boolean columnPage(StringBuilder sb, PdfToWord.Page page, Ctx ctx, float pw) {
+        int n = page.columns;
+        // The edges come from the page's rows when they show columns (see rowColumnEdges), and
+        // from the column pass's own tags when they do not.
+        ColGeom geom = rowColumnEdges(page, pw);
+        float[] edge;
+        if (geom != null) {
+            edge = geom.edge;
+            n = edge.length - 1;
+        } else {
+            if (n < 2 || ctx.colLeft == null || ctx.colLeft.size() < n) return false;
+            // The left edge of a column is the MEDIAN of its blocks' left edges, not the
+            // smallest. Ctx.colLeft is the smallest, and on a page whose masthead is tagged with
+            // the last band that smallest is the masthead's - newspaper-2col-fullwidth-headline's
+            // "THE MORNING LEDGER" sits at x=100 and is tagged column 1, so the second column's
+            // edge reads as 99.7 pt against the 303 pt the page sets it at, and every line of the
+            // first column then straddles that "gutter" and is refused. One block out of thirty
+            // cannot move a median.
+            edge = new float[n + 1];
+            for (int c = 0; c < n; c++) {
+                java.util.List<Float> lefts = new ArrayList<>();
+                for (Object b : page.blocks) {
+                    if (!(b instanceof PdfToWord.Para)) continue;
+                    PdfToWord.Para q = (PdfToWord.Para) b;
+                    if (q.column != c || q.left <= 0f) continue;
+                    lefts.add(q.left);
                 }
-                int want = full ? 1 : page.columns;
-                if (want != curCols) {
-                    sb.append("<w:p><w:pPr><w:sectPr>")
-                      .append(sectPrXml(pw, ph, curCols, secGap))
-                      .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
-                    curCols = want;
-                    ctx.lastBaseline = -1f;
-                    ctx.newPage = false;
-                    // flowTw is NOT reset here. A continuous section break starts a new column on
-                    // the SAME sheet, so the page's budget is still the page's budget; resetting
-                    // it made the guard start again halfway down the page, which is how a page
-                    // measured at 842 pt could still be written at 844.
+                if (lefts.isEmpty()) return false;
+                java.util.Collections.sort(lefts);
+                edge[c] = lefts.get(lefts.size() / 2);
+                if (c > 0 && edge[c] <= edge[c - 1] + 1f) return false;
+            }
+            if (edge[n - 1] >= pw - 1f) return false;
+            edge[n] = pw;
+        }
+        if (n < 2) return false;
+        float gutter = edge[1];
+
+        // Where each block belongs: a column index, -1 for a block drawn across the gutter, and
+        // -2 for a block that is positioned rather than flowed (a picture, a drawn shape).
+        //
+        // The extent comes from the block's own LINE BOXES, not from the paragraph's left/right.
+        // The column pass widens a paragraph that straddles a band cut: 62's "For the ayacutdars
+        // of Halagere, Yediyur and seven other" reports right = 526 pt although the page drew it
+        // to 281 pt, and on the paragraph's own numbers it reads as a full-width headline. It
+        // was that misreading that made the old code break the page into six sections.
+        int nb = page.blocks.size();
+        int[] home = new int[nb];
+        for (int i = 0; i < nb; i++) {
+            Object b = page.blocks.get(i);
+            float l = 0f, r = 0f;
+            boolean known = false;
+            if (b instanceof PdfToWord.Para) {
+                PdfToWord.Para q = (PdfToWord.Para) b;
+                l = Float.MAX_VALUE;
+                r = -Float.MAX_VALUE;
+                for (PdfToWord.Box bx : q.boxes) {
+                    if (bx.runs.isEmpty()) continue;
+                    l = Math.min(l, bx.x);
+                    r = Math.max(r, bx.right);
+                    known = true;
+                }
+                if (!known && q.right > q.left) {
+                    l = q.left;
+                    r = q.right;
+                    known = true;
                 }
+            } else if (b instanceof PdfToWord.Table) {
+                PdfToWord.Table q = (PdfToWord.Table) b;
+                l = q.left;
+                r = q.right;
+                known = r > l;
             }
-            if (block instanceof PdfToWord.Para) {
-                para(sb, (PdfToWord.Para) block, ctx);
-            } else if (block instanceof PdfToWord.Table) {
-                table(sb, (PdfToWord.Table) block, ctx);
-            } else if (block instanceof Picture) {
-                picture(sb, (Picture) block, ctx);
-            } else if (block instanceof Shape) {
-                if (!((Shape) block).consumed) shape(sb, (Shape) block, ctx);
+            if (!known) {
+                home[i] = -2;
+            } else if (l < gutter - 1f && r > gutter + 1f) {
+                home[i] = -1;
+            } else {
+                int c = 0;
+                while (c + 1 < n && l >= edge[c + 1] - 1f) c++;
+                home[i] = c;
             }
         }
-        if (page.columns > 1 && curCols != page.columns) {
-            sb.append("<w:p><w:pPr><w:sectPr>")
-              .append(sectPrXml(pw, ph, curCols, secGap))
-              .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
+
+        // The band the columns occupy, vertically: the baselines on which TWO columns are both
+        // set. That is what a column is - the two of them standing side by side - and it is the
+        // only test that tells the columns from header furniture that merely sits at a column's
+        // x. brochure-3col-with-sidebar-box's "Edition 2026" starts at the third column's edge and
+        // annual-review-2col-uneven-columns' 6 pt "K" is a drop cap in the first, and both are
+        // ALONE on their baseline, on the masthead's own lines; counting either as column
+        // content drags the band's top up over the masthead, and the masthead then reads as
+        // full-width text inside the columns and the page is refused.
+        float[] bTop = new float[nb];
+        int[] bMask = new int[nb];
+        for (int i = 0; i < nb; i++) {
+            Object b = page.blocks.get(i);
+            bTop[i] = blockTop(b);
+            bMask[i] = 0;
+            if (b instanceof PdfToWord.Para) {
+                for (PdfToWord.Box z : ((PdfToWord.Para) b).boxes) {
+                    if (z.runs.isEmpty() || z.right <= z.x) continue;
+                    int c = columnAt(z.x, edge, n);
+                    if (c >= 0) bMask[i] |= 1 << c;
+                }
+            }
+        }
+        java.util.List<Float> shared = new ArrayList<>();
+        for (int i = 0; i < nb; i++) {
+            if (bMask[i] == 0 || bTop[i] < 0f) continue;
+            int m = 0;
+            for (int j = 0; j < nb; j++) {
+                if (bMask[j] == 0 || bTop[j] < 0f) continue;
+                if (Math.abs(bTop[j] - bTop[i]) <= 3f) m |= bMask[j];
+            }
+            if (Integer.bitCount(m) >= 2) shared.add(bTop[i]);
+        }
+        if (shared.isEmpty()) {
+            // A page whose columns do not share a baseline - a newspaper whose two columns are
+            // set on their own leading - still has a band: the extent of the blocks that are in
+            // a column. A full-width element drawn inside it will be refused below, which is the
+            // honest answer for those pages.
+            for (int i = 0; i < nb; i++) {
+                if (home[i] < 0 || bTop[i] < 0f) continue;
+                shared.add(bTop[i]);
+            }
+        }
+        if (shared.isEmpty()) return false;
+        java.util.Collections.sort(shared);
+        // The band is the longest RUN of shared baselines. A single shared line is not columns:
+        // a brochure's header puts its title at the first column's x and its edition line at the
+        // third's, and they sit on one baseline 65 pt above the body. Two columns are a run of
+        // shared baselines, one line apart; a lone one is furniture.
+        float colTop = shared.get(0);
+        int runBest = 1, runCur = 1;
+        float runStart = shared.get(0);
+        for (int i = 1; i < shared.size(); i++) {
+            float gap = shared.get(i) - shared.get(i - 1);
+            if (gap <= 40f) {
+                runCur++;
+            } else {
+                runCur = 1;
+                runStart = shared.get(i);
+            }
+            if (runCur > runBest) { runBest = runCur; colTop = runStart; }
+        }
+        float colBottom = -Float.MAX_VALUE;
+        for (int i = 0; i < nb; i++) {
+            boolean inCells = home[i] >= 0
+                    || (home[i] == -1 && splitColumns(page.blocks.get(i), edge, n) != null);
+            if (!inCells || bTop[i] < colTop - 3f) continue;
+            colBottom = Math.max(colBottom, blockBottom(page.blocks.get(i)));
+        }
+        // A page whose bands the column pass detected but whose prose never sits in them - a
+        // page of full-width lines that a vertical gutter on a form mis-tagged - is not a column
+        // page at all.
+        if (colBottom <= colTop) return false;
+
+        // Everything above the band is a band of its own, everything below is another, and what
+        // is left between them has to be column content. That is the shape a table can describe:
+        // a full-width band, then the columns, then a full-width band.
+        //
+        // A full-width block drawn INSIDE the band is the shape it cannot: a newspaper whose
+        // headline and byline sit between column fragments. Forcing that into a table both moves
+        // its text out of the columns and repeats it, so the page is written as an ordinary
+        // single-column flow instead - one page with a correct order beats one page with a
+        // scrambled one.
+        float tol = 2f;
+        java.util.TreeSet<Integer> used = new java.util.TreeSet<>();
+        @SuppressWarnings("unchecked")
+        java.util.List<Object>[] cells = new java.util.List[n];
+        for (int c = 0; c < n; c++) cells[c] = new ArrayList<>();
+        java.util.List<Object> before = new ArrayList<>();
+        java.util.List<Object> after = new ArrayList<>();
+        for (int i = 0; i < nb; i++) {
+            Object b = page.blocks.get(i);
+            float t = blockTop(b), bt = blockBottom(b);
+            if (home[i] == -2 || t < 0f || bt <= 0f) {
+                // Positioned rather than flowed - a picture or a drawn shape. It carries its own
+                // x and y, so it goes after the table and lands where the page put it.
+                after.add(b);
+                continue;
+            }
+            if (bt <= colTop + tol) { before.add(b); continue; }
+            if (t >= colBottom - tol) { after.add(b); continue; }
+            if (home[i] >= 0) {
+                // The cell's own edge is the column's edge, so the indent inside it is measured
+                // from that edge (bandLeftTw). Take the column from the geometry just computed
+                // rather than from the tag the column pass left on the paragraph, so the two
+                // cannot disagree about which edge to subtract.
+                if (b instanceof PdfToWord.Para) ((PdfToWord.Para) b).column = home[i];
+                cells[home[i]].add(b);
+                used.add(home[i]);
+                continue;
+            }
+            // A block drawn across the gutter is usually a masthead, a headline or a running
+            // footer - one line that really does run the width of the paper. But the column pass
+            // also cuts LINES at the gutter and keeps both halves on one baseline, so a "row" of
+            // two boxes can hold the bottom of the left column's line and the top of the right
+            // column's, and its extent then reads as full width when it is nothing of the kind.
+            // 62's "For the ayacutdars of Halagere, Yediyur and seven other" is one of those:
+            // its second box is the right column's "The forum has requested the deputy
+            // commissioner to take up". Such a block belongs to two cells, not to a band, so it
+            // is split by box.
+            int[] parts = splitColumns(b, edge, n);
+            if (parts != null) {
+                PdfToWord.Para q = (PdfToWord.Para) b;
+                for (int k = 0; k < q.boxes.size(); k++) {
+                    cells[parts[k]].add(oneBoxPara(q, q.boxes.get(k), parts[k]));
+                    used.add(parts[k]);
+                }
+                continue;
+            }
+            return false;
+        }
+        // One cell holding everything is not a column page either: it is a single flow whose
+        // lines happened to be tagged with bands. Checked before anything is written, so a
+        // refusal leaves the caller's flow untouched.
+        if (used.size() < 2) return false;
+
+        // The bands are written in the order the page drew them, top to bottom.
+        //
+        // Not in block order: the block pass orders a page by column and then by y, so a
+        // decorative initial can come before a masthead that sits ABOVE it - annual-review's "K"
+        // drop cap is block 0 and the letterhead is block 1, though the letterhead is 8 pt
+        // higher. A flow cannot put the second paragraph above the first, so the letterhead got
+        // no space before it and the whole page below it moved down by the drop cap's height.
+        sortByTop(before);
+        sortByTop(after);
+        for (Object b : before) emitBlock(sb, b, ctx);
+
+        // The table's grid: each column at the page's own edges, the last one running to the
+        // paper's edge. The cell margins are zero, so a cell's text edge IS the column's edge -
+        // which is what bandLeftTw() subtracts from every indent inside it.
+        int[] gridTw = new int[n];
+        int totalTw = 0;
+        for (int c = 0; c < n; c++) {
+            gridTw[c] = (int) Math.max(1L, Math.round((edge[c + 1] - edge[c]) * TWIPS_PER_PT));
+            totalTw += gridTw[c];
+        }
+        int indTw = (int) Math.max(0L, Math.round(edge[0] * TWIPS_PER_PT));
+
+        // The band's vertical extent, from the boxes the page drew.
+        float bandTop = Float.MAX_VALUE, bandBottom = -Float.MAX_VALUE;
+        for (int c = 0; c < n; c++) {
+            for (Object b : cells[c]) {
+                float t = blockTop(b), bt = blockBottom(b);
+                if (t < 0f || bt <= 0f) continue;
+                bandTop = Math.min(bandTop, t);
+                bandBottom = Math.max(bandBottom, bt);
+            }
+        }
+        if (bandBottom <= bandTop) return false;
+        // The row's top edge is where the FLOW has got to, not the band's first baseline: the
+        // table is placed after the paragraphs above it, so its top is the bottom of the last of
+        // them, and each cell's first line is then spaced from that edge by exactly the gap the
+        // page left. Measuring from the band's top instead dropped the gap between the deck and
+        // the columns, and put 62's left column 15 pt above the page's y.
+        //
+        // The band's top is the fallback for a page whose bands came out taller than the flow
+        // that precedes them - which cannot happen on a well-measured page, and must not put the
+        // table below the paper if it does.
+        float flowTopPt = ctx.flowTw / (float) TWIPS_PER_PT;
+        float rowTopPt = flowTopPt <= bandTop + 0.5f ? flowTopPt : bandTop;
+
+        // ONE ROW PER BAND, not one row for the whole page.
+        //
+        // A page can be set in columns more than once - a brochure whose three columns carry one
+        // block of prose and then a second block of specifications below it. The page reads
+        // band by band: all three columns of the first band, then all three of the second. A
+        // single row cannot say that; it says "all of column one, then all of column two", which
+        // is why 63_three_column_brochure still scored 33 % on reading order with its lines all
+        // in the right place. A row per band says it exactly, and the bands are where the page
+        // left a gap across EVERY column at once.
+        java.util.List<float[]> subs = new java.util.ArrayList<>();
+        {
+            java.util.List<float[]> iv = new ArrayList<>();
+            for (int c = 0; c < n; c++) {
+                for (Object b : cells[c]) {
+                    float t = blockTop(b), bt = blockBottom(b);
+                    if (t < 0f || bt <= 0f) continue;
+                    iv.add(new float[]{t, bt});
+                }
+            }
+            if (iv.isEmpty()) return false;
+            java.util.Collections.sort(iv, new java.util.Comparator<float[]>() {
+                public int compare(float[] a, float[] b) { return Float.compare(a[0], b[0]); }
+            });
+            float curT = iv.get(0)[0], curB = iv.get(0)[1];
+            for (int i = 1; i < iv.size(); i++) {
+                // A gap that no column fills is the end of a band. 30 pt is two or three lines of
+                // body type: less than that is the leading between two lines, or the slack under a
+                // short line, and not a band break. Measured on the six column documents: at 12 pt
+                // 62_two_col_newsletter_pull_quote splits at its pull quote and its reading order
+                // falls from 89 % to 75 %, while 63_three_column_brochure is unaffected; at 30 pt
+                // both hold (62 at 89 %, 63 at 96 %).
+                if (iv.get(i)[0] - curB > 30f) {
+                    subs.add(new float[]{curT, curB});
+                    curT = iv.get(i)[0];
+                    curB = iv.get(i)[1];
+                } else {
+                    curB = Math.max(curB, iv.get(i)[1]);
+                }
+            }
+            subs.add(new float[]{curT, curB});
+        }
+
+        String noBorder = "<w:top w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
+                + "<w:left w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
+                + "<w:bottom w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
+                + "<w:right w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
+                + "<w:insideH w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
+                + "<w:insideV w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>";
+
+        sb.append("<w:tbl><w:tblPr>")
+                .append("<w:tblW w:w=\"").append(totalTw).append("\" w:type=\"dxa\"/>")
+                .append("<w:tblInd w:w=\"").append(indTw).append("\" w:type=\"dxa\"/>")
+                .append("<w:tblBorders>").append(noBorder).append("</w:tblBorders>")
+                .append("<w:tblLayout w:type=\"fixed\"/>")
+                .append("<w:tblCellMar><w:top w:w=\"0\" w:type=\"dxa\"/>")
+                .append("<w:left w:w=\"0\" w:type=\"dxa\"/>")
+                .append("<w:bottom w:w=\"0\" w:type=\"dxa\"/>")
+                .append("<w:right w:w=\"0\" w:type=\"dxa\"/></w:tblCellMar>")
+                .append("</w:tblPr><w:tblGrid>");
+        for (int c = 0; c < n; c++) {
+            sb.append("<w:gridCol w:w=\"").append(gridTw[c]).append("\"/>");
+        }
+        sb.append("</w:tblGrid>");
+
+        float rowEndPt = rowTopPt;
+        for (int band = 0; band < subs.size(); band++) {
+            float subTop = subs.get(band)[0], subBottom = subs.get(band)[1];
+            // Each cell is written first and measured, because the row's height is the TALLEST
+            // cell's, not the band's.
+            StringBuilder[] cellXml = new StringBuilder[n];
+            int[] cellTw = new int[n];
+            for (int c = 0; c < n; c++) {
+                cellXml[c] = new StringBuilder(1 << 10);
+                // Each cell is a flow of its own, and it starts where the row starts: the first
+                // line's gap is measured from there, not from the line above the table.
+                ctx.inColumn = true;
+                ctx.cellLeftPt = edge[c];
+                ctx.cellRightPt = edge[c + 1];
+                ctx.afterTablePt = rowEndPt;
+                ctx.lastBaseline = -1f;
+                ctx.lastLinePt = 0f;
+                ctx.newPage = false;
+                ctx.positioned = false;
+                ctx.lastWasTable = false;
+                boolean any = false;
+                for (Object b : cells[c]) {
+                    float t = blockTop(b);
+                    if (t < subTop - 0.5f || t > subBottom + 0.5f) continue;
+                    emitBlock(cellXml[c], b, ctx);
+                    any = true;
+                }
+                // A cell must hold a block-level element, and a table must be followed by a
+                // paragraph inside its cell. A 1-twip line is the cheapest one there is.
+                if (!any) {
+                    cellXml[c].append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
+                            .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\"")
+                            .append(" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
+                            .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
+                }
+                ctx.inColumn = false;
+                cellTw[c] = flowTwOf(cellXml[c]);
+            }
+            int rowTw = 1;
+            for (int c = 0; c < n; c++) rowTw = Math.max(rowTw, cellTw[c]);
+            // hRule EXACT, at the height the cells really write.
+            //
+            // "atLeast" is the obvious choice and it is wrong here. LibreOffice then decides the
+            // row from its own model of the cell content, and on a page that already carries a
+            // band above the columns it sizes the row to the rest of the sheet:
+            // annual-review-2col-uneven-columns declared a 364 pt row and got one that ended at
+            // the foot of the paper, so the running footer - and the anchored shapes after it -
+            // were pushed onto a second, empty page. Measured: hRule="atLeast" -> 2 pages,
+            // hRule="exact" -> 1 page, all 41 lines present.
+            //
+            // Exact is safe because every paragraph in a cell is written with w:lineRule="exact"
+            // and its own w:before, so the height of the cell's content IS this sum - the
+            // renderer has no line-box of its own to add to it.
+            sb.append("<w:tr><w:trPr><w:cantSplit/>")
+                    .append("<w:trHeight w:val=\"").append(rowTw)
+                    .append("\" w:hRule=\"exact\"/></w:trPr>");
+            for (int c = 0; c < n; c++) {
+                sb.append("<w:tc><w:tcPr><w:tcW w:w=\"").append(gridTw[c])
+                        .append("\" w:type=\"dxa\"/><w:vAlign w:val=\"top\"/></w:tcPr>")
+                        .append(cellXml[c]).append("</w:tc>");
+            }
+            sb.append("</w:tr>");
+            rowEndPt = rowEndPt + rowTw / (float) TWIPS_PER_PT;
+        }
+        sb.append("</w:tbl>");
+
+        // Everything after the columns - the running footer, and any picture or shape drawn on
+        // the page - continues the flow from the last row's real bottom edge.
+        ctx.afterTablePt = rowEndPt;
+        ctx.lastBaseline = -1f;
+        ctx.lastLinePt = 0f;
+        ctx.newPage = false;
+        ctx.positioned = false;
+        ctx.lastWasTable = false;
+        ctx.flowTw = Math.max(ctx.flowTw, (int) Math.round(rowEndPt * TWIPS_PER_PT));
+        for (Object b : after) emitBlock(sb, b, ctx);
+        return true;
+    }
+
+    /**
+     * The height a cell's own paragraphs occupy: every {@code w:before} plus every
+     * {@code w:line} in it.
+     *
+     * <p>{@link #spacingTw} deliberately ignores the spacing inside a table, because a row's
+     * height is carried by its {@code w:trHeight} and counting both would charge the page twice.
+     * That is the right rule for the PAGE and the wrong one for the ROW, whose height is exactly
+     * this sum for its tallest cell.
+     */
+    private static int flowTwOf(CharSequence xml) {
+        int sum = 0;
+        int i = 0;
+        while (i < xml.length()) {
+            if (startsWith(xml, BEFORE, i)) {
+                sum += digits(xml, i + BEFORE.length());
+                i += BEFORE.length();
+            } else if (startsWith(xml, LINE, i)) {
+                sum += digits(xml, i + LINE.length());
+                i += LINE.length();
+            } else {
+                i++;
+            }
+        }
+        return sum;
+    }
+
+    /** Orders a page's bands top to bottom, as the page drew them. */
+    private static void sortByTop(java.util.List<Object> blocks) {
+        java.util.Collections.sort(blocks, new java.util.Comparator<Object>() {
+            public int compare(Object a, Object b) {
+                float ta = blockTop(a), tb = blockTop(b);
+                if (ta < 0f) return tb < 0f ? 0 : 1;
+                if (tb < 0f) return -1;
+                return Float.compare(ta, tb);
+            }
+        });
+    }
+
+    /** Writes one of a page's blocks. */
+    private static void emitBlock(StringBuilder sb, Object block, Ctx ctx) {
+        if (block instanceof PdfToWord.Para) {
+            para(sb, (PdfToWord.Para) block, ctx);
+        } else if (block instanceof PdfToWord.Table) {
+            table(sb, (PdfToWord.Table) block, ctx);
+        } else if (block instanceof Picture) {
+            picture(sb, (Picture) block, ctx);
+        } else if (block instanceof Shape) {
+            if (!((Shape) block).consumed) shape(sb, (Shape) block, ctx);
         }
     }
 
@@ -806,21 +1539,31 @@ public final class DocxWriter {
     /** How many column bands this page's paragraphs occupy, and the widest gutter between them. */
     /** The left edge of the column a paragraph sits in, in twips, or 0 for a one-column page. */
     private static int bandLeftTw(Ctx ctx, int column) {
-        // Only a section that really is set in columns may subtract one. See Ctx.secCols: on a
-        // one-column section the paragraph's w:ind is measured from the page edge, so a
-        // column-relative indent has nothing to be relative to and lands the line at x=0.
-        if (ctx.secCols <= 1) return 0;
+        if (ctx.inColumn) return (int) Math.round(ctx.cellLeftPt * TWIPS_PER_PT);
+        // Only a layout-table CELL may subtract one. A cell's text edge IS its column's edge, so
+        // the indent inside it is measured from that edge and the page's own x has to come off.
+        // Outside a cell the paragraph's w:ind is measured from the page edge, so a
+        // column-relative indent has nothing to be relative to and lands the line at x=0 - which
+        // is what a form page did, whose vertical gutters give its field rows column 1, 2 and 3
+        // while nothing on the page is set in columns at all (401_trifold_brochure, 300.6 pt).
+        if (!ctx.inColumn) return 0;
         if (ctx.colLeft == null || ctx.colLeft.size() <= 1) return 0;
         Float left = ctx.colLeft.get(column);
         return left == null ? 0 : (int) Math.round(left * TWIPS_PER_PT);
     }
 
     private static int[] pageColumns(PdfToWord.Page page) {
-        // The decision is made in PdfToWord.proseColumns, from the page's UNSPLIT lines. It cannot
-        // be made here: asBands cuts a four-point slice out of every line at the gutter, so by the
-        // time a Para exists every band is half a page wide by construction and the "gutter"
-        // between them is 4-12 pt whatever the page really is.
-        if (page.columns > 1) return new int[]{page.columns, Math.round(page.columnGap)};
+        // The page's SECTION is always one column, whatever the page's own column count is.
+        //
+        // A page set in newspaper columns is written as a layout table instead - see
+        // columnPage(). A section's columns are set by w:cols and a paragraph cannot carry a
+        // column count of its own, so the only way to hold a full-width band and two columns on
+        // one sheet is to make the columns the table's columns. That is also the only structure
+        // Google Docs renders on one page: it does not honour a continuous section break, and
+        // turns each one into a page break (see the note in pageBody).
+        //
+        // The page's own column count is still read by columnPage(), from page.columns - it is
+        // the DETECTION that matters, not the section.
         return new int[]{1, 0};
     }
 
@@ -1457,7 +2200,22 @@ public final class DocxWriter {
         float pitch = !ctx.newPage && ctx.lastBaseline >= 0f ? first.y - ctx.lastBaseline : -1f;
         float linePt = flowLinePt(pitch, size, ctx.lastLinePt);
         int beforeTw = 0;
-        if (ctx.newPage) {
+        if (ctx.afterTablePt >= 0f) {
+            // Same rule as flowFromBox: the row is placed against the table's measured edge
+            // rather than spaced from a baseline that the table replaced.
+            float topPt = first.y - LINE_BASE * linePt;
+            float edgeGap = topPt - ctx.afterTablePt;
+            ctx.afterTablePt = -1f;
+            if (edgeGap * TWIPS_PER_PT > gapCapTw(ctx)) {
+                // Too far below the table to be a gap - a running footer on the last line of
+                // the sheet. It is a position, so the row's fields are anchored where the page
+                // drew them rather than spaced from the table's bottom edge.
+                ctx.positioned = true;
+                for (PdfToWord.Box ab : cols) anchorBox(sb, p, ab, ctx);
+                return;
+            }
+            beforeTw = (int) Math.max(0L, Math.round(edgeGap * TWIPS_PER_PT));
+        } else if (ctx.newPage) {
             float topGap = first.y - LINE_BASE * linePt;
             if (topGap > 0f) {
                 beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
@@ -1760,7 +2518,18 @@ public final class DocxWriter {
         // The alignment is the position, so the indent must not double it. A line centred on the
         // paper keeps the whole text area; one centred inside a column gets the page's own extent
         // back as symmetric indents, so its centre is the centre the page used.
-        if (p.align == 1) {
+        if (ctx.inColumn) {
+            // Inside a column cell the cell IS the column: it is exactly as wide as the band the
+            // page drew, so a centred line is centred by w:jc against zero indents, and a
+            // right-aligned one is measured from the cell's right edge rather than the paper's.
+            if (p.align == 1) {
+                leftTw = 0;
+            } else if (p.align == 2) {
+                leftTw = 0;
+                rightTw = (int) Math.max(0L,
+                        Math.round((ctx.cellRightPt - b.right) * TWIPS_PER_PT));
+            }
+        } else if (p.align == 1) {
             float centre = (b.x + b.right) / 2f;
             if (Math.abs(centre - ctx.pageWidthPt / 2f) > 2f) {
                 rightTw = (int) Math.max(0L, Math.round((ctx.pageWidthPt - b.right) * TWIPS_PER_PT));
@@ -1776,7 +2545,29 @@ public final class DocxWriter {
         float pitch = !ctx.newPage && ctx.lastBaseline >= 0f ? b.y - ctx.lastBaseline : -1f;
         float linePt = flowLinePt(pitch, b.size, ctx.lastLinePt);
         int beforeTw = 0;
-        if (ctx.newPage) {
+        if (ctx.afterTablePt >= 0f) {
+            // The box above this one is a layout table - or the top of a column cell - and a
+            // table's height is decided by the renderer from its own line boxes, not by the
+            // page's baselines. So this line is placed against the measured edge: the gap is
+            // exactly what the page left between that edge and this line's box top.
+            float topPt = b.y - LINE_BASE * linePt;
+            float edgeGap = topPt - ctx.afterTablePt;
+            ctx.afterTablePt = -1f;
+            // Inside a cell a wide gap is SPACE, not a position: the cell is a fixed rectangle
+            // whose height is measured from exactly what it writes, so spending the gap keeps the
+            // line where the page put it and keeps it as text. Anchoring it instead made a text
+            // box - not editable in Google Docs - and on brochure-3col-with-sidebar-box, whose
+            // columns hold more than one band, that turned 24 lines into text boxes.
+            if (!ctx.inColumn && edgeGap * TWIPS_PER_PT > gapCapTw(ctx)) {
+                // A footer 340 pt below the columns is not a gap the flow may spend, it is a
+                // position - the rule the pitch branch below already applies. Spending what the
+                // cap allows instead put 62's running footer 246 pt above the foot of the page.
+                ctx.positioned = true;
+                anchorBox(sb, p, b, ctx);
+                return;
+            }
+            beforeTw = (int) Math.max(0L, Math.round(edgeGap * TWIPS_PER_PT));
+        } else if (ctx.newPage) {
             // The FIRST line on a page still has to land at its own y. The section carries zero
             // margins, so without this it starts at the very top of the sheet: on file 21 every
             // line measured 46 pt high against the PDF, a constant offset with the pitch already
@@ -1802,7 +2593,9 @@ public final class DocxWriter {
                 // with it: on 331_pid_diagram the clamp landed the diagram's "CHILLED WATER"
                 // label 114 pt above the box that holds it. Anchoring the line at its own y is
                 // what the page did, and from here on the page is placed rather than flowed.
-                if (extra * TWIPS_PER_PT > gapCapTw(ctx)) {
+                // Same rule inside a cell: a gap between two bands of the same column is space
+                // the cell can hold, not a reason to float the line out of the text.
+                if (!ctx.inColumn && extra * TWIPS_PER_PT > gapCapTw(ctx)) {
                     ctx.positioned = true;
                     anchorBox(sb, p, b, ctx);
                     return;
diff --git a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
index 6aa9127..0788b8c 100644
--- a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
+++ b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
@@ -680,6 +680,26 @@ public final class PdfToWord {
                 starts.clear(); starts.addAll(ruleGutters);
             }
         }
+        // The page's column count is the number of bands the cut actually made, not the earlier
+        // proseColumns() estimate.
+        //
+        // proseColumns() runs at the top of this method, before any of the three gutter
+        // detectors below has finished - it clusters the raw lines' left edges and requires the
+        // bands to be near-equal in width, so it answers 1 for a page whose columns are uneven
+        // and for a page whose gutter is only visible to the glyph projection or to a vertical
+        // rule. `starts` is the list the cut is really made from (asBands), so it is the only
+        // honest answer to "how many columns is this page set in", and it is the one the writer
+        // needs: it groups the page's blocks back into the bands they were cut out of, so a
+        // count that disagrees with `starts` would put a block in the wrong cell.
+        //
+        // Capped at 4 because that is the widest newspaper grid the block pass is built for
+        // (proseColumns refuses more), and a page that needed five would be a table.
+        page.columns = starts.isEmpty() ? 1 : Math.min(4, starts.size() + 1);
+        if (page.columns > 1 && !starts.isEmpty()) {
+            float gLo = Float.MAX_VALUE;
+            for (int k = 1; k < starts.size(); k++) gLo = Math.min(gLo, starts.get(k) - starts.get(k - 1));
+            page.columnGap = gLo == Float.MAX_VALUE ? 0f : gLo;
+        }
         uprightIfPageIsUpsideDown(glyphs);
         List<Line> lines = toLines(glyphs, asBands(starts));
         List<Line> ring = new ArrayList<>();
```

---

## Appendix B — how to reproduce

```
git clone --depth 1 https://github.com/kavopdf/app W && cd W
bash tools/verify-engine.sh
CP=libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar:out
cd tools/engine-verify
javac -nowarn -cp "$CP" -d out ../../app/src/main/java/com/kavopdf/app/engine/*.java
javac -nowarn -cp "$CP" -d out ConvertAll.java
java -Xmx900m -Djava.awt.headless=true -Dp2w.assets=$PWD/libs/aar/assets \
     -cp "$CP" ConvertAll <corpusdir> <outdir>
python3 tools/p2w-bench/gate.py --corpus <corpusdir> --out <outdir> \
     --baseline tools/p2w-bench/base208.json --check
python3 tools/p2w-bench/verify_visual.py <source.pdf> <generated.docx>
```

The corpus is `pdf-to-word-test-corpus-v3.zip` + `p2w-batch-1.zip` + `p2w-all-groups.zip` from the
`corpus-v1` release, flattened into one directory (208 PDFs).
