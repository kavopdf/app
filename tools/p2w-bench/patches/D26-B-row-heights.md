# D-26 cause 2 of 2 — table row heights: give every row the page's own pitch

**Patch** (against `kavopdf/app`, `app/src/main/java/com/kavopdf/app/engine/`), applied to a clean
`--depth 1` clone and built with `tools/verify-engine.sh`.

**Status: works, and the gate is clean — but only for tables whose rows the page bounds with
rules. The two headline documents in the bug report (80_gstin_pan_cin_ifsc_table,
79_inr_indian_digit_grouping_table) are tables found by whitespace alone, and this patch does
NOT change them.** Section 5 says exactly why, with the measurements that made me stop.

---

## 1. The bug, restated in the model

`DocxWriter.table()` wrote every row at the same height:

```java
int rowCount = Math.max(1, t.rows.size());
float extentPt = t.bottom - t.top;
int rowTw = extentPt > 0f ? (int) Math.round(extentPt / rowCount * TWIPS_PER_PT) : 0;
```

That is the table's extent divided by its row count — an **average**. It is the page's pitch only
when every row is the same height. A tall header row, a merged cell or one row of wrapped text
makes it wrong for every row, and each row then lands at a height the page never drew. That is
per row, not cumulative, which is what the -0.09 correlation between y and error was telling us.

The cell's line box had the same problem from the other side: `cellLineTw = rowTw` put a single
line at "the foot of the average row", which is the wrong place in any row that is not the
average height.

## 2. What the patch does

**`PdfToWord.java`** — the model now carries the page's own measurement, per row:

* `Table.rowH` — the row's height in points: the distance between the two horizontal rules that
  bound it. Filled by both rule-reading passes (`tableFromCells`, the grid pass in
  `buildTables`) and propagated through `keyValuePanels`, which re-orders rows.
* `Table.rowLead` — how far below its own top rule the row's first baseline was drawn, in points.
  A row of the right height is only half the job: the text still has to sit where the page put
  it inside that row.

**`DocxWriter.java`** — per row:

* `w:trHeight` is the row's own pitch instead of the average, and `w:hRule="exact"` when the
  pitch already holds the row's text (one line per `w:br`, each at `rowLineTw`). When the pitch
  is smaller than the text it stays `atLeast` and grows — `exact` clips, and a clipped row is a
  page the reader cannot read.
* A single-line cell's line box is `rowLead / LINE_BASE` (LINE_BASE is the already-measured 0.8
  of the line box where a baseline sits), so the baseline lands back on the page's.
* The border hairline is **not** subtracted from an exact row (an exact row is that height and
  nothing more) but is still subtracted on the average path, exactly as before.

