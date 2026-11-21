# Engine anchor guard — PDF rule → Word floating drawing, and the `w:tc` suppression

Repo: `https://github.com/kavopdf/app`, cloned `--depth 1` to `/scratch/work/CS`.
HEAD is `dcdd9a5 claim: fixer takes the slot` — a **shallow clone, so `git log --all --oneline` holds exactly one commit**; nothing below depends on history, everything is quoted from the working tree at that commit.

Everything here was verified two ways: by reading the clone (line numbers are `file:line` at HEAD) and by **building and running the engine** (`tools/p2w-bench/build-engine.sh` → `ConvertOne`) on 3 corpus PDFs that ship in the repo plus 2 synthetic PDFs built for this question. Probe builds were made in scratch copies (`/scratch/work/CS-guard`, `/scratch/work/CS-guard2`, `/scratch/work/CS-patch`); **the clone itself was never edited, committed or pushed.**

---

## CODE MAP

### 1. Where a PDF rule becomes a `Shape` (the model object)

| step | file:line | what happens |
|:--|:--|:--|
| rule drawn as a **thin filled rectangle** | `PdfToWord.java:6714` `fillPath()` → `emitFill(false)` | the page's fill path enters the shape builder |
| it becomes a rect shape | `PdfToWord.java:6092` `addShape(cl, fill, alpha, line, lw, pathIsEllipse() ? 1 : 0);` | `kind == 0` (rect), `fillRgb` set, `lineRgb == -1` |
| shape object built | `PdfToWord.java:5951`–`5968` | `DocxWriter.Shape sh = new DocxWriter.Shape(r[0], -r[3], r[2]-r[0], r[3]-r[1]); … rules.shapes.add(sh);` |
| rule drawn as a **stroked line** | `PdfToWord.java:6705` `strokePath()` → `emitStroke()` (`:6199`) | a stroke becomes a band as thick as the stroke |
| that band is added | `PdfToWord.java:6236`–`6241` `addShape(clipped(new float[]{x0, segY0 - w/2f, x1, segY0 + w/2f}), …)` | horizontal / vertical segment → filled band, same `Shape` |
| the collector | `PdfToWord.java:5721` `private static final class RuleCollector extends PDFGraphicsStreamEngine`; rule arrays at `:5643` `static final class Rules` | `rules.horizontal` / `rules.vertical` / `rules.shapes` |
| shapes reach the page | `PdfToWord.java:7276` `out.shapes.addAll(collector.rules.shapes);` | one `List<DocxWriter.Shape>` per page |

The `Shape` type itself: `DocxWriter.java:2512` `public static final class Shape`, geometry `:2513` `public float xPt, topPt, wPt, hPt;`, flags `:2561` `consumed`, `:2576` `stampFrame`.

### 2. Where a `Shape` is turned into a `<w:drawing>`

| step | file:line | what happens |
|:--|:--|:--|
| per-page shape list | `DocxWriter.java:1121`–`1125` `List<Shape> outlines = new ArrayList<>(); … ctx.curShapes = outlines;` | the page's shapes |
| block dispatch | `DocxWriter.java:2265` `emitBlock(...)`, Shape branch `:2272`–`:2281` | `if (!s.consumed) shape(sb, s, ctx);` |
| **the emitter** | `DocxWriter.java:2772` `private static void shape(StringBuilder sb, Shape s, Ctx ctx)` | **the only function that emits a rule drawing**; its only caller is `emitBlock` (`:2281`) |
| the drawing itself | `DocxWriter.java:2774`–`2786`, closes at `:2823` | see below |
| the only "is this a rule" predicate in HEAD | `DocxWriter.java:2845` `private static boolean isHairline(Shape s)` | `lo <= 1.5f && hi > 2f`; used **only** to keep a hairline's fill alive (`:2804`), it does **not** dispatch or suppress anything |

The anchor the drawing is written into — `DocxWriter.java:2774`–`2786` (verbatim):

```java
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:drawing>")
                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
                .append(" simplePos=\"0\" relativeHeight=\"").append(relHeight).append("\"")
                .append(" behindDoc=\"1\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
                .append("<wp:simplePos x=\"0\" y=\"0\"/>")
                .append("<wp:positionH relativeFrom=\"page\"><wp:posOffset>").append(offX)
```

