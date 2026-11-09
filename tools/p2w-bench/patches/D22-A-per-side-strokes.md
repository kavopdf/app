# D-22-A — every table border side carries the page's own stroke

**Verdict:** done, and proven by measurement. 895 of 900 emitted border sides now match a
line the PDF actually draws (before: 495 of 900). The 208-document gate prints
`no document got worse`. Engine suites: 81/81 behavioural checks, 29/29 PDF→Word checks,
3/3 real-document checks.

Repo: `kavopdf/app`, engine `app/src/main/java/com/kavopdf/app/engine/{PdfToWord,DocxWriter}.java`.
Corpus: all three `corpus-v1` assets, 208 documents. Patch: 2 files, +426 / −34, no new files (PdfToWord +343/−7, DocxWriter +83/−27).

---

## 1. What was wrong

`Rules.horizontal` was `float[]{y, x1, x2}` and `Rules.vertical` was `float[]{x, y1, y2}`:
a rule was geometry and nothing else. So the writer had no stroke to read, and
`DocxWriter.borders(boolean outer, boolean innerH, boolean innerV)` wrote `TABLE_RULE_SZ = 8`
(1 pt) in `TABLE_RULE_COLOUR = "000000"` on **every drawn side of every table**. Measured over
the corpus: **900 border sides, one single stroke — `sz=8`, `000000`, 900 times.** A table the
page rules at 0.4 pt in grey and a table it frames at 2 pt both came out at 1 pt black.

The shape path already carried `lineWidthPt` / `lineRgb` / `lineAlpha`; the rule path did not.

## 2. The parallel-list design (why not wider arrays)

`Rules` gains two lists and two accessors, and every recording site goes through the accessors
so the lists cannot part:

```java
final List<float[]> horizontal = new ArrayList<>();   // {y, x1, x2}      unchanged
final List<float[]> vertical   = new ArrayList<>();   // {x, y1, y2}      unchanged
final List<float[]> hStroke    = new ArrayList<>();   // {widthPt, rgb, alpha} same index
final List<float[]> vStroke    = new ArrayList<>();   // {widthPt, rgb, alpha} same index

void addH(float[] rule, float[] stroke) { horizontal.add(rule); hStroke.add(stroke); }
void addV(float[] rule, float[] stroke) { vertical.add(rule);   vStroke.add(stroke); }
float[] hStrokeAt(int i) { return i >= 0 && i < hStroke.size() ? hStroke.get(i) : null; }
float[] vStrokeAt(int i) { return i >= 0 && i < vStroke.size() ? vStroke.get(i) : null; }
```

The arrays themselves are **not** widened to six elements. `rules.horizontal` / `rules.vertical`
have eleven existing readers in this file — the column pass (678, 686), the edge build for the
table passes (743, 747), the row-major test (3058), `markInnerRules` (4673, 4680), the tally
helper (4743, 4828) and the two line-order collectors (5446, 5447). A widened array would not
fail to compile at any of them: index 1 and 2 would quietly stop being the segment's ends and
become, say, the width and the colour. A parallel list a reader does not know about cannot
change any reader's answer. `hStrokeAt`/`vStrokeAt` return `null` rather than throwing if the
lists ever part, and `null` already means "no stroke known", so the failure mode is the old
behaviour rather than a wrong number.

Three places had to be taught to carry the list or the indices would have parted:

| site | change |
|---|---|
| `rulesOf()` | copies `hStroke` / `vStroke` out of the collector with their rules |
| `flipY()` | copies them unchanged — a stroke is a weight and a colour, not a coordinate |
| `splitPairTable()` | the rebuilt `Table` inherits `t.sideStroke` |

## 3. Where the stroke is recorded — and where it is corrected

`RuleCollector.strokeOf()` reads the three values that are already in hand for the shape path:

```java
private float[] strokeOf() {
    int rgb = rgbOf(getGraphicsState().getStrokingColor());
    if (rgb < 0) return null;                       // no stroke colour ⇒ no stroke to describe
    float w = Math.max(0.1f, getGraphicsState().getLineWidth());
    float a = (float) getGraphicsState().getAlphaConstant();   // CA, the stroking constant
    return new float[]{w, rgb, a};
}
```

Called at both recording sites named in the brief: `appendRectangle` (the `re` → four edges) and
`lineTo` (a straight segment). Both now add through `rules.addH` / `rules.addV`.

**One addition beyond the brief, because the brief's assumption is not always true.** A rule is
recorded while the path is being *built*; the paint operator arrives afterwards. `re … S` strokes,
but `re … f` fills and paints no line at all — and the stroking colour and width read during
construction are then whatever was left over from an earlier object. That is how a 0.5 pt grey grid
rule could be described as 1 pt black: the PDF's default line width with no colour in force. So
`RuleCollector` now remembers where the current path started
(`pathRulesH` / `pathRulesV`, set in `resetPath()`) and stamps the truth at the operator:

* `strokePath()` / `fillAndStrokePath()` → `stampPathRules(true)`, the real `strokeOf()`;
* `fillPath()` → `stampPathRules(false)`: a **thin band** (≤ 1.5 pt across) *is* a hairline, so it
  gets `{thickness, non-stroking colour, non-stroke alpha}`; any other fill-only path gets
  `null`, and its edges contribute no stroke at all.

That hook alone took the match share from 97.7 % to 99.4 % — 16 border sides across the corpus that
were carrying a stroke the page never paints.

## 4. From rules to six sides

`PdfToWord.Table.sideStroke` is `float[6][]`, `{widthPt, rgb, alpha}` or null, in
`DocxWriter.TABLE_SIDES` order — `{top, left, bottom, right, insideH, insideV}`.

`markSideStrokes(t, topRules)` runs once, on the settled table list (`tables = solid;`), in the
lines' own frame (y down), where the page's rule list is still in hand:

* **outer four** — `edgeStroke()`: the rule whose coordinate is within `SIDE_TOL = 2.5 pt` of that
  edge (or within `SIDE_FRAME_TOL = 24 pt` when the table's bounds are its *ink*, which is what the
  whitespace pass measures — the frame round `04_stamp_180deg`'s fee table stands 8–14 pt outside
  it) **and** which covers at least half the table's width/height. Nearest wins; exact beats frame;
  a tie goes to the heavier rule.
