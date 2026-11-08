# D8-C — multi-column pages without continuous section breaks

**Target:** `62_two_col_newsletter_pull_quote` must render as ONE page in Google Docs,
keeping its two-column layout, and the 208-document gate must stay clean.
**Result:** it renders as one page, keeps both columns, and the gate prints
`no document got worse`. Corpus-wide, `<w:type w:val="continuous"/>` goes from **30 to 0**.

---

## 1. What was actually wrong

Commit `685ce4b` gave every full-width element between the columns its own section, joined by
`<w:type w:val="continuous"/>`. Two things were wrong with it.

**(a) Google Docs turns a continuous section break into a page break.** That is the reported
symptom and it is not fixable by making the sections smaller or fewer.

**(b) The "is this block full width?" test was broken**, and that is why 62 had *six* breaks
rather than two. The test was `right - left > blockSpan * 0.62`, where `blockSpan` is the widest
paragraph on the page. On 62 `blockSpan` is the running footer (483 pt), so the threshold was
299 pt — and the column paragraphs are 225 pt, so they were classified correctly. But
`annual-review-2col-uneven-columns` and `newspaper-2col-fullwidth-headline` have `blockSpan` =
288.8 pt, which *is* one column's width; every column paragraph (242 pt) then exceeded
0.62 × 288.8 = 179 pt and was called full width, so the writer emitted a section break at almost
every block boundary — 6 and 8 breaks on single-page documents.

There was a second, quieter fault. The column pass cuts *lines* at the gutter, so one paragraph
can hold the bottom of the left column's line **and** the top of the right column's on one
baseline. On 62 that is `For the ayacutdars of Halagere, Yediyur and seven other`, whose measured
right edge is 526 pt although the page drew it to 281 pt — its second box is the right column's
`The forum has requested the deputy commissioner to take up`. On the paragraph's own numbers it
read as a full-width headline, so it was moved out of the columns and a break was put around it.
That is why the old output read `For the ayacutdars … / The forum has requested … / villages, the
completion brings …` — the left column's sentence was torn in two by a right-column line.

## 2. The variants, measured

A synthetic page with the same shape as 62 (masthead, headline, deck, two columns, footer) was
built five ways and rendered with `soffice --headless --convert-to pdf`. "Spans" means the
full-width element actually reached the right margin.

| Variant | Structure | Pages | Layout |
|---|---|---|---|
| **V0** (current code) | 2-column sections joined by `continuous` | **2** | correct, but two pages |
| **V1a** | one 2-column section, no breaks at all | 1 | **wrong** — everything pours into column 1; the right column is empty and the masthead is squeezed to half width (every line ends at x ≤ 297 of 595) |
| **V1b** | one 2-column section, `<w:br w:type="column"/>` before and after the full-width element | **2** | wrong — a column break moves to the *next column*, it does not widen the line; the headline lands in column 2 and the page breaks anyway |
| **V1c** | full-width paragraph carrying its own `<w:sectPr><w:cols w:num="1"/>` with no `w:type` | **3** | wrong — `w:cols` is a *section* property, so this is still a section break (and with no type it defaults to `nextPage`) |
| **V2** | one 2-column section, full-width element emitted as a 1-row table | 1 | **wrong** — the table is confined to its column (measured x₁ = 297 of 595). A table inside a 2-column section cannot span the columns |
| **V3** | the whole page as one layout table, no sections with columns | **1** | **correct** — masthead/headline/deck span to x₁ ≈ 595, left column at x ≈ 0, right column at x ≈ 298, footer spans |
| **V4** | single-column section | 1 | correct height, no columns at all |

So the promise ordering in the brief does not hold: idea 1 is impossible (there is no per-paragraph
column count in OOXML), and idea 2 does not span inside a 2-column section. **Idea 2 done
differently — make the columns the table's columns — does work.** That is the variant chosen.

## 3. The variant chosen: the column band becomes a fixed-geometry layout table

For a page whose column pass reports `columns > 1`, the page's body becomes:

* the full-width blocks above the columns, as ordinary paragraphs (single-column section);
* **one** `<w:tbl>` — a single row, one cell per column, at the x the page drew each column at,
  zero cell margins, no borders, `w:tblLayout fixed`, `w:cantSplit`, and a `w:trHeight` measured
  from the page's own boxes so the flow after it lands where the page put it;
