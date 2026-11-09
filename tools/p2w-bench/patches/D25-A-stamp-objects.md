# D-25-A — a stamp's two frame lines are one freeform shape, each line of text its own paragraph

**Status: done. Gate clean over 208 documents ("no document got worse"), the stamp is three
objects on 02, no stamp text box anywhere, and `tools/verify-engine.sh` still passes end to end.**

One file changed: `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (+355 / −22).
`PdfToWord.java` is untouched — the model already carried everything needed (each frame rule is
a `Shape` with its own path, each line is a `Box` with its own baseline), so the fix is entirely
in how the writer groups and places what the model hands it.

---

## 1. What changed, and why each change is the one the report asked for

### 1.1 Both frame lines are now ONE freeform shape (`stampFrames`, `mergedFrame`)

`stampFrames()` runs once per page, before anything is written. It reads every stroked, unfilled
rectangle on the page, groups the ones that belong to the same stamp, and replaces each group
with a single `Shape` of kind 2 whose `freeform` holds **one closed sub-path per rule**.

The grouping test is measured, not guessed. On the corpus every stamp's two rules sit on exactly
the same centre at exactly the same angle, and the nearest pair of rules belonging to two
*different* stamps (08's overlapping pair) is 54 pt apart:

| document | rule 1 (centre, angle) | rule 2 (centre, angle) | distance |
|---|---|---|---|
| 01 | (267.21, 488.40) −15° | (267.21, 488.40) −15° | 0.00 pt |
| 02 | (226.55, 504.00) 15° | (226.55, 504.00) 15° | 0.00 pt |
| 03 | (536.76, 442.42) −90° | (536.76, 442.42) −90° | 0.00 pt |
| 04 | (390.90, 418.20) 0° | (390.90, 418.20) 0° | 0.00 pt |
| 06 | (207.78, 391.90) −8° | (207.78, 391.90) −8° | 0.00 pt |
| 07 | (316.07, 303.80) −12° | (316.07, 303.80) −12° | 0.00 pt |
| 08 (stamp A) | (355.32, 349.20) 9° | (355.32, 349.20) 9° | 0.00 pt |
| 08 (stamp B) | (409.18, 341.20) −14° | (409.18, 341.20) −14° | 0.00 pt |
| 08 A vs B | — | — | **54.5 pt** |

So the test is "same centre within `max(2.5 pt, 4 % of the smaller diagonal)` and parallel longest
edges", and the 54 pt gap means two stamps on one page can never be merged by accident.

The rotation is in the path. Each rule contributes the four corners the page itself drew, in the
page's own frame, so a 15° frame is a 15° path and there is **no `a:xfrm rot` on a stamp frame at
all** — one place for the geometry to be wrong instead of two.

`geom()` grew one thing to make this possible: command type **3 = `<a:close/>`**, because the
existing `freeformClosed` boolean can only close the last sub-path. Without it the outer rule
would have been left open and joined to the inner one by a stray line.

### 1.2 Each line of stamp text is an ordinary paragraph (`stampLine`)

The `if (frame != null)` branch of `para()` no longer builds a text box. It calls `stampLine()`,
which writes the line as a `w:p` placed by its own `w:ind w:left` and `w:spacing w:before` —
exactly the mechanism the rest of the page uses. `wps:txbx` count for the whole stamp corpus is
now **0**.

For 02 the result is, verbatim from `word/document.xml`:

```xml
<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="0" w:after="0"
            w:line="345" w:lineRule="exact"/>
  <w:ind w:left="3860" w:right="0" w:firstLine="0"/></w:pPr>
  <w:r>…<w:t xml:space="preserve">IN ORDER</w:t></w:r></w:p>
