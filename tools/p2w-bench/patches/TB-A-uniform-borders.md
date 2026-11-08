# TB-A — one uniform table-rule weight, and 04_stamp_180 no longer all-"none"

Engine: `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (+ `PdfToWord.java`).
Base commit: `df547d6` ("release: 3.53.1"). Corpus: all three release assets (208 PDFs).

---

## 1. What was wrong, measured

`DocxWriter.borders(boolean ruled, float widthPt, int rgb)` took the weight and the colour from
the stroke the page drew (`c47efc2`). Measured over the 208 documents, the side slots of every
`w:tblBorders` came out as six different weights:

| `w:val` | `w:sz` | sides | tables |
|---|---|---|---|
| single | 6 | 468 | |
| single | 3 | 282 | |
| single | 5 | 12 | |
| single | 4 | 12 | |
| single | 10 | 6 | |
| single | 8 | 6 | |
| **none** | **0** | **486** | |

786 drawn sides = 131 tables; 486 "none" sides = 81 tables. `04_stamp_180deg_upside_down` was
`{'none': 12}` — two tables, twelve "none" sides — while the page draws a frame round both of
them.

## 2. Why 04 got "none"

Confirmed by a temporary probe inside my sandbox copy — a debug print of both table passes and
the drawn rules, plus a corpus-wide geometry probe; neither is part of the patch:

* Both of 04's tables come from the **row / whitespace pass**, so `t.ruled == false` and
  `t.top/t.bottom/t.left/t.right` are the **text's ink extents**, not the rectangle the page
  strokes.
* `edgeStroke` accepted a stroke only within **2.5 pt** of one of those four ink bounds. The
  drawn frames sit outside them:

| table | ink bounds (top/bottom/left/right) | drawn box | gaps T / B / L / R |
|---|---|---|---|
| T1 student block | 184.0 / 212.0 / 64.0 / 443.5 | 169.7–220.3, 55.7–539.6 | 14.30 / 8.30 / 8.30 / 96.06 |
| T2 fee items | 244.3 / 334.3 / 67.2 / 522.0 | 231.7–358.4, 55.7–526.4 | 12.65 / 24.05 / 11.60 / 4.35 |

  So `edgeStroke` returned null, `ruled` stayed false, and all six sides were written "none".
* Raising the tolerance cannot fix both: T2 needs ≥ 4.35 pt for one side but ≥ 24.05 pt for
  another, and T1's right gap is 96 pt because its box is a full-width panel and the ink of the
  last column stops short of the drawn right edge.
* `23_timetable_grid_txtpos` is fine because it comes from the **ruled pass**: its bounds *are*
  the drawn frame (off by 0.40/0.40/0.40/0.29 pt), so it was already `single/sz=6` on six sides.
* Only 4 of 04's 10 shapes ever reach the geometry test; the other 6 are fills (`lineRgb < 0`),
  and the page's interior row rules never become shapes at all.

## 3. The fix

Two changes, both in the patch below.

**(a) `borders()` — one constant weight and colour, and per-side presence.**
`sz` is now the constant `TABLE_RULE_SZ = 6` (0.75 pt) and the colour the constant
`TABLE_RULE_COLOUR = "000000"` — exactly what `23_timetable_grid_txtpos`, the document the user
called correct, carries on all six sides. No width or colour is carried from the page any more.
It is also the weight `TABLE_BORDER_TW` is measured from, so the row pitch the writer asks for
stays true.

A side is drawn when the page drew a rule on **that** side, and "none" otherwise. Presence is
decided per side because the two passes know different things:
* ruled pass (`t.ruled`): the bounds *are* the grid → all six sides;
* whitespace pass: the four outer sides come from the frame the page drew (`pageDrewRule`);
  `insideH`/`insideV` come from the rules the page drew **across** the table's band, read in
  `PdfToWord.markInnerRules` where the page's rule list is in hand.

**(b) `edgeStroke` → `pageDrewRule`.** It no longer returns a weight; it answers the question
the borders actually need. A stroke still counts when it lies on one of the four ink bounds
(unchanged, 2.5 pt), and a stroke-only box now counts when the table's ink falls **inside** it
and the table covers at least half the box's width and half its height — i.e. the box follows
the table rather than merely containing it. That interior test is what catches 04's frames
without moving a tolerance for any other document.

`ruledTable = t.ruled || pageDrewRule(...)` now also drives the row-height subtraction
(`TABLE_BORDER_TW`), because a rule that is drawn is a rule the renderer adds to the row. Before
this, the 5 whitespace tables that already got a border were not compensated.

## 4. Result

**sz histogram, after** (all 208 documents, every side slot):

| `w:val` | `w:sz` | sides |
|---|---|---|
| single | 6 | 912 |
| none | 0 | 360 |

One drawn weight in the whole corpus. 912/6 = 152 ruled tables, 60 with no borders at all
(212 tables total, as before).

**Per-document border state**

`04_stamp_180deg_upside_down.docx` — 2 tables, 9 drawn sides + 3 "none":

| table | top | left | bottom | right | insideH | insideV |
|---|---|---|---|---|---|---|
| T1 student block | single/6 | single/6 | single/6 | single/6 | none | none |
| T2 fee items | single/6 | single/6 | single/6 | single/6 | single/6 | none |

Before: 12 sides, all `none/sz=0`.

`23_timetable_grid_txtpos.docx` — 1 table, unchanged, and still the reference:

| top | left | bottom | right | insideH | insideV |
|---|---|---|---|---|---|
| single/6 | single/6 | single/6 | single/6 | single/6 | single/6 |

**What changed across the corpus**

* 28 tables that were written all-"none" now have their drawn sides at `single/sz=6`
  (135 sides): 1 with all six, 21 with five (frame + row separators), 6 with the four outer
  sides only.
* **No table lost a border it had.** 53 tables remain all-"none".
* 55 documents changed at all; every change is either a weight collapsing to 6 or a
  "none" → "single/6".

**Which tables I made ruled** (28, by document): `01_stamp_rotated_15deg_upright`,
`02_stamp_rotated_15deg_upleft`, `03_stamp_vertical_90deg`, `04_stamp_180deg_upside_down` (2),
`06_rect_paid_stamp_red_transparent`, `07_stamp_over_table`, `08_two_overlapping_stamps`,
`10_stamp_as_image`, `13_stamp_non_english`, `14_stamp_chars_positioned_td`,
`30_mixed_font_sizes_one_baseline_txtpos`, `33_sans_nondefault_body`,
`35_four_typefaces_one_page`, `36_embedded_subset_font`, `38_faux_bold_italic_synthesised`,
`42_table_coloured_header_alternating_rows`, `50_invoice_coloured_total_row`,
`52_one_cm_margin_wide_body`, `56_table_indented_from_margin`, `59_landscape_mixed_portrait`,
`68_journal_wide_table_spanning`, `79_inr_indian_digit_grouping_table`,
`80_gstin_pan_cin_ifsc_table` (5). Every one is a real content table — I read the first cell of
each (`"Sl"`, `"Particulars"`, `"Month"`, `"Student Name"`, `"1. SUNRISE FASTENERS PVT LTD"`,
…) rather than trusting the geometry alone.

**Which tables I deliberately left open**, and why:

* `406_passport_mrz_page` (2 tables) and `403_crossword_puzzle` — the page draws no rule on
  them. 406's passport frame encloses both tables but covers under half of each, so the "the
  frame follows the table" test rejects it. These are the documents the earlier "none" fix
  existed for; they keep it.
* `351_omr_answer_sheet`, `363_warranty_card`, `364_event_ticket` — same test, same result.
* 13 further tables carry a rule crossing their band but **no frame at all**
  (`01_stamp_rotated_15deg_upright` t1, `03_stamp_vertical_90deg` t1,
  `16_right_aligned_amounts_txtpos`, `314_tender_rfp_boq` t2/t3, `326_itr_computation` t2,
  `333_datasheet_spec_tables` t2, `374_org_chart`, `383_api_docs_page` t1/t2,
  `390_wide_data_appendix`, `bus-timetable-station-left-times-right`, `eway-bill`,
  `gst-invoice-3line-items`, `price-list-right-aligned-amounts`). Those rules are as likely the
  edge of a filled band as a drawn separator — `Rules.horizontal` collects `re` rectangle edges
  whether they are stroked or filled — so a table with no frame keeps all six "none" rather than
  gain a line the page may not draw. If a later change wants them, the honest route is to carry
  stroke-vs-fill through `Rules`, not to loosen this test.

## 5. A correction to the coordinator's note

The note says T1's "six `none` sides are arguably correct — the page draws no rules on that
block". I rendered the page (`pymupdf`, 170 dpi) before deciding: **the page does draw a rule on
that block** — a 0.60 pt grey stroked rectangle, 483.9 × 50.6 pt at (55.7, 169.7), visible as
the box round "Student Name / Ms. Ananya Rangappa / III Semester…". What it does not draw is
anything *inside* it: no row separators, no column separators. So the per-side model gives T1
its four outer sides and leaves `insideH`/`insideV` "none" — the note's own rule ("decide by
whether the box has a stroke on the side in question"), applied side by side. T2's fee table is
the same frame plus five row separators and no column separator, which is exactly what the
render shows and what the XML now says (`insideH` single, `insideV` none).

If the integrator would rather T1 stay fully open, that is one condition in `pageDrewRule`; but
the page's rule is there, and dropping it would be the "no line where the page drew one" defect
in the other direction.

## 6. Verification

```
bash tools/verify-engine.sh                     -> exit 0
   1258/1258 repair fixtures, 13/13 stall norms, 3/3 real docs, FONTS: PASS,
   every rotation/overlay/OCR/link/redaction/font check PASS