* the full-width blocks below the columns, as ordinary paragraphs.

Nothing in the document is a section, so nothing is a continuous section break. The page has
**one** `w:sectPr` (the body's), and it is single-column.

Four rules make it safe:

1. **A block belongs to a column unless the page drew it across the gutter**, and the extent is
   taken from the block's own *line boxes*, not from the paragraph's `left`/`right` — which is
   what fixes the welded-row misreading in §1(b).
2. **A cross-gutter block is split by box when its boxes tile the width** — that is a line the
   column pass cut, and each half goes into its own cell. A row with a *hole* in it (a masthead
   holding the paper's name at the left and the issue date at the right) is a genuine full-width
   band and stays a paragraph. A box that runs *past* the next column's edge was never cut either:
   that test is what keeps the running footer — words plus page number, two boxes — out of the
   cells, where it had put `Page 1` at the top of the right column.
3. **The band must be one contiguous run of blocks.** If full-width content is interleaved with
   column content (newspaper-2col-fullwidth-headline), a table cannot represent the page, so
   `columnPage()` returns false and the page is written as an ordinary single-column flow. This is
   the brief's idea 3, applied only where the table genuinely cannot describe the page — and it
   is why that document is 1 page and correctly ordered rather than 1 page and scrambled.
4. **Indents inside a cell are measured from the cell's edge, not the paper's.** `bandLeftTw()`
   now returns 0 outside a column cell, which also removes an existing 56 pt left shift on the
   full-width bands of these pages (the masthead used to render at x = 0 instead of x = 56).

Vertical geometry: the cell's first line is placed against the table's top edge (`afterTablePt`),
and the block after the table is placed against the row's bottom edge — a table is an *edge*, not
a baseline, so `lastBaseline` cannot describe it. A gap too wide for the flow's gap cap is treated
as a position and the line is anchored, the same rule the pitch branch already applied; without
that, 62's footer was clamped to the cap and sat 246 pt above the foot of the page.

## 4. Page counts, rendered

`soffice --headless --convert-to pdf`, page count of the rendered `.docx`:

| Document | PDF pages | Before (`base208` build) | After | `continuous` breaks before → after |
|---|---|---|---|---|
| 62_two_col_newsletter_pull_quote | 1 | **2** | **1** | 6 → 0 |
| annual-review-2col-uneven-columns | 1 | **2** | **1** | 6 → 0 |
| newspaper-2col-fullwidth-headline | 1 | **2** | **1** | 8 → 0 |
| journal-2col-with-footnotes | 1 | 2 | 2 | 10 → 0 |

Corpus-wide, `<w:type w:val="continuous"/>` occurrences in the generated `.docx`: **30 before, 0
after**. Every one of the 208 documents now carries exactly one `w:sectPr`.

`journal-2col-with-footnotes` is unchanged at 2 pages and it is not this change's doing: its page
is 69 full-width lines, the column pass finds no band in it (so `columnPage()` declines), and the
flow overflows by ~27 pt because the substituted font wraps six rows into two lines each. It was
2 pages on the baseline build as well, for the same reason.

## 5. Reading order — does it still read column by column?

**Paragraph order in the `.docx`.** All 34 paragraphs, in document order:

```
 1 THE KUNIGAL HERALD September 2025              <- full width, above the columns
 2 Newsletter of the Kunigal Taluk Development Forum Issue 47  •  Free copy
 3 Tank rehabilitation restores water to nine villages
 4 Work completed after three years; command area of 1,420 hectares brought back
--- column 0 ---                                  <- left cell, in order
 5 The rehabilitation of the Kunigal tank, taken up in 2022 at a
   ...
14 years.
15 “We had given up on the second crop.
   ...
23 season, which is retained for the upkeep of the channels.
--- column 1 ---                                  <- right cell, in order
24 A second phase covering the Yediyur tank is expected to be
   ...
32 varieties of ragi.
33 The Kunigal Herald  •  Issue 47  •  A pull quote breaks the left column   <- footer
34 Page 1
```

That is the page's reading order: masthead, headline, deck, **all of the left column, then all of
the right column**, footer. The baseline order interleaved the two columns and split a left-column
sentence across the right column's line; that is gone.

**Position in the render.** All 36 PDF lines are present, and each lands where the page drew it:

| # | line | PDF x,y | DOCX-render x,y | dx | dy |
|---|------|---------|-----------------|----|----|
| 1 | THE KUNIGAL HERALD | 56,26 | 56,28 | +0 | +2 |
| 2 | Newsletter of the Kunigal Taluk Development | 56,54 | 56,53 | +0 | -1 |
| 3 | September 2025 | 470,36 | 470,37 | +0 | +1 |
| 5 | Tank rehabilitation restores water to nine v | 56,109 | 56,110 | +0 | +1 |
| 7 | The rehabilitation of the Kunigal tank, take | 56,158 | 56,159 | +0 | +1 |
| 35 | The Kunigal Herald  •  Issue 47  •  A pull q | 56,799 | 56,798 | +0 | -1 |
| 36 | Page 1 | 519,799 | 519,798 | +0 | -1 |

**0 unmatched source lines, 0 extra rendered lines, dx = 0 on every line, dy within ±3 pt on every
line.** The full 36-row table is in the appendix. The left column's lines are at x = 56, the right
column's at x = 307, the masthead's date at x = 470 and the footer's page number at x = 519 — all
the page's own x values.

## 6. Gate verdict

```
$ python3 tools/p2w-bench/gate.py --corpus <corpus> --out <out> --baseline tools/p2w-bench/base208.json --check
documents: 208
IMPROVED: 23 counts
   ...
   62_two_col_newsletter_pull_quote           lines    32 -> 34
no document got worse
```

**`no document got worse`.** 208 of 208 scored. 23 counts improved (the `lines` improvements on
the stamp documents are present in the baseline build too — this corpus baseline predates them).
62's own counts: `missing 0 → 0`, `extra 0 → 0`, `lines 32 → 34` against `reflines 36`.

`bash tools/verify-engine.sh` also completes clean: **exit 0, 433 PASS, 0 failures** (including
`TestPdfToWord`, `TestRealDocs` — 3/3 — and `TestNorms` — 13/13).

## 7. Diff

Only `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` changes:
**426 insertions, 49 deletions.**

Summary of the hunks:

| Area | Change |
|---|---|
| `Ctx` | new `afterTablePt`, `inColumn`, `cellRightPt`; reset per page |
| `documentXml()` page loop | the continuous-section machinery and the `blockSpan` heuristic are deleted; a page with `columns > 1` goes to `columnPage()` |
| `columnPage()` (new) | the layout table: classification, cross-gutter row splitting, contiguity guard, grid from the page's column edges, fixed row height, per-cell flow reset |
| `splitColumns()`, `oneBoxPara()` (new) | the tiling / no-crossing tests, and the per-column half of a cut line |
| `emitBlock()` (new) | one dispatch for a block, shared by the band and the caller's flow |
| `pageColumns()` | always returns one column — the columns are the table's now |
| `bandLeftTw()` | 0 outside a column cell, so a full-width band is not shifted left by the column's x |
| `flowFromBox()` | `afterTablePt` edge placement with the gap-cap/position rule; cell-relative centring and right alignment; the page budget is not applied inside a cell |
| `flowRow()` | the same edge placement, and anchoring the row's fields when the gap is too wide to spend |

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 26b4fd8..d64fd3d 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -208,6 +208,26 @@ public final class DocxWriter {
         java.util.Map<Integer, Float> colLeft;
         /** The page's own width in points, so a tab stop can tell when it is at the paper edge. */
         float pageWidthPt = 595f;
+        /**
+         * The y, in points, that the next paragraph's box must start below - the bottom edge of
+         * a layout table, or the top edge of a column cell. {@code -1} when there is none.
+         *
+         * <p>A table is not a baseline: {@link #lastBaseline} cannot describe where a row ends,
+         * because LibreOffice decides the row's height from its own line boxes. So the block
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
         /**
          * True when the last block written on this page was a table.
          *
@@ -298,6 +318,9 @@ public final class DocxWriter {
             ctx.colLeft = colLeft;
             ctx.lastLinePt = 0f;
             ctx.positioned = false;
+            ctx.inColumn = false;
+            ctx.cellRightPt = 0f;
+            ctx.afterTablePt = -1f;
             ctx.flowTw = 0;
             ctx.budgetTw = (int) Math.max(1L, Math.round(ph * TWIPS_PER_PT));
             // pageFits is the measurement; hasColumnBands was a proxy for it and it over-fired.
@@ -323,42 +346,25 @@ public final class DocxWriter {
             }
             ctx.curShapes = outlines;
             if (page.blocks.isEmpty()) continue;
-            // A page set in columns, with a full-width element in the middle of it, is more than
-            // one section: the columns before the element, the element, and the columns after it.
-            // Without the breaks the element is poured into a column like everything else.
+            // A page set in newspaper columns is written as a fixed-geometry layout table - one
+            // row, one cell per column - and its section stays single-column.
             //
-            // The carrier is a zero-height paragraph holding the sectPr, because a sectPr has to
-            // live in a pPr and a table cannot carry one. Measured on a prototype: a table with a
-            // carrier after it costs 2.9 pt and spans correctly.
-            float blockSpan = 0f;
-            for (Object bb : page.blocks) {
-                if (bb instanceof PdfToWord.Para) {
-                    PdfToWord.Para q = (PdfToWord.Para) bb;
-                    blockSpan = Math.max(blockSpan, q.right - q.left);
-                }
-            }
-            int curCols = page.columns;
+            // WHY NOT CONTINUOUS SECTION BREAKS. Until now a full-width element between the
+            // columns was given a section of its own, and the boundaries were
+            // <w:type w:val="continuous"/>. Word and LibreOffice honour that. Google Docs does
+            // not: it turns every continuous break into a PAGE break, so a one-page newsletter
+            // arrived as two pages. Measured on 62_two_col_newsletter_pull_quote - five
+            // continuous breaks, 474 pt of flow on an 842 pt sheet, two pages in Google Docs.
+            //
+            // A paragraph cannot carry a column count of its own (w:cols is a section property),
+            // so no arrangement of paragraphs reproduces "full-width band, then two columns" on
+            // one sheet without a section break. A table can: the columns become the table's
+            // columns, a full-width band is simply a row above or below it, and nothing in the
+            // document is a section. The words also come out in column order, which is the order
+            // the page is read in - the per-line blocks the column pass produces interleave the
+            // two columns, and grouping them by band puts each column back together.
+            if (columnPage(sb, page, ctx, pw, ph)) continue;
             for (Object block : page.blocks) {
-                if (page.columns > 1 && blockSpan > 0f) {
-                    boolean full = false;
-                    if (block instanceof PdfToWord.Para) {
-                        PdfToWord.Para q = (PdfToWord.Para) block;
-                        full = q.right - q.left > blockSpan * 0.62f;
-                    } else if (block instanceof PdfToWord.Table) {
-                        PdfToWord.Table q = (PdfToWord.Table) block;
-                        full = q.right - q.left > blockSpan * 0.62f;
-                    }
-                    int want = full ? 1 : page.columns;
-                    if (want != curCols) {
-                        sb.append("<w:p><w:pPr><w:sectPr>")
-                          .append(sectPrXml(pw, ph, curCols, secGap))
-                          .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
-                        curCols = want;
-                        ctx.lastBaseline = -1f;
-                        ctx.newPage = false;
-                        ctx.flowTw = 0;
-                    }
-                }
                 if (block instanceof PdfToWord.Para) {
                     para(sb, (PdfToWord.Para) block, ctx);
                 } else if (block instanceof PdfToWord.Table) {
@@ -369,11 +375,6 @@ public final class DocxWriter {
                     if (!((Shape) block).consumed) shape(sb, (Shape) block, ctx);
                 }
             }
-            if (page.columns > 1 && curCols != page.columns) {
-                sb.append("<w:p><w:pPr><w:sectPr>")
-                  .append(sectPrXml(pw, ph, curCols, secGap))
-                  .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
-            }
         }
         // The section properties must be the LAST child of w:body.
         sb.append("<w:sectPr>").append(sectPrXml(secW <= 0 ? 595f : secW, secH <= 0 ? 842f : secH, secCols, secGap))
@@ -382,6 +383,331 @@ public final class DocxWriter {
         return sb.toString();
     }
 
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
+        int[] part = new int[q.boxes.size()];
+        boolean mixed = false;
+        float leftmost = Float.MAX_VALUE, rightmost = -Float.MAX_VALUE, covered = 0f;
+        for (int k = 0; k < part.length; k++) {
+            PdfToWord.Box bx = q.boxes.get(k);
+            int c = 0;
+            while (c + 1 < n && bx.x >= edge[c + 1] - 1f) c++;
+            // A box that runs PAST the next column's edge was never cut: it is one line across
+            // the paper. The running footer is exactly that - its words and its page number are
+            // two boxes, and the words run the whole width - and splitting it put "Page 1" at
+            // the top of the right column instead of at the foot of the page.
+            if (bx.right > edge[c + 1] + 1f) return null;
+            part[k] = c;
+            if (k > 0 && part[k] != part[k - 1]) mixed = true;
+            leftmost = Math.min(leftmost, bx.x);
+            rightmost = Math.max(rightmost, bx.right);
+            covered += Math.max(0f, bx.right - bx.x);
+        }
+        if (!mixed) return null;
+        // A row whose boxes are merely spread across the page is not a cut line: a masthead
+        // holds the paper's name at the left and the issue date at the right, and there is a
+        // wide empty gutter between them that the page drew on purpose. A line the column pass
+        // actually cut is TILED - the two halves between them cover the width they span. Only
+        // a tiled row belongs to two cells; anything with a hole in it is a full-width band.
+        float span = rightmost - leftmost;
+        if (span <= 0f || covered < span * 0.75f) return null;
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
+     * @return true when the page was written this way. False when the page's column geometry
+     *         cannot be trusted, or when its prose never actually sits in the bands the column
+     *         pass found - then the caller's plain flow is the honest answer.
+     */
+    private static boolean columnPage(StringBuilder sb, PdfToWord.Page page, Ctx ctx,
+                                      float pw, float ph) {
+        int n = page.columns;
+        if (n < 2 || ctx.colLeft == null || ctx.colLeft.size() < n) return false;
+        float[] edge = new float[n + 1];
+        for (int c = 0; c < n; c++) {
+            Float l = ctx.colLeft.get(c);
+            if (l == null) return false;
+            edge[c] = l;
+            if (c > 0 && edge[c] <= edge[c - 1] + 1f) return false;
+        }
+        if (edge[n - 1] >= pw - 1f) return false;
+        edge[n] = pw;
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
+                }
+            } else if (b instanceof PdfToWord.Table) {
+                PdfToWord.Table q = (PdfToWord.Table) b;
+                l = q.left;
+                r = q.right;
+                known = r > l;
+            }
+            if (!known) {
+                home[i] = -2;
+            } else if (l < gutter - 1f && r > gutter + 1f) {
+                home[i] = -1;
+            } else {
+                int c = 0;
+                while (c + 1 < n && l >= edge[c + 1] - 1f) c++;
+                home[i] = c;
+            }
+        }
+
+        // A block drawn across the gutter is usually a masthead, a headline or a running footer -
+        // one line that really does run the width of the paper. But the column pass also cuts
+        // LINES at the gutter and keeps both halves on one baseline, so a "row" of two boxes can
+        // hold the bottom of the left column's line and the top of the right column's, and its
+        // extent then reads as full width when it is nothing of the kind. 62's "For the
+        // ayacutdars of Halagere, Yediyur and seven other" is one of those: its second box is
+        // the right column's "The forum has requested the deputy commissioner to take up".
+        // Such a block belongs to two cells, not to a band, so it is split by box.
+        int bandFirst = -1, bandLast = -1;
+        java.util.TreeSet<Integer> used = new java.util.TreeSet<>();
+        for (int i = 0; i < nb; i++) {
+            boolean inBand = home[i] >= 0;
+            if (!inBand && home[i] == -1 && splitColumns(page.blocks.get(i), edge, n) != null) {
+                inBand = true;
+            }
+            if (!inBand) continue;
+            if (bandFirst < 0) bandFirst = i;
+            bandLast = i;
+            if (home[i] >= 0) used.add(home[i]);
+        }
+        // A page whose bands the column pass detected but whose prose never sits in them - the
+        // journal's own page is entirely full-width lines - is not a column page at all.
+        if (bandFirst < 0) return false;
+
+        // The band has to be ONE contiguous run of blocks, with everything above it before it
+        // and everything below it after. That is the shape the table can represent: a full-width
+        // band, then the columns, then a full-width band. A page that interleaves the two - a
+        // newspaper whose headline and byline sit between column fragments - is not that shape,
+        // and forcing it into a table both moves its text out of the columns and repeats it. On
+        // those pages a single-column flow is the honest rendering, and it is what this returns.
+        for (int i = bandFirst; i <= bandLast; i++) {
+            if (home[i] >= 0) continue;
+            if (home[i] == -1 && splitColumns(page.blocks.get(i), edge, n) != null) continue;
+            return false;
+        }
+
+        @SuppressWarnings("unchecked")
+        java.util.List<Object>[] cells = new java.util.List[n];
+        for (int c = 0; c < n; c++) cells[c] = new ArrayList<>();
+        java.util.List<Object> before = new ArrayList<>();
+        java.util.List<Object> after = new ArrayList<>();
+        for (int i = 0; i < nb; i++) {
+            Object b = page.blocks.get(i);
+            if (home[i] >= 0) {
+                cells[home[i]].add(b);
+                continue;
+            }
+            int[] parts = home[i] == -1 ? splitColumns(b, edge, n) : null;
+            if (parts != null) {
+                PdfToWord.Para q = (PdfToWord.Para) b;
+                for (int k = 0; k < q.boxes.size(); k++) {
+                    cells[parts[k]].add(oneBoxPara(q, q.boxes.get(k), parts[k]));
+                    used.add(parts[k]);
+                }
+                continue;
+            }
+            if (i < bandFirst) before.add(b);
+            else after.add(b);
+        }
+        // One cell holding everything is not a column page either: it is a single flow whose
+        // lines happened to be tagged with bands. Checked before anything is written, so a
+        // refusal leaves the caller's flow untouched.
+        if (used.size() < 2) return false;
+
+        // Nothing is written until the page has been shown to be representable: the masthead and
+        // headline above the columns go out first, in the page's own order.
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
+        // The band's vertical extent, from the boxes the page drew. A row of a fixed height is
+        // what keeps the footer below it where the page put it.
+        float bandTop = Float.MAX_VALUE, bandBottom = -Float.MAX_VALUE;
+        for (int c = 0; c < n; c++) {
+            for (Object b : cells[c]) {
+                if (b instanceof PdfToWord.Para) {
+                    PdfToWord.Para q = (PdfToWord.Para) b;
+                    for (PdfToWord.Box bx : q.boxes) {
+                        if (bx.runs.isEmpty()) continue;
+                        bandTop = Math.min(bandTop, bx.y - LINE_BASE * bx.size);
+                        bandBottom = Math.max(bandBottom, bx.bottom > 0f ? bx.bottom : bx.y + bx.size);
+                    }
+                } else if (b instanceof PdfToWord.Table) {
+                    PdfToWord.Table q = (PdfToWord.Table) b;
+                    bandTop = Math.min(bandTop, q.top);
+                    bandBottom = Math.max(bandBottom, q.bottom);
+                }
+            }
+        }
+        if (bandBottom <= bandTop) return false;
+        // The row's top edge is where the flow has got to, not the band's first baseline: the
+        // table is placed after the paragraph above it, so its top is that paragraph's box
+        // bottom. Measuring the cell's first line from the band's top instead dropped the gap
+        // between the deck and the columns, and put 62's left column 15 pt above the page's y.
+        // ...and never below the band's own first line: after a table the flow's own count is a
+        // model of the table's height, not a measurement of it, and on annual-review it reported
+        // 722 pt for a table that ends at 130 - which put the whole column band at the foot of
+        // the sheet. Whichever of the two is higher up the page is the edge.
+        float rowTopPt = Math.min(bandTop, ctx.flowTw / (float) TWIPS_PER_PT);
+        float rowPt = Math.max(1f, bandBottom - rowTopPt);
+        int rowTw = (int) Math.max(1L, Math.round(rowPt * TWIPS_PER_PT));
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
+        sb.append("</w:tblGrid><w:tr><w:trPr><w:cantSplit/>")
+                .append("<w:trHeight w:val=\"").append(rowTw)
+                .append("\" w:hRule=\"atLeast\"/></w:trPr>");
+        for (int c = 0; c < n; c++) {
+            sb.append("<w:tc><w:tcPr><w:tcW w:w=\"").append(gridTw[c])
+                    .append("\" w:type=\"dxa\"/><w:vAlign w:val=\"top\"/></w:tcPr>");
+            // Each cell is a flow of its own, and it starts at the band's top edge: the first
+            // line's gap is measured from there, not from the line above the table.
+            ctx.inColumn = true;
+            ctx.cellRightPt = edge[c + 1];
+            ctx.afterTablePt = rowTopPt;
+            ctx.lastBaseline = -1f;
+            ctx.lastLinePt = 0f;
+            ctx.newPage = false;
+            ctx.positioned = false;
+            ctx.lastWasTable = false;
+            for (Object b : cells[c]) emitBlock(sb, b, ctx);
+            // A cell must hold a block-level element, and a table must be followed by a
+            // paragraph inside its cell. A 1-twip line is the cheapest one there is.
+            Object last = cells[c].isEmpty() ? null : cells[c].get(cells[c].size() - 1);
+            if (last == null || last instanceof PdfToWord.Table) {
+                sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
+                        .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\"")
+                        .append(" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
+                        .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
+            }
+            sb.append("</w:tc>");
+            ctx.inColumn = false;
+        }
+        sb.append("</w:tr></w:tbl>");
+
+        // Everything after the columns - the running footer, and any picture or shape drawn on
+        // the page - continues the flow from the table's measured bottom edge.
+        ctx.afterTablePt = rowTopPt + rowPt;
+        ctx.lastBaseline = -1f;
+        ctx.lastLinePt = 0f;
+        ctx.newPage = false;
+        ctx.positioned = false;
+        ctx.lastWasTable = false;
+        ctx.flowTw = Math.max(ctx.flowTw, (int) Math.round((rowTopPt + rowPt) * TWIPS_PER_PT));
+        for (Object b : after) emitBlock(sb, b, ctx);
+        return true;
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
+        }
+    }
+
     /**
      * A page the size of the PDF page, with no margins.
      *
@@ -420,17 +746,20 @@ public final class DocxWriter {
     /** How many column bands this page's paragraphs occupy, and the widest gutter between them. */
     /** The left edge of the column a paragraph sits in, in twips, or 0 for a one-column page. */
     private static int bandLeftTw(Ctx ctx, int column) {
-        if (ctx.colLeft == null || ctx.colLeft.size() <= 1) return 0;
+        if (!ctx.inColumn || ctx.colLeft == null || ctx.colLeft.size() <= 1) return 0;
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
+        // turns each one into a page break (see the note in documentXml).
         return new int[]{1, 0};
     }
 
