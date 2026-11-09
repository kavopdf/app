# D-26, cause 1 — cumulative vertical drift made absolute

**Verdict, up front.** The vertical position in `DocxWriter` is now absolute instead of
incremental, and the accumulated drift is gone: on the two documents the defect was measured
on, the error no longer grows down the page. `verify_visual.py` on
`16_right_aligned_amounts_txtpos` goes from median dy **10.5 pt → 2.0 pt** and worst
**38.2 pt → 2.0 pt** (16 % → 100 % of lines within 3 pt); on
`20_numbered_list_separate_column_txtpos` median **51.1 pt → 1.7 pt**, worst
**101.4 pt → 13.5 pt**. The 208-document gate prints **"no document got worse"**.

**Two things did not come out clean, and they are in this report rather than out of it.**
`79_inr_indian_digit_grouping_table` loses the drift (spread of dy 15.1 pt → 10.6 pt, error/y
correlation −0.263 → +0.026) but its median **rises 2.3 → 8.4 pt**: the whole table now sits a
constant ~6 pt low instead of straddling zero. And in an eight-document sample taken outside the
five named ones, two documents (`303_discharge_summary`, `318_court_summons_form`) moved the same
way — the drift is removed, a constant offset remains. Section 6 says which and why.

---

## 1. What was actually wrong — two causes, not one

**Cause 1, the flow (this is the one the brief names).** `w:before` was computed from the pitch
between two *PDF* baselines:

```java
float pitch = b.y - ctx.lastBaseline;                                  // PDF truth
float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;
if (extra > 0f) beforeTw = round(extra * TWIPS_PER_PT);                // else: 0
```

The arithmetic is right and the page is not, because the gap only exists when it is **positive**.
`flowLinePt` floors the solved box at the em, so on any page set tighter than 1.15 em — which is
most of them — `extra` came out negative, was written as **zero**, and the line landed low by the
difference. The next paragraph then measured its pitch from the PDF's baseline again, so the
model never saw the error again while the reader kept it, and every line added its own. 0.3 pt a
line is 10.5 pt at the median of one page and 38 pt at its foot. That is exactly why the error
correlated with y (−0.65 and +0.72) instead of being noise. Rounding to twips was the smaller
half of it; the dropped negative gap was the larger.

**Cause 2, the table (found while proving cause 1, and it is what the two "table" documents in
the brief are actually showing).** Every table row was written at the table's extent divided by
its row count:

```java
int rowTw = round((t.bottom - t.top) / rowCount * TWIPS_PER_PT);   // one number for every row
```

That is only true of evenly spaced rows, and the extent is not the row grid: on
`16_right_aligned_amounts` the average is 18.3 pt while the page's own pitch is 19 pt, so each of
the 13 rows sat 1.45 pt closer to the one above than the page had it — the same 38 pt at the foot
of the table, from a different line of code. `verify_visual` measured that document at
dy −3.2 on the first row and −13.4 on the ninth, per-row, which is how the table cause was
separated from the flow cause: the flow fix alone moved it **not at all** (median 10.5 before and
after), because every line of that document is inside a table.

## 2. The change

1. **`Ctx.flowY` / `Ctx.flowBoxPt`** — where the *reader* will put the last baseline, built from
   the twips actually written (so rounding is in it), and the height of that box as written.
   Reset to −1 wherever the flow's position on the sheet stops being known: a new sheet, a page
   break, a squeeze re-run, a new column of a continuous section.
2. **`place()`** — the gap is `targetY − (top of this paragraph)`, less the part of the box above
   its own baseline. A flow cannot go backwards, so when the target is above the flow the gap is
   zero and the overshoot is left on the page; the next line starts from the position that was
   written, so the overshoot is **absorbed there instead of accumulated**. When the target is so
   close that no box of the line's own em reaches it, the box gives way first, floored at the em.
3. **`resync()`** — called after every paragraph written, from `beforeTw`/`lineTw` as emitted.
   This is the re-sync the brief's step 3 asks for, and it is unconditional rather than
   threshold-based: the running position is always the truth, so there is nothing to accumulate.
4. **`PdfToWord.Table.rowEdge`** — the page's own row edges, recorded by all three table builders
   (grid, ruled, whitespace). The writer gives each row the height the page gave *that* row.
5. **`PdfToWord.Table.rowTopPt`** — the table's first row's top edge, which is not always
   `rowEdge[0]` (the grid pass reads a cell's rectangle, whose y is the rule *below* the row's
   text). The spacer above a table is now placed from it, absolutely.
6. The gap-wider-than-the-cap path still anchors the line as a text box, but now records the
   anchored line's y as the flow's position, and the flow after a table resumes from the table's
   bottom edge plus the 4 pt carrier paragraph.

The two call sites the brief points at (`flowRow`, `flowFromBox`) are now three lines each; the
arithmetic moved into `place()`/`resync()`.