* **inner two** — `insideStroke()`: the rules strictly inside the band that cover ≥ half the span,
  reduced to one answer by `dominant()`: **most rules, then most covered length**. Counting rules
  rather than summing length is what stops one long odd rule (a stamp's box edge) from being read
  as the weight a twelve-row grid is ruled at.
* **a side with no rule of its own** — `bandStroke()`: the same dominance over every rule lying on
  or inside the table, i.e. the stroke the table *is* ruled at. This is what keeps a table the page
  rules only across (`303_discharge_summary`: 35 horizontal 0.4 pt rules, not one vertical) from
  getting a 1 pt black left and right edge. Only a table with no rule at all keeps the old constant.

Deliberately **not** a median over the page: that was the earlier attempt, and it produced numbers
that matched no drawn line anywhere.

## 5. What the writer emits

`borders()` now takes six weights and six colours, one per side:

```java
private static String borders(int[] sideSz, String[] sideColour,
                              boolean outer, boolean innerH, boolean innerV)
```

and the caller builds them from the table:

```java
for (int i = 0; i < 6; i++) {
    float[] stroke = t.sideStroke[i];
    sideSz[i]     = stroke == null ? TABLE_RULE_SZ     : szOf(stroke[0]);
    sideColour[i] = stroke == null ? TABLE_RULE_COLOUR : borderColour(stroke);
}
```

Whether a side is **drawn** is unchanged (`ruled` / `innerH` / `innerV` / `pageDrewRule`); only
its weight and colour changed. A side the page did not draw is still `w:val="nil"`.

### Clamp values used

`w:sz` is in **eighths of a point** and its valid range is **2 … 96** (0.25 pt … 12 pt). A page
rule of 0.1 pt would round to `sz=1`, which is invalid and which a reader may drop along with the
whole `tblBorders` element.

```java
private static final int TABLE_RULE_SZ_MIN = 2;    // 0.25 pt
private static final int TABLE_RULE_SZ_MAX = 96;   // 12 pt

private static int szOf(float widthPt) {
    int sz = Math.round(Math.max(0.1f, widthPt) * 8f);
    return Math.max(TABLE_RULE_SZ_MIN, Math.min(TABLE_RULE_SZ_MAX, sz));
}
```

**On this corpus the clamp never engages**: 0 of 900 emitted sides sit at `sz=2` and 0 at `sz=96`.
It is a guard, not a working value. The narrowest side actually written is `sz=3` (0.375 pt, a
0.4 pt page rule) and the widest `sz=16` (2 pt). 22 of 900 sides still fall back to the old
`sz=8`/`000000` — sides on tables where no rule could be read at all.

### Opacity has no home in `w:tblBorders` — the limitation, stated

`w:tblBorders` carries only `w:val`, `w:sz`, `w:space`, `w:color`. There is no `w:alpha`. A faint
rule therefore cannot be written as a black rule at 30 %; it is written as **the colour that rule
looks like on white**:

```java
c' = round(c * a + 255 * (1 - a))    // per channel; a = CA from the graphics state
```

A 30 % black hairline becomes `D8D8D8`. This is an approximation with three known edges:
it assumes a white page (on a tinted band the blend goes the wrong way), it does not model a rule
overlapping another rule, and the colour is no longer the page's colour if the reader recolours the
page. It is the best the format allows, and it is not hidden. **396 of 900 sides** (44 %) are
written this way — almost all of them `sz=4` in `9B9B9B`, i.e. the 0.5 pt hairline at ~39 % that
most of this corpus uses for its grid. Before this change every one of those was 1 pt black.

## 6. Proof — drawn PDF lines against emitted borders

Script: `compare_strokes.py` (Python + PyMuPDF 2.1 / MuPDF 1.28.6). For every document it reads

* **the PDF side** with `page.get_drawings()`: every stroked axis-aligned `l` item, every edge of a
  stroked `re`, and every *filled* band ≤ 1.5 pt thick (the way most generators draw a hairline),
  each as `(width_pt, r, g, b, stroke_opacity, orientation)`;
* **the .docx side** from `word/document.xml`: every `w:tblBorders` side with `w:val="single"`,
  as `(side, sz, colour)`.

A side matches when its width is within **0.4 pt** (covers the 1/8 pt rounding of `w:sz`) of a drawn
rule **of the same orientation in the same document** and its colour is within **24 per channel** of
that rule's colour blended by its own opacity. Sides for which the page draws no rule of that
orientation at all are counted separately — no weight could ever match them, and they are the
"writer claims a side the page never drew" defect, not D-22.

### Before / after, whole corpus

| | before | after |
|---|---|---|
| documents that emit table borders | 99 | 99 |
| emitted border sides (`w:val="single"`) | 900 | 900 |
| matched to a drawn PDF line | **495 (55.0 %)** | **895 (99.4 %)** |
| distinct `(sz, colour)` pairs used | **1** — `(8, 000000)` × 900 | **14** |
| sides not `000000` | 0 | 444 |
| documents with 0 % match | 21 | 0 |
| documents at 100 % | — | 97 |
| documents improved | — | 55 |
| documents worse | — | 1 (`07_stamp_over_table`, 6/6 → 5/6) |
| tables whose six sides are not all equal | 0 | 32 |

The stroke set actually emitted now (all 900 sides):

| `w:sz` | colour | sides | what it is |
|---|---|---|---|
| 4 | 9B9B9B | 396 | 0.5 pt black at ~39 % opacity, blended |
| 3 | 000000 | 279 | 0.4 pt black hairline |
| 4 | 000000 | 75 | 0.5 pt black |
| 6 | 000000 | 69 | 0.75 pt black |
| 8 | 000000 | 22 | fallback: page draws no rule on any side |
| 4 | 595959 | 20 | 0.5 pt grey |
| 3 | 808080 | 12 | 0.4 pt mid grey |
| 5 | 595959 | 9 | 0.6 pt grey |
| 16 | 000000 | 6 | 2 pt black frame |
| 3 | BFBFBF | 5 | 0.4 pt black at ~25 % |
| 5 | 000000 | 4 | 0.6 pt black |
| 12 / 13 / 4 | 0D6B2E / 000000 / BFBFBF | 1 each | the residuals below |

### Three documents, side by side

`80_gstin_pan_cin_ifsc_table` — the page draws 0.5 pt `#595959` rules (10 horizontal, 10 vertical):

```
before  <w:top    w:val="single" w:sz="8" w:color="000000"/>  …  ×4 sides
after   <w:top    w:val="single" w:sz="4" w:color="595959"/>  …  ×4 sides
```

`324_loan_amortisation_schedule` — 2 214 rules, all 0.4 pt black:

```
before  … w:sz="8" w:color="000000"   ×6 sides
after   … w:sz="3" w:color="000000"   ×6 sides
```

`01_stamp_rotated_15deg_upright` — six sides that are genuinely not one weight:

```
before  top/left/bottom/right/insideH/insideV all w:sz="8" w:color="000000"
after   top w:sz="4"  insideH w:sz="4"  left/bottom/right w:sz="6"  insideV nil
```

That last one is the user's request visible in one element: the page rules the row separators
lighter than the frame, and the .docx now does too. A table whose six sides differ **will** look
uneven — that is the page.

### The five remaining misses

| document | side | emitted | why |
|---|---|---|---|
| `07_stamp_over_table` | insideV | `sz=12` `0D6B2E` | a green 1.44 pt **stamp box** is drawn *over* the table; its two vertical edges are the only rules strictly inside the band, so they win the inner-side dominance. The page's own separators are the 0.7 pt black frame. |
| `360_restaurant_menu` | left, right ×2 tables | `sz=8` `000000` | the page draws **no** rule on these two menus at all (they are whitespace tables; the 0.8 pt green/red rules on the page belong to another region), so `bandStroke` is null and the old constant stands. The right fix is `nil`, and that is a *drawnness* decision, not a stroke one — see §8. |

This is the one document that the metric scores worse than before (6/6 → 5/6), because the constant
`8/000000` it used to emit happened to coincide with a 1 pt black line elsewhere in that PDF while
the green separator matches nothing. I did not special-case it: every rule that would ignore the
stamp's edge (ignore rules that are part of a closed rectangle, or ignore a stroke no outer side
uses) would also throw away a header rule that is genuinely heavier than the table's frame, which
is a real and common pattern. Documenting one wrong side is better than breaking many right ones.