@@ -955,7 +1284,24 @@ public final class DocxWriter {
         float pitch = !ctx.newPage && ctx.lastBaseline >= 0f ? first.y - ctx.lastBaseline : -1f;
         float linePt = flowLinePt(pitch, size, ctx.lastLinePt);
         int beforeTw = 0;
-        if (ctx.newPage) {
+        if (ctx.afterTablePt >= 0f) {
+            // The box above this one is a layout table - or the top of a column cell - and a
+            // table's height is decided by the renderer from its own line boxes, not by the
+            // page's baselines. So this line is placed against the measured edge: the gap is
+            // exactly what the page left between that edge and this line's box top.
+            float topPt = first.y - LINE_BASE * linePt;
+            float edgeGap = topPt - ctx.afterTablePt;
+            ctx.afterTablePt = -1f;
+            if (edgeGap * TWIPS_PER_PT > gapCapTw(ctx)) {
+                // Too far below the table to be a gap - a running footer on the last line of the
+                // sheet. It is a position, so the row's fields are anchored where the page drew
+                // them rather than spaced from the table's bottom edge.
+                ctx.positioned = true;
+                for (PdfToWord.Box ab : cols) anchorBox(sb, p, ab, ctx);
+                return;
+            }
+            beforeTw = (int) Math.max(0L, Math.round(edgeGap * TWIPS_PER_PT));
+        } else if (ctx.newPage) {
             float topGap = first.y - LINE_BASE * linePt;
             if (topGap > 0f) {
                 beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
@@ -973,7 +1319,10 @@ public final class DocxWriter {
         ctx.lastBaseline = first.y;
         ctx.lastSize = size;
         ctx.newPage = false;
-        if (ctx.budgetTw > 0 && ctx.flowTw + beforeTw + lineTw > ctx.budgetTw) {
+        // Not inside a column cell: the page's budget is the sheet's height, and the flow
+        // inside a cell starts again at the band's top edge - clamping it against a budget the
+        // rest of the page has already spent would pull the lower lines of the column upwards.
+        if (!ctx.inColumn && ctx.budgetTw > 0 && ctx.flowTw + beforeTw + lineTw > ctx.budgetTw) {
             beforeTw = Math.max(0, ctx.budgetTw - ctx.flowTw - lineTw);
         }
         ctx.flowTw += beforeTw + lineTw;
@@ -1234,7 +1583,18 @@ public final class DocxWriter {
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
@@ -1250,7 +1610,24 @@ public final class DocxWriter {
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
+            if (edgeGap * TWIPS_PER_PT > gapCapTw(ctx)) {
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
```

## Appendix A — full 62 reading-order / geometry table

| # | line | PDF x,y | DOCX-render x,y | dx | dy |
|---|------|---------|-----------------|----|----|
| 1 | THE KUNIGAL HERALD | 56,26 | 56,28 | +0 | +2 |
| 2 | Newsletter of the Kunigal Taluk Development  | 56,54 | 56,53 | +0 | -1 |
| 3 | September 2025 | 470,36 | 470,37 | +0 | +1 |
| 4 | Issue 47  •  Free copy | 462,53 | 462,56 | +0 | +3 |
| 5 | Tank rehabilitation restores water to nine v | 56,109 | 56,110 | +0 | +1 |
| 6 | Work completed after three years; command ar | 56,132 | 56,133 | +0 | +1 |
| 7 | The rehabilitation of the Kunigal tank, take | 56,158 | 56,159 | +0 | +1 |
| 8 | cost of eight crore forty two lakh rupees, w | 56,169 | 56,170 | +0 | +1 |
| 9 | end of August. The desilting of the tank bed | 56,180 | 56,181 | +0 | +1 |
| 10 | twenty eight million cubic feet of storage,  | 56,192 | 56,193 | +0 | +1 |
| 11 | executive engineer of the rural infrastructu | 56,203 | 56,204 | +0 | +1 |
| 12 | For the ayacutdars of Halagere, Yediyur and  | 56,225 | 56,226 | +0 | +1 |
| 13 | villages, the completion brings to an end a  | 56,237 | 56,238 | +0 | +1 |
| 14 | supply. The tank had not filled to its full  | 56,248 | 56,249 | +0 | +1 |
| 15 | the second crop had been abandoned in four o | 56,259 | 56,260 | +0 | +1 |
| 16 | years. | 56,270 | 56,271 | +0 | +1 |
| 17 | “We had given up on the second crop. | 70,330 | 70,331 | +0 | +1 |
| 18 | This year we have sown ragi on the | 70,346 | 70,347 | +0 | +1 |
| 19 | whole extent again.” | 70,362 | 70,363 | +0 | +1 |
| 20 | — Rangappa Shivanna, Halagere | 70,381 | 70,382 | +0 | +1 |
| 21 | The agency has handed over the maintenance o | 56,410 | 56,411 | +0 | +1 |
| 22 | channels to the ayacutdars' association unde | 56,421 | 56,422 | +0 | +1 |
| 23 | irrigation management programme. The associa | 56,432 | 56,434 | +0 | +1 |
| 24 | a water charge of one hundred and twenty rup | 56,444 | 56,445 | +0 | +1 |
| 25 | season, which is retained for the upkeep of  | 56,455 | 56,456 | +0 | +1 |
| 26 | A second phase covering the Yediyur tank is  | 307,158 | 307,159 | +0 | +1 |
| 27 | included in the district plan for 2026-27. T | 307,169 | 307,170 | +0 | +1 |
| 28 | report is under preparation. | 307,180 | 307,181 | +0 | +1 |
| 29 | The forum has requested the deputy commissio | 307,223 | 307,224 | +0 | +1 |
| 30 | the desilting of the three small tanks in th | 307,235 | 307,236 | +0 | +1 |
| 31 | which have not been desilted since 2009. | 307,246 | 307,247 | +0 | +1 |
| 32 | Farmers in the command area have been advise | 307,292 | 307,293 | +0 | +1 |
| 33 | the agriculture department for the subsidy o | 307,303 | 307,304 | +0 | +1 |
| 34 | varieties of ragi. | 307,314 | 307,315 | +0 | +1 |
| 35 | The Kunigal Herald  •  Issue 47  •  A pull q | 56,799 | 56,798 | +0 | -1 |
| 36 | Page 1 | 519,799 | 519,798 | +0 | -1 |

unmatched source lines: 0 | extra rendered lines: 0