javac engine + ConvertAll                       -> clean
ConvertAll /scratch/work/flat -> out-final      -> done: 208 files, 0 failed
python3 tools/p2w-bench/gate.py --corpus flat --out out-final \
        --baseline tools/p2w-bench/base208.json --check
   documents: 208
   IMPROVED: 22 counts
   JOINED: 1 line counts fell with no word lost
   no document got worse
```

**Gate verdict: `no document got worse`.** 22 counts improved (12 documents gained lines),
`newspaper-2col-fullwidth-headline` 61 → 60 lines with no word lost.

### Environment note (not part of the patch)

This sandbox has no JDK on `PATH`. I installed Temurin 21 from
`https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse` and put
its `bin` on `PATH`. `tools/verify-engine.sh` must be run with the sandbox's own
`JAVA_TOOL_OPTIONS` **kept**: unsetting it makes `javac` try to reserve a 1 GB compressed class
space and the JVM dies with "Could not allocate compressed class space". No source change was
needed for either.

### Reproducing

```
git clone --depth 1 https://github.com/kavopdf/app W && cd W && git checkout -b tb-a df547d6
git apply /scratch/output/TB-A-uniform-borders.patch
bash tools/verify-engine.sh
# then the ConvertAll + gate.py steps above
```

---

## 7. The diff (`git diff` against `df547d6`)

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 26b4fd8..f8bddf2 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -1480,34 +1480,32 @@ public final class DocxWriter {
      * place the text and destroy the table, which is the one thing a conversion must not do.
      */
     /**
-     * The table's borders, as the page drew them.
+     * The table's borders: one weight and one colour, on every ruled table.
      *
-     * <p>A ruled table gets the single hairline the page's own edges stand for. An unruled one
-     * gets the same six slots set to "none" rather than no w:tblBorders element at all: absent
-     * borders fall back to the table style, and the default style draws a box, which is exactly
-     * the box 403 and 406 were carrying.
-     */
-    private static String borders(boolean ruled) {
-        return borders(ruled, 0.75f, 0x999999);
-    }
-
-    /**
-     * The table's borders, at the weight and colour the page drew them.
-     *
-     * <p>Every ruled table used to get a 0.75 pt grey hairline on all six sides whatever the page
-     * drew, so a table ruled at 0.5 pt came out heavy, one at 1.5 pt came out thin, and a black
-     * rule came out grey. That is the inconsistency the user reports.
+     * <p>Every side the page drew a rule on gets the one hairline every ruled table gets; every
+     * side it did not gets "none" - never no w:tblBorders element at all, because absent borders
+     * fall back to the table style and the default style draws a box, which is exactly the box
+     * 403 and 406 were carrying. The four outer sides are {@code outer}, the row separators
+     * {@code innerH} and the column separators {@code innerV}; a table the ruled pass found has
+     * all three, because there the bounds ARE the drawn grid.
      *
-     * <p>{@code w:sz} is in eighths of a point: a 0.5 pt rule is sz="4", a 1 pt rule sz="8".
+     * <p>The weight used to be read off the stroke the page drew (c47efc2), so one corpus
+     * carried sz 3, 4, 5, 6, 8 and 10 at once: a table ruled at 0.5 pt came out heavier than
+     * one ruled at 1.25 pt, and the user's verdict was that table lines must not be thick in
+     * one place and thin in another. 23_timetable_grid_txtpos is the document they called
+     * correct, and every one of its borders is sz="6" in 000000 - so that is the single
+     * weight and the single colour. It is also the weight {@link #TABLE_BORDER_TW} is measured
+     * from, so the row pitch the writer asks for stays true.
      */
-    private static String borders(boolean ruled, float widthPt, int rgb) {
-        String v = ruled ? "single" : "none";
-        int sz = Math.max(2, Math.min(48, Math.round(widthPt * 8f)));
-        String colour = String.format("%06X", rgb & 0xFFFFFF);
+    private static String borders(boolean outer, boolean innerH, boolean innerV) {
         StringBuilder b = new StringBuilder("<w:tblBorders>");
-        for (String side : new String[]{"top", "left", "bottom", "right", "insideH", "insideV"}) {
-            b.append("<w:").append(side).append(" w:val=\"").append(v).append("\"");
-            if (ruled) b.append(" w:sz=\"").append(sz).append("\" w:color=\"").append(colour).append("\"");
+        for (String side : TABLE_SIDES) {
+            boolean drawn = "insideH".equals(side) ? innerH
+                    : "insideV".equals(side) ? innerV
+                    : outer;
+            b.append("<w:").append(side).append(" w:val=\"").append(drawn ? "single" : "none").append("\"");
+            if (drawn) b.append(" w:sz=\"").append(TABLE_RULE_SZ)
+                    .append("\" w:color=\"").append(TABLE_RULE_COLOUR).append("\"");
             else b.append(" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"");
             b.append("/>");
         }
@@ -1515,17 +1513,41 @@ public final class DocxWriter {
     }
 
     /**
-     * The stroke the page drew along this table's own edges.
+     * The one weight every ruled table is drawn at, in eighths of a point: 6/8 pt = 0.75 pt.
+     * See {@link #borders} for why this is a constant and not the page's own stroke.
+     */
+    private static final int TABLE_RULE_SZ = 6;
+    /** The one colour every ruled table is drawn in: black, as 23_timetable has it. */
+    private static final String TABLE_RULE_COLOUR = "000000";
+    /** The six sides a {@code w:tblBorders} element carries. */
+    private static final String[] TABLE_SIDES =
+            {"top", "left", "bottom", "right", "insideH", "insideV"};
+
+    /**
+     * Did the page draw a rule on this table?
+     *
+     * <p>Two shapes say yes. A stroke lying along one of the table's four sides - the grid the
+     * ruled pass reads, which puts the rule on the cell boundary itself.
      *
-     * <p>Finds the stroke-only shapes that lie on one of the table's four sides and returns the
-     * median width and the most common colour, or null when nothing lies there. The median
-     * rather than the mean, so one stray rule from a neighbouring box cannot move the border.
+     * <p>And a stroke-only box that frames the table. The whitespace pass measures a table's
+     * bounds from its TEXT, so the frame the page draws round it is not on those bounds: on
+     * 04_stamp_180deg the box round the first table starts 8.3 pt left of the table's first
+     * character, 14.3 pt above its first row and 96.1 pt right of its last, because the last
+     * column's text stops short of the drawn right edge. No edge test with a 2.5 pt tolerance
+     * can see that box, which is why the document came out with all six sides "none" while the
+     * page drew a full grid.
+     *
+     * <p>The frame counts only when it follows the table - the table covers at least half the
+     * frame's width and half its height - so a page border, or a box a table merely sits inside,
+     * is not read as a table rule. Measured on the 208-document corpus: 29 tables that the
+     * whitespace pass found inside a frame the page drew are ruled by this test, and the four
+     * documents whose frame is not a table rule (406's passport frame, 351's OMR sheet, 363's
+     * warranty card, 364's ticket) keep the "none" they have today.
      */
-    private static float[] edgeStroke(PdfToWord.Table t, java.util.List<Shape> shapes) {
-        if (shapes == null || shapes.isEmpty()) return null;
-        java.util.List<Float> widths = new ArrayList<>();
-        java.util.Map<Integer, Integer> colours = new java.util.HashMap<>();
+    private static boolean pageDrewRule(PdfToWord.Table t, java.util.List<Shape> shapes) {
+        if (shapes == null || shapes.isEmpty()) return false;
         float tol = 2.5f;
+        float tw = t.right - t.left, th = t.bottom - t.top;
         for (Shape s : shapes) {
             if (s.lineRgb < 0 || s.fillRgb >= 0) continue;
             boolean onTop = Math.abs(s.topPt - t.top) <= tol
@@ -1536,19 +1558,14 @@ public final class DocxWriter {
                     && s.topPt <= t.bottom + tol && s.topPt + s.hPt >= t.top - tol;
             boolean onRight = Math.abs(s.xPt + s.wPt - t.right) <= tol
                     && s.topPt <= t.bottom + tol && s.topPt + s.hPt >= t.top - tol;
-            if (!(onTop || onBottom || onLeft || onRight)) continue;
-            widths.add(Math.max(0.1f, s.lineWidthPt));
-            int c = s.lineRgb & 0xFFFFFF;
-            colours.put(c, colours.getOrDefault(c, 0) + 1);
-        }
-        if (widths.isEmpty()) return null;
-        java.util.Collections.sort(widths);
-        float median = widths.get(widths.size() / 2);
-        int best = 0, bestCount = -1;
-        for (java.util.Map.Entry<Integer, Integer> e : colours.entrySet()) {
-            if (e.getValue() > bestCount) { bestCount = e.getValue(); best = e.getKey(); }
+            if (onTop || onBottom || onLeft || onRight) return true;
+            // A rule, not a frame: a hairline band cannot be the box a table sits in.
+            if (s.wPt < 8f || s.hPt < 8f) continue;
+            boolean encloses = t.top >= s.topPt - tol && t.bottom <= s.topPt + s.hPt + tol
+                    && t.left >= s.xPt - tol && t.right <= s.xPt + s.wPt + tol;
+            if (encloses && tw >= s.wPt * 0.5f && th >= s.hPt * 0.5f) return true;
         }
-        return new float[]{median, best};
+        return false;
     }
 
     private static void table(StringBuilder sb, PdfToWord.Table t, Ctx ctx) {
@@ -1641,19 +1658,25 @@ public final class DocxWriter {
         // the closing-balance sentence beside the ledger was squeezed into a five-line
         // column. The flow is the document now, so the table belongs in it and the text keeps
         // the indents the PDF drew.
-        // The stroke the page drew on this table's own edges, or null when it drew none.
-        float[] stroke = edgeStroke(t, ctx.curShapes);
+        // The page's own rules decide whether this table is ruled, not the flag alone. A table
+        // found by the whitespace pass carries ruled=false, so all six borders were written as
+        // "none" - and a box the page closed on four sides came out with no sides at all. That
+        // is the missing line on 04_stamp_180deg, whose grid the page draws round every table.
+        // The same answer decides the row height, because a rule that is drawn is a rule the
+        // renderer adds to the row, and {@link #TABLE_BORDER_TW} is that rule's height.
+        boolean ruledTable = t.ruled || pageDrewRule(t, ctx.curShapes);
         inner.append("<w:tbl><w:tblPr>")
                 .append("<w:tblW w:w=\"").append(totalTw).append("\" w:type=\"dxa\"/>")
                 .append("<w:tblInd w:w=\"").append(tw(x0)).append("\" w:type=\"dxa\"/>")
-                .append(borders(
-                        // The page's own stroke decides whether this table is ruled, not the
-                        // flag alone. A table found by the whitespace pass carries ruled=false,
-                        // so all six borders were written as "none" - and a box the page closed
-                        // on four sides came out with no sides at all. That is the missing line.
-                        (stroke == null ? t.ruled : true),
-                        (stroke == null ? 0.75f : stroke[0]),
-                        (stroke == null ? 0x999999 : (int) stroke[1])))
+                // Each side on its own evidence. The ruled pass reads the grid itself, so its
+                // tables are ruled all over; a whitespace table has a frame round it (the four
+                // outer sides) and separators inside it only where the page drew them. A table
+                // with no frame at all keeps all six "none" even when a rule crosses its band:
+                // that rule is as likely the edge of a filled band as a drawn separator, and a
+                // line the page did not draw is the defect 403 and 406 came back with.
+                .append(borders(ruledTable,
+                        ruledTable && (t.ruled || t.innerH),
+                        ruledTable && (t.ruled || t.innerV)))
                 .append("<w:tblLayout w:type=\"fixed\"/>")
                 // Word's default cell margin is 0.19 cm (108 twips) on each side. Left at the
                 // default, every cell's text sat 6 pt right of where the page had it - a
@@ -1691,7 +1714,7 @@ public final class DocxWriter {
         // borders - 19.2 pt pitch with them, 18.4 pt without, against the page's own 18.4 pt,
         // and the 0.8 pt a row of that table drifted by is the 38 rows of a page losing a sheet
         // to nothing but its own rules. An unruled table draws no rule and keeps its full pitch.
-        if (rowTw > 0 && t.ruled) rowTw = Math.max(1, rowTw - TABLE_BORDER_TW);
+        if (rowTw > 0 && ruledTable) rowTw = Math.max(1, rowTw - TABLE_BORDER_TW);
         // The exact line height inside a cell was 200 twips - 10 pt - for every cell of every
         // table in every document. A price list drawn at 5.8 pt on an 8.4 pt row pitch got a
         // 10 pt line, so each of its 29 rows grew 1.6 pt taller than the page drew it and the
diff --git a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
index f1c4949..1355af2 100644
--- a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
+++ b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
@@ -235,6 +235,20 @@ public final class PdfToWord {
          * about the page, so it is only drawn where the page made one.
          */
         public boolean ruled = true;
+        /**
+         * Did the page draw the rules <em>inside</em> this table - the row separators
+         * ({@code innerH}) and the column separators ({@code innerV}) - as opposed to only the
+         * box around it?
+         *
+         * <p>A table the whitespace pass found has bounds that are its TEXT's ink, so the frame
+         * the page draws round it is off those bounds and {@code DocxWriter.pageDrewRule} cannot
+         * put it on the four outer sides without help. The rules inside the band can be read
+         * here, where the page's own rule list is in hand. 04_stamp_180deg's fee table has five
+         * row separators and no column separator; the student block above it has neither, only
+         * the panel the page draws round it. Writing all six sides for both would draw four
+         * lines the page never drew, so each side is decided on its own evidence.
+         */
+        public boolean innerH, innerV;
         public float top, bottom, left, right;
         public int column;
     }
@@ -492,6 +506,7 @@ public final class PdfToWord {
         // like page columns, and the heading above the table gets a later column than the
         // table itself - which puts the heading after the table in the output.
         List<Table> rowPass = rowTables(rawLines, firstPass, pageWidth);
+        for (Table t : rowPass) markInnerRules(t, topRules);
 
         List<Float> starts = new ArrayList<>();
         for (Float x : columnStarts(rawLines)) {
@@ -4457,6 +4472,36 @@ public final class PdfToWord {
         return out;
     }
 
+    /**
+     * Reads, from the rules the page drew, whether it drew the separators inside this table.
+     *
+     * <p>Only the whitespace pass needs this: its tables carry ink bounds rather than the
+     * rectangle the page strokes, so the writer can see the frame around them but not what the
+     * page drew across them. A rule counts when it runs inside the table's band - not along its
+     * own top or bottom - and covers at least half the table's width (or height, for a column
+     * separator). One rule of either kind is enough to say the page drew a grid rather than a
+     * panel.
+     */
+    private static void markInnerRules(Table t, Rules rules) {
+        if (rules == null) return;
+        float w = t.right - t.left, h = t.bottom - t.top;
+        if (w <= 0f || h <= 0f) return;
+        for (float[] r : rules.horizontal) {                       // {y, x1, x2}
+            if (r[0] <= t.top + 1f || r[0] >= t.bottom - 1f) continue;
+            if (Math.min(r[2], t.right) - Math.max(r[1], t.left) >= w * 0.5f) {
+                t.innerH = true;
+                break;
+            }
+        }
+        for (float[] r : rules.vertical) {                          // {x, y1, y2}
+            if (r[0] <= t.left + 1f || r[0] >= t.right - 1f) continue;
+            if (Math.min(r[2], t.bottom) - Math.max(r[1], t.top) >= h * 0.5f) {
+                t.innerV = true;
+                break;
+            }
+        }
+    }
+
     /**
      * Builds tables from the lines the page actually draws.
      *
```