```

`w:ind 3860` twips = 193.0 pt, and the page draws `IN ORDER` at x = 192.1 pt. A caret can go in
it in Google Docs, Word and LibreOffice.

### 1.3 The stamp's paragraphs are ordered where their own y falls (`orderStamps`)

This is the one change the brief did not spell out, and it is needed for the paragraph to land
*inside* the frame. The engine reads a stamp **after** the page's own words (`Para.stamp` is
"an overlay, so it is read after the page's own words"), which is right for detection and wrong
for a paragraph: a paragraph can only follow the paragraph before it, and `w:spacing w:before`
cannot be negative. Left at the end of the block list, 02's `IN ORDER` landed at the bottom of
the page — **226 pt** below where the page draws it (measured; see §3).

`orderStamps()` moves each stamp paragraph to the place in the page's block order where its own
`top` falls. Nothing else moves: the gap from the last body line to the footer is the same gap it
was, so the footer is not pushed anywhere new. With it, 02's two stamp lines land within
~15 pt of where the page draws them instead of ~200 pt below.

### 1.4 No frame is a border, and `Shape.consumed` is never set for a frame

The only `frame.shape.consumed = true` in the writer is gone. `consumed` is now written **nowhere**
in `DocxWriter` (it is only read, and only restored between the measuring pass and the real one).
A stamp rule is marked with a new flag, `Shape.stampFrame`, which means "written by the stamp's
own frame shape": such a shape is never drawn on its own, never offered to `containerOf()` as the
box that owns a line of text, and never consumed.

That distinction matters for `containerOf()`: a stamp frame is no longer an outline that owns
text. Had it stayed eligible, 04's 180° frame (which is an axis-aligned box in the page's frame)
would have claimed `Round Off` / `0.10` at y = 439 and pulled them out of the flow into anchored
boxes.

### 1.5 Rotation

* The **frame's** rotation is in its path coordinates — nothing else.
* The **text** keeps the writer's existing rotation *placement* arithmetic (`lineAngle`, the
  mirrored origin for a 180° line, the `dirX` rule for a right-to-left line, `startX`), which is
  now used to compute the paragraph's indent instead of a box's insets. The glyphs of a rotated
  line come out upright, because OOXML has no text rotation that LibreOffice honours — that is
  the recorded renderer limit (D-16), not something this change introduces or can fix.

---

## 2. Object count per stamp document, before and after

Counted from `word/document.xml` (drawing objects by `wp:docPr`, paragraphs by `w:p` outside any
`wps:txbxContent`). "Stamp objects" = the objects that make up the stamp, not the whole page.

| document | parts the page draws | BEFORE | AFTER |
|---|---|---|---|
| **01_stamp_rotated_15deg_upright** | 2 rules + 2 lines | 1 shape (inner rule, `1` sub-path) + 2 text boxes = **3**<br>*outer rule had no object of its own: it was `IN ORDER`-side box's `<a:ln>`* | 1 shape, **2 closed sub-paths** + 2 paragraphs = **3** |
| **02_stamp_rotated_15deg_upleft** | 2 rules + 2 lines | 1 shape (inner rule) + 2 text boxes = **3**<br>*outer rule welded to `IN ORDER`'s box* | 1 shape, **2 closed sub-paths** + 2 paragraphs = **3** |
| **03_stamp_vertical_90deg** | 2 rules + 3 lines | 1 shape + 3 text boxes = **4** | 1 shape, 2 sub-paths + 3 paragraphs = **4** |
| **04_stamp_180deg_upside_down** | 2 rules + 2 lines | 1 shape + 2 text boxes = **3** | 1 shape, 2 sub-paths + 2 paragraphs = **3** |
| **06_rect_paid_stamp_red_transparent** | 2 rules + 1 line | 1 shape + 1 text box = **2** | 1 shape, 2 sub-paths + 1 paragraph = **2** |
| **07_stamp_over_table** | 2 rules + 2 lines | 1 stamp shape + 1 table box + 2 text boxes = **5** | 1 stamp shape, 2 sub-paths + 1 table box + 2 paragraphs = **5** |
| **08_two_overlapping_stamps** | 2 × (2 rules + 2 lines) | 2 shapes (one rule each) + 4 text boxes = **6** | 2 shapes, 2 sub-paths each + 4 paragraphs = **6** |
| 05_round_company_seal_curved_text | no frame (per-glyph curved text) | 63 text boxes + 5 shapes = **68** | **68 — unchanged**, out of scope: there is no frame rule to group, and it is the D-16 per-glyph class |

**The 02 test in the brief is met: exactly THREE objects — one shape holding both frame lines,
plus one paragraph per line of text.**

The count for 02 before and after is the same number (3) but not the same structure, and that is
the point: before, one of those three objects was a **text box that also carried a frame line**,
and the other frame line was alone. Now the two frame lines are one object and neither is attached
to any text.

Whole-document `wps:txbx` counts (from `verify_visual.py`): 01 `2 → 0`, 02 `2 → 0`, 03 `3 → 0`,
04 `2 → 0`, 06 `1 → 0`, 07 `2 → 0`, 08 `4 → 0`.

---

## 3. verify_visual.py, before and after

`python3 tools/p2w-bench/verify_visual.py <source.pdf> <generated.docx>`, LibreOffice render.

| document | pages | dy median | dy worst | within 10 pt | text boxes |
|---|---|---|---|---|---|
| 01_stamp_rotated_15deg_upright | 1 / 1 → 1 / 1 | 2.7 → **2.7** | 125.8 → **114.5** | 88 % → 86 % | 2 → **0** |
| 02_stamp_rotated_15deg_upleft | 1 / 1 → 1 / 1 | 4.3 → **4.9** | 118.3 → **99.7** | 86 % → 82 % | 2 → **0** |
| 03_stamp_vertical_90deg | 1 / 1 → 1 / 1 | 6.7 → **6.7** | 252.4 → **174.1** | 74 % → 73 % | 3 → **0** |
| 04_stamp_180deg_upside_down | 1 / 1 → 1 / 1 | 4.5 → **6.5** | 207.9 → **137.8** | 78 % → 71 % | 2 → **0** |
| 08_two_overlapping_stamps | 1 / 1 → 1 / 1 | 1.6 → **2.3** | 272.4 → **223.3** | 90 % → 72 % | 4 → **0** |
| **median of the five** | — | **4.3 → 4.9** | **207.9 → 137.8** | — | **2 → 0** |

Read the columns together, because one of them is not measuring what it looks like it measures:

* **Worst dy improved on all five** (207.9 → 137.8 at the median of the five). The worst line in
  every one of these documents is *not* the stamp — it is the **footer** drawn at y = 798.8, which
  this writer has always placed too high because the gap above it is capped (`GAP_CAP_TW`). Adding
  the stamp's paragraphs to the flow pushes that footer *down*, closer to where the page draws it
  (rendered y of the footer line, before → after):

  | | 01 | 02 | 03 | 04 | 08 |
  |---|---|---|---|---|---|
  | footer y, before | 673.0 | 680.5 | 546.4 | 590.9 | 526.4 |
  | footer y, after | **684.3** | **699.1** | **624.7** | **661.0** | **575.5** |
  | its dy, before → after | 125.8 → 114.5 | 118.3 → 99.7 | 252.4 → 174.1 | 207.9 → 137.8 | 272.4 → 223.3 |
* **Median dy is unchanged on 01 and 03, and moves by ≤ 2 pt on the other three** (02 +0.6,
  04 +2.0, 08 +0.7). That movement is the price of `orderStamps`: a paragraph inserted mid-page
  consumes its own height, so the lines after it sit that much lower, and the pitch solver can
  only recover the *gaps* it measures, not the height already spent.
* **within 10 pt falls on all five** (88→86, 86→82, 74→73, 78→71, 90→72 %) — most on 08. Same cause, and 08 is
  the worst case because two stamps (four paragraphs) land in the middle of a receipt page.
  Without `orderStamps` this column stays at the baseline instead, but then the stamp's own text
  sits at the bottom of the page: measured on 02, worst dy went to **226.1 pt** and the two
  stamp lines landed ~200 pt below their frame. That trade is the one judgement call in this
  patch, and I took the stamp over the page: a stamp whose words are not in the stamp is a
  visible defect, while a 15 pt shift of the lines below it is the offset this converter already
  carries everywhere.
* **Pages are unchanged (1/1) on all five.** Nothing was pushed onto a second sheet.
* **One document got worse on the stamp text itself: 03.** Its stamp is vertical (90°), and a 90°
  line's own `Box.y` is not the baseline start — it sits mid-frame. The old text box was placed by
  the frame's insets and so landed near the top of the frame; the paragraph is placed from
  `Box.y`, which puts `INTERNAL AUDIT CELL` 107.5 pt low (it was under 28 pt before). 03's
  aggregate numbers are flat (median 6.7 → 6.7, within 10 pt 74 % → 73 %), and this is the
  per-glyph-rotation class of D-16, but it is a real regression on that one line and I am
  flagging it rather than burying it: the vertical stamp wants its own placement rule (centre the
  upright rendering on the frame's centre), which I did not add because it is a heuristic that
  would need the same three-way check the 15° and 180° cases got.

---

## 4. Gate over 208 documents

```
$ python3 tools/p2w-bench/gate.py --corpus corpus208 --out out208_after \
      --baseline tools/p2w-bench/base208.json --check