### The diff

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 9216473..36de32a 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -2449,6 +2449,21 @@ public final class DocxWriter {
         // A cell that holds SEVERAL lines is the case that was wrong: charging the pitch to
         // every line charged the row twice over and doubled it. There the line is the cell's
         // own text - 1.25 em of its size, below - and the row stays the page's own pitch.
+        //
+        // THE PAGE'S OWN ROW PITCH. rowTw above is the table's extent divided by its row count,
+        // and that is an average: it is the page's pitch only when every row of the table is
+        // the same height, and a page with a tall header row, a merged cell or one row of
+        // wrapped text does not have even rows. Every row was then written at the average and
+        // each one landed at a height the page never drew - D-26 cause 2. It is per row, not
+        // cumulative: on 80_gstin_pan_cin_ifsc_table the correlation between y and error was
+        // -0.09 while 53 of 63 lines sat more than 3 pt off, and on
+        // invoice-line-items-qty-rate-amount every row was about 19 pt low.
+        //
+        // t.rowH is that pitch, measured by the pass that read the page: the distance between
+        // the two rules that bound each row. When the pass could not measure it - a table found
+        // by whitespace alone has no rules to measure between - the list is a different size and
+        // the average is used, exactly as before.
+        boolean perRowPitch = t.rowH.size() == t.rows.size();
         int cellLineTw = rowTw > 0 ? rowTw : 200;
         int naturalLineTw = rowTw > 0 ? Math.min(rowTw, 200) : 200;
         for (int r = 0; r < t.rows.size(); r++) {
@@ -2463,7 +2478,35 @@ public final class DocxWriter {
                 for (int i = 0; i < cv.length(); i++) if (cv.charAt(i) == '\n') n++;
                 if (n > rowParts) rowParts = n;
             }
+            // This row's own pitch, when the page gave one: the distance between the two rules
+            // that bound it, which is the height the page really gave the row. The average above
+            // is used only when the pass could not measure it.
+            int rowPitchRawTw = 0;
+            if (perRowPitch) {
+                float pitchPt = t.rowH.get(r);
+                if (pitchPt > 0.5f) rowPitchRawTw = (int) Math.round(pitchPt * TWIPS_PER_PT);
+            }
+            // The height the row is asked for is the page's own pitch, with nothing taken off for
+            // the rule the renderer draws inside it: a row written "exact" is that height and
+            // nothing more, and subtracting the hairline made every exact row 0.75 pt short
+            // (measured: a rendered pitch of 19.25 pt against the page's 20 on
+            // 79_inr_indian_digit_grouping_table). The average path keeps its old subtraction.
+            int rowPitchTw = rowPitchRawTw > 0 ? rowPitchRawTw : rowTw;
+            // A single line sits in its row where the PAGE drew it. rowLead is the distance
+            // from the row's top rule down to that line's baseline, and a line box puts its
+            // baseline at LINE_BASE of its own height - so a box of lead / LINE_BASE lands the
+            // baseline on the page's. Without this a row of the right height still put its text
+            // in the wrong place: on 23_timetable_grid_txtpos the rows are a uniform 40 pt and
+            // the page draws the period labels 16.8 pt into the row, while the table's average
+            // line box of 37.25 pt put them 24 pt in - every line 12 pt low, which is a bigger
+            // error than the row-height defect this change removes.
             int baseLineTw = rowParts > 1 ? naturalLineTw : cellLineTw;
+            if (rowParts == 1 && t.rowLead.size() == t.rows.size()) {
+                float leadPt = t.rowLead.get(r);
+                if (leadPt > 0.5f) {
+                    baseLineTw = (int) Math.max(1L, Math.round(leadPt * TWIPS_PER_PT / LINE_BASE));
+                }
+            }
             // The row's own line height, never smaller than its own text. cellLineTw is the
             // table's extent divided by its row count, which is an average - correct only when
             // the rows are evenly spaced. On a page with a tall header row, a merged cell or a
@@ -2495,15 +2538,30 @@ public final class DocxWriter {
             // already carries the type-size floor, so the floor is taken before the scaling and
             // the scaled row is held at it.
             int typeFloorTw = rowLineTw;
-            int rowHeightTw = Math.max(rowTw, rowLineTw);
+            int rowHeightTw = Math.max(rowPitchTw, rowLineTw);
             if (ctx.squeeze != 1f) {
                 rowHeightTw = Math.max(typeFloorTw, twScale(rowHeightTw, ctx.squeeze));
                 rowLineTw = Math.max(typeFloorTw, twScale(rowLineTw, ctx.squeeze));
+                rowPitchTw = Math.max(typeFloorTw, twScale(rowPitchTw, ctx.squeeze));
+            }
+            // How tall the cell's paragraphs really are: one line per w:br, each set at
+            // rowLineTw. hRule="exact" makes the row that height and CLIPS whatever is taller, so
+            // exact is only used when the page's own pitch already holds the row's text. A row
+            // whose pitch is smaller than its text keeps "atLeast" and grows: a clipped row is a
+            // page the reader cannot read, which is worse than a row 2 pt low.
+            int contentTw = rowLineTw * rowParts;
+            boolean rowExact = rowPitchRawTw > 0 && rowPitchRawTw >= contentTw;
+            if (rowExact) {
+                rowHeightTw = rowPitchRawTw;
+                if (ctx.squeeze != 1f) {
+                    rowHeightTw = Math.max(typeFloorTw, twScale(rowHeightTw, ctx.squeeze));
+                }
             }
             inner.append("<w:tr>");
-            if (rowTw > 0) {
+            if (rowTw > 0 || rowPitchTw > 0) {
                 inner.append("<w:trPr><w:trHeight w:val=\"").append(rowHeightTw)
-                     .append("\" w:hRule=\"atLeast\"/><w:cantSplit/></w:trPr>");
+                     .append("\" w:hRule=\"").append(rowExact ? "exact" : "atLeast")
+                     .append("\"/><w:cantSplit/></w:trPr>");
             }
             int c = 0;
             while (c < cols) {
diff --git a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
index 6aa9127..7a0df1f 100644
--- a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
+++ b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
@@ -221,6 +221,34 @@ public final class PdfToWord {
          * were thrown away here, because a cell is written as a string and a font name.
          */
         public final List<List<Integer>> colors = new ArrayList<>();
+        /**
+         * The height the PAGE gave each row, in points - one entry per row, in row order.
+         *
+         * <p>It is the distance between the two horizontal rules that bound the row. Empty when
+         * the pass that built the table did not measure it - a table found by whitespace alone
+         * draws no rules, and a band between two baselines is not a row box - in which case the
+         * writer falls back on the table's extent divided by its row count.
+         *
+         * <p>That average is the defect this list exists to remove: it is correct only when
+         * every row of the table is the same height, and a page with a tall header, a merged
+         * cell or one row of wrapped text does not have even rows. Each row then landed at a
+         * height the page never drew, which is D-26 cause 2 - 80_gstin_pan_cin_ifsc_table had
+         * 53 of its 63 lines more than 3 pt from where the page drew them, and the error was
+         * per row rather than cumulative (correlation between y and error -0.09).
+         */
+        public final List<Float> rowH = new ArrayList<>();
+        /**
+         * How far below its own top rule the first line of each row was drawn, in points - one
+         * entry per row, in row order. Empty when the pass did not measure it.
+         *
+         * <p>A row's height is only half of where its text lands: the other half is where in
+         * the row the page put it. On 23_timetable_grid_txtpos the rows are a uniform 40 pt and
+         * the page draws the period labels 16.8 pt below the row's top rule - so a row given the
+         * right height but the table's average line box still puts every line 12 pt low, which
+         * is what the render measured. The lead is a baseline, so the writer can place it
+         * exactly: a line box of lead / 0.8 puts its baseline back on the page's.
+         */
+        public final List<Float> rowLead = new ArrayList<>();
         public boolean header;
         /**
          * Did the page draw the lines that make this a table?
@@ -4833,6 +4861,21 @@ public final class PdfToWord {
         cx[ncol] = right;
         t.colX = cx;
         t.header = nrow > 1;
+        // The page's own row pitch: the two rules that bound each row. R holds the top edge of
+        // every row, in ascending y, so row r runs from R[r] to R[r+1] - and the last row runs
+        // to the bottom of the lowest cell, which is where the page's last rule is.
+        for (int r = 0; r < nrow; r++) {
+            float yTop = R.get(r);
+            float yBot = r + 1 < nrow ? R.get(r + 1) : bottom;
+            t.rowH.add(Math.max(0f, yBot - yTop));
+            // The baseline of the first line the page drew in this row, measured from the
+            // row's own top rule - the vertical half of the same measurement.
+            float base = Float.MAX_VALUE;
+            for (int c = 0; c < ncol; c++) {
+                for (Glyph g : buckets.get(r).get(c)) base = Math.min(base, g.y);
+            }
+            t.rowLead.add(base == Float.MAX_VALUE ? 0f : Math.max(0f, base - yTop));
+        }
         int filled = 0;
         for (int r = 0; r < nrow; r++) {
             List<String> row = new ArrayList<>();
@@ -5176,6 +5219,10 @@ public final class PdfToWord {
             // at its rule: it is wherever the page drew it, centred, right-aligned or padded.
             float[][] firstX = new float[rows][cols];
             for (float[] rowX : firstX) java.util.Arrays.fill(rowX, Float.NaN);
+            // The topmost baseline in each row, so the writer can put the text back where the
+            // page drew it inside the row it now measures correctly.
+            float[] rowBaseY = new float[rows];
+            java.util.Arrays.fill(rowBaseY, Float.MAX_VALUE);
             for (Line line : lines) {
                 float cx = (line.x + line.right) / 2f;
                 int r = band(ys, line.y);
@@ -5186,6 +5233,7 @@ public final class PdfToWord {
                 if (faces[r][c] == null) faces[r][c] = fontOf(line.glyphs);
                 if (Float.isNaN(sizes[r][c])) sizes[r][c] = sizeOf(line.glyphs);
                 if (Float.isNaN(firstX[r][c])) firstX[r][c] = visibleX(line.glyphs, line.x);
+                if (line.y < rowBaseY[r]) rowBaseY[r] = line.y;
             }
 
             int filled = 0;
@@ -5237,6 +5285,14 @@ public final class PdfToWord {
             colX[cols] = right;
             t.colX = colX;
             t.header = rows > 1;
+            // ys are the page's own horizontal rules, so the row pitch is the gap between two
+            // of them - measured, not the region's height divided by its row count.
+            for (int r = 0; r < rows; r++) {
+                float yTop = ys.get(r);
+                t.rowH.add(Math.max(0f, ys.get(r + 1) - yTop));
+                t.rowLead.add(rowBaseY[r] == Float.MAX_VALUE
+                        ? 0f : Math.max(0f, rowBaseY[r] - yTop));
+            }
             for (int r = 0; r < rows; r++) {
                 List<String> row = new ArrayList<>();
                 List<String> rowFonts = new ArrayList<>();
@@ -5469,6 +5525,16 @@ public final class PdfToWord {
             t.colors.add(textCols);
         }
         t.bottom = bottom;
+        // A table the whitespace pass found has no rules of its own, so it has no rows to
+        // measure: its bounds are its TEXT's baselines and the band between two baselines is
+        // not a row box. Giving its rows the baseline deltas was measured and rejected - the
+        // rows of 80_gstin_pan_cin_ifsc_table came out 16/14/14/14 pt, whose sum is 58 pt
+        // against the 44 pt its own extent charges the flow, and each of its five dealer blocks
+        // pushed the next one 11 pt further down the page (median dy 5.8 -> 24.3). Using the
+        // page's drawn rules instead fixed the pitch on 79_inr_indian_digit_grouping_table but
+        // only by moving the table's bottom onto the rule box, which made the table swallow the
+        // next line: 326_itr_computation lost "Tax before cess 1,82,100" from its slab table.
+        // The rows of these tables stay unmeasured and the writer keeps its average.
         float[] cx2 = new float[columns.size() + 1];
         for (int i = 0; i < columns.size(); i++) cx2[i] = columns.get(i);
         cx2[columns.size()] = Math.max(right, columns.get(columns.size() - 1));
@@ -5610,6 +5676,9 @@ public final class PdfToWord {
             out.cellX.add(new ArrayList<>(java.util.Arrays.asList(xOf(t, r, c), Float.NaN)));
             out.cellR.add(new ArrayList<>(java.util.Arrays.asList(rOf(t, r, c), Float.NaN)));
             out.colors.add(new ArrayList<>(java.util.Arrays.asList(colorOf(t, r, c), -1)));
+            // The heading keeps its own row height, taken from the row it came from.
+            if (t.rowH.size() == t.rows.size()) out.rowH.add(t.rowH.get(r));
+            if (t.rowLead.size() == t.rows.size()) out.rowLead.add(t.rowLead.get(r));
         }
         for (int side = 0; side < 2; side++) {
             int from = side == 0 ? 0 : split;
@@ -5631,6 +5700,9 @@ public final class PdfToWord {
                         rOf(t, r, a), b < 0 ? Float.NaN : rOf(t, r, b))));
                 out.colors.add(new ArrayList<>(java.util.Arrays.asList(
                         colorOf(t, r, a), b < 0 ? -1 : colorOf(t, r, b))));
+                // A panel row is still the row the page drew, at the page's own pitch.
+                if (t.rowH.size() == t.rows.size()) out.rowH.add(t.rowH.get(r));
+                if (t.rowLead.size() == t.rows.size()) out.rowLead.add(t.rowLead.get(r));
             }
         }
         // The label column is as wide as the left panel's label column was; the value column
```

## 3. Proof — `verify_visual.py` on the five documents

Each row is `python3 tools/p2w-bench/verify_visual.py <source.pdf> <generated.docx>`; "before" is
the unpatched engine, "after" is the patch. Both are the same 208-document corpus conversion.

| document | | median dy | worst dy | within 3 pt | within 10 pt |
|---|---|---|---|---|---|
| 80_gstin_pan_cin_ifsc_table | before | 5.8 pt | 79.7 pt | 16% | 95% |
| | after | 5.8 pt | 79.7 pt | 16% | 95% |
| 79_inr_indian_digit_grouping_table | before | 2.3 pt | 9.0 pt | 61% | 100% |
| | after | 2.3 pt | 9.0 pt | 61% | 100% |
| 23_timetable_grid_txtpos | before | 6.8 pt | 12.1 pt | 15% | 76% |
| | **after** | **6.0 pt** | **6.0 pt** | 12% | **100%** |
| invoice-line-items-qty-rate-amount | before | 19.4 pt | 22.3 pt | 5% | 12% |
| | **after** | **14.9 pt** | **21.1 pt** | 5% | 12% |
| gst-invoice-multipage-item-table | before | 8.5 pt | 380.4 pt | 2% | 59% |
| | **after** | **1.5 pt** | 381.2 pt | **54%** | 60% |

Page counts and line counts are unchanged in all five (1/1, 1/1, 1/1, 1/1, 4/4; lines 68, 48,
66, 87, 373). The reading-order shares are unchanged (11%, 100%, 21%, 21%, 5%) — this change is
about y, not about order.

### What the numbers say, honestly

* **gst-invoice-multipage-item-table** is the clearest win: median dy 8.5 → 1.5 pt and the share
  of lines within 3 pt 2% → 54%, over 373 lines on four pages. Its item rows have a genuinely
  uneven pitch (18/18/19/18/19…) and the average was wrong for every one of them.
* **23_timetable_grid_txtpos**: the rows are now exactly the page's 40 pt (rendered rule pitch
  measured at 40.0 against the page's 40.0, was 38.3), and every line is within 10 pt. But the
  share within 3 pt **fell** from 15% to 12%, because what is left is a single constant offset
  (all 66 lines sit 6.0 pt low, spread 0.0) instead of a drift that happened to cross zero in the
  middle of the table. The drift is gone; the constant is the pre-existing table-top offset
  described below, which used to be masked by the drift.
* **invoice-line-items-qty-rate-amount**: 19.4 → 14.9 pt. Its table's rows were already
  rule-measured and consistent; what moved is the text inside them. Its residual is also the
  table-top offset, which on this page is ~15 pt.
* **80_gstin_pan_cin_ifsc_table and 79_inr_indian_digit_grouping_table: no change at all.** Both
  are whitespace tables (see §5). I did not make them worse, and I did not make them better.

**The remaining constant.** Once the rows stop drifting, what is left on 23 and 79 is one number
per page: the table's top rule lands a few points below where the page drew it (5.2 pt on 79,
6.0 pt on 23, ~15 pt on the invoice). That is a different, pre-existing defect — it is written
down in `DocxWriter.table()` itself ("MEASURED AND REVERTED: … the table's own top y is recorded
in REMAINING-DEFECTS.md and is not fixed here") — and I left it alone. With the drift gone it is
now the largest single error on every table page, so it is the next thing to fix.

## 4. The gate — 208 documents

```
$ python3 tools/p2w-bench/gate.py --corpus /scratch/work/corpus/flat \
      --out /scratch/work/out_final --baseline tools/p2w-bench/base208.json --check
documents: 208
no document got worse
```

Corpus: `pdf-to-word-test-corpus-v3.zip` (75) + `p2w-batch-1.zip` (80) + `p2w-all-groups.zip`
(53), 208 PDFs, all converted (208 files, 0 failed).

`tools/verify-engine.sh` also passes on the patched tree: engine 81/81, hostile input 9/9,
image PDF 41/41, cache policy 16/16, stalls 10/10, repair 188/188, detector norms 13/13, real
documents 3/3, fonts PASS.

`hRule="exact"` fires on 1418 rows across 74 of the 208 documents; the rest stay `atLeast`.

## 5. What did NOT work, and why (measured, then reverted)

The two documents the bug report leads with are **whitespace tables**: the page draws no grid
inside them (80 draws only the page frame at y=80 and y=793.9; 79 draws six horizontal rules and
no vertical rule at all), so `findTables`/`buildTables` find nothing and `buildRowTable` builds
the table from cell positions instead. For those, `t.top`/`t.bottom` are the **text's baselines**,
not a rule box.

Three things were tried on them, each built, converted over all 208 and measured:

1. **Row pitch from the baseline deltas** (`rowH[r] = y[r+1] - y[r]`, last row repeats).
   80_gstin: rows 16/14/14/14 pt — individually right — but they sum to 58 pt against the 44 pt
   its own extent charges the flow, and each of the five dealer blocks pushed the next one ~11 pt
   down the page. **Median dy 5.8 → 24.3 pt, worst 79.7 → 139.7.** Reverted.
2. **Row pitch from the page's drawn rules**, which 79 does have, by anchoring the rule window to
   the row baselines (`windowFits`) and moving the table's bounds onto the rule box
   (`t.bottom = t.top + sum(rowH)`). 79's rows became exactly 20.0 pt and its rendered rule pitch
   exactly matched the page — **but the gate failed**: `326_itr_computation` lost "Tax before
   cess 1,82,100" and `04_stamp_180deg_upside_down` lost "Total 77,020.00". Moving the bottom
   down over the next row's baseline makes the table *own* that line and it is never written.
   Reverted.
3. **Same rule window, but also moving `t.top` onto the first rule** (the table's bounds become
   the rule box, which is what the ruled pass has): 79's rows and its table box were then exactly
   right, but the table jumped **13.4 pt up the page** (rendered top rule 126.6 against the page's
   140.0, median dy -11.7) because the spacer that positions a table in the flow is calibrated on
   `t.top` being a *baseline*, not a rule. Reverted.

So the honest position: the page's row pitch is only knowable where the page draws the row
boundaries, and a whitespace table's bounds are a different kind of object. Fixing 80 and 79
needs the whitespace pass to own a rule box (and to stop swallowing the line below it) before it
can own a pitch. That is a bigger change than this one and it is not in this patch.

## 6. Cell margins (item 3 of the brief)

No change was needed: `w:tblCellMar` is already `0` on all four sides for every table
(`DocxWriter` line ~2402) and again in the `TableNormal` style, so nothing is added to the row
height there. I verified this rather than assuming it — the measured row pitch matches the asked
`w:trHeight` to within 0.1 pt on the rule-measured tables, which it could not do with a non-zero
cell margin.

## 7. Files

* `D26-B.patch` — the diff above as a file (apply with `git apply`).
* Every measurement in this report is reproducible with
  `tools/p2w-bench/verify_visual.py` and `tools/p2w-bench/gate.py` on the corpus in the brief.