## 3. The diff

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (+194/−52),
`app/src/main/java/com/kavopdf/app/engine/PdfToWord.java` (+58). Apply from the repo root with
`git apply`.

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 9216473..66d1fb6 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -359,6 +359,8 @@ public final class DocxWriter {
         ctx.newPage = true;
         ctx.lastBaseline = -1f;
         ctx.lastLinePt = 0f;
+        ctx.flowY = -1f;
+        ctx.flowBoxPt = 0f;
         ctx.lastWasTable = false;
     }
 
@@ -416,6 +418,26 @@ public final class DocxWriter {
          * bottom edge is a box edge and not a baseline.
          */
         float lastLinePt = 0f;
+        /**
+         * Where the READER will put the last baseline emitted, in points from the page top.
+         *
+         * <p>This is not {@link #lastBaseline}: that is where the PDF drew the line, which is
+         * where the line was ASKED to go. This is where the page it was written into actually
+         * ends up, so it carries the rounding, the clamped gap and the shortened box with it.
+         * The space-before of the next paragraph is measured from here, so an error is spent
+         * once and then re-synced instead of being carried down the page (D-26).
+         *
+         * <p>-1 means the flow's position on the sheet is not known - the first line of a
+         * sheet, or a new column of a continuous section - and the caller must place from the
+         * page's top edge instead.
+         */
+        float flowY = -1f;
+        /**
+         * The height of the last line box AS WRITTEN (through the squeeze and the twip
+         * rounding), in points. Its lower {@code 1 - LINE_BASE} is what is left below the
+         * baseline before the next paragraph's space-before starts.
+         */
+        float flowBoxPt = 0f;
         /** Set at a page break so the first line on a page carries no gap. */
         boolean newPage = true;
         /** Flow height already spent on this page, in twips. */
@@ -558,6 +580,8 @@ public final class DocxWriter {
                 ctx.newPage = true;
             }
             ctx.lastBaseline = -1f;
+            ctx.flowY = -1f;
+            ctx.flowBoxPt = 0f;
             java.util.Map<Integer, Float> colLeft = new java.util.HashMap<>();
             for (Object b4 : page.blocks) {
                 if (!(b4 instanceof PdfToWord.Para)) continue;
@@ -658,6 +682,8 @@ public final class DocxWriter {
                     ctx.flowTw = 0;
                     ctx.lastBaseline = -1f;
                     ctx.lastLinePt = 0f;
+                    ctx.flowY = -1f;
+                    ctx.flowBoxPt = 0f;
                     ctx.positioned = false;
                     ctx.newPage = true;
                     ctx.lastWasTable = false;
@@ -744,6 +770,10 @@ public final class DocxWriter {
                       .append("<w:type w:val=\"continuous\"/></w:sectPr></w:pPr></w:p>");
                     curCols = want;
                     ctx.lastBaseline = -1f;
+                    // A new column is a new flow: its lines are placed from the column's own
+                    // top, so the running position on the sheet is no longer known.
+                    ctx.flowY = -1f;
+                    ctx.flowBoxPt = 0f;
                     ctx.newPage = false;
                     // flowTw is NOT reset here. A continuous section break starts a new column on
                     // the SAME sheet, so the page's budget is still the page's budget; resetting
@@ -1456,18 +1486,11 @@ public final class DocxWriter {
         // charged one pitch, not one per field.
         float pitch = !ctx.newPage && ctx.lastBaseline >= 0f ? first.y - ctx.lastBaseline : -1f;
         float linePt = flowLinePt(pitch, size, ctx.lastLinePt);
-        int beforeTw = 0;
-        if (ctx.newPage) {
-            float topGap = first.y - LINE_BASE * linePt;
-            if (topGap > 0f) {
-                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
-            } else if (first.y > 0f) {
-                linePt = Math.min(linePt, Math.max(size, first.y / LINE_BASE));
-            }
-        } else if (pitch > 0f) {
-            float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;
-            if (extra > 0f) beforeTw = (int) Math.min(gapCapTw(ctx), Math.round(extra * TWIPS_PER_PT));
-        }
+        // Absolute, not incremental: the gap is measured from where the reader really put the
+        // line above, so no rounding or clamped gap is carried down the page (D-26).
+        float[] pl = place(ctx, first.y, size, pitch, linePt);
+        linePt = pl[1];
+        int beforeTw = (int) Math.round(Math.min(pl[0], gapCapTw(ctx)));
         int lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
         // The squeeze factor is 1 on every page whose own flow already fits the paper; on the
         // pages it is not, the guard is handed the heights the page will really be written with,
@@ -1500,6 +1523,9 @@ public final class DocxWriter {
         ctx.lastBaseline = first.y;
         ctx.lastSize = size;
         ctx.newPage = false;
+        // Re-sync the running position to what was written, not to what was intended. A page
+        // break inside the block above starts a new sheet, so the top is the paper's top again.
+        resync(ctx, flowTopPt(ctx), beforeTw, lineTw);
 
         // A tab stop's position is measured from the page margin, NOT from the paragraph's own
         // indent - the section has zero margins, so the page margin is x=0 and a stop is the
@@ -1738,6 +1764,93 @@ public final class DocxWriter {
         return Math.max(4f, Math.min(natural, Math.max(size, solved)));
     }
 
+    /**
+     * The gap and the box that put this line's baseline at its own y on the sheet.
+     *
+     * <p>This is the whole of D-26. The vertical position used to be INCREMENTAL: the gap was
+     * {@code pitch - rest of the previous box - this line's part above its baseline}, and the
+     * pitch was the distance between two baselines in the PDF. The model was arithmetically
+     * right and the page was not, because the gap only exists when it is positive: whenever the
+     * solved box was floored at the em (a PDF that sets its lines tighter than 1.15 em, which
+     * most do), the gap came out negative, was written as zero, and the line landed low by the
+     * difference. The next paragraph then measured its pitch from the PDF's baseline again - so
+     * the error was never seen again by the model, but the reader kept it, and each line added
+     * its own. On 16_right_aligned_amounts 0.3 pt per line became 10.5 pt at the median and 38 pt
+     * at the foot of one page; on 20_numbered_list_separate_column 101 pt. That is why the error
+     * correlated with y (-0.65 and +0.72) instead of being noise.
+     *
+     * <p>So the position is now ABSOLUTE. {@link Ctx#flowY} is where the reader will really put
+     * the last baseline - built from the twips that were actually written, so rounding is in it
+     * too - and the gap is simply {@code target - (top of this paragraph)}, less the part of the
+     * box above its own baseline. The running position is then re-synced to what was written,
+     * not to what was intended, so an error is spent on the line that caused it and the next
+     * line starts from the truth again.
+     *
+     * <p>Two cases cannot be solved by spacing, because a flow cannot go backwards:
+     * <ul>
+     *   <li>the target is above where the flow already is (the line above overshot). The gap is
+     *       zero and the overshoot is left on the page - and, because the next call starts from
+     *       the position that was written, absorbed there instead of accumulated. That is the
+     *       re-sync, and it is why this is bounded rather than growing;</li>
+     *   <li>the target is so close that no box of the line's own em size can reach it. The box is
+     *       shortened to the largest that still lands on or above the target, floored at the em
+     *       so the glyphs are not clipped, and the rest is the first case.</li>
+     * </ul>
+     *
+     * @param targetY the baseline the PDF drew, in points from the top of the sheet
+     * @param size    the line's font size, the floor for its box
+     * @param pitch   the distance to the previous baseline on this page, or -1 when unknown
+     * @param linePt  the box {@link #flowLinePt} asked for
+     * @return {@code {spaceBeforeTw, linePt}}
+     */
+    private static float[] place(Ctx ctx, float targetY, float size, float pitch, float linePt) {
+        if (ctx.newPage) {
+            // The first line of a sheet: the flow starts at the paper's top edge, so the gap is
+            // the whole distance down to the top of this line's box. Unchanged from before -
+            // there is nothing above it to be incremental about.
+            float topGap = targetY - LINE_BASE * linePt;
+            if (topGap > 0f) {
+                return new float[]{Math.min(2000f, topGap * (float) TWIPS_PER_PT), linePt};
+            }
+            if (targetY > 0f) linePt = Math.min(linePt, Math.max(size, targetY / LINE_BASE));
+            return new float[]{0f, linePt};
+        }
+        if (ctx.flowY < 0f) {
+            // The flow's position on this sheet is not known (a new column of a continuous
+            // section): fall back to the pitch model, which is the behaviour that was there.
+            float extra = pitch > 0f
+                    ? pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt : 0f;
+            return new float[]{extra > 0f ? extra * (float) TWIPS_PER_PT : 0f, linePt};
+        }
+        // Where this paragraph starts: the rest of the previous line's box, below its baseline.
+        float topPt = ctx.flowY + (1f - LINE_BASE) * ctx.flowBoxPt;
+        float d = targetY - topPt;
+        if (d <= 0f) return new float[]{0f, linePt};      // the flow cannot go backwards
+        // A box taller than d / LINE_BASE would put its own baseline below the target, and a
+        // negative gap is not something a reader will honour - so the box gives way first, down
+        // to the em and no further.
+        float maxBox = d / LINE_BASE;
+        if (linePt > maxBox) linePt = Math.max(size, maxBox);
+        float before = d - LINE_BASE * linePt;
+        if (before < 0f) before = 0f;
+        return new float[]{before * (float) TWIPS_PER_PT, linePt};
+    }
+
+    /**
+     * Records where the reader will put the baseline just written, from the twips that were
+     * actually emitted. The next paragraph is measured from here.
+     */
+    private static void resync(Ctx ctx, float topPt, int beforeTw, int lineTw) {
+        ctx.flowY = topPt + beforeTw / (float) TWIPS_PER_PT + LINE_BASE * (lineTw / (float) TWIPS_PER_PT);
+        ctx.flowBoxPt = lineTw / (float) TWIPS_PER_PT;
+    }
+
+    /** The top of the paragraph about to be written, in points from the top of the sheet. */
+    private static float flowTopPt(Ctx ctx) {
+        if (ctx.newPage || ctx.flowY < 0f) return 0f;
+        return ctx.flowY + (1f - LINE_BASE) * ctx.flowBoxPt;
+    }
+
     /** A paragraph with no page coordinates of its own: the old flowing behaviour. */
     /**
      * One PDF line as a real Word paragraph.
@@ -1775,41 +1888,28 @@ public final class DocxWriter {
         // box is the page's own line height rather than a guess at it - see flowLinePt.
         float pitch = !ctx.newPage && ctx.lastBaseline >= 0f ? b.y - ctx.lastBaseline : -1f;
         float linePt = flowLinePt(pitch, b.size, ctx.lastLinePt);
-        int beforeTw = 0;
-        if (ctx.newPage) {
-            // The FIRST line on a page still has to land at its own y. The section carries zero
-            // margins, so without this it starts at the very top of the sheet: on file 21 every
-            // line measured 46 pt high against the PDF, a constant offset with the pitch already
-            // correct. Measured, not guessed - dy was -46.2, -48.3, -45.0, -46.6 over the first
-            // four lines of the page. The lift is the part of the box above its baseline, and
-            // where the box is taller than the space the page leaves, the box is shortened to
-            // fit rather than the line being placed below its own y.
-            float topGap = b.y - LINE_BASE * linePt;
-            if (topGap > 0f) {
-                beforeTw = (int) Math.min(2000L, Math.round(topGap * TWIPS_PER_PT));
-            } else if (b.y > 0f) {
-                linePt = Math.min(linePt, Math.max(b.size, b.y / LINE_BASE));
-            }
-        } else if (pitch > 0f) {
-            // Where the previous baseline is, plus the rest of its box, plus this line's own part
-            // above its baseline, plus this gap, must equal the pitch the page used. Only a gap
-            // wider than the box can carry - a diagram's boxes 90 pt apart, a footer 422 pt below
-            // the text - still needs spacing, and flowLinePt has refused to put that in the box.
-            float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;
-            if (extra > 0f) {
-                // A gap wider than the flow may spend is not a gap, it is a position. Clamping it
-                // puts the line somewhere the page never put it, and every line after it drifts
-                // with it: on 331_pid_diagram the clamp landed the diagram's "CHILLED WATER"
-                // label 114 pt above the box that holds it. Anchoring the line at its own y is
-                // what the page did, and from here on the page is placed rather than flowed.
-                if (extra * TWIPS_PER_PT > gapCapTw(ctx)) {
-                    ctx.positioned = true;
-                    anchorBox(sb, p, b, ctx);
-                    return;
-                }
-                beforeTw = (int) Math.round(extra * TWIPS_PER_PT);
-            }
+        // Absolute placement (D-26): the gap is the distance from where the reader really put
+        // the line above to where this one belongs, not the pitch between two PDF baselines.
+        float[] pl = place(ctx, b.y, b.size, pitch, linePt);
+        linePt = pl[1];
+        if (!ctx.newPage && ctx.flowY >= 0f && pl[0] > gapCapTw(ctx)) {
+            // A gap wider than the flow may spend is not a gap, it is a position. Clamping it
+            // puts the line somewhere the page never put it, and every line after it drifts
+            // with it: on 331_pid_diagram the clamp landed the diagram's "CHILLED WATER"
+            // label 114 pt above the box that holds it. Anchoring the line at its own y is what
+            // the page did, and from here on the page is placed rather than flowed.
+            ctx.positioned = true;
+            anchorBox(sb, p, b, ctx);
+            // The anchored line is on the sheet at its own y, so the flow resumes from there.
+            ctx.flowY = b.y;
+            ctx.flowBoxPt = 0f;
+            return;
         }
+        // The FIRST line on a page has to land at its own y too, and place() does that: the
+        // section carries zero margins, so the flow starts at the paper's top edge and the gap
+        // is the whole distance down to the top of this line's box (file 21 used to sit 46 pt
+        // high on every line without it).
+        int beforeTw = (int) Math.round(Math.min(pl[0], gapCapTw(ctx)));
         int lineTw = (int) Math.max(1L, Math.round(linePt * TWIPS_PER_PT));
         // A page's flow must end where the paper does. The gap above is clamped per line, but
         // 43 of them add up, and a page whose flow overruns by a few points sends its last line
@@ -1839,6 +1939,9 @@ public final class DocxWriter {
         ctx.lastBaseline = b.y;
         ctx.lastSize = b.size;
         ctx.newPage = false;
+        // Re-sync to what was written, so the next paragraph is measured from the reader's
+        // position rather than from the PDF's (D-26).
+        resync(ctx, flowTopPt(ctx), beforeTw, lineTw);
         sb.append("<w:p><w:pPr>");
         if (p.heading > 0) {
             sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
@@ -2331,7 +2434,18 @@ public final class DocxWriter {
         // paragraph rather than w:spacing on the table because OOXML gives a table no
         // before-spacing of its own.
         int spacerTw = 0;
-        if (!ctx.newPage && !ctx.lastWasTable && ctx.lastBaseline >= 0f && t.top > ctx.lastBaseline) {
+        if (!ctx.newPage && !ctx.lastWasTable && ctx.flowY >= 0f && !Float.isNaN(t.rowTopPt)) {
+            // The table's top is placed ABSOLUTELY, from the flow's real position (D-26): the
+            // spacer is the distance from where the reader will be to where the page drew the
+            // table's top edge. The arithmetic this replaces measured that distance from the
+            // previous PDF baseline less a line - and a table's top has been a few points out
+            // ever since, which is the defect REMAINING-DEFECTS.md records as unfixed.
+            float prevLine = Math.max(4f, ctx.lastSize * LINE_FACTOR);
+            float extraAbs = t.rowTopPt - flowTopPt(ctx);
+            if (extraAbs >= prevLine * 1.2f) {
+                spacerTw = (int) Math.min(2880L, Math.round(extraAbs * TWIPS_PER_PT));
+            }
+        } else if (!ctx.newPage && !ctx.lastWasTable && ctx.lastBaseline >= 0f && t.top > ctx.lastBaseline) {
             float prevLine = Math.max(4f, ctx.lastSize * LINE_FACTOR);
             // MEASURED AND REVERTED: charging the spacer as (t.top - baseline) minus this line's
             // own slack below its baseline - the rule the flow itself now uses - put 390's table
@@ -2353,6 +2467,10 @@ public final class DocxWriter {
                     .append(spacerTw)
                     .append("\" w:lineRule=\"exact\"/><w:rPr><w:sz w:val=\"2\"/></w:rPr></w:pPr></w:p>");
             ctx.flowTw += spacerTw;
+            // The spacer is a line of its own: the table now starts at the flow's position
+            // after it, which is the y the page drew the table's top at.
+            ctx.flowY = flowTopPt(ctx) + spacerTw / (float) TWIPS_PER_PT;
+            ctx.flowBoxPt = 0f;
         }
 
         StringBuilder inner = new StringBuilder(512);
@@ -2449,10 +2567,29 @@ public final class DocxWriter {
         // A cell that holds SEVERAL lines is the case that was wrong: charging the pitch to
         // every line charged the row twice over and doubled it. There the line is the cell's
         // own text - 1.25 em of its size, below - and the row stays the page's own pitch.
-        int cellLineTw = rowTw > 0 ? rowTw : 200;
-        int naturalLineTw = rowTw > 0 ? Math.min(rowTw, 200) : 200;
+        // The page's own row edges, when the pass that built the table measured them. Every row
+        // then takes the height the page gave THAT row, so a table whose rows are not evenly
+        // spaced - a ledger's header, a wrapped address - no longer drifts by the average of its
+        // neighbours: 1.45 pt a row on 16_right_aligned_amounts, 38 pt by the foot of the table
+        // (D-26, cause 2). Where the edges are not known, the average is used exactly as before.
+        float[] rowEdge = t.rowEdge;
+        boolean exactRows = rowEdge != null && rowEdge.length == t.rows.size() + 1;
         for (int r = 0; r < t.rows.size(); r++) {
             List<String> row = t.rows.get(r);
+            // This row's own pitch. A ruled table's rule lies inside the row's box, so it comes
+            // off here exactly as it comes off the average above.
+            int rowTwHere = rowTw;
+            if (exactRows) {
+                float pitchPt = rowEdge[r + 1] - rowEdge[r];
+                if (pitchPt > 0.5f && pitchPt < 2000f) {
+                    rowTwHere = (int) Math.round(pitchPt * TWIPS_PER_PT);
+                    if (ruledTable) rowTwHere = Math.max(1, rowTwHere - TABLE_BORDER_TW);
+                }
+            }
+            // The line inside the cell follows the row it is in: a cell's text is drawn at the
+            // foot of its own row on most of this corpus, so the line height is the row's pitch.
+            int cellLineHere = rowTwHere > 0 ? rowTwHere : 200;
+            int naturalLineHere = rowTwHere > 0 ? Math.min(rowTwHere, 200) : 200;
             // Does any cell of this row hold more than one line of the page? A numbered item's
             // marker, a calendar's holiday name under its date, a two-line address in a box.
             int rowParts = 1;
@@ -2463,7 +2600,7 @@ public final class DocxWriter {
                 for (int i = 0; i < cv.length(); i++) if (cv.charAt(i) == '\n') n++;
                 if (n > rowParts) rowParts = n;
             }
-            int baseLineTw = rowParts > 1 ? naturalLineTw : cellLineTw;
+            int baseLineTw = rowParts > 1 ? naturalLineHere : cellLineHere;
             // The row's own line height, never smaller than its own text. cellLineTw is the
             // table's extent divided by its row count, which is an average - correct only when
             // the rows are evenly spaced. On a page with a tall header row, a merged cell or a
@@ -2495,13 +2632,13 @@ public final class DocxWriter {
             // already carries the type-size floor, so the floor is taken before the scaling and
             // the scaled row is held at it.
             int typeFloorTw = rowLineTw;
-            int rowHeightTw = Math.max(rowTw, rowLineTw);
+            int rowHeightTw = Math.max(rowTwHere, rowLineTw);
             if (ctx.squeeze != 1f) {
                 rowHeightTw = Math.max(typeFloorTw, twScale(rowHeightTw, ctx.squeeze));
                 rowLineTw = Math.max(typeFloorTw, twScale(rowLineTw, ctx.squeeze));
             }
             inner.append("<w:tr>");
-            if (rowTw > 0) {
+            if (rowTwHere > 0) {
                 inner.append("<w:trPr><w:trHeight w:val=\"").append(rowHeightTw)
                      .append("\" w:hRule=\"atLeast\"/><w:cantSplit/></w:trPr>");
             }
@@ -2658,6 +2795,11 @@ public final class DocxWriter {
         // The table's bottom edge is where its content ended, not a baseline inside a line box,
         // so there is no slack of its own to carry into the next line's advance.
         ctx.lastLinePt = 0f;
+        // The flow's real position after a table is the table's bottom edge plus the 4 pt carrier
+        // Word requires after it, because that carrier is a line the next paragraph starts under
+        // (D-26: the position is where the reader is, not where the PDF drew).
+        ctx.flowY = t.bottom + POST_TABLE_TW / (float) TWIPS_PER_PT;
+        ctx.flowBoxPt = 0f;
         ctx.newPage = false;
         ctx.lastWasTable = true;
     }
diff --git a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
index 6aa9127..a563c12 100644
--- a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
+++ b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
@@ -248,6 +248,31 @@ public final class PdfToWord {
          * lines the page never drew, so each side is decided on its own evidence.
          */
         public boolean innerH, innerV;
+        /**
+         * The y of every row's top edge, in points, with one more entry than there are rows -
+         * the last entry is the bottom edge of the last row. Null when the pass that built the
+         * table did not know them.
+         *
+         * <p>The writer gave every row the table's extent divided by its row count, which is only
+         * true of a table whose rows are evenly spaced. A ledger with a taller header, a wrapped
+         * address or a merged cell does not have those, and every row below the odd one out then
+         * sits a little further from the page than the row above it: 1.45 pt a row on
+         * 16_right_aligned_amounts, 38 pt by the foot of the table, and it is why the error there
+         * correlated with y. These are the page's own row edges, so each row can be given the
+         * height the page gave it (D-26, cause 2).
+         */
+        public float[] rowEdge;
+        /**
+         * The y of the table's first row's TOP edge, in points, when the pass that built the
+         * table could tell where that edge is ({@link Float#NaN} otherwise).
+         *
+         * <p>{@link #rowEdge} gives each row its own height, but its first entry is not always
+         * the table's top: the grid pass reads a cell's rectangle, whose y is the rule BELOW the
+         * row's text (on 16_right_aligned_amounts the first entry is 156 pt while the page's
+         * first baseline is 148 and the row's top edge is 137). Placing the table from the first
+         * entry therefore put it one pitch low. This is the edge the flow is placed against.
+         */
+        public float rowTopPt = Float.NaN;
         public float top, bottom, left, right;
         public int column;
     }
@@ -4828,6 +4853,15 @@ public final class PdfToWord {
             left = Math.min(left, c[0]); right = Math.max(right, c[2]);
         }
         t.top = top; t.bottom = bottom; t.left = left; t.right = right;
+        // The page's own row edges, so a row can be given its own height instead of the average.
+        // A cell's rectangle carries the rule BELOW its row, so the first edge is one pitch above
+        // the first cell's y and row r's top is the cell y of row r-1.
+        float firstPitch = nrow > 1 ? Math.max(1f, R.get(1) - R.get(0)) : Math.max(1f, bottom - R.get(0));
+        float[] rowEdge = new float[nrow + 1];
+        rowEdge[0] = R.get(0) - firstPitch;
+        for (int r = 1; r <= nrow; r++) rowEdge[r] = R.get(r - 1);
+        t.rowEdge = rowEdge;
+        t.rowTopPt = rowEdge[0];
         float[] cx = new float[ncol + 1];
         for (int i = 0; i < ncol; i++) cx[i] = C.get(i);
         cx[ncol] = right;
@@ -5227,6 +5261,12 @@ public final class PdfToWord {
             t.bottom = bottom;
             t.left = left;
             t.right = right;
+            // The grid's own row rules: rows = ys.size() - 1 and row r is ys[r]..ys[r+1]. A rule
+            // is a row's top edge, so the first one is the table's top.
+            float[] rowEdge = new float[rows + 1];
+            for (int r = 0; r <= rows; r++) rowEdge[r] = ys.get(r);
+            t.rowEdge = rowEdge;
+            t.rowTopPt = rowEdge[0];
             // The rule positions the columns were cut at, so the .docx can use the same widths
             // instead of five equal ones.
             float[] colX = new float[cols + 1];
@@ -5398,6 +5438,9 @@ public final class PdfToWord {
         t.ruled = false;
         t.top = rows.get(from).get(0).y;
         float bottom = t.top, left = Float.MAX_VALUE, right = 0;
+        // The baseline each row was drawn on, so the row can be given the height the page gave
+        // it rather than the table's average (D-26, cause 2).
+        List<Float> rowTops = new ArrayList<>();
         for (int r = from; r < to; r++) {
             String[] line = new String[columns.size()];
             String[] lineFonts = new String[columns.size()];
@@ -5467,8 +5510,23 @@ public final class PdfToWord {
             t.cellX.add(textXs);
             t.cellR.add(textRs);
             t.colors.add(textCols);
+            float rowY = Float.MAX_VALUE;
+            for (Line cell : rows.get(r)) rowY = Math.min(rowY, cell.y);
+            rowTops.add(rowY == Float.MAX_VALUE ? (rowTops.isEmpty() ? t.top : rowTops.get(rowTops.size() - 1)) : rowY);
         }
         t.bottom = bottom;
+        // One more entry than there are rows: the last row's bottom edge is one row pitch below
+        // its own top, because the last baseline the page drew is a baseline and not an edge.
+        float[] rowEdge = new float[rowTops.size() + 1];
+        for (int i = 0; i < rowTops.size(); i++) rowEdge[i] = rowTops.get(i);
+        float lastPitch = rowTops.size() >= 2
+                ? Math.max(1f, rowEdge[rowTops.size() - 1] - rowEdge[rowTops.size() - 2])
+                : Math.max(1f, bottom - (rowTops.isEmpty() ? t.top : rowEdge[0]));
+        rowEdge[rowTops.size()] = (rowTops.isEmpty() ? t.top : rowEdge[rowTops.size() - 1]) + lastPitch;
+        t.rowEdge = rowEdge;
+        // These edges are baselines, so the table's top edge is one ascent (DocxWriter.LINE_BASE
+        // of the row's own pitch) above the first one.
+        t.rowTopPt = rowEdge[0] - 0.8f * lastPitch;
         float[] cx2 = new float[columns.size() + 1];
         for (int i = 0; i < columns.size(); i++) cx2[i] = columns.get(i);
         cx2[columns.size()] = Math.max(right, columns.get(columns.size() - 1));
```

## 4. `verify_visual.py` — the five named documents

`python3 tools/p2w-bench/verify_visual.py <pdf> <docx> --json`, LibreOffice render, every PDF
line matched to a render line by its text. `dy` is the absolute vertical error in points.

| document | median dy before → after | worst dy before → after | within 3 pt before → after | within 10 pt before → after |
|---|---|---|---|---|
| 16_right_aligned_amounts_txtpos | **10.5 → 2.0** | **38.2 → 2.0** | **16 % → 100 %** | 45 % → 100 % |
| 20_numbered_list_separate_column_txtpos | **51.1 → 1.7** | **101.4 → 13.5** | 15 % → 52 % | 15 % → 52 % |
| 21_form_labels_x60_values_x300_txtpos | 0.9 → 0.9 | 2.4 → 2.4 | 100 % → 100 % | 100 % → 100 % |
| 79_inr_indian_digit_grouping_table | 2.3 → **8.4** | 9.0 → 9.3 | 61 % → **13 %** | 100 % → 100 % |
| 80_gstin_pan_cin_ifsc_table | 5.8 → 3.6 | 79.7 → 90.8 | 16 % → 43 % | 95 % → 95 % |

Pages, line counts and matched share are unchanged on all five (1 page each, 64/33/66/47/73 PDF
lines, match share 100/100/46/66/86 %). The 46 % match on file 21 and the 66 %/86 % on 79/80 are
pre-existing and identical before and after: those PDF lines are merged into single `w:tab` rows
by design, so there is no separate render line to match them to.

### Is the drift actually gone? (signed dy, per line)

`dy_median` is a median of magnitudes, which can hide a drift that crosses zero. These are the
signed errors, first line to last, plus their correlation with y:

| document | corr(y, dy) before → after | first → last line, before | first → last line, after | spread before → after |
|---|---|---|---|---|
| 16_right_aligned_amounts | **−0.653 → +0.110** | +1.3 → −13.2 | +1.3 → +1.7 | 39.5 → 3.8 |
| 20_numbered_list | **+0.723 → −0.195** | +1.3 → +34.6 | +1.3 → +0.7 | 100.6 → 15.2 |
| 21_form_labels | +0.169 → −0.283 | +1.3 → +2.1 | +1.3 → +0.7 | 2.7 → 4.1 |
| 79_inr_grouping_table | −0.263 → +0.026 | +1.3 → −1.4 | +1.3 → −4.0 | 15.1 → 10.6 |
| 80_gstin_table | −0.085 → +0.136 | +1.2 → −33.2 | +1.2 → −22.1 | 115.3 → 115.3 |

The correlation with y — the signature of accumulation — is gone on both documents the defect was
measured on (−0.653 → 0.110, +0.723 → −0.195), and the error at the foot of the page is now the
error at its head. On 79 the drift is gone too but the mean moved from −1.2 to −6.1: that is the
constant offset described below, not accumulation.

## 5. Eight more documents (not in the brief, measured the same way)

| document | median/worst/within-3 before | after | pages |
|---|---|---|---|
| 22_invoice_four_columns_txtpos | 5.3 / 43.8 / 37 % | 4.0 / 28.7 / 14 % | 1 → 1 |
| 303_discharge_summary | 0.6 / 13.5 / 59 % | **7.8** / 8.8 / 43 % | 1 → 1 |
| 315_gazette_notification | 38.9 / 70.1 / 17 % | **22.2** / 64.8 / 23 % | 1 → 1 |
| 318_court_summons_form | 11.7 / 225.7 / 13 % | 13.0 / 225.7 / 13 % | 1 → 1 |
| 331_pid_diagram | 1.5 / 1.7 / 100 % | 1.5 / 1.7 / 100 % | 1 → 1 |
| 390_wide_data_appendix | 3.3 / 9.6 / 47 % | **0.1 / 2.4 / 100 %** | 1 → 1 |
| 402_calendar_month_grid | 9.0 / 29.2 / 7 % | 9.0 / 29.2 / 7 % | 1 → 1 |
| 62_two_col_newsletter_pull_quote | 22.0 / 474.0 / 6 % | **1.5 / 23.8 / 83 %** | 2 → 2 |

Six of eight are better or unchanged in median, two of them (390, 62) substantially. Two are
worse in median while better in worst-case: 303 (0.6 → 7.8, but worst 13.5 → 8.8 — the drift
traded for a constant offset) and 318 (11.7 → 13.0, worst unchanged).

## 6. What is honestly not fixed, and where the regressions come from

* **A table's top is still a few points out, and making the rows exact exposes it.**
  `79_inr_indian_digit_grouping_table` used to have 15.25 pt rows against a 20 pt page pitch, so
  the rows pulled the text back up by more than the table's own top error pushed it down, and the
  errors cancelled through zero (median 2.3 pt, 61 % within 3 pt — by luck, not by placement).
  With the rows at the page's pitch, the top error is no longer hidden: the table now sits a
  uniform ~6 pt low (median 8.4, worst 9.3, i.e. 0.9 pt of drift instead of 15). The same pattern
  is what moves 303 (0.6 → 7.8) and 318 (11.7 → 13.0). The cause is the intra-row baseline: a
  cell's line height is the row's pitch, which puts the text 0.8 × pitch below the row's top,
  while the page drew it 13.5 pt below a 20 pt row (0.675 × pitch) on 79. Fixing that needs a
  per-row *baseline* (not just a per-row edge) in the model; `rowEdge` for the whitespace pass is
  already baseline-based, the grid and ruled passes are not. That is the next move and it is not
  in this patch.
* **The 48 % of lines on 20_numbered_list that are still 13.5 pt out** are a single block of the
  page, not a drift: the median is 1.7 pt and the last line is +0.7 pt. It is the second column
  of the list, which is a column-band placement question rather than a flow one.
* **80_gstin_table's worst case got worse** (79.7 → 90.8) although its median improved (5.8 →
  3.6) and 43 % of lines are now within 3 pt (was 16 %). That document also has the pre-existing
  reading-order failure (longest run in PDF order 11 % of lines, identical before and after) —
  its two-column key/value grid is interleaved, which is not a vertical-position defect.
* **303 and 318** are the two documents in the sample I would look at first if this is merged;
  both are form/table pages of the kind described above.

## 7. Gate and engine tests

```
$ python3 tools/p2w-bench/gate.py --corpus <corpus> --out <out> --baseline tools/p2w-bench/base208.json --check
documents: 208
IMPROVED: 3 counts
   62_two_col_newsletter_pull_quote           lines    32 -> 34
   journal-2col-with-footnotes                lines    60 -> 70
   newspaper-2col-fullwidth-headline          lines    60 -> 61
no document got worse
```

G1 (the engine's own tests, run with the assets directory on the classpath as
`verify-engine.sh` does):

```
TestPdfToWord  PDF2WORD TOTAL: 29 passed, 0 failed
TestRealDocs   REALDOCS TOTAL: 3 passed, 0 failed
   300_prescription_rx  96.8% ok   311_fir_police_form 97.0% ok   350_question_paper 81.7% ok
```

(Without `libs/aar/assets` on the classpath these two tests fail with
`resource '.../Times-Roman.afm' not found` and report 0.0 %; that is the harness needing the
assets directory, not this change — the same failure happens on the unmodified tree.)

## 8. How this was built and measured

```
git clone --depth 1 https://github.com/kavopdf/app W && cd W
# JDK 17 (Temurin) and the PDFBox-Android aar + BouncyCastle jars under /scratch/work/libs
cd tools/engine-verify && javac -nowarn -cp "$CP" -d out ../../app/src/main/java/com/kavopdf/app/engine/*.java
javac -nowarn -cp "$CP" -d out ConvertAll.java
java -Xmx900m -Djava.awt.headless=true -Dp2w.assets=libs/aar/assets -cp "$CP" ConvertAll <corpusdir> <outdir>
python3 tools/p2w-bench/verify_visual.py <pdf> <docx> --json
python3 tools/p2w-bench/gate.py --corpus <corpusdir> --out <outdir> --baseline tools/p2w-bench/base208.json --check
```

Two environment notes for reproducing: the 208 documents must be converted in chunks of ~50
(one JVM over all 208 dies with a native OOM in this sandbox at ~160 documents, not a code
fault), and `gate.py` reads a flat corpus directory, so the three release zips are unpacked into
one folder of 208 PDFs.

**Files changed:** `DocxWriter.java`, `PdfToWord.java`. Nothing else in the tree is touched; the
bench scripts, the baseline and the corpus are untouched.