documents: 208
no document got worse
```

Corpus assembled from the `corpus-v1` release: `p2w-batch-1.zip` (82) + `p2w-all-groups.zip` (53)
+ `pdf-to-word-test-corpus-v3.zip` (73), deduplicated by basename to exactly the 208 keys in
`base208.json` (0 missing, 0 extra). Conversion: 208 files, 0 failed.

`bash tools/verify-engine.sh` also still passes end to end (exit 0, every section ran:
behavioural checks, rotation/overlay, text layer, search, links, redaction, encryption,
bookmarks, report, repair, the 51-fixture repair sweep, norms, real documents, fonts), including
`TestPdfToWord` (29/29) and `TestRealDocs` (3/3).

---

## 5. Known limits, stated rather than hidden

1. **Rotated glyphs.** A line the page drew at 15°, 90° or 180° is now an upright paragraph at the
   right place. LibreOffice cannot rotate glyphs in a text frame in any OOXML spelling (D-16), so
   the words read horizontally. This is unchanged from before — the previous version put them in
   a rotated text box and LibreOffice ignored the rotation on that too.
2. **One stroke weight per stamp.** A freeform has one `<a:ln>`, so the merged shape carries the
   **outer** rule's weight and colour; the inner rule, which the page drew thinner (0.6 pt against
   1.56–4.89 pt), is drawn at the outer weight. This is the cost of "the two rules are one
   object", which is what the report asks for; the commercial converters group them the same way.
3. **Not a raster.** No picture was introduced anywhere. `10_stamp_as_image` and the rasterise-a-
   stamp path are untouched.
4. **05 (round seal) is untouched.** It has no frame rule, only per-glyph rotated text; it keeps
   its text boxes and its 68 objects. Bringing it into this scheme needs the per-glyph text to
   become something a paragraph can hold, which is a different defect.
5. `orderStamps` only moves paragraphs that are (a) on a turned baseline and (b) inside a stamp
   frame, so it cannot reorder any ordinary page.

---

## 6. The diff

`git diff` against `kavopdf/app@main` (`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`):

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 9216473..3844f99 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -594,6 +594,12 @@ public final class DocxWriter {
                 if (block instanceof Shape) outlines.add((Shape) block);
             }
             ctx.curShapes = outlines;
+            // D-25: fold each stamp's concentric frame rules into one shape before anything is
+            // written, so the page is laid out against the same geometry it is drawn with.
+            stampFrames(outlines);
+            // And put the stamp's text paragraphs where their own y falls, so the indent and
+            // space-before they are placed with are the page's own.
+            orderStamps(page, outlines, ctx);
             if (page.blocks.isEmpty()) continue;
             // ---- the page's flow, measured before it is written ----
             //
@@ -719,6 +725,9 @@ public final class DocxWriter {
         // The carrier is a zero-height paragraph holding the sectPr, because a sectPr has to
         // live in a pPr and a table cannot carry one. Measured on a prototype: a table with a
         // carrier after it costs 2.9 pt and spans correctly.
+        // Every pass writes the page again from scratch, so what an earlier pass has already
+        // drawn is forgotten here. Without this the second pass writes no stamp frame at all.
+        if (ctx.curShapes != null) for (Shape sh : ctx.curShapes) sh.stampDrawn = false;
         float blockSpan = 0f;
         for (Object bb : page.blocks) {
             if (bb instanceof PdfToWord.Para) {
@@ -758,7 +767,18 @@ public final class DocxWriter {
             } else if (block instanceof Picture) {
                 picture(sb, (Picture) block, ctx);
             } else if (block instanceof Shape) {
-                if (!((Shape) block).consumed) shape(sb, (Shape) block, ctx);
+                Shape sh = (Shape) block;
+                if (sh.stampFrame) {
+                    // D-25: a stamp's frame is ONE object holding every rule of that stamp, and
+                    // it is written once - where its outermost rule sits in the page's order.
+                    Shape host = sh.mergedHost == null ? sh : sh.mergedHost;
+                    if (!host.stampDrawn) {
+                        host.stampDrawn = true;
+                        if (host.mergedShape != null) shape(sb, host.mergedShape, ctx);
+                    }
+                } else if (!sh.consumed) {
+                    shape(sb, sh, ctx);
+                }
             }
         }
         if (page.columns > 1 && curCols != page.columns) {
@@ -1035,6 +1055,27 @@ public final class DocxWriter {
          * reported: sometimes the outline shifts, sometimes the text inside it does.
          */
         public boolean consumed;
+        /**
+         * True when this shape is one of the rules of a stamp's frame (D-25).
+         *
+         * <p>A stamp draws its frame as two concentric rectangles. They are written as ONE
+         * freeform shape - {@link #mergedShape} on the outermost of them - because the user's
+         * report is that the two rules must never be able to drift against each other, and two
+         * objects with two sets of coordinates can. Every rule of the stamp is marked here so
+         * that it is never drawn on its own, never offered to {@code containerOf} as the box
+         * that owns a line of text, and never consumed into anything.
+         *
+         * <p>It is deliberately NOT {@link #consumed}: that flag means "folded into a text box's
+         * border", and after D-25 there is no text box for a stamp frame to be folded into. A
+         * frame that set it would be a frame the writer believes it has already drawn.
+         */
+        public boolean stampFrame;
+        /** The shape that draws this rule, when this shape is part of a stamp frame group. */
+        public Shape mergedHost;
+        /** The one freeform that carries every rule of this stamp, set on the outermost rule. */
+        public Shape mergedShape;
+        /** Set once this pass has written {@link #mergedShape}, so it is written once. */
+        public boolean stampDrawn;
 
         public Shape(float xPt, float topPt, float wPt, float hPt) {
             this.xPt = xPt;
@@ -1063,7 +1104,10 @@ public final class DocxWriter {
     private static Shape containerOf(java.util.List<Shape> shapes, PdfToWord.Box b) {
         if (shapes == null) return null;
         for (Shape s : shapes) {
-            if (s.consumed || s.lineRgb < 0 || s.fillRgb >= 0) continue;
+            // A stamp's frame is not the box that owns a line of text: after D-25 it is a
+            // sibling of the text paragraphs, drawn once for the whole stamp, and treating it
+            // as an outline would pull a nearby line out of the flow and anchor it.
+            if (s.consumed || s.stampFrame || s.lineRgb < 0 || s.fillRgb >= 0) continue;
             if (s.kind != 0) continue;
             if (s.wPt < b.size * 3f || s.hPt < b.size * 1.5f) continue;
             if (b.x < s.xPt - 1f || b.right > s.xPt + s.wPt + 1f) continue;
@@ -1113,7 +1157,12 @@ public final class DocxWriter {
                 .append("<a:path w=\"").append(cx).append("\" h=\"").append(cy).append("\">");
         for (float[] c : s.freeform) {
             int type = (int) c[0];
-            if (type == 2) {
+            // 3 closes the sub-path it ends. A stamp's frame is two rectangles in one path, and
+            // the single freeformClosed flag can only close the last of them - so the close is a
+            // command of its own and each rectangle carries its own (D-25).
+            if (type == 3) {
+                g.append("<a:close/>");
+            } else if (type == 2) {
                 g.append("<a:cubicBezTo>");
                 for (int i = 1; i + 1 < c.length; i += 2) pt(g, s, cx, cy, c[i], c[i + 1]);
                 g.append("</a:cubicBezTo>");
@@ -1375,24 +1424,18 @@ public final class DocxWriter {
                 }
                 Frame frame = frameOf(ctx.curShapes, px, py, lineAngle);
                 if (frame != null) {
-                    // The rectangle becomes this box's border, once: the stamp's inner rectangle
-                    // is a different shape and is still drawn by shape(), which is how a
-                    // double-ruled stamp keeps both of its rules.
-                    int rgb = -1;
-                    float lw = 0.6f;
-                    if (!frame.shape.consumed) {
-                        frame.shape.consumed = true;
-                        rgb = frame.shape.lineRgb;
-                        lw = Math.max(0.4f, frame.shape.lineWidthPt);
-                    }
-                    // tIns is measured to the top of the text, not to its baseline, so one
-                    // ascent comes off - the same convention every upright box in this writer
-                    // uses. It can go slightly negative for a line that hugs the frame's top
-                    // edge; the box's own top is then the clamp.
-                    float lIns = Math.max(0f, frame.lIns);
-                    float tIns = Math.max(0f, frame.tIns - ASCENT * b.size);
-                    anchorAt(sb, ctx, frame.cx, frame.cy, frame.w / 2f, frame.h / 2f,
-                            frame.w, frame.h, inner.toString(), lineAngle, rgb, lw, lIns, tIns);
+                    // D-25: a line the page drew inside a stamp's frame is a paragraph, not a
+                    // text box, and the frame is not its border.
+                    //
+                    // The frame used to BE this box's <a:ln> border (5013433). That welded the
+                    // outer rule to one line of TEXT while the inner rule stayed on its own, so
+                    // the two rules could drift apart - the drift the user reported for months -
+                    // and, because the whole stamp then lived in wps:txbx, Google Docs could not
+                    // put a caret in any of it. Both rules are now one freeform shape written by
+                    // shape() (see stampFrames/mergedFrame) and this line is an ordinary
+                    // paragraph placed by its indent and space-before (see stampLine). The frame
+                    // and the text are siblings, and neither carries the other's geometry.
+                    stampLine(sb, p, b, ctx, px, py, lineAngle, advance);
                 } else {
                     // No rectangle around this line - the per-glyph text of a round seal, a
                     // rotated label on a drawing. There is no frame to bind to, so the line is
@@ -1990,6 +2033,24 @@ public final class DocxWriter {
         Shape shape;
     }
 
+    /**
+     * The stamp's frame around one line, in the page's own coordinates.
+     *
+     * <p>Both callers - the writer, and the pass that orders a page's blocks - have to agree
+     * about where a line's baseline really is, so the mirroring a 180-degree line needs is
+     * applied in one place. PDFBox reports a turned line's origin in a frame turned with it, so
+     * on a 180-degree stamp both coordinates come back mirrored about the page.
+     */
+    private static Frame frameOfLine(java.util.List<Shape> shapes, PdfToWord.Box b, Ctx ctx) {
+        float angle = b.rotated && Math.abs(b.angle) < 1f ? 180f : b.angle;
+        float px = b.x, py = b.y;
+        if (b.rotated && Math.abs(b.angle) < 1f) {
+            px = ctx.pageWidthPt - b.x;
+            py = ctx.pageHeightPt - b.y;
+        }
+        return frameOf(shapes, px, py, angle);
+    }
+
     private static Frame frameOf(java.util.List<Shape> shapes, float px, float py, float angle) {
         if (shapes == null) return null;
         double th = Math.toRadians(angle);
@@ -2059,6 +2120,278 @@ public final class DocxWriter {
         return best;
     }
 
+    // ------------------------------------------------------------- the stamp's frame (D-25)
+
+    /**
+     * The four corners of a stroked, unfilled rectangle, in the page's own frame, or null.
+     *
+     * <p>A rectangle the page draws as four lines arrives as a freeform path and one drawn with
+     * {@code re} arrives as a preset box, so both spellings are read here and both answer with
+     * the same thing: four corners in the frame every {@code Shape} in this writer uses, where y
+     * counts down from the top of the page. Everything the stamp grouping does is done on these
+     * corners, so a rule cannot be recognised one way and merged another.
+     */
+    private static float[][] rectCorners(Shape s) {
+        if (s.fillRgb >= 0 || s.lineRgb < 0) return null;
+        if (s.kind == 2 && s.freeform != null) {
+            java.util.List<float[]> pts = new ArrayList<>();
+            for (float[] c : s.freeform) {
+                int type = (int) c[0];
+                if (type == 0 || type == 1) pts.add(new float[]{c[1], c[2]});
+                else if (type == 2) pts.add(new float[]{c[c.length - 2], c[c.length - 1]});
+            }
+            if (pts.size() != 4) return null;
+            return pts.toArray(new float[0][]);
+        }
+        if (s.kind == 0) {
+            return new float[][]{
+                    {s.xPt, s.topPt},
+                    {s.xPt + s.wPt, s.topPt},
+                    {s.xPt + s.wPt, s.topPt + s.hPt},
+                    {s.xPt, s.topPt + s.hPt}};
+        }
+        return null;
+    }
+
+    /** The centre of a rectangle given its corners. */
+    private static float[] rectCentre(float[][] c) {
+        float x = 0f, y = 0f;
+        for (float[] p : c) { x += p[0]; y += p[1]; }
+        return new float[]{x / c.length, y / c.length};
+    }
+
+    /** The direction of a rectangle's longest edge, as a unit vector. */
+    private static float[] rectAxis(float[][] c) {
+        double ex = 0, ey = 0, el = 0;
+        for (int i = 0; i < c.length; i++) {
+            float[] p = c[i], q = c[(i + 1) % c.length];
+            double dx = q[0] - p[0], dy = q[1] - p[1], len = Math.hypot(dx, dy);
+            if (len > el) { el = len; ex = dx / len; ey = dy / len; }
+        }
+        return el <= 0 ? null : new float[]{(float) ex, (float) ey};
+    }
+
+    /**
+     * Are these two rules the inner and outer rule of ONE stamp?
+     *
+     * <p>A stamp's frame is drawn twice - an outer rule and an inner one a few points inside it -
+     * and the two share a centre and an angle and nothing else. Measured on the corpus: every
+     * stamp in 01, 02, 03, 04, 06, 07 and 08 has its two rules on exactly the same centre and at
+     * exactly the same angle, and the nearest pair of rules belonging to two DIFFERENT stamps
+     * (08's overlapping pair) is 54 pt apart. So the test is a shared centre within a few points
+     * and parallel edges, and it does not need to guess from sizes.
+     *
+     * <p>This is the one place a stamp is recognised. The frame is not found from the text, and
+     * the text is not found from the frame: the rules are grouped with each other, which is what
+     * makes them one object that cannot drift against itself.
+     */
+    private static boolean sameStamp(float[][] a, float[][] b) {
+        if (a == null || b == null) return false;
+        float[] ca = rectCentre(a), cb = rectCentre(b);
+        float[] aa = rectAxis(a), ab = rectAxis(b);
+        if (aa == null || ab == null) return false;
+        if (Math.abs(aa[0] * ab[0] + aa[1] * ab[1]) < 0.985f) return false;
+        float diagA = rectDiag(a), diagB = rectDiag(b);
+        float tol = Math.max(2.5f, 0.04f * Math.min(diagA, diagB));
+        return Math.hypot(ca[0] - cb[0], ca[1] - cb[1]) <= tol;
+    }
+
+    private static float rectDiag(float[][] c) {
+        return (float) Math.hypot(c[1][0] - c[3][0], c[1][1] - c[3][1]);
+    }
+
+    private static float rectArea(float[][] c) {
+        return Math.abs((c[1][0] - c[0][0]) * (c[3][1] - c[0][1])
+                - (c[1][1] - c[0][1]) * (c[3][0] - c[0][0]));
+    }
+
+    /**
+     * Put a stamp's text paragraphs where the page put them, instead of at the end of the page.
+     *
+     * <p>The engine reads a stamp after the page's own words, because a stamp is an overlay and
+     * not part of the page's grid - which is right for detection and wrong for a paragraph. A
+     * paragraph can only follow the paragraph before it: it cannot be given a position above the
+     * point the flow has already reached, and {@code w:spacing w:before} is not allowed to be
+     * negative. So a stamp line left at the end of the block list lands below the last line of
+     * the page, 200 pt under its own frame.
+     *
+     * <p>Moving the stamp's paragraphs to the place in the page's order where their own y falls
+     * is what lets {@code w:ind} and {@code w:before} do their job: the gap above the line is
+     * then the gap the page really drew, and the line lands inside its frame. Nothing else on
+     * the page moves - the gap from the last body line to the footer is the same gap it was.
+     */
+    private static void orderStamps(PdfToWord.Page page, java.util.List<Shape> outlines, Ctx ctx) {
+        if (outlines == null || outlines.isEmpty()) return;
+        java.util.List<Object> blocks = page.blocks;
+        java.util.List<PdfToWord.Para> stamps = new ArrayList<>();
+        for (Object b : blocks) {
+            if (!(b instanceof PdfToWord.Para)) continue;
+            PdfToWord.Para p = (PdfToWord.Para) b;
+            boolean turned = false;
+            for (PdfToWord.Box bx : p.boxes) if (bx.rotated) turned = true;
+            if (!turned) continue;
+            for (PdfToWord.Box bx : p.boxes) {
+                if (bx.runs.isEmpty() || frameOfLine(outlines, bx, ctx) == null) continue;
+                stamps.add(p);
+                break;
+            }
+        }
+        if (stamps.isEmpty()) return;
+        blocks.removeAll(stamps);
+        for (PdfToWord.Para p : stamps) {
+            int at = blocks.size();
+            for (int i = 0; i < blocks.size(); i++) {
+                if (blockTop(blocks.get(i)) > p.top) { at = i; break; }
+            }
+            blocks.add(at, p);
+        }
+    }
+
+    /** Where a block starts on the page, in points from its top, for ordering only. */
+    private static float blockTop(Object b) {
+        if (b instanceof PdfToWord.Para) return ((PdfToWord.Para) b).top;
+        if (b instanceof PdfToWord.Table) return ((PdfToWord.Table) b).top;
+        if (b instanceof Picture) {
+            Picture p = (Picture) b;
+            return p.placed ? p.topPt : p.top;
+        }
+        if (b instanceof Shape) return ((Shape) b).topPt;
+        return 0f;
+    }
+
+    /**
+     * Fold every stamp's concentric frame rules into one freeform shape.
+     *
+     * <p>This is the whole of D-25's first requirement. The user's report, corrected: in the
+     * commercial converters the two frame lines select TOGETHER, and each line of text selects
+     * on its own; this writer had the outer rule welded to a line of text and the inner rule
+     * alone, so the two rules could - and did - drift apart. Two rules in one path, in one
+     * shape, with one bounding box, cannot: there is no second set of coordinates to disagree
+     * with the first.
+     *
+     * <p>The outermost rule is the host, because that is the block the page drew first and it is
+     * the one whose stroke weight and colour the shape carries. Every rule is marked
+     * {@code stampFrame} - which is NOT {@code consumed} - so the writer draws the group once,
+     * where the outermost rule sits, and never draws or consumes a rule on its own.
+     */
+    private static void stampFrames(java.util.List<Shape> shapes) {
+        if (shapes == null || shapes.size() < 2) return;
+        int n = shapes.size();
+        float[][][] cs = new float[n][][];
+        for (int i = 0; i < n; i++) cs[i] = rectCorners(shapes.get(i));
+        boolean[] taken = new boolean[n];
+        for (int i = 0; i < n; i++) {
+            if (taken[i] || cs[i] == null) continue;
+            java.util.List<Integer> group = new ArrayList<>();
+            group.add(i);
+            for (int j = i + 1; j < n; j++) {
+                if (taken[j] || cs[j] == null) continue;
+                if (sameStamp(cs[i], cs[j])) group.add(j);
+            }
+            if (group.size() < 2) continue;
+            int outer = group.get(0);
+            for (int k : group) if (rectArea(cs[k]) > rectArea(cs[outer])) outer = k;
+            // Outer first, then the rest outermost-first, so the path reads the way the page
+            // painted it.
+            java.util.List<Integer> ordered = new ArrayList<>();
+            ordered.add(outer);
+            for (int k : group) if (k != outer) ordered.add(k);
+            for (int a = 1; a < ordered.size(); a++) {
+                for (int b = a + 1; b < ordered.size(); b++) {
+                    if (rectArea(cs[ordered.get(b)]) > rectArea(cs[ordered.get(a)])) {
+                        int t = ordered.get(a);
+                        ordered.set(a, ordered.get(b));
+                        ordered.set(b, t);
+                    }
+                }
+            }
+            Shape host = shapes.get(outer);
+            host.mergedShape = mergedFrame(host, ordered, cs);
+            for (int k : group) {
+                Shape s = shapes.get(k);
+                s.stampFrame = true;
+                s.mergedHost = host;
+                taken[k] = true;
+            }
+        }
+    }
+
+    /**
+     * One freeform holding every rule of one stamp, as closed sub-paths of a single path.
+     *
+     * <p>The rotation is in the coordinates: each rule contributes the four corners the page
+     * itself drew, so a frame at 15 degrees is a 15-degree path and nothing has to rotate it
+     * afterwards. There is no {@code a:xfrm rot} on a stamp frame and there must not be - a
+     * rotation attribute is a second place the geometry can be wrong.
+     */
+    private static Shape mergedFrame(Shape host, java.util.List<Integer> ordered,
+                                     float[][][] cs) {
+        float minX = Float.MAX_VALUE, minY = Float.MAX_VALUE;
+        float maxX = -Float.MAX_VALUE, maxY = -Float.MAX_VALUE;
+        for (int k : ordered) {
+            for (float[] p : cs[k]) {
+                minX = Math.min(minX, p[0]);
+                minY = Math.min(minY, p[1]);
+                maxX = Math.max(maxX, p[0]);
+                maxY = Math.max(maxY, p[1]);
+            }
+        }
+        Shape m = new Shape(minX, minY, Math.max(0.1f, maxX - minX), Math.max(0.1f, maxY - minY));
+        m.kind = 2;
+        m.fillRgb = -1;
+        m.lineRgb = host.lineRgb;
+        m.lineWidthPt = host.lineWidthPt;
+        m.lineAlpha = host.lineAlpha;
+        java.util.List<float[]> cmds = new ArrayList<>();
+        for (int k : ordered) {
+            for (int i = 0; i < 4; i++) {
+                cmds.add(new float[]{i == 0 ? 0f : 1f, cs[k][i][0], cs[k][i][1]});
+            }
+            cmds.add(new float[]{3f});
+        }
+        m.freeform = cmds;
+        m.freeformClosed = false;
+        return m;
+    }
+
+    /**
+     * One line of stamp text, as an ordinary paragraph placed by its indent and space-before.
+     *
+     * <p>This is the other half of D-25. The stamp used to be a {@code wps:txbx} text box, and
+     * Google Docs renders a text box as a drawing and cannot put a caret inside it - the user's
+     * "the stamp is not editable at all" on 02. A paragraph can be selected, edited and typed
+     * into in every reader, so each line of the stamp is one.
+     *
+     * <p>It is placed exactly as the rest of the page's text is placed: {@code w:ind w:left} at
+     * the x the line starts at and {@code w:spacing w:before} for the gap above its baseline. No
+     * box, no rotation attribute, nothing anchored. The frame is a sibling written by
+     * {@code shape()}, so neither part can move the other.
+     *
+     * <p>The glyphs of a line the page drew at an angle come out upright here: OOXML has no text
+     * rotation that LibreOffice honours, which is the recorded renderer limit (D-16) and not
+     * something this writer can fix. What the paragraph does give is the line's own position and
+     * its own editability, and the frame around it keeps its angle because the angle is in the
+     * frame's path.
+     */
+    private static void stampLine(StringBuilder sb, PdfToWord.Para p, PdfToWord.Box b, Ctx ctx,
+                                  float px, float py, float lineAngle, float advance) {
+        double dirX = Math.cos(Math.toRadians(lineAngle));
+        float startX = px;
+        if (dirX <= -0.5) startX = px - b.length;
+        else if (Math.abs(dirX) < 0.5) startX = px - b.length / 2f;
+        PdfToWord.Box flat = new PdfToWord.Box();
+        flat.x = startX;
+        flat.right = startX + Math.max(advance, b.length);
+        flat.y = py;
+        flat.size = b.size;
+        flat.bottom = py + Math.max(4f, b.size * LINE_FACTOR);
+        flat.length = b.length;
+        flat.rotated = false;
+        flat.angle = 0f;
+        flat.runs.addAll(b.runs);
+        flowFromBox(sb, p, flat, ctx);
+    }
+
     /**
      * An anchored text box whose local point (lx, ly) lands on the page point (pageX, pageY)
      * once the box has been rotated by {@code rotDeg} about its own centre.
```