Two facts matter for the guard: the **anchor paragraph is created by `shape()` itself** (`<w:p>` at `:2774`), and its position is `relativeFrom="page"` (`:2783`, `:2785`) with `layoutInCell="1"` (`:2781`).

### 3. Where the anchor paragraph is created

`DocxWriter.java:2774` — inside `shape()`. It is **not** a paragraph the caller supplied: `shape()` writes its own one-line `<w:p>`, so the drawing's anchor paragraph is whatever block position the emitter happens to be at.

### 4. Does the emitter know it is inside a `w:tc`?

**The state exists on `Ctx`; the answer at the moment the drawing is written is nonetheless "no", because the anchor paragraph is never inside a `w:tc`.**

Cell context that does exist:

| fact | file:line |
|:--|:--|
| `Ctx` (mutable per-write state) | `DocxWriter.java:749` `private static final class Ctx` |
| `boolean inColumn;` — "True while writing the inside of a layout-table cell" | `DocxWriter.java:898` |
| cell edges `cellRightPt` / `cellLeftPt` | `DocxWriter.java:900`, `:911` |
| set true per cell | `DocxWriter.java:2101` `ctx.inColumn = true;` |
| **the one place a block is emitted inside a cell** | `DocxWriter.java:2126` `emitBlock(cellXml[c], b, ctx);` |
| cleared after the cell | `DocxWriter.java:2138` `ctx.inColumn = false;` |
| cleared at body level | `DocxWriter.java:1097`, `:1215` |

And the reason `inColumn` can never be true at `shape()`: **a `Shape` is never routed into a cell.**

* `columnPage()` classifies every block at `DocxWriter.java:1827`–`1831`: a block with no known text extent gets `home[i] = -2` (the comment at `:1833` says it outright — "Positioned rather than flowed - a picture or a drawn shape"). A `Shape` is not a `PdfToWord.Para` and not a `PdfToWord.Table`, so `known` stays false and `home[i] == -2` always.
* `DocxWriter.java:1908`–`1911`: `if (home[i] == -2 || t < 0f || bt <= 0f) { … after.add(b); continue; }` — every shape goes to `after`, which is emitted at `:2194` **after** the layout table, i.e. at body level with `inColumn == false`.
* `cells[...]` is filled only for `home[i] >= 0` (`DocxWriter.java:1922` `cells[home[i]].add(b);`), which a shape never has.
* `table()` (`DocxWriter.java:5767`) builds its `w:tc` content from `t.rows` strings only — no block objects, so no shapes either.

**Measured** (build + convert, `tc-depth` = `<w:tc>` nesting depth at each `<w:drawing>`):