## 7. The gate and the engine suites

```
$ python3 tools/p2w-bench/gate.py --corpus <corpus> --out <out> \
      --baseline tools/p2w-bench/base208.json --check
documents: 208
no document got worse
```

Run on the corpus flattened to one directory (the gate enumerates `os.listdir`, and the three
release zips unpack into subdirectories; 208 unique names, no collisions). Baseline run of the
unpatched tree prints the same line, so the comparison is like for like.

```
TestEngine       TOTAL: 81 passed, 0 failed
TestPdfToWord    PDF2WORD TOTAL: 29 passed, 0 failed
TestRealDocs     REALDOCS TOTAL: 3 passed, 0 failed   (96.8 % / 97.0 % / 81.7 %)
```

Suites run and seen passing on this build: `TestEngine` 81/81, `TestHostile` 9/9,
`TestPdfToWord` 29/29, `TestRealDocs` 3/3, `FONTS: PASS`, `TestCachePolicy` 16/16,
`TestFlatten` PASS, `TestMeta` PASS. `tools/verify-engine.sh` was also run: it rebuilds everything
from scratch and passes through the font checks above before it reaches the OCR section, which
needs a PyMuPDF install plus a render pass and did not finish within the 300 s command limit. The OCR, rotation, crop and encryption paths are untouched by this patch — it adds
data to `Rules`/`Table` and changes two `w:tblBorders` attributes — and the shape/opacity path
(`<a:ln>`, `lineAlpha`) is not modified at all.

Structural checks on the 208 outputs: every `.docx` is well-formed XML, no `w:sz` outside 2…96,
and the built output is byte-identical in `document.xml` to the build the numbers above were
measured on.

## 8. What this does not do

* **Opacity is a blended colour**, not an opacity (§5). There is no other home for it in
  `w:tblBorders`.
* **Drawn-vs-nil is untouched.** Whether a side exists is still decided by `ruled` / `innerH` /
  `innerV` / `pageDrewRule`. `360_restaurant_menu` shows the seam: the page draws nothing and the
  writer still claims four sides. Making `sideStroke == null` mean "nil" would fix it, but it
  changes which lines exist rather than how heavy they are, and the 403/406 history in
  `borders()` is a warning about getting that wrong. It deserves its own change.
* **`TABLE_BORDER_TW` still charges the old 0.75 pt rule** to every row's height (15 twips). With
  per-side weights the honest charge is `(sz[top] + sz[bottom]) / 16` pt; on this corpus that moves
  row heights by well under a point and it is not part of D-22, so it was left alone rather than
  folded into a change that has to keep the gate clean.
* **The shape path is unchanged.** `Shape` already carried `lineWidthPt` / `lineRgb` / `lineAlpha`
  and `<a:ln>` already wrote all three; D-22's "everywhere, not only tables" half was already true
  there.

## 9. Reproduce

```bash
# build (JDK 17, the repo's own verify script or the four jars it downloads)
git clone --depth 1 https://github.com/kavopdf/app W && cd W
bash tools/verify-engine.sh
CP=$LIBS/aar/classes.jar:$LIBS/bcprov.jar:$LIBS/bcpkix.jar:$LIBS/bcutil.jar:out   # $LIBS = where verify-engine.sh put them
cd tools/engine-verify && javac -nowarn -cp "$CP" -d out ../../app/src/main/java/com/kavopdf/app/engine/*.java
javac -nowarn -cp "$CP" -d out ConvertAll.java
java -XX:+UseSerialGC -XX:ActiveProcessorCount=1 -Xmx900m -Djava.awt.headless=true \
     -Dp2w.assets=$LIBS/aar/assets -cp "$CP" ConvertAll <corpus> <out>
# gate
python3 tools/p2w-bench/gate.py --corpus <corpus> --out <out> --baseline tools/p2w-bench/base208.json --check
# the proof (run against the pre-patch output too — that is the 55.0 %)
python3 compare_strokes.py <corpus> <out> --json after.json
```

## 10. The diff

`PdfToWord.java`, +343 / −7:

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
index 6aa9127..aa62e84 100644
--- a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
+++ b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
@@ -248,6 +248,27 @@ public final class PdfToWord {
          * lines the page never drew, so each side is decided on its own evidence.
          */
         public boolean innerH, innerV;
+        /**
+         * The stroke the page drew on each of the table's six sides, in
+         * {@link DocxWriter#TABLE_SIDES} order - {@code {top, left, bottom, right, insideH,
+         * insideV}} - each {@code {widthPt, rgb, alpha}}, or null where no rule this pass could
+         * see lies on that side.
+         *
+         * <p>D-22. {@code w:tblBorders} carried one constant weight and one constant colour on
+         * all six sides of every table (see {@code DocxWriter.borders}), so a table the page
+         * ruled at 0.4 pt in grey came out at 1 pt in black and a table the page ruled at 2 pt
+         * came out at 1 pt too. The user's words: some rules are thick, some thin, some dark,
+         * some faint, and in the .docx they were all one weight and one colour. Each side now
+         * carries the stroke of the rule that actually lies on it - filled by
+         * {@code PdfToWord.markSideStrokes}, where the page's own rule list is in hand.
+         *
+         * <p>Null is not "undrawn": whether a side is drawn is still decided by {@link #ruled},
+         * {@link #innerH} and {@link #innerV}. Null only means no rule of its own was read, and
+         * {@code markSideStrokes} then lends it the stroke the table's other rules are drawn at;
+         * a table with no rule at all leaves it null, and the writer falls back to the old
+         * constant - so a side that used to be right stays right.
+         */
+        public final float[][] sideStroke = new float[6][];
         public float top, bottom, left, right;
         public int column;
     }
