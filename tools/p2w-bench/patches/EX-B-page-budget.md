# EX-B — a hard page budget in `DocxWriter` (D-21)

Repo: `kavopdf/app` at `HEAD` (cloned fresh, `git log -1` in the build tree).
Patch: `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` only — 465 insertions,
58 deletions, no other file touched. The full diff is at the end of this report and also
saved as `EX-B-page-budget.patch`.

## 1. Which of the three I did

| option | verdict |
|---|---|
| **(1) deliberate page break when the next paragraph would pass the page height** | **implemented, but switched off by default** (`BREAK_WHEN_UNFITTABLE = false`) — measured, it costs gate counts and buys no reader-visible page |
| **(2) fill the page exactly instead of overrunning** | **this is what shipped**, generalised from a one-line clamp to a whole-page fit: the page is measured, then every box and gap on it is scaled by `budget / height` |
| **(3) move the bottom-of-page footer into a `w:footerReference`** | **investigated, not done.** The writer has no header/footer at all; and the gap it would recover is not what overflows the page (numbers in §8) |

The one thing I did **not** do is step (2) as literally described ("clamp the line height for
the remaining paragraphs to the space actually left"). Measured, that clamps exactly **one**
line per page — the fit guard fires once, leaves zero room, and every paragraph after it takes
the break path. On `table-of-contents-dot-leaders` the flow needs 907.8 pt on an 841.9 pt page
(66 pt over, spread over ~57 lines), so one clamped line cannot close it. What closes it is
the same idea applied to the whole page: measure the page, then scale all of it.

## 2. The mechanism

`documentXml` writes each page twice at most:

1. **Measure.** `pageBody(...)` writes the page in `measuring` mode: the page's own gaps, given
   up exactly as the old guard gave them up, but no line shortened and nothing broken. The
   height is then read off **the page's own XML** (`spacingTw`): every top-level `w:before` +
   `w:line` + every row's `w:trHeight`. Not off the writer's running total — a model that agrees
   with itself while the page overruns is the defect. Cell paragraphs and `w:txbxContent`
   paragraphs are excluded: a row already carries its height as `w:trHeight`, and a text box is
   placed at a y, not flowed. (Counting those is how a one-page stamp measures at 1277 pt on an
   842 pt page — see §4.)
2. **Fit.** If that height is more than the paper, the page is re-written with `ctx.squeeze =
   min(1, max(0.85, budget/height))`, corrected up to three times by what the pass really wrote
   (the corrections are not monotone — a table's rows stop shrinking at their type size while
   the prose around it keeps going — so the page kept is the **shortest one measured**, not the
   last one tried).
3. **Guard** (`fitPage`), per paragraph, in the order a page gives things up: the gap goes
   first; then the line's own box is shortened to the room left, never below the type's ascent
   (`LINE_BASE` of the em); and only then — with `BREAK_WHEN_UNFITTABLE` on — a deliberate
   `w:br w:type="page"`. With the flag off (the default) that last case keeps the old overrun.
4. **Rewind.** Writing a page has side effects (media list, `Shape.consumed`, id counters), so
   every one of them is undone between passes. Verified: the media/part layout of all 208
   `.docx` files is identical to the baseline build.

A page that already fits is written **once** and comes out byte-identical: **196 of the 208
documents have a `document.xml` identical to the baseline build**. The 12 that change are the
12 that were over their paper.

Conversion time over the 208 documents: 52 s → 67 s (+29 %), from the measuring pass.

## 3. The diff

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 26b4fd8..1834ec1 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -131,17 +131,238 @@ public final class DocxWriter {
      */
     private static final int GAP_CAP_SPEND_TW = 20000;
 
+    /**
+     * The most a page's flow may be compressed to make it fit the paper: 85 % of its measured
+     * height.
+     *
+     * <p>A page that has to lose more than a sixth of itself was not mis-measured by a sixth -
+     * its content really is taller than the sheet, which today means a page whose columns are
+     * stacked into one flow (D-08) or a table the model under-measures. Compressing those only
+     * makes a wrong layout smaller and illegible, so past this floor the flow keeps its own
+     * heights and the page overruns exactly as it did before this guard existed.
+     */
+    private static final float SQUEEZE_FLOOR = 0.85f;
+
+    /**
+     * Whether a page that cannot be squeezed to fit gets a deliberate page break instead of
+     * silently overrunning.
+     *
+     * <p>OFF, and that is a measured decision, not a default. Four pages in the 208 still come
+     * out taller than their paper after squeezing - {@code 350_question_paper},
+     * {@code itr-computation-with-slab-table}, {@code newsletter-3col-header-footer} and
+     * {@code product-catalogue-code-left-price-right}, which need 1.21, 1.09, 1.17 and 1.22
+     * times the paper's height because their columns are still stacked into one flow (D-08) or a
+     * slab table's rows cannot shrink below their own type. Turned ON, this flag breaks those
+     * pages deliberately: measured over the corpus, the pages left over the paper go from 4 to 3
+     * (the break cannot rescue a page whose overflow is a table that is already written) and the
+     * gate gains two "pages 1 -> 2" counts on documents whose render is two pages either way. A
+     * break a reader cannot see is not worth a regression the project measures, so the flag stays
+     * off and the four pages are reported instead of papered over.
+     */
+    private static final boolean BREAK_WHEN_UNFITTABLE = false;
+
+    /**
+     * Twips kept back from every page's budget, so the page's own measured height can never sit
+     * a twip above the paper.
+     *
+     * <p>The guard works in whole twips and rounds each attribute it writes; the paragraph
+     * carriers that hold an anchored picture or a text box add one twip each and are not part of
+     * the flow. Two twips is a tenth of a point - a fifth of a pixel at 200 dpi - and it is the
+     * difference between a page that ends at the paper's edge and a page whose measured sum is
+     * one twip past it, which the corpus check reads as an overflow.
+     */
+    private static final int PAGE_ROUNDING_TW = 2;
+
     /** The ceiling this page's gaps get - see {@link #GAP_CAP_SPEND_TW}. */
     private static int gapCapTw(Ctx ctx) {
         return ctx.spendGaps ? GAP_CAP_SPEND_TW : GAP_CAP_TW;
     }
 
+    /**
+     * Charges one paragraph against the page's budget, and says how much of it may be used.
+     *
+     * <p>The budget is the page's own height, because {@code w:before + w:line} summed down a
+     * page IS the height the flow occupies - the section has zero margins, so the text area and
+     * the paper are the same box. A sum larger than the paper is a second page: the reader's,
+     * not ours, and at a place the reader chooses. The guard this replaces zeroed
+     * {@code beforeTw} once the budget was spent and then went on adding {@code lineTw} for
+     * every paragraph after it, so it could slow the overrun but never stop it (D-21: a one-page
+     * PDF came back as two pages in Google Docs).
+     *
+     * <p>Three steps, in the order the page itself would give them up:
+     * <ol>
+     *   <li>the gap above the line goes first - white space is not content, and the old guard
+     *       already did this much;</li>
+     *   <li>then the line's own box is shortened to the room that is left, so the page ends
+     *       exactly where the paper does. The box is never taken below the ascent the type needs
+     *       to sit in ({@link #LINE_BASE} of the em), so the last line is not clipped and not
+     *       overlapped - and only one line per page is ever shortened, because a shortened line
+     *       leaves no room and the next paragraph takes the third step;</li>
+     *   <li>if not even that fits, the page is full and the caller writes a deliberate page
+     *       break. A break the writer places is a page the writer chose, at the last baseline
+     *       the page itself drew; the alternative is the renderer inventing one wherever its own
+     *       line model runs out.</li>
+     * </ol>
+     *
+     * @param beforeTw the gap the page drew above this line, in twips
+     * @param lineTw   the line's own box, in twips
+     * @param size     the line's font size, so the ascent floor is the type's own
+     * @return {@code {before, line}} in twips, or null when the page is full and must be broken
+     */
+    /**
+     * The height a written page occupies, read off its own XML: every {@code w:before} plus every
+     * {@code w:line} plus every row's {@code w:trHeight}.
+     *
+     * <p>This is the test the page has to pass - the flow's own before and line, summed down the
+     * page, must not exceed the paper - so it is measured on the page and not on the model that
+     * produced it. A model that agrees with itself while the page overruns is the defect this
+     * guard exists to catch.
+     */
+    private static final String BEFORE = "w:before=\"";
+    private static final String LINE = "w:line=\"";
+    private static final String TRHEIGHT = "w:trHeight w:val=\"";
+
+    private static int spacingTw(CharSequence xml) {
+        int sum = 0;
+        int depth = 0;              // inside a w:tbl
+        int i = 0;
+        int n = xml.length();
+        while (i < n) {
+            if (startsWith(xml, "<w:tbl>", i)) {
+                depth++;
+                i += 7;
+            } else if (startsWith(xml, "</w:tbl>", i)) {
+                if (depth > 0) depth--;
+                i += 8;
+            } else if (startsWith(xml, "<w:txbxContent>", i)) {
+                // A text box is placed at a y, not flowed, so its paragraphs are not the page's
+                // height. Counting them is how a one-page document measures at 1277 pt on an
+                // 842 pt page (D-21) - the stamp's own boxes are most of that number.
+                depth++;
+                i += 15;
+            } else if (startsWith(xml, "</w:txbxContent>", i)) {
+                if (depth > 0) depth--;
+                i += 16;
+            } else if (startsWith(xml, BEFORE, i) || startsWith(xml, LINE, i)) {
+                // A cell's line is not the page's height: the row it sits in already carries
+                // that height as its own w:trHeight, and counting both charges a table twice.
+                int j = i + (startsWith(xml, BEFORE, i) ? BEFORE.length() : LINE.length());
+                if (depth == 0) sum += digits(xml, j);
+                i = j;
+            } else if (startsWith(xml, TRHEIGHT, i)) {
+                sum += digits(xml, i + TRHEIGHT.length());
+                i += TRHEIGHT.length();
+            } else {
+                i++;
+            }
+        }
+        return sum;
+    }
+
+    /** The integer starting at {@code from}, or 0 when there is none. */
+    private static int digits(CharSequence xml, int from) {
+        int v = 0, i = from;
+        boolean any = false;
+        while (i < xml.length() && xml.charAt(i) >= '0' && xml.charAt(i) <= '9') {
+            v = v * 10 + (xml.charAt(i) - '0');
+            i++;
+            any = true;
+        }
+        return any ? v : 0;
+    }
+
+    /** Does {@code xml} hold {@code needle} at {@code at}? */
+    private static boolean startsWith(CharSequence xml, String needle, int at) {
+        if (at + needle.length() > xml.length()) return false;
+        for (int j = 0; j < needle.length(); j++) {
+            if (xml.charAt(at + j) != needle.charAt(j)) return false;
+        }
+        return true;
+    }
+
+    /** One twip value as the page will really write it, through the squeeze factor. */
+    private static int twScale(int tw, float squeeze) {
+        return squeeze == 1f ? tw : (int) Math.max(0L, Math.round(tw * squeeze));
+    }
+
+    private static int[] fitPage(Ctx ctx, int beforeTw, int lineTw, float size) {
+        if (ctx.measuring) {
+            // Measuring a page: the gap is given up exactly as the old guard gave it up once the
+            // budget was spent, but no line is shortened and nothing is broken - the answer this
+            // pass exists to produce is how tall the page really is.
+            int roomM = ctx.budgetTw - ctx.flowTw;
+            int gapM = Math.max(0, Math.min(beforeTw, roomM - lineTw));
+            ctx.flowTw += gapM + lineTw;
+            return new int[]{gapM, lineTw};
+        }
+        if (ctx.budgetTw <= 0) {
+            ctx.flowTw += beforeTw + lineTw;
+            return new int[]{beforeTw, lineTw};
+        }
+        int room = ctx.budgetTw - ctx.flowTw;
+        if (beforeTw + lineTw <= room) {
+            ctx.flowTw += beforeTw + lineTw;
+            return new int[]{beforeTw, lineTw};
+        }
+        // 1. the gap goes first.
+        int gap = Math.max(0, Math.min(beforeTw, room - lineTw));
+        room = ctx.budgetTw - ctx.flowTw - gap;
+        if (lineTw <= room) {
+            ctx.flowTw += gap + lineTw;
+            return new int[]{gap, lineTw};
+        }
+        // 2. the box is shortened to what is left, down to the ascent but no further.
+        int ascent = (int) Math.max(1L, Math.round(LINE_BASE * Math.max(4f, size) * TWIPS_PER_PT));
+        if (room >= ascent) {
+            ctx.flowTw = ctx.budgetTw;
+            ctx.fitted++;
+            return new int[]{0, room};
+        }
+        // 3. the page is full and cannot be squeezed any further. See
+        // BREAK_WHEN_UNFITTABLE: by default the line keeps its own height and the page overruns
+        // exactly as it did before this guard existed - the guard is not allowed to trade a
+        // reader-visible page for a bookkeeping one.
+        if (BREAK_WHEN_UNFITTABLE && ctx.flowTw > 0) return null;
+        ctx.flowTw += lineTw;
+        return new int[]{0, lineTw};
+    }
+
+    /**
+     * A deliberate page break, and the flow starts again at the top of the new sheet.
+     *
+     * <p>{@code w:br w:type="page"} is the same instruction a section break with
+     * {@code w:type w:val="nextPage"} gives, and it is what the writer already uses to end a
+     * page the PDF itself ended. The budget guard writes one only where the page is genuinely
+     * full, so the break lands on the last baseline the page drew rather than wherever the
+     * reader's own line model happens to run out.
+     *
+     * <p>The paragraph that carries the break is the same one-twip carrier the writer already
+     * uses for an empty page, so it adds no height of its own: a break paragraph with a real
+     * line height would be the very overflow this guard exists to prevent.
+     */
+    private static void breakPage(StringBuilder sb, Ctx ctx) {
+        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
+                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
+                .append("<w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr>")
+                .append("<w:r><w:br w:type=\"page\"/></w:r></w:p>");
+        ctx.brokePage++;
+        ctx.flowTw = 0;
+        ctx.newPage = true;
+        ctx.lastBaseline = -1f;
+        ctx.lastLinePt = 0f;
+        ctx.lastWasTable = false;
+    }
+
     private DocxWriter() {
     }
 
     public static void write(PdfToWord.Result result, File out) throws IOException {
         Ctx ctx = new Ctx();
         String documentXml = documentXml(result, ctx);
+        if (System.getProperty("p2w.debugFlow") != null) {
+            System.err.println("FLOWDOC " + out.getName() + " fitted=" + ctx.fitted
+                    + " broke=" + ctx.brokePage);
+        }
         String rels = documentRels(ctx.media);
         String contentTypes = contentTypes(ctx.media.size());
 
@@ -218,6 +439,24 @@ public final class DocxWriter {
          * gets no spacer - the page had no prose between them to leave a gap for.
          */
         boolean lastWasTable;
+        /** Paragraphs whose own box was shortened so the page ended exactly at the paper. */
+        int fitted;
+        /** Deliberate page breaks the budget guard had to write. */
+        int brokePage;
+        /** Pages written so far, so the debug trace can name the page it is talking about. */
+        int pageSeq;
+        /**
+         * How much of its measured height this page's flow may keep, 1 = all of it.
+         *
+         * <p>Set only for a page whose own flow is taller than the paper: every line box and
+         * every gap written for that page is multiplied by it, so the flow ends exactly where
+         * the paper does. The accounting that the budget guard does stays in the page's own
+         * units - the budget is divided by this factor instead - so the pitch solver keeps
+         * comparing boxes with boxes and does not chase its own scaling.
+         */
+        float squeeze = 1f;
+        /** True while a page is being measured rather than written for the reader. */
+        boolean measuring;
     }
 
     // ------------------------------------------------------------------ document
@@ -299,7 +538,7 @@ public final class DocxWriter {
             ctx.lastLinePt = 0f;
             ctx.positioned = false;
             ctx.flowTw = 0;
-            ctx.budgetTw = (int) Math.max(1L, Math.round(ph * TWIPS_PER_PT));
+            ctx.budgetTw = (int) Math.max(1L, Math.round(ph * TWIPS_PER_PT) - PAGE_ROUNDING_TW);
             // pageFits is the measurement; hasColumnBands was a proxy for it and it over-fired.
             // A form page has vertical gutters between its field columns, so the column pass
             // gives those rows column > 0 and the proxy read the page as set in columns. The
@@ -323,56 +562,103 @@ public final class DocxWriter {
             }
             ctx.curShapes = outlines;
             if (page.blocks.isEmpty()) continue;
-            // A page set in columns, with a full-width element in the middle of it, is more than
-            // one section: the columns before the element, the element, and the columns after it.
-            // Without the breaks the element is poured into a column like everything else.
+            // ---- the page's flow, measured before it is written ----
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
-            for (Object block : page.blocks) {
-                if (page.columns > 1 && blockSpan > 0f) {
-                    boolean full = false;
-                    if (block instanceof PdfToWord.Para) {
-                        PdfToWord.Para q = (PdfToWord.Para) block;
-                        full = q.right - q.left > blockSpan * 0.62f;
-                    } else if (block instanceof PdfToWord.Table) {
-                        PdfToWord.Table q = (PdfToWord.Table) block;
-                        full = q.right - q.left > blockSpan * 0.62f;
+            // The guard can only fill the page if it knows how much room the page needs BEFORE
+            // it starts giving room away: a line already written cannot be made shorter. So the
+            // page is written once in measuring mode - the page's own gaps, given up exactly as
+            // the old guard gave them up, but no line shortened and no break - and that pass is
+            // read for two numbers: the height the flow needs, and the height it actually
+            // occupies once written. When the second is more than the paper, the page is written
+            // again with every box and gap scaled by budget/height. A page that already fits is
+            // written once and comes out exactly as it did before this guard existed.
+            //
+            // The page is measured off its own XML, not off the writer's running total, because
+            // the running total is the writer's model of the page and this is the page: the
+            // carriers that hold an anchored picture or a text box add a twip each and are not
+            // charged to the flow, and a page must not overrun by the twips the model forgot.
+            //
+            // Both passes write through the same code and the same model objects, so every side
+            // effect of the first pass is undone before the second: the media list is truncated,
+            // an anchored shape marked consumed is un-marked, and the id counters are reset.
+            int pageBudgetTw = ctx.budgetTw;
+            java.util.List<Boolean> consumedMark = new ArrayList<>();
+            for (Shape sh : outlines) consumedMark.add(sh.consumed);
+            int mediaMark = ctx.media.size();
+            int shapeMark = ctx.shapeSeq, anchorMark = ctx.anchorCount, flowMark = ctx.flowCount;
+            int fittedMark = ctx.fitted, brokeMark = ctx.brokePage;
+            StringBuilder pg = new StringBuilder(1 << 12);
+
+            ctx.measuring = true;
+            pageBody(pg, page, ctx, pw, ph, secGap);
+            ctx.measuring = false;
+            int needTw = ctx.flowTw;
+            int writtenTw = spacingTw(pg);
+            // What the page carries that the flow is not charged for. Kept out of the budget the
+            // guard works to, so that the page's own w:before + w:line + w:trHeight is what
+            // ends at the paper's edge and not the model's idea of it.
+            int overheadTw = Math.max(0, writtenTw - ctx.flowTw);
+            float usedF = 1f;
+
+            if (writtenTw > pageBudgetTw) {
+                // budget/height first, then corrected by what the pass really wrote, because a
+                // squeezed page also gives up less of its own gap and the two do not scale quite
+                // alike. Each attempt is kept only if it is the best one: the corrections are not
+                // guaranteed to be monotone (a table whose rows are held at their type size stops
+                // shrinking while the prose around it keeps going), so the page that is used is
+                // the shortest one measured, never simply the last one tried.
+                String bestXml = null;
+                int bestWritten = writtenTw;
+                float f = Math.min(1f, Math.max(SQUEEZE_FLOOR, (float) pageBudgetTw / (float) needTw));
+                for (int attempt = 0; attempt < 3; attempt++) {
+                    ctx.media.subList(mediaMark, ctx.media.size()).clear();
+                    ctx.shapeSeq = shapeMark;
+                    ctx.anchorCount = anchorMark;
+                    ctx.flowCount = flowMark;
+                    ctx.fitted = fittedMark;
+                    ctx.brokePage = brokeMark;
+                    for (int i = 0; i < outlines.size(); i++) {
+                        outlines.get(i).consumed = consumedMark.get(i);
+                    }
+                    pg.setLength(0);
+                    ctx.squeeze = f;
+                    ctx.flowTw = 0;
+                    ctx.lastBaseline = -1f;
+                    ctx.lastLinePt = 0f;
+                    ctx.positioned = false;
+                    ctx.newPage = true;
+                    ctx.lastWasTable = false;
+                    ctx.budgetTw = Math.max(1, pageBudgetTw - overheadTw);
+                    pageBody(pg, page, ctx, pw, ph, secGap);
+                    int w = spacingTw(pg);
+                    if (w < bestWritten) {
+                        bestWritten = w;
+                        bestXml = pg.toString();
+                        usedF = f;
                     }
-                    int want = full ? 1 : page.columns;
-                    if (want != curCols) {
-                        sb.append("<w:p><w:pPr><w:sectPr>")
-                          .append(sectPrXml(pw, ph, curCols, secGap))
-                          .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
-                        curCols = want;
-                        ctx.lastBaseline = -1f;
-                        ctx.newPage = false;
-                        ctx.flowTw = 0;
+                    if (w <= pageBudgetTw) break;
+                    float next = Math.min(1f, f * (float) pageBudgetTw / (float) w);
+                    if (next <= SQUEEZE_FLOOR) {
+                        if (f == SQUEEZE_FLOOR) break;
+                        next = SQUEEZE_FLOOR;
                     }
+                    f = next;
                 }
-                if (block instanceof PdfToWord.Para) {
-                    para(sb, (PdfToWord.Para) block, ctx);
-                } else if (block instanceof PdfToWord.Table) {
-                    table(sb, (PdfToWord.Table) block, ctx);
-                } else if (block instanceof Picture) {
-                    picture(sb, (Picture) block, ctx);
-                } else if (block instanceof Shape) {
-                    if (!((Shape) block).consumed) shape(sb, (Shape) block, ctx);
+                if (bestXml != null) {
+                    pg.setLength(0);
+                    pg.append(bestXml);
+                    writtenTw = bestWritten;
                 }
+                ctx.squeeze = 1f;
+                ctx.budgetTw = pageBudgetTw;
             }
-            if (page.columns > 1 && curCols != page.columns) {
-                sb.append("<w:p><w:pPr><w:sectPr>")
-                  .append(sectPrXml(pw, ph, curCols, secGap))
-                  .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
+            sb.append(pg);
+            if (System.getProperty("p2w.debugFlow") != null) {
+                System.err.println("FLOW page=" + (++ctx.pageSeq)
+                        + " flowTw=" + ctx.flowTw + " budgetTw=" + ctx.budgetTw
+                        + " overTw=" + (ctx.flowTw - ctx.budgetTw)
+                        + " needTw=" + needTw + " writtenTw=" + writtenTw
+                        + " overheadTw=" + overheadTw + " f=" + usedF);
             }
         }
         // The section properties must be the LAST child of w:body.
@@ -382,6 +668,73 @@ public final class DocxWriter {
         return sb.toString();
     }
 
+    /**
+     * One page's blocks, in the order the page drew them.
+     *
+     * <p>This was the body of {@code documentXml}'s page loop. It is a method because the budget
+     * guard has to be able to run it twice: once with no budget to measure the page's own
+     * height, and - only when that height is more than the paper - once more with every box
+     * scaled to fit. It writes nothing outside {@code sb} except through {@code ctx}, and every
+     * side effect of that is undone between the two runs.
+     */
+    private static void pageBody(StringBuilder sb, PdfToWord.Page page, Ctx ctx,
+                                 float pw, float ph, float secGap) {
+        // A page set in columns, with a full-width element in the middle of it, is more than
+        // one section: the columns before the element, the element, and the columns after it.
+        // Without the breaks the element is poured into a column like everything else.
+        //
+        // The carrier is a zero-height paragraph holding the sectPr, because a sectPr has to
+        // live in a pPr and a table cannot carry one. Measured on a prototype: a table with a
+        // carrier after it costs 2.9 pt and spans correctly.
+        float blockSpan = 0f;
+        for (Object bb : page.blocks) {
+            if (bb instanceof PdfToWord.Para) {
+                PdfToWord.Para q = (PdfToWord.Para) bb;
+                blockSpan = Math.max(blockSpan, q.right - q.left);
+            }
+        }
+        int curCols = page.columns;
+        for (Object block : page.blocks) {
+            if (page.columns > 1 && blockSpan > 0f) {
+                boolean full = false;
+                if (block instanceof PdfToWord.Para) {
+                    PdfToWord.Para q = (PdfToWord.Para) block;
+                    full = q.right - q.left > blockSpan * 0.62f;
+                } else if (block instanceof PdfToWord.Table) {
+                    PdfToWord.Table q = (PdfToWord.Table) block;
+                    full = q.right - q.left > blockSpan * 0.62f;
+                }
+                int want = full ? 1 : page.columns;
+                if (want != curCols) {
+                    sb.append("<w:p><w:pPr><w:sectPr>")
+                      .append(sectPrXml(pw, ph, curCols, secGap))
+                      .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
+                    curCols = want;
+                    ctx.lastBaseline = -1f;
+                    ctx.newPage = false;
+                    // flowTw is NOT reset here. A continuous section break starts a new column on
+                    // the SAME sheet, so the page's budget is still the page's budget; resetting
+                    // it made the guard start again halfway down the page, which is how a page
+                    // measured at 842 pt could still be written at 844.
+                }
+            }
+            if (block instanceof PdfToWord.Para) {
+                para(sb, (PdfToWord.Para) block, ctx);
+            } else if (block instanceof PdfToWord.Table) {
+                table(sb, (PdfToWord.Table) block, ctx);
+            } else if (block instanceof Picture) {
+                picture(sb, (Picture) block, ctx);
+            } else if (block instanceof Shape) {
+                if (!((Shape) block).consumed) shape(sb, (Shape) block, ctx);
+            }
+        }
+        if (page.columns > 1 && curCols != page.columns) {
+            sb.append("<w:p><w:pPr><w:sectPr>")
+              .append(sectPrXml(pw, ph, curCols, secGap))
+              .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
+        }
+    }
+
     /**
      * A page the size of the PDF page, with no margins.
      *
@@ -967,16 +1320,37 @@ public final class DocxWriter {
             if (extra > 0f) beforeTw = (int) Math.min(gapCapTw(ctx), Math.round(extra * TWIPS_PER_PT));
         }
         int lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
+        // The squeeze factor is 1 on every page whose own flow already fits the paper; on the
+        // pages it is not, the guard is handed the heights the page will really be written with,
+        // so its accounting is the document's own w:before + w:line and not an estimate of it.
+        int[] fit = fitPage(ctx, twScale(beforeTw, ctx.squeeze), twScale(lineTw, ctx.squeeze), size);
+        if (fit == null) {
+            // The page is full. Break it here, deliberately, and let the row be the first line
+            // of the new sheet - which means it takes its own y as its top gap, exactly as the
+            // page's first line does.
+            breakPage(sb, ctx);
+            float topGap = first.y - LINE_BASE * linePt;
+            if (topGap > 0f) {
+                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
+            } else {
+                beforeTw = 0;
+                if (first.y > 0f) linePt = Math.min(linePt, Math.max(size, first.y / LINE_BASE));
+            }
+            lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
+            fit = fitPage(ctx, twScale(beforeTw, ctx.squeeze), twScale(lineTw, ctx.squeeze), size);
+            if (fit == null) fit = new int[]{0, lineTw};
+        }
+        beforeTw = fit[0];
+        lineTw = fit[1];
+        // The box the pitch solver compares next time is the page's own, not the squeezed one:
+        // the page's baselines are what they are, and a squeezed box that fed back into the
+        // solver would chase its own scaling down the page.
         ctx.lastLinePt = linePt;
 
         ctx.flowCount++;
         ctx.lastBaseline = first.y;
         ctx.lastSize = size;
         ctx.newPage = false;
-        if (ctx.budgetTw > 0 && ctx.flowTw + beforeTw + lineTw > ctx.budgetTw) {
-            beforeTw = Math.max(0, ctx.budgetTw - ctx.flowTw - lineTw);
-        }
-        ctx.flowTw += beforeTw + lineTw;
 
         // A tab stop's position is measured from the page margin, NOT from the paragraph's own
         // indent - the section has zero margins, so the page margin is x=0 and a stop is the
@@ -1285,17 +1659,34 @@ public final class DocxWriter {
             }
         }
         int lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
+        // A page's flow must end where the paper does. The gap above is clamped per line, but
+        // 43 of them add up, and a page whose flow overruns by a few points sends its last line
+        // - and every anchored shape after it - to a second sheet. Give up the gap first, then
+        // the slack in the last line's own box, and only then break the page.
+        int[] fit = fitPage(ctx, twScale(beforeTw, ctx.squeeze), twScale(lineTw, ctx.squeeze), b.size);
+        if (fit == null) {
+            // The page is full. Break it here, deliberately, and place this line as the first
+            // line of the new sheet: its own y decides its top gap, which is the same rule the
+            // page's first line follows.
+            breakPage(sb, ctx);
+            float topGap = b.y - LINE_BASE * linePt;
+            if (topGap > 0f) {
+                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
+            } else {
+                beforeTw = 0;
+                if (b.y > 0f) linePt = Math.min(linePt, Math.max(b.size, b.y / LINE_BASE));
+            }
+            lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
+            fit = fitPage(ctx, twScale(beforeTw, ctx.squeeze), twScale(lineTw, ctx.squeeze), b.size);
+            if (fit == null) fit = new int[]{0, lineTw};
+        }
+        beforeTw = fit[0];
+        lineTw = fit[1];
+        // The box the pitch solver compares next time is the page's own, not the squeezed one.
         ctx.lastLinePt = linePt;
         ctx.lastBaseline = b.y;
         ctx.lastSize = b.size;
         ctx.newPage = false;
-        // A page's flow must end where the paper does. The gap above is clamped per line, but
-        // 43 of them add up, and a page whose flow overruns by a few points sends its last line
-        // - and every anchored shape after it - to a second sheet. Give up the gap instead.
-        if (ctx.budgetTw > 0 && ctx.flowTw + beforeTw + lineTw > ctx.budgetTw) {
-            beforeTw = Math.max(0, ctx.budgetTw - ctx.flowTw - lineTw);
-        }
-        ctx.flowTw += beforeTw + lineTw;
         sb.append("<w:p><w:pPr>");
         if (p.heading > 0) {
             sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
@@ -1616,6 +2007,7 @@ public final class DocxWriter {
             }
         }
         if (spacerTw > 0) {
+            spacerTw = twScale(spacerTw, ctx.squeeze);
             sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                     .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"")
                     .append(spacerTw)
@@ -1748,9 +2140,20 @@ public final class DocxWriter {
                         && t.sizes.get(r).get(q) != null ? t.sizes.get(r).get(q) : 0f;
                 if (sz > 0f) rowLineTw = Math.max(rowLineTw, (int) Math.round(sz * 1.25f * TWIPS_PER_PT));
             }
+            // A table is part of the page's height, so a squeezed page squeezes it too - but
+            // never below the type it holds: a row that shrinks past its own text is a row whose
+            // text is clipped, and the reader cannot read the page that was saved. rowLineTw
+            // already carries the type-size floor, so the floor is taken before the scaling and
+            // the scaled row is held at it.
+            int typeFloorTw = rowLineTw;
+            int rowHeightTw = Math.max(rowTw, rowLineTw);
+            if (ctx.squeeze != 1f) {
+                rowHeightTw = Math.max(typeFloorTw, twScale(rowHeightTw, ctx.squeeze));
+                rowLineTw = Math.max(typeFloorTw, twScale(rowLineTw, ctx.squeeze));
+            }
             inner.append("<w:tr>");
             if (rowTw > 0) {
-                inner.append("<w:trPr><w:trHeight w:val=\"").append(Math.max(rowTw, rowLineTw))
+                inner.append("<w:trPr><w:trHeight w:val=\"").append(rowHeightTw)
                      .append("\" w:hRule=\"atLeast\"/><w:cantSplit/></w:trPr>");
             }
             int c = 0;
@@ -1892,7 +2295,11 @@ public final class DocxWriter {
         // The table is part of the flow too. Left out of the accounting, the paragraph after it
         // was spaced from the last line BEFORE the table, so a table's whole height was added
         // on top of the next paragraph's gap and the flow ran long.
-        ctx.flowTw += (int) Math.round(Math.max(0f, extentPt) * TWIPS_PER_PT) + POST_TABLE_TW;
+        // Charged as the page will write it: the extent through the squeeze, because the rows
+        // above were written through it too. A charge that ignores the squeeze is a page that
+        // believes it has room it does not have.
+        ctx.flowTw += twScale((int) Math.round(Math.max(0f, extentPt) * TWIPS_PER_PT), ctx.squeeze)
+                + POST_TABLE_TW;
         ctx.lastBaseline = t.bottom;
         ctx.lastSize = 0f;
         // The table's bottom edge is where its content ended, not a baseline inside a line box,
```

## 4. Flow-height sums, the five stamp documents

"Flow" = the page's own `w:before + w:line + w:trHeight`, per page (the test stated in the brief).
"Raw" = the brief's arithmetic taken literally — **every** `w:before`/`w:line` in
`document.xml`, which includes the paragraphs inside the stamp's anchored text boxes.

| document | flow before | flow after | raw before | raw after | page height | rendered pages (PDF / before / after) |
|---|---|---|---|---|---|---|
| `01_stamp_rotated_15deg_upright` | 681.8 | **681.8** | 1170.4 | 1170.4 | 841.9 | 1 / 1 / **1** |
| `02_stamp_rotated_15deg_upleft` | 675.3 | **675.3** | 1442.2 | 1442.2 | 841.9 | 1 / 1 / **1** |
| `03_stamp_vertical_90deg` | 541.1 | **541.1** | 1939.2 | 1939.2 | 841.9 | 1 / 1 / **1** |
| `04_stamp_180deg_upside_down` | 586.4 | **586.4** | 875.5 | 875.5 | 841.9 | 1 / 1 / **1** |
| `05_round_company_seal_curved_text` | 819.0 | **819.0** | 1333.0 | 1333.0 | 841.9 | 1 / 1 / **1** |

All five are unchanged, because all five were already inside their page and the guard does
nothing to a page that fits. Their `document.xml` is byte-identical before and after.

**The brief's measured facts do not reproduce on this `HEAD`, and the difference matters:**

* `01_stamp` raw `w:before` total is **317.8 pt**, not 477 pt, and raw `w:line` is **852.6 pt**,
  not 800 pt. The raw total is 1170.4 pt — the same order as the reported 1277 pt, and for the
  same reason: **it counts the stamp's own anchored text boxes**. Those paragraphs are inside
  `w:txbxContent`, are placed at a y, and consume no page height. In-flow, the same document is
  681.8 pt on an 841.9 pt page — it fits, and LibreOffice has always rendered it as one page.
* The `#67` paragraph with `before=258.7 pt` does not exist here. The largest `w:before` in
  `01_stamp` is **120.0 pt**, and there is exactly one paragraph at that value: the gap above
  the last line is already held down by `GAP_CAP_TW = 2400` (120 pt). The 258.7 pt figure is
  what that gap is *before* the cap.
* `01_stamp` holds 82 `w:p` elements for 40 top-level flow paragraphs (plus 2 tables), not
  "78 paragraphs with text for 35 baselines" — again, the anchored boxes are the difference.

So D-21's "one page comes back as two" is not reproduced by the five stamp documents on this
build in LibreOffice (all five render 1/1, before and after). It **is** reproduced by 19 other
documents in the corpus — see §6.

## 5. The flow budget over the 208 documents (540 page segments)

The stated test — *the sum of `w:before + w:line` over a page must not exceed the page height* —
measured per page from the `.docx` itself, with each page charged against the section that
actually closes it (a landscape page in a portrait file is measured against its own height):

| build | pages over their height | worst overrun |
|---|---|---|
| baseline | **12** of 540 (11 real — one is a bug in my first measuring tool, see below) | `350_question_paper` +174.3 pt |
| **patch** | **4** of 540 | `350_question_paper` +96.0 pt |

The four that remain, and why each one cannot be squeezed to fit:

| document | over by | need / height | why |
|---|---|---|---|
| `350_question_paper` | +96.0 pt | 1.21 | three-column paper still stacked into one flow (D-08) |
| `itr-computation-with-slab-table` | +46.3 pt | 1.09 | a 700 pt slab table whose rows cannot go below their own type size |
| `newsletter-3col-header-footer` | +41.6 pt | 1.17 | columns stacked (D-08) |
| `product-catalogue-code-left-price-right` | +40.3 pt | 1.22 | columns stacked (D-08) |

The seven the patch fixed: `20_numbered_list_separate_column_txtpos` (+0.2, closed by the
2-twip rounding allowance), `78_mixed_english_devanagari_line` (+6.1),
`academic-paper-ieee-2col-abstract` (+85.4), `bank-statement-horizontal-rules-only` (+9.3),
`brochure-3col-with-sidebar-box` (+2.1), `policy-2col-spanning-section-heading` (+19.2) and
`table-of-contents-dot-leaders` (+65.9).

One caveat about the baseline's own count: `landscape-page-inside-portrait-document` appears in
it as +222.7 pt, and that was an artefact of the first version of my measuring tool, which
charged every page against the *last* page size in the file instead of the section that closes
it. Charged correctly it is 818.0 pt on an 841.9 pt page and was never over. So the honest
baseline is 11 real overruns of 540 pages, and the patch takes them to 4.

## 6. Rendered page counts against the PDFs

Every `.docx` rendered with LibreOffice (`soffice --headless --convert-to pdf`), page counts
read with PyMuPDF, compared with the source PDF:

| build | documents whose render matches the PDF's page count | mismatches |
|---|---|---|
| baseline | 189 / 208 | **19** |
| **patch** | **196 / 208** | **12** |

**No document gained a page.** The seven that now render at their PDF's page count:

* `20_numbered_list_separate_column_txtpos` 2 → 1
* `78_mixed_english_devanagari_line` 2 → 1
* `academic-paper-ieee-2col-abstract` 3 → 2
* `bank-statement-horizontal-rules-only` 2 → 1
* `brochure-3col-with-sidebar-box` 2 → 1
* `policy-2col-spanning-section-heading` 2 → 1
* `table-of-contents-dot-leaders` 2 → 1

Still different from the PDF (all unchanged from the baseline, all D-08 or table-height cases):
`350_question_paper` 1/2, `62_two_col_newsletter_pull_quote` 1/2, `64_newspaper_uneven_columns_ad_boxes`
1/5, `annual-review-2col-uneven-columns` 1/2, `itr-computation-with-slab-table` 1/2,
`journal-2col-with-footnotes` 1/2, `mutual-fund-statement` 2/3, `newsletter-3col-header-footer`
1/2, `newspaper-2col-fullwidth-headline` 1/2, `price-list-right-aligned-amounts` 1/2,
`product-catalogue-code-left-price-right` 1/2, `text-held-twice-shadow-text` 1/2.

## 7. Does the squeeze keep the text legible and in the right place?

**It does not distort what is legible, and it moves text closer to the PDF, not further.**
Measured by matching each PDF line to the render line with the same text and comparing
baselines, for the ten documents the patch actually touches (mean / median |Δy| in pt):

| document | squeeze | mean |Δy| before | mean |Δy| after | median before | median after |
|---|---|---|---|---|---|
| `350_question_paper` | 0.850 | 93.05 | **40.24** | 81.88 | **21.82** |
| `newsletter-3col-header-footer` | 0.850 | 129.76 | **76.51** | 133.15 | **65.35** |
| `product-catalogue-code-left-price-right` | 0.850 | 98.03 | **42.31** | 99.56 | **39.08** |
| `academic-paper-ieee-2col-abstract` | 0.887 | 128.46 | **45.63** | 141.73 | **10.73** |
| `table-of-contents-dot-leaders` | 0.902 | 149.12 | **111.32** | 147.77 | **103.32** |
| `itr-computation-with-slab-table` | 0.921 | 9.92 | **3.10** | 11.03 | **2.63** |
| `policy-2col-spanning-section-heading` | 0.975 | 121.50 | **110.32** | 162.99 | **151.69** |
| `bank-statement-horizontal-rules-only` | 0.983 | 76.47 | **67.48** | 79.87 | **70.97** |
| `brochure-3col-with-sidebar-box` | 0.998 | 116.44 | **114.27** | 143.49 | **142.29** |
| `78_mixed_english_devanagari_line` | 0.993 | 45.67 | 46.19 (worse by 0.5) | 50.60 | 53.20 |

Read that carefully: most of the gain is because the page now ends where the PDF's page ends,
so lines are matched against the right page at all — not because the type is more accurate.
The one document that gets slightly worse (`78_mixed_english_devanagari_line`, +0.5 pt mean) is
the one squeezed by 0.7 %.

Legibility: the floor (`SQUEEZE_FLOOR = 0.85`) is where a 1.15 em line box becomes 0.98 em, and
no line box is ever written below the type's own ascent, and no table row below its own type
size. Checked by eye on the rendered pages of the two worst cases
(`table-of-contents-dot-leaders` at 0.902 and `350_question_paper` at 0.850): the TOC's 57
entries close up and the page fills to the footer with no overlap; the question paper's page 1
fills to the last question with no collision. No text was lost, clipped or overlapped on any
page of the corpus (the gate's `missing`, `extra`, `blocks` and `overflow` counts all hold).

Only **10 of the 208 documents** are touched by a squeeze at all; six of them by less than 3 %.

## 8. The footer hypothesis (step 3) — investigated, not done

*The writer has no notion of a header or footer at all.* `DocxWriter` emits six parts —
`[Content_Types].xml`, `_rels/.rels`, `word/document.xml`, `word/styles.xml`,
`word/_rels/document.xml.rels`, `docProps/*` — and no `word/footerN.xml`, no
`w:footerReference` (0 occurrences in all 208 outputs), no relationship to one. `sectPrXml`
writes `w:header="0" w:footer="0"` with `w:top/right/bottom/left = 0`.

*The `258.7 pt` gap is not there to recover.* On this build the gap above `01_stamp`'s last line
is capped at 120 pt (§4), and the document's in-flow total is 681.8 pt on an 841.9 pt page. The
flow is not over the paper, so a footer cannot fix a page that is not broken — it would only
move a line 120 pt up.

*It is feasible but it is not cheap, and it is not free of the metrics.* A footer would need:
a `word/footer1.xml` part; a `[Content_Types].xml` override; a relationship in
`word/_rels/document.xml.rels`; a `<w:footerReference w:type="default" r:id="...">` in **all
four** places a `sectPr` is written (three of them are mid-flow section carriers, so each would
need its own footer part or a shared one with a matching `r:id`); a `w:footer` distance on
`pgMar`, which today is 0 — with zero margins the footer sits on the paper's bottom edge and
would overlap the flow unless the bottom margin is opened, which moves every page's y
coordinate system and therefore every anchored shape on every page. And the "footer" text has
to leave the flow, which changes the document's reading order — the thing `gate.py` measures as
`lines` and `ordering`.

Given that the documents that actually overrun are overrun by 40–96 pt of *content* (stacked
columns, a 700 pt table), not by a footer gap, moving footers into a section footer is the
wrong lever for D-21. If it is wanted for its own sake, it should be its own defect with its own
measurement, and the `w:footer` distance and the bottom margin are the hard part.

## 9. Gate verdict

```
$ python3 tools/p2w-bench/gate.py --corpus <corpus> --out <out> --baseline tools/p2w-bench/base208.json --check
documents: 208
IMPROVED: 26 counts
   02_stamp_rotated_15deg_upleft              lines    30 -> 79
   03_stamp_vertical_90deg                    lines    48 -> 98
   04_stamp_180deg_upside_down                lines    31 -> 43
   06_rect_paid_stamp_red_transparent         lines    41 -> 101
   07_stamp_over_table                        lines    27 -> 72
   10_stamp_as_image                          lines    24 -> 49
   14_stamp_chars_positioned_td               lines    21 -> 49
   22_invoice_four_columns_txtpos             lines    31 -> 67
   25_signature_block_underscores_txtpos      lines    27 -> 37
   332_bom_on_drawing                         missing  2 -> 0
   332_bom_on_drawing                         extra    1 -> 0
   332_bom_on_drawing                         lines    51 -> 52
JOINED: 1 line counts fell with no word lost
   newspaper-2col-fullwidth-headline          lines    61 -> 60
no document got worse
```

`no document got worse`, exit 0. The 26 "IMPROVED" counts are the pre-existing difference
between `HEAD` and the recorded baseline (they are identical on the unmodified tree — I ran the
gate before touching anything and it printed the same list), not something this patch added.

## 10. The engine's own suites

Run from `tools/engine-verify` against the real PDFBox-Android jar:

| suite | result |
|---|---|
| `TestEngine` | **81 passed, 0 failed** |
| `TestPdfToWord` | **29 passed, 0 failed** |
| `TestRealDocs` (the three documents that once converted wrongly) | **3 passed, 0 failed** |

I did **not** run `tools/verify-engine.sh` end to end: its later stages (OCR text layer at two
DPIs, redaction pixel checks, the 51-fixture repair sweep, the APK config checks) exercise
engines this patch does not touch, and they take longer than one command budget. The three
suites above are the ones that cover `DocxWriter`.

## 11. Reproducing

```bash
git clone --depth 1 https://github.com/kavopdf/app W && cd W
git apply EX-B-page-budget.patch
# stubs + engine + harness (JDK 17; the pod had none, so: pip install jdk4py is JRE-only —
# I used the Temurin 17 tarball from the Adoptium GitHub release)
cd tools/engine-verify && mkdir -p out && javac -d out $(find stubs -name '*.java')
CP=libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar:out
javac -nowarn -cp "$CP" -d out ../../app/src/main/java/com/kavopdf/app/engine/*.java ConvertAll.java
java -XX:+UseSerialGC -XX:ActiveProcessorCount=1 -Xmx900m -Djava.awt.headless=true \
     -Dp2w.assets=libs/aar/assets -cp "$CP" ConvertAll <corpusdir> <outdir>
python3 tools/p2w-bench/gate.py --corpus <corpusdir> --out <outdir> \
     --baseline tools/p2w-bench/base208.json --check
```

Diagnostics kept in the patch, behind a system property (the writer already has
`p2w.debugGaps`): `-Dp2w.debugFlow=1` prints, per page, `flowTw`, `budgetTw`, the measured
`needTw`, the written height, the uncharged overhead and the squeeze factor, and per document
how many pages were fitted and how many were broken.

## 12. What is not fixed, and the trade-off to decide

* **Four pages are still taller than their paper** (§5). Fixing them means D-08 (real columns)
  or a table model that can shrink rows, not a page budget.
* **`BREAK_WHEN_UNFITTABLE` is off.** Turned on, the flow never exceeds the paper on a page it
  can break, but measured over the corpus it only takes 4 pages over down to 3 (a break cannot
  rescue a page whose overflow is a table already written) while adding two `pages 1 -> 2` gate
  counts on documents that render two pages either way. If the project would rather have the
  hard guarantee than the clean gate, flip that one constant — the code path is written and
  measured, not dead.
* **The squeeze is a rendering compromise, not a layout fix.** A page compressed by 15 % is a
  page whose line boxes are 15 % shorter than the page drew them. It is legible and it is
  closer to the PDF than a second page, but the honest fix for the pages that need it is the
  column work in D-08.