| document | `<w:drawing>` | `tc-depth` at each drawing | `<w:tbl>` |
|:--|--:|:--|--:|
| `300_prescription_rx.pdf` (ships in repo) | 43 | all `0` | 2 |
| `311_fir_police_form.pdf` (ships in repo) | 65 | all `0` | 3 |
| `350_question_paper.pdf` (ships in repo) | 1 | `0` | 0 |
| synthetic `ruled_inrow.pdf` (thin filled rect drawn inside a table's first row band) | 2 | all `0` | 1 |

So: a rule that the page drew **inside** a table cell still leaves the writer as a **body-level** page-anchored drawing after the table. The code cannot tell, because there is nothing to tell — its anchor paragraph is not in a cell. The knowledge that *would* answer the question (the cell rectangles just written) exists only inside `table()` and `columnPage()`, and is thrown away.

---

## THE GUARD

### A. The literal guard — 11 added lines, applies clean to HEAD

`/scratch/output/rule-drawing-in-cell-guard.patch` (verified: `git apply --check` exits 0 against the clone):

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 4ead19d..dd60f9a 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -834,6 +834,8 @@ public final class DocxWriter {
         int cellWrapHits;
         /** The shapes on the page being written, so a stamp can find its own outline. */
         java.util.List<Shape> curShapes;
+        /** Drawings not written because their anchor paragraph sits inside a table cell. */
+        int shapesInCell;
         /**
          * The lines of each stamp, keyed by the shape that carries that stamp's frame.
          *
@@ -2770,6 +2772,17 @@ public final class DocxWriter {
      * it exists to make visible. A rule drawn behind text is still a rule.
      */
     private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
+        // A PAGE-ANCHORED DRAWING WRITTEN FROM INSIDE A CELL LANDS OUTSIDE IT.
+        //
+        // wp:positionH/positionV below are relativeFrom="page" and the run's own paragraph is
+        // a block of the w:tc it sits in, so the offset is read from the wrong origin: the same
+        // reason anchorBox() refuses to anchor a line in a column cell (see ZERO_GAP_ANCHOR and
+        // ctx.inColumn). The rule is suppressed here and stays a drawing everywhere else - this
+        // is a placement guard, not a change of construct.
+        if (ctx.inColumn) {
+            ctx.shapesInCell++;
+            return;
+        }
         int id = SHAPE_ID_BASE + (ctx.shapeSeq++);
         long cx = Math.max(1, Math.round(s.wPt * EMU_PER_PT));
         long cy = Math.max(1, Math.round(s.hPt * EMU_PER_PT));
```

It is the same shape of guard the writer already trusts in the anchored-text path — `DocxWriter.java:3464` `if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage) {` and `:4383`, documented at `:299`–`:300`: *"why a line inside a column cell is left alone (a page-anchored box written from inside a cell lands outside it)"*. The drawing stays a `wps:wsp` drawing everywhere else; only the in-cell emission is dropped.

**Honest status: it is a no-op today.** Built and run (`/scratch/work/CS-guard`, guard printing on fire): the guard never fired and the output was **byte-identical** to HEAD on all five PDFs — `300_prescription_rx` 43→43 drawings, `311_fir_police_form` 65→65, `350_question_paper` 1→1, `ruled_incell` 2→2, `ruled_inrow` 2→2. That is the same fact as §4: no `Shape` ever reaches a cell.

### B. The plumbing that makes it know — the smallest change, with sites

Because the emitter is not in a cell and cannot be, "the anchor paragraph sits in a `w:tc`" has to be *made* true, or replaced by the equivalent the writer can see: **the rule's own box lies inside a cell of the table just written.** Nothing in `shape()`'s signature changes — `Ctx` is already threaded (`shape(StringBuilder, Shape, Ctx)`), so this is one field, two fill sites and one predicate:

```diff
@@ -834,6 +834,8 @@ public final class DocxWriter {
         java.util.List<Shape> curShapes;
+        /** Cell rectangles of the last table written, in points: {left, top, right, bottom}. */
+        java.util.List<float[]> cellRects = new java.util.ArrayList<>();
@@ -2101,6 +2103,8 @@   (columnPage's per-cell setup)
                 ctx.inColumn = true;
                 ctx.cellLeftPt = edge[c];
                 ctx.cellRightPt = edge[c + 1];
+                ctx.cellRects.clear();
+                ctx.cellRects.add(new float[]{edge[c], subTop, edge[c + 1], subBottom});
@@ -2769,7 +2773,17 @@
+    /** Is this shape's box inside one cell of the table just written? */
+    private static boolean insideACell(Shape s, Ctx ctx) {
+        for (float[] c : ctx.cellRects) {
+            if (s.xPt >= c[0] - 0.5f && s.xPt <= c[2] + 0.5f
+                    && s.topPt >= c[1] - 0.5f && s.topPt + s.hPt <= c[3] + 0.5f) return true;
+        }
+        return false;
+    }
+
     private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
+        if (ctx.inColumn || insideACell(s, ctx)) return;
         int id = SHAPE_ID_BASE + (ctx.shapeSeq++);
@@ -5975,6 +5989,22 @@   (table(): after edgeTw is built, before the row loop)
+        {
+            ctx.cellRects.clear();
+            int nr = Math.max(1, t.rows.size());
+            boolean er = t.rowEdge != null && t.rowEdge.length == nr + 1;
+            for (int r = 0; r < nr; r++) {
+                float ry0 = er ? t.rowEdge[r] : t.top + (t.bottom - t.top) * r / nr;
+                float ry1 = er ? t.rowEdge[r + 1] : t.top + (t.bottom - t.top) * (r + 1) / nr;
+                for (int c = 0; c < cols; c++) {
+                    ctx.cellRects.add(new float[]{x0 + edgeTw[c] / (float) TWIPS_PER_PT, ry0,
+                            x0 + edgeTw[c + 1] / (float) TWIPS_PER_PT, ry1});
+                }
+            }
+        }
```

Exact call sites to touch (all in `DocxWriter.java`):

1. `Ctx` at `:749` — add the field (next to `curShapes` at `:836`).
2. `table()` at `:5767` — fill after `edgeTw` is computed (`:5977`–`:5978`); `x0`, `edgeTw`, `t.rowEdge`, `t.top`, `t.bottom`, `cols` are all already in scope.
3. `columnPage()` at `:1668` — fill inside the per-cell setup at `:2101`–`:2103`; `edge[c]`, `edge[c+1]`, `subTop`, `subBottom` are already in scope.
4. `shape()` at `:2772` — the guard. No signature change; `ctx` is already a parameter.

This variant was built and run (`/scratch/work/CS-guard2`). It **does** fire — which is the coverage problem below.

---

## COVERAGE RISK

Guard **A** (`ctx.inColumn`): suppresses **nothing** today. Measured 0 drawings across 5 documents, output byte-identical to HEAD. Risk: zero; value: zero until something routes a `Shape` into a cell.

Guard **B** (cell-rectangle geometry): suppresses a lot, and not only rules. Measured on the same builds:

| document | HEAD drawings | guard-B drawings | suppressed |
|:--|--:|--:|--:|
| `300_prescription_rx` | 43 | 18 | **25 (58 %)** |
| `311_fir_police_form` | 65 | 45 | **20 (31 %)** |
| `350_question_paper` | 1 | 1 | 0 |
| `ruled_inrow` (synthetic, rule inside row 1) | 2 | 1 | 1 — the intended case |
| `ruled_incell` (rule above the table band) | 2 | 2 | 0 |

What the 25 suppressed shapes on `300_prescription_rx` actually are, from the guard's own log and from HEAD's XML: the page's **table row bands** — `452 × 17 pt` boxes at y 170/187/204/221/238 carrying **both** a pale fill and a hairline (`<a:solidFill><a:srgbClr val="EEF2F8"/>` plus `<a:ln w="5080">`, i.e. 0.4 pt) — and the table's **vertical cell separators**, `0.4 × 17 pt` at x 51.8/211.8/271.8/411.8. So a geometric guard does not stop at "rules": it deletes row shading bands and column separators that lie in the same cells. Whether any individual one is *redundant* with the `w:tblBorders` the table already emits cannot be determined without a render — and `tools/p2w-bench/verify_google.py:1096 _rule_segments()` reads `page.get_drawings()` only, so `32_stroke_lines` would not tell you either.

Not determinable from this clone, and therefore not claimed: how many of the suppressed boxes are duplicated by the table's own borders, and what a renderer does with the difference.

The safe reading of both measurements: the condition the request names ("the anchor paragraph is inside a `w:tc`") **never occurs in this engine**, and the nearest condition the engine *can* compute ("the box lies inside a cell") is far wider than the request — it takes 58 % of one document's drawings with it.

---

## CARRIER PATCH

**Found.** `tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch` — 14 061 bytes, one file (`DocxWriter.java`), referenced by `benchmarks/blast-carrier-2008.json:3` (`"engine_patched": "HEAD + rule-carrier-horizontal-only-2008.patch (docx fingerprint 78ab519d6e92a2ee)"`) and by every `benchmarks/gverify-carrier-2008/*.json:9` (`"engine_patch": "rule-carrier-horizontal-only-2008"`).

It is **not in the tree**: `shape()` at HEAD (`:2772`) has no `isRuleShape` dispatch, and `grep -n isRuleShape DocxWriter.java` finds nothing. `git apply --check` (and `--3way --check`) on the clone **exits 0** — the patch applies cleanly to HEAD despite its `@@ -2770` hunk header, i.e. it was cut two lines above where `shape()` now sits.

Its siblings, all in the same directory: `rule-carrier-tblppr-2008.patch` (11 883 B, **byte-identical to** `rule-carrier-per-rule-2008.patch` — verified by md5) and `rule-carrier-followed-by-block-2008.patch` (13 368 B, same `@@ -2770,6 +2770,18 @@` dispatch). The measurement narrative is `tools/p2w-bench/FINDINGS/32_stroke_lines-RULE-CARRIER-LANDED-2008.md`.

### The dispatch hunk (verbatim, `@@ -2770,6 +2770,18 @@`)

```diff
     private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
+        // A RULE IS NOT A DRAWING ANY MORE.
+        //
+        // Google Docs drops an anchored {@code <w:drawing>} and keeps its anchor, so a rule
+        // the page drew arrived as a stray U+200B and no line at all - 32_stroke_lines, 145
+        // documents, and the largest single class left in the pipeline. A page rule is now a
+        // floating 1x1 table whose one border IS the rule: measured to render, to sit within
+        // 0.5 pt of the requested twips, and to cost 0.00 pt of flow. See
+        // tools/p2w-bench/FINDINGS/32_stroke_lines-TBLPPR-ZERO-FLOW-1905-f1x.md.
+        if (isRuleShape(s)) {
+            ruleCarrier(sb, s, ctx);
+            return;
+        }
         int id = SHAPE_ID_BASE + (ctx.shapeSeq++);
```

The predicate it dispatches on (verbatim, from the added `isRuleShape`, including the horizontal-only clause the patch is named for):

```java
    private static boolean isRuleShape(Shape s) {
        if (s.consumed || s.stampFrame || s.kind != 0) return false;
        if (s.fillRgb < 0 && s.lineRgb < 0) return false;
        if (s.fillRgb < 0 && s.lineWidthPt > RULE_MAX_PT) return false;
        float lo = Math.min(s.wPt, s.hPt), hi = Math.max(s.wPt, s.hPt);
        // A RULE IS HORIZONTAL. …
        if (s.wPt < s.hPt) return false;
        return lo <= RULE_MAX_PT && hi > 2f && hi >= lo * 4f;
    }
```

with `private static final float RULE_MAX_PT = 4.0f;` (matched to `verify_google.py:1044 RULE_THIN = 4.0`).

### The hunk that emits the carrier — **this is the current alternative construct**

A page rule is written as a **floating 1×1 `w:tbl` whose one `w:tcBorders` edge is the rule**, followed by a 1-twip carrier paragraph. Verbatim from the patch (`ruleCarrier`, the `sb.append` chain; four lines of the `w:tblCellMar` comment block elided, marked `…`):

```java
        sb.append("<w:tbl><w:tblPr>")
                .append("<w:tblpPr w:vertAnchor=\"margin\" w:horzAnchor=\"margin\"")
                .append(" w:tblpX=\"").append(xTw).append("\" w:tblpY=\"").append(yTw)
                .append("\" w:leftFromText=\"0\" w:rightFromText=\"0\"")
                .append(" w:topFromText=\"0\" w:bottomFromText=\"0\"/>")
                .append("<w:tblW w:w=\"").append(cellTw).append("\" w:type=\"dxa\"/>")
                .append("<w:tblBorders>")
                .append("<w:top w:val=\"nil\"/><w:left w:val=\"nil\"/>")
                .append("<w:bottom w:val=\"nil\"/><w:right w:val=\"nil\"/>")
                .append("<w:insideH w:val=\"nil\"/><w:insideV w:val=\"nil\"/>")
                .append("</w:tblBorders>")
                .append("<w:tblLayout w:type=\"fixed\"/>")
                … // the w:tblCellMar note, then the zeroed margins:
                .append("<w:tblCellMar><w:top w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:left w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:bottom w:w=\"0\" w:type=\"dxa\"/>")
                .append("<w:right w:w=\"0\" w:type=\"dxa\"/></w:tblCellMar>")
                .append("</w:tblPr>")
                .append("<w:tblGrid><w:gridCol w:w=\"").append(cellTw)
                .append("\"/></w:tblGrid>")
                .append("<w:tr><w:trPr><w:trHeight w:val=\"").append(rowTw)
                .append("\" w:hRule=\"exact\"/></w:trPr>")
                .append("<w:tc><w:tcPr>")
                .append("<w:tcW w:w=\"").append(cellTw).append("\" w:type=\"dxa\"/>")
                .append("<w:tcBorders>");
        for (int i = 0; i < 4; i++) {
            String side = TABLE_SIDES[i];
            if (side.equals(edge)) {
                sb.append("<w:").append(side).append(" w:val=\"single\" w:sz=\"").append(sz)
                        .append("\" w:space=\"0\" w:color=\"").append(colour).append("\"/>");
            } else {
                sb.append("<w:").append(side).append(" w:val=\"nil\"/>");
            }
        }
        sb.append("</w:tcBorders></w:tcPr>")
                .append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\"")
                .append(" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr>")
                .append("</w:pPr></w:p>")
                .append("</w:tc></w:tr></w:tbl>")
                // A CARRIER NEEDS A BLOCK AFTER IT, OR GOOGLE LAYS IT OUT IN FLOW.
                … // the measured note
                .append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\"")
                .append(" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr></w:p>");
```

Geometry inside it (`horizontal = s.wPt >= s.hPt`): `edge = horizontal ? "top" : "left"`, `cellTw = horizontal ? lenTw : weightTw`, `rowTw = horizontal ? 1 : lenTw`, and the rule is placed at the middle of the painted band — `xTw = xPt + (horizontal ? 0 : weightPt/2)`, `yTw = topPt + (horizontal ? weightPt/2 : 0)`, all in twips from the **margin** anchor (the writer's pages have zero margins, `sectPrXml`, `DocxWriter.java:2292`).

What the patch does **not** do: it contains no cell test. `ruleCarrier` writes a body-level floating table exactly where `shape()` wrote a body-level floating drawing — same `emitBlock` call site (`DocxWriter.java:2281`), same page-anchored geometry. So neither construct is emitted inside a `w:tc` today, and guard **A** would sit in front of both with the same effect (none).

Per its own FINDINGS file, the patch is written, compiled and measured on one document (`394_map_with_legend`, Google 41/42 → 42/42) and **deliberately not committed**: "an engine change may not land without a full-corpus measurement of the tree (`regress.py --check`)". Unmeasured per that file: the other 144 rule-carrying documents, multi-rule pages (46 carriers on one page in `407_id_card_front_back`), and vertical rules.

---

## How the claims above were verified

1. `git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS`; every line number read from that tree.
2. `bash tools/p2w-bench/build-engine.sh` → fetches a JDK 17 (Adoptium) + PDFBox-Android 2.0.27.0 + BouncyCastle, compiles `stubs/`, `app/src/main/java/com/kavopdf/app/engine/` and `ConvertOne` — "engine built - ConvertAll ready (33s)".
3. `java ConvertOne <pdf> <dir>` on `tools/engine-verify/real/pdfs/*.pdf` and two synthetic PDFs (`pymupdf`: 4×3 text grid + a 1.2 pt filled rect, one inside the first row's band at y 126, one above the table at y 100, one well below at y 300).
4. `tc-depth` scan of the emitted `word/document.xml` (tag walk counting `<w:tc>`/`</w:tc>` around each `<w:drawing>`) → every drawing at depth 0.
5. Guard A applied in `/scratch/work/CS-guard`, rebuilt, converted → byte-identical `document.xml` on all five, guard never fired.
6. Guard B applied in `/scratch/work/CS-guard2`, rebuilt, converted → fires; drawing counts 43→18, 65→45, 1→1, 2→1, 2→2.
7. `git apply --check tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch` → exit 0; `md5sum` comparison of `rule-carrier-tblppr-2008.patch` vs `rule-carrier-per-rule-2008.patch` → identical.
8. No commit, no push, no edit to `/scratch/work/CS`. The two deliverable diffs were generated from scratch copies and re-checked with `git apply --check` against the untouched clone.