@@ -800,6 +821,11 @@ public final class PdfToWord {
             else for (Line line : lines) if (line.inside(t)) line.consumed = false;
         }
         tables = solid;
+        // Every table that survives carries the stroke the page drew on each of its six sides,
+        // read here - the last point at which the page's own rule list is still in hand and the
+        // table's bounds are final. D-22: the writer used to draw all six at one constant
+        // weight and one constant colour whatever the page did.
+        for (Table t : tables) markSideStrokes(t, topRules);
 
         // Text already sitting in a table cell must not also come out as body text: the bill of
         // lading appeared twice, once as a run-on paragraph and once as its proper table.
@@ -3762,6 +3788,47 @@ public final class PdfToWord {
     static final class Rules {
         final List<float[]> horizontal = new ArrayList<>();   // {y, x1, x2}
         final List<float[]> vertical = new ArrayList<>();     // {x, y1, y2}
+        /**
+         * The stroke each horizontal rule was drawn with: {@code {widthPt, rgb, alpha}}, at the
+         * SAME index as its rule in {@link #horizontal}.
+         *
+         * <p>D-22: a rule's weight and opacity are the page's own, and the model had nowhere to
+         * keep them - a rule was three floats of geometry, so every table border downstream was
+         * written at one constant weight and one constant colour however the page drew it.
+         *
+         * <p>These are PARALLEL lists, not wider arrays. Widening {@code {y, x1, x2}} to six
+         * floats would silently misread at every existing reader of {@code rules.horizontal}
+         * (there are eleven of them, in the column pass, the table passes and the row pass), and
+         * a reader that does not know about the extra elements reads index 1 and 2 as the
+         * segment's ends - a wrong answer, not a compile error. A list nobody reads yet cannot
+         * break anybody. Add through {@link #addH} / {@link #addV} so the two lists stay in step.
+         */
+        final List<float[]> hStroke = new ArrayList<>();
+        /** The stroke each vertical rule was drawn with, at the same index as {@link #vertical}. */
+        final List<float[]> vStroke = new ArrayList<>();
+
+        /** Records a horizontal rule and the stroke it was drawn with, index for index. */
+        void addH(float[] rule, float[] stroke) {
+            horizontal.add(rule);
+            hStroke.add(stroke);
+        }
+
+        /** Records a vertical rule and the stroke it was drawn with, index for index. */
+        void addV(float[] rule, float[] stroke) {
+            vertical.add(rule);
+            vStroke.add(stroke);
+        }
+
+        /** The stroke at a horizontal rule's index, or null when the lists have parted. */
+        float[] hStrokeAt(int i) {
+            return i >= 0 && i < hStroke.size() ? hStroke.get(i) : null;
+        }
+
+        /** The stroke at a vertical rule's index, or null when the lists have parted. */
+        float[] vStrokeAt(int i) {
+            return i >= 0 && i < vStroke.size() ? vStroke.get(i) : null;
+        }
+
         int images;
         /**
          * The raster images the page draws, in draw order, with the rectangle each one covers.
@@ -3800,6 +3867,8 @@ public final class PdfToWord {
         private float pxMax = Float.NaN, pyMax = Float.NaN;
         /** What the path is made of - a rectangle, one straight line, or something curved. */
         private int pMoves, pLines, pCurves, pRects;
+        /** How many rules the lists held when the current path started (see stampPathRules). */
+        private int pathRulesH, pathRulesV;
         /** The single segment's own end points, for the axis-aligned line case. */
         private float segX0 = Float.NaN, segY0 = Float.NaN, segX1 = Float.NaN, segY1 = Float.NaN;
         /**
@@ -3859,6 +3928,10 @@ public final class PdfToWord {
             cmds = new java.util.ArrayList<>();
             cmdsOverflow = false;
             pathClosed = false;
+            // The rule lists' sizes at the start of this path: the rules this path adds are the
+            // ones the paint operator will be told about when it arrives.
+            pathRulesH = rules.horizontal.size();
+            pathRulesV = rules.vertical.size();
         }
 
         /** Records one path operator, unless the path has grown past what a shape can carry. */
@@ -4054,6 +4127,69 @@ public final class PdfToWord {
             addShape(cl, fill, alpha, line, lw, pathIsEllipse() ? 1 : 0);
         }
 
+        /**
+         * The stroke in force right now, as {@code {widthPt, rgb, alpha}} - the weight, the
+         * colour and the constant alpha the page will paint the current path with.
+         *
+         * <p>The same three values the shape path already reads (4039, 4102 and
+         * {@code addShape}). A rule was recorded as geometry alone, so the page's 0.4 pt grey
+         * grid rule and its 2 pt black frame arrived at the writer as the same thing.
+         */
+        private float[] strokeOf() {
+            int rgb = rgbOf(getGraphicsState().getStrokingColor());
+            // No stroke colour in force means there is no stroke to describe. A `re` that the
+            // page only FILLS is still a table-border candidate here, and its four edges used to
+            // be recorded with the PDF's default line width (1 pt) and no colour at all - which
+            // is how a 0.5 pt grey grid rule came out as a 1 pt black border. Record nothing and
+            // the side falls back to the table's own stroke instead.
+            if (rgb < 0) return null;
+            float w = Math.max(0.1f, getGraphicsState().getLineWidth());
+            float a = (float) getGraphicsState().getAlphaConstant();
+            return new float[]{w, rgb, a};
+        }
+
+        /**
+         * Gives the rules this path added the stroke the path is actually painted with.
+         *
+         * <p>A rule is recorded while the path is being BUILT, and the paint operator comes
+         * after it: {@code re ... S} strokes, {@code re ... f} fills and paints no line at all.
+         * The graphics state during construction is usually the one that paints, but not when a
+         * page draws a filled band and leaves a stroking colour set from earlier - 07_stamp_
+         * over_table then reported a 1.5 pt green column separator inside a table the page rules
+         * in 0.7 pt black. So the stroke is stamped here, at the operator, where it is known.
+         *
+         * <p>A fill-only path that is a thin band IS a hairline: the band's thickness is the
+         * weight and its fill colour is the colour, which is how most generators draw a rule. Any
+         * other fill-only path paints no rule, and its edges keep no stroke at all - the table
+         * border then falls back to the table's own stroke rather than to a colour nothing on the
+         * page uses.
+         */
+        private void stampPathRules(boolean stroked) {
+            float[] stroke = stroked ? strokeOf() : bandFillStroke();
+            for (int i = Math.max(0, pathRulesH); i < rules.horizontal.size(); i++) {
+                if (i < rules.hStroke.size()) rules.hStroke.set(i, stroke);
+            }
+            for (int i = Math.max(0, pathRulesV); i < rules.vertical.size(); i++) {
+                if (i < rules.vStroke.size()) rules.vStroke.set(i, stroke);
+            }
+        }
+
+        /** The stroke a fill-only path implies: a thin band is a hairline, anything else none. */
+        private float[] bandFillStroke() {
+            if (Float.isNaN(pxMin)) return null;
+            if (pCurves != 0) return null;
+            boolean rect = pRects == 1 && pLines == 0;
+            boolean quad = pLines == 4 && pRects == 0;
+            if (!rect && !quad) return null;
+            int fill = rgbOf(getGraphicsState().getNonStrokingColor());
+            if (fill < 0) return null;
+            float alpha = (float) getGraphicsState().getNonStrokeAlphaConstant();
+            float hgt = pyMax - pyMin, wid = pxMax - pxMin;
+            if (hgt <= 1.5f && wid > 2f) return new float[]{Math.max(0.1f, hgt), fill, alpha};
+            if (wid <= 1.5f && hgt > 2f) return new float[]{Math.max(0.1f, wid), fill, alpha};
+            return null;
+        }
+
         /** True when two boxes are the same to a hundredth of a point. */
         private static boolean same(float[] a, float[] b) {
             if (a == null || b == null) return a == b;
@@ -4167,14 +4303,20 @@ public final class PdfToWord {
             float maxX = Math.max(Math.max(p0.x, p1.x), Math.max(p2.x, p3.x));
             float minY = Math.min(Math.min(p0.y, p1.y), Math.min(p2.y, p3.y));
             float maxY = Math.max(Math.max(p0.y, p1.y), Math.max(p2.y, p3.y));
-            // A rectangle is a table border candidate: keep all four edges.
+            // A rectangle is a table border candidate: keep all four edges, each with the
+            // stroke the page is drawing the path with right now. The width, the colour and
+            // the alpha are all in the graphics state at this point, and they are the ones a
+            // `S` after this `re` will paint with. (A `re` that is only filled, never stroked,
+            // records the fill-only stroke it did not use; see D-22's note in the report - a
+            // path's own paint operator is not visible here.)
+            float[] stroke = strokeOf();
             if (maxX - minX > 2) {
-                rules.horizontal.add(new float[]{minY, minX, maxX});
-                rules.horizontal.add(new float[]{maxY, minX, maxX});
+                rules.addH(new float[]{minY, minX, maxX}, stroke);
+                rules.addH(new float[]{maxY, minX, maxX}, stroke);
             }
             if (maxY - minY > 2) {
-                rules.vertical.add(new float[]{minX, minY, maxY});
-                rules.vertical.add(new float[]{maxX, minY, maxY});
+                rules.addV(new float[]{minX, minY, maxY}, stroke);
+                rules.addV(new float[]{maxX, minY, maxY}, stroke);
             }
             // A path may mix a `re` with other segments - a hatch region clips a rectangle and
             // then draws lines in the same path object - so the rectangle is part of the path
@@ -4314,10 +4456,15 @@ public final class PdfToWord {
             grow(x, y);
             segX0 = lastX; segY0 = lastY; segX1 = x; segY1 = y;
             float dx = Math.abs(x - lastX), dy = Math.abs(y - lastY);
+            // The stroke this segment will be painted with: the same three values the shape
+            // path reads at 4039 and 4102, taken here so a rule keeps the page's own weight.
+            float[] stroke = null;
             if (dx <= 0.8f && dy > 2f) {
-                rules.vertical.add(new float[]{lastX, Math.min(lastY, y), Math.max(lastY, y)});
+                stroke = strokeOf();
+                rules.addV(new float[]{lastX, Math.min(lastY, y), Math.max(lastY, y)}, stroke);
             } else if (dy <= 0.8f && dx > 2f) {
-                rules.horizontal.add(new float[]{lastY, Math.min(lastX, x), Math.max(lastX, x)});
+                stroke = strokeOf();
+                rules.addH(new float[]{lastY, Math.min(lastX, x), Math.max(lastX, x)}, stroke);
             }
             lastX = x;
             lastY = y;
@@ -4355,6 +4502,7 @@ public final class PdfToWord {
 
         @Override
         public void strokePath() {
+            stampPathRules(true);
             emitStroke();
             commitClip();
             resetPath();
@@ -4363,6 +4511,7 @@ public final class PdfToWord {
 
         @Override
         public void fillPath(android.graphics.Path.FillType fillType) {
+            stampPathRules(false);
             emitFill(false);
             commitClip();
             resetPath();
@@ -4371,6 +4520,7 @@ public final class PdfToWord {
 
         @Override
         public void fillAndStrokePath(android.graphics.Path.FillType fillType) {
+            stampPathRules(true);
             emitFill(true);
             commitClip();
             resetPath();
@@ -4495,6 +4645,10 @@ public final class PdfToWord {
             collector.processPage(page);
             out.horizontal.addAll(collector.rules.horizontal);
             out.vertical.addAll(collector.rules.vertical);
+            // The strokes travel with their rules or the parallel lists part here, and every
+            // index after this point reads another rule's weight. D-22.
+            out.hStroke.addAll(collector.rules.hStroke);
+            out.vStroke.addAll(collector.rules.vStroke);
             out.images = collector.rules.images;
             out.pictures.addAll(collector.rules.pictures);
             out.shapes.addAll(collector.rules.shapes);
@@ -4533,6 +4687,182 @@ public final class PdfToWord {
         }
     }
 
+    /** How far off a table's own edge a rule may sit and still be that side's rule. */
+    private static final float SIDE_TOL = 2.5f;
+    /**
+     * How far off it may sit when the table's bounds are its TEXT's ink rather than the
+     * rectangle the page strokes - the whitespace pass measures ink, so the frame the page
+     * draws round a table can stand 8 to 15 pt outside it (04_stamp_180deg: 8.3 pt left of the
+     * first character, 14.3 pt above the first row).
+     */
+    private static final float SIDE_FRAME_TOL = 24f;
+
+    /**
+     * Records, on the table, the stroke the page drew along each of its six sides (D-22).
+     *
+     * <p>Called where the page's own rule list is in hand - the same place
+     * {@link #markInnerRules} is called, and in the lines' own frame (y down). Each side is
+     * matched on its own: the outer four against the rules that lie along that edge, the two
+     * inner sides against the rules that run across the table's band.
+     *
+     * <p>Which rule wins when several lie on one side. On an outer edge the NEAREST rule wins -
+     * a table whose top edge is also the bottom edge of the band above it has two rules within
+     * tolerance and the one the table's own line is the nearer. Across an inner side the rule
+     * that covers the most length wins, so a 12-row grid reports the weight it is ruled at
+     * twelve times rather than the one odd rule some generator drew once. Both are a real rule
+     * on that side; neither is a median over the page, which is what the earlier attempt
+     * computed and why its numbers matched no drawn line anywhere.
+     */
+    private static void markSideStrokes(Table t, Rules rules) {
+        if (rules == null) return;
+        float w = t.right - t.left, h = t.bottom - t.top;
+        if (w <= 0f || h <= 0f) return;
+        t.sideStroke[0] = edgeStroke(rules, true, t.top, t.left, t.right, w);      // top
+        t.sideStroke[2] = edgeStroke(rules, true, t.bottom, t.left, t.right, w);   // bottom
+        t.sideStroke[1] = edgeStroke(rules, false, t.left, t.top, t.bottom, h);    // left
+        t.sideStroke[3] = edgeStroke(rules, false, t.right, t.top, t.bottom, h);   // right
+        t.sideStroke[4] = insideStroke(rules, true, t.top, t.bottom, t.left, t.right, w);   // insideH
+        t.sideStroke[5] = insideStroke(rules, false, t.left, t.right, t.top, t.bottom, h);  // insideV
+        // A side the page drew no rule along still gets a weight, because the side is written
+        // either way. It takes the table's own stroke rather than the writer's old constant.
+        float[] tableStroke = bandStroke(rules, t);
+        if (tableStroke != null) {
+            for (int i = 0; i < 6; i++) if (t.sideStroke[i] == null) t.sideStroke[i] = tableStroke;
+        }
+    }
+
+    /**
+     * The stroke of the rule lying along one outer edge of a table, or null.
+     *
+     * @param horizontal true for a rule that runs across the page, matched on its y
+     * @param at         the edge's coordinate in the rules' own frame
+     * @param a0,a1      the extent the rule has to cover, along the table's other axis
+     * @param span       the table's size along that axis, for the half-coverage test
+     */
+    private static float[] edgeStroke(Rules rules, boolean horizontal, float at,
+                                      float a0, float a1, float span) {
+        List<float[]> geom = horizontal ? rules.horizontal : rules.vertical;
+        float[] best = null;
+        float bestDistance = Float.MAX_VALUE;
+        for (int i = 0; i < geom.size(); i++) {
+            float[] g = geom.get(i);
+            float distance = Math.abs(g[0] - at);
+            if (distance > SIDE_FRAME_TOL) continue;
+            // Half the table's width has to lie on the rule: a 3 pt tick beside the corner is
+            // not the table's edge, and neither is the page frame.
+            if (Math.min(g[2], a1) - Math.max(g[1], a0) < span * 0.5f) continue;
+            float[] stroke = horizontal ? rules.hStrokeAt(i) : rules.vStrokeAt(i);
+            if (stroke == null) continue;
+            // Exact beats frame, then the nearest wins; a tie goes to the heavier rule, which
+            // is the one a reader sees as the edge.
+            boolean exact = distance <= SIDE_TOL;
+            if (best == null) {
+                best = stroke;
+                bestDistance = distance;
+                continue;
+            }
+            boolean bestExact = bestDistance <= SIDE_TOL;
+            if (exact != bestExact) {
+                if (exact) { best = stroke; bestDistance = distance; }
+                continue;
+            }
+            if (distance < bestDistance - 0.01f) {
+                best = stroke;
+                bestDistance = distance;
+            } else if (Math.abs(distance - bestDistance) <= 0.01f && stroke[0] > best[0]) {
+                best = stroke;
+            }
+        }
+        return best;
+    }
+
+    /**
+     * The stroke the page rules one inner side of a table at, or null.
+     *
+     * <p>An inner side is one element in {@code w:tblBorders} for every separator of that
+     * direction, so the rules inside the band have to be reduced to one answer: the stroke
+     * carrying the most length wins. A row separator that is 0.4 pt grey for twelve rows and a
+     * single 2 pt black line under the header row report 0.4 pt grey, which is what the table
+     * is ruled at.
+     */
+    private static float[] insideStroke(Rules rules, boolean horizontal, float lo, float hi,
+                                        float a0, float a1, float span) {
+        java.util.LinkedHashMap<String, float[]> byStroke = new java.util.LinkedHashMap<>();
+        tally(byStroke, rules, horizontal, lo + 1f, hi - 1f, a0, a1, span);
+        return dominant(byStroke);
+    }
+
+    /**
+     * The stroke this table's own rules are drawn at, for a side that has no rule of its own.
+     *
+     * <p>A table the page rules only across (303_discharge_summary draws 35 horizontal rules at
+     * 0.4 pt and not one vertical rule) still has six sides in {@code w:tblBorders}, because the
+     * ruled pass put its bounds on the grid. Two of those sides have no rule to read a weight
+     * off. The constant that stood in for them was 1 pt black against a table ruled at 0.4 pt
+     * black - a side visibly heavier than every other side of the same table, which is the very
+     * thing D-22 is about. So a side with no rule of its own takes the stroke the table's rules
+     * ARE drawn at: the stroke carrying the most length among the rules that lie anywhere on or
+     * inside the table. It is the table's own ink, not a median over the page.
+     */
+    private static float[] bandStroke(Rules rules, Table t) {
+        float w = t.right - t.left, h = t.bottom - t.top;
+        java.util.LinkedHashMap<String, float[]> byStroke = new java.util.LinkedHashMap<>();
+        // The frame tolerance, not the side tolerance: a whitespace table's bounds are its ink,
+        // so the rules round it stand up to 15 pt outside its own band (see SIDE_FRAME_TOL).
+        tally(byStroke, rules, true, t.top - SIDE_FRAME_TOL, t.bottom + SIDE_FRAME_TOL,
+                t.left, t.right, w);
+        tally(byStroke, rules, false, t.left - SIDE_FRAME_TOL, t.right + SIDE_FRAME_TOL,
+                t.top, t.bottom, h);
+        return dominant(byStroke);
+    }
+
+    /**
+     * Adds the rules that cross one band to a per-stroke running total of covered length.
+     *
+     * @param lo,hi the band's edges, in the rules' own frame, exclusive
+     * @param a0,a1 the extent a rule has to cover, along the table's other axis
+     * @param span  the table's size along that axis, for the half-coverage test
+     */
+    private static void tally(java.util.LinkedHashMap<String, float[]> byStroke, Rules rules,
+                              boolean horizontal, float lo, float hi,
+                              float a0, float a1, float span) {
+        List<float[]> geom = horizontal ? rules.horizontal : rules.vertical;
+        for (int i = 0; i < geom.size(); i++) {
+            float[] g = geom.get(i);
+            if (g[0] <= lo || g[0] >= hi) continue;
+            float cover = Math.min(g[2], a1) - Math.max(g[1], a0);
+            if (cover < span * 0.5f) continue;
+            float[] stroke = horizontal ? rules.hStrokeAt(i) : rules.vStrokeAt(i);
+            if (stroke == null) continue;
+            String key = Math.round(stroke[0] * 8f) + "|" + (int) stroke[1] + "|"
+                    + Math.round(stroke[2] * 20f);
+            float[] acc = byStroke.get(key);
+            // {rules, covered length, widthPt, rgb, alpha} - the rule COUNT decides, because one
+            // long rule that crosses the band is as likely a stamp's edge or a band's outline as
+            // a separator, while the twelve rules a grid is ruled with are the grid.
+            if (acc == null) byStroke.put(key, new float[]{1f, cover, stroke[0], stroke[1], stroke[2]});
+            else { acc[0] += 1f; acc[1] += cover; }
+        }
+    }
+
+    /**
+     * The stroke the most rules in a {@link #tally} are drawn with, or null when it is empty.
+     *
+     * <p>Most rules, then most covered length. Counting the rules rather than summing their
+     * length is what keeps a stamp's green outline - one 1.5 pt rule lying inside a table's band
+     * on 07_stamp_over_table - from being read as the weight the table's column separators are
+     * ruled at. The length is the tie-break, so two strokes used equally often resolve to the one
+     * that covers more of the table.
+     */
+    private static float[] dominant(java.util.LinkedHashMap<String, float[]> byStroke) {
+        float[] best = null;
+        for (float[] acc : byStroke.values()) {
+            if (best == null || acc[0] > best[0]
+                    || (acc[0] == best[0] && acc[1] > best[1])) best = acc;
+        }
+        return best == null ? null : new float[]{best[2], best[3], best[4]};
+    }
+
     /**
      * Builds tables from the lines the page actually draws.
      *
@@ -5085,6 +5415,10 @@ public final class PdfToWord {
         Rules out = new Rules();
         for (float[] h : in.horizontal) out.horizontal.add(new float[]{pageHeight - h[0], h[1], h[2]});
         for (float[] v : in.vertical) out.vertical.add(new float[]{v[0], pageHeight - v[2], pageHeight - v[1]});
+        // A stroke is a weight and a colour, not a coordinate: it is the same in either frame,
+        // so the parallel lists are copied across unchanged and keep their indices.
+        out.hStroke.addAll(in.hStroke);
+        out.vStroke.addAll(in.vStroke);
         out.images = in.images;
         return out;
     }
@@ -5597,6 +5931,8 @@ public final class PdfToWord {
 
         Table out = new Table();
         out.ruled = t.ruled;
+        // The rebuilt record stands where the old one stood, so it keeps the page's strokes.
+        for (int i = 0; i < 6; i++) out.sideStroke[i] = t.sideStroke[i];
         // The record's own heading - the numbered line that is not a label/value pair - keeps
         // its place at the top, because it introduces both panels.
         for (int r = 0; r < t.rows.size(); r++) {
```

`DocxWriter.java`, +83 / −27:

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 9216473..cf133df 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -2179,26 +2179,34 @@ public final class DocxWriter {
      * place the text and destroy the table, which is the one thing a conversion must not do.
      */
     /**
-     * The table's borders: one weight and one colour, on every ruled table.
+     * The table's borders: each of the six sides at its own weight and its own colour.
      *
-     * <p>Every side the page drew a rule on gets the one hairline every ruled table gets; every
-     * side it did not gets "none" - never no w:tblBorders element at all, because absent borders
+     * <p>Every side the page drew a rule on gets that side's OWN weight and colour - D-22: the
+     * six sides are six arguments now, one per side, taken from the rule that actually lies on
+     * that side ({@link PdfToWord.Table#sideStroke}). A side the page did not draw gets "nil" -
+     * never no w:tblBorders element at all, because absent borders
      * fall back to the table style and the default style draws a box, which is exactly the box
      * 403 and 406 were carrying. The four outer sides are {@code outer}, the row separators
      * {@code innerH} and the column separators {@code innerV}; a table the ruled pass found has
      * all three, because there the bounds ARE the drawn grid.
      *
-     * <p>The weight used to be read off the stroke the page drew (c47efc2), so one corpus
-     * carried sz 3, 4, 5, 6, 8 and 10 at once: a table ruled at 0.5 pt came out heavier than
-     * one ruled at 1.25 pt, and the user's verdict was that table lines must not be thick in
-     * one place and thin in another. 23_timetable_grid_txtpos is the document they called
-     * correct, and every one of its borders is sz="6" in 000000 - so that is the single
-     * weight and the single colour. It is also the weight {@link #TABLE_BORDER_TW} is measured
-     * from, so the row pitch the writer asks for stays true.
+     * <p>The history matters, because this has now been the other way twice. The weight used to
+     * be read off the stroke the page drew (c47efc2), but off the PAGE's stroke rather than the
+     * rule on the side being written, so a table ruled at 0.5 pt came out heavier than one ruled
+     * at 1.25 pt and the numbers matched no line anywhere; the answer then was one constant
+     * (D-22's predecessor). D-22 is the third state and the one the user asked for: the page's
+     * own weight and opacity, side by side on the same table, so a table ruled at 0.4 pt grey
+     * inside a 2 pt black frame comes out that way. A table whose six sides genuinely differ
+     * will look uneven - that is the page, not a bug.
+     *
+     * <p>A side with no stroke ({@code sideStroke} null) keeps the old constant, sz 8 in
+     * 000000, so nothing that used to be right changes.
      */
-    private static String borders(boolean outer, boolean innerH, boolean innerV) {
+    private static String borders(int[] sideSz, String[] sideColour,
+                                  boolean outer, boolean innerH, boolean innerV) {
         StringBuilder b = new StringBuilder("<w:tblBorders>");
-        for (String side : TABLE_SIDES) {
+        for (int i = 0; i < TABLE_SIDES.length; i++) {
+            String side = TABLE_SIDES[i];
             boolean drawn = "insideH".equals(side) ? innerH
                     : "insideV".equals(side) ? innerV
                     : outer;
@@ -2206,33 +2214,72 @@ public final class DocxWriter {
             // by definition - a reader resolves it to whatever it thinks a line is, usually the
             // flipped text colour - and it was written on 486 sides across 59 documents. A side
             // the page did not draw is no line at all, and "nil" says that without naming a
-            // colour that someone else will decide. The weight stays one constant: the user's
-            // verdict was that table lines must not be thick in one place and thin in another.
+            // colour that someone else will decide.
             b.append("<w:").append(side).append(" w:val=\"").append(drawn ? "single" : "nil").append("\"");
-            if (drawn) b.append(" w:sz=\"").append(TABLE_RULE_SZ)
-                    .append("\" w:color=\"").append(TABLE_RULE_COLOUR).append("\"");
+            if (drawn) b.append(" w:sz=\"").append(sideSz[i])
+                    .append("\" w:color=\"").append(sideColour[i]).append("\"");
             b.append("/>");
         }
         return b.append("</w:tblBorders>").toString();
     }
 
     /**
-     * The one weight every ruled table is drawn at, in eighths of a point: 6/8 pt = 0.75 pt.
-     * See {@link #borders} for why this is a constant and not the page's own stroke.
-     */
-    /**
-     * The one weight every ruled table is drawn at, in eighths of a point: 8/8 pt = 1 pt.
+     * The weight a side falls back to when the page's own stroke for it was not read: sz 8, in
+     * eighths of a point, so 1 pt.
      *
      * <p>Measured off the two commercial converters, which are the same engine and produce
      * byte-identical styles, settings and theme parts: every one of their six table sides is
-     * <code>w:sz="8" w:color="000000"</code>. This writer used 6 (0.75 pt), which is lighter than
-     * the page draws and lighter than the market leader. One weight and one colour still - the
-     * user's requirement is that the line matches the page, and where the page rules its table
-     * evenly that is a single weight.
+     * <code>w:sz="8" w:color="000000"</code>. That is still the fallback, but it is no longer
+     * the answer for every side: since D-22 a side carries the weight of the rule that lies on
+     * it, and this value only stands in where no rule could be read (see {@link #borders}).
      */
     private static final int TABLE_RULE_SZ = 8;
-    /** The one colour every ruled table is drawn in: black, as 23_timetable has it. */
+    /** The colour a side falls back to when the page's own stroke for it was not read. */
     private static final String TABLE_RULE_COLOUR = "000000";
+    /**
+     * The range {@code w:sz} accepts, in eighths of a point: 2 (0.25 pt) to 96 (12 pt).
+     *
+     * <p>Outside it the value is invalid and a reader is free to drop the border or the whole
+     * table property. A page rule of 0.1 pt - a hairline, and the PDF spec allows one - rounds
+     * to sz 1 and would be thrown away; a 14 pt bar rounds to 112 and is not a table border. So
+     * a width read off the page is clamped into the range rather than written as read.
+     */
+    private static final int TABLE_RULE_SZ_MIN = 2;
+    private static final int TABLE_RULE_SZ_MAX = 96;
+
+    /**
+     * A stroke width in points as {@code w:sz}, in eighths of a point, clamped to 2..96.
+     *
+     * <p>0.1 pt clamps to sz 2 (0.25 pt) and anything at or above 12 pt clamps to sz 96. The
+     * clamp is a real loss of fidelity at both ends - a 0.1 pt hairline is drawn a quarter point
+     * thick - and it is the narrower loss: a border outside the range is not a border at all.
+     */
+    private static int szOf(float widthPt) {
+        int sz = Math.round(Math.max(0.1f, widthPt) * 8f);
+        return Math.max(TABLE_RULE_SZ_MIN, Math.min(TABLE_RULE_SZ_MAX, sz));
+    }
+
+    /**
+     * A border's colour: the page's own, blended toward the white page by the rule's opacity.
+     *
+     * <p>{@code w:tblBorders} has no opacity - the element carries only {@code w:val},
+     * {@code w:sz}, {@code w:space} and {@code w:color} - so a faint rule cannot be written as
+     * a black rule at 30 % alpha. It is written as the colour that rule looks like on white:
+     * {@code c' = c*a + 255*(1-a)} per channel. A 30 % black hairline becomes D8D8D8, which is
+     * what a reader sees on the page. This is an approximation - on a page whose background is
+     * not white it is the wrong direction, and where a rule overlaps another rule the blend is
+     * not the page's - and it is stated in the report rather than hidden.
+     */
+    private static String borderColour(float[] stroke) {
+        int rgb = (int) stroke[1];
+        if (rgb < 0) return TABLE_RULE_COLOUR;
+        float a = stroke.length > 2 ? Math.max(0f, Math.min(1f, stroke[2])) : 1f;
+        if (a >= 0.999f) return hex(rgb);
+        int r = Math.round(((rgb >> 16) & 0xFF) * a + 255f * (1f - a));
+        int g = Math.round(((rgb >> 8) & 0xFF) * a + 255f * (1f - a));
+        int b = Math.round((rgb & 0xFF) * a + 255f * (1f - a));
+        return hex((r << 16) | (g << 8) | b);
+    }
     /** The six sides a {@code w:tblBorders} element carries. */
     private static final String[] TABLE_SIDES =
             {"top", "left", "bottom", "right", "insideH", "insideV"};
@@ -2380,6 +2427,15 @@ public final class DocxWriter {
         // The same answer decides the row height, because a rule that is drawn is a rule the
         // renderer adds to the row, and {@link #TABLE_BORDER_TW} is that rule's height.
         boolean ruledTable = t.ruled || pageDrewRule(t, ctx.curShapes);
+        // Six weights and six colours, one per side, read off the rule that lies on that side
+        // (D-22). A side with no stroke keeps the old constant, so nothing that was right moves.
+        int[] sideSz = new int[6];
+        String[] sideColour = new String[6];
+        for (int i = 0; i < 6; i++) {
+            float[] stroke = t.sideStroke[i];
+            sideSz[i] = stroke == null ? TABLE_RULE_SZ : szOf(stroke[0]);
+            sideColour[i] = stroke == null ? TABLE_RULE_COLOUR : borderColour(stroke);
+        }
         inner.append("<w:tbl><w:tblPr>")
                 .append("<w:tblW w:w=\"").append(totalTw).append("\" w:type=\"dxa\"/>")
                 .append("<w:tblInd w:w=\"").append(tw(x0)).append("\" w:type=\"dxa\"/>")
@@ -2392,7 +2448,7 @@ public final class DocxWriter {
                 // with no frame at all keeps all six undrawn even when a rule crosses its band:
                 // that rule is as likely the edge of a filled band as a drawn separator, and a
                 // line the page did not draw is the defect 403 and 406 came back with.
-                .append(borders(ruledTable,
+                .append(borders(sideSz, sideColour, ruledTable,
                         ruledTable && (t.ruled || t.innerH),
                         ruledTable && (t.ruled || t.innerV)))
                 .append("<w:tblLayout w:type=\"fixed\"/>")
```
