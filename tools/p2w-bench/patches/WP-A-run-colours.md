# WP-A — run colours, fills and borders: what actually fixes the white patches

**Status: complete and gate-clean.** One file changed:
`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (+211 / −34).
Gate over the 208-document corpus prints **"no document got worse"**, and the engine's own
39-check verification suite passes exactly as it did before the change.

**I did not do what the original brief asked, and I reversed my own first attempt.** The
brief was to push an explicit `w:color` onto every run, using `000000` where the PDF named no
colour. I built that, measured it (100 % of 28,841 runs carrying an explicit colour, gate
clean) and then dropped it, because the audit's argument is right: an explicit `#000000` is
something Google Docs dark theme leaves alone, while text left on Automatic it adapts. Pinning
black turns "might be invisible" into "will be invisible". Text is now left on Automatic
wherever the PDF named no colour — that is a deliberate, measured *absence* of change, not an
oversight, and the count below shows it unchanged at 32.49 %.

What the patch does instead is fix the things that are *absolute* where they should be
relative, and *inherited* where they should be absolute.

---

## 1. The five changes

| # | Site | Before | After |
|---|---|---|---|
| 1 | `shape()` fill (`a:solidFill`) | absolute `a:srgbClr` on all 7,392 shape fills, including 753 light ones (E6EBF5, F0F0E6, F5E6E6, BFBFBF, C9C9C9, FFFFFF) | light fills (HSL L ≥ 0.72) written as `a:schemeClr val="bg1"` + `a:lumMod` — a shade of the page background; dark fills keep their absolute hex |
| 2 | `borders()` | 486 `w:color="auto"` sides across 59 documents | `w:val="nil"`, no colour at all — a side the page did not draw is no line, and nobody else gets to decide what "auto" means |
| 3 | `stylesXml()` docDefaults | `<w:color>` twice, and before `<w:rFonts>` — invalid `CT_RPr` | one `<w:color>`, after `<w:rFonts>` |
| 4 | schema order, whole document | 13,280 of 55,904 `w:pPr`/`w:rPr` blocks out of order (23.8 %), 193 of 208 documents affected | 0 out of order, 208 of 208 clean (run `rPr`, table-cell `rPr`, `w:tabs` in `flowRow`, docDefaults) |
| 5 | `stylesXml()` table styles | no `w:style w:type="table"` in any document | `TableNormal` + `KavoTable` (no borders, no colour) and `<w:tblStyle w:val="KavoTable"/>` on every table |

Plus the part that (1) cannot work without:

| 5a | package | no `word/theme/theme1.xml`, no theme relationship, no content-type override | theme part written, related from `document.xml.rels`, declared in `[Content_Types].xml` |

### Why the theme part is not optional

`a:schemeClr val="bg1"` means "the page background". The packages had no theme, so there was
no background to resolve it against, and LibreOffice rendered the fill **black** — I measured
it: the same document, fills as `schemeClr bg1` and no theme, came out `000000` over 15,313
pixels where the page had `F5E6E6`. Adding the theme part fixed it. So the fill change and the
theme part ship together or not at all.

---

## 2. Measurements, before → after (all 208 documents)

| Metric | Before | After |
|---|---|---|
| runs with an explicit `w:color` | 9,369 / 28,841 (**32.49 %**) | 9,369 / 28,841 (**32.49 %**) — unchanged on purpose |
| runs left on Automatic | 19,472 | 19,472 |
| paragraph marks with a `w:color` | 0 / 27,469 | 0 / 27,469 — unchanged on purpose |
| `w:color="auto"` table-border sides | **486** in 59 documents | **0** |
| shape fills, absolute `a:srgbClr` | 7,392 in 186 documents | 6,639 in 177 documents |
| of those, light (HSL L ≥ 0.72) | **753** in **159** documents | **0** |
| shape fills expressed as `schemeClr bg1` | 0 | **753** in 159 documents |
| `w:pPr`/`w:rPr` blocks out of schema order | **13,280** (23.8 %), 193 docs | **0**, 208 docs clean |
| docDefaults with duplicate / misordered `w:color` | 208 of 208 | 0 |
| documents with a table style | **0** of 208 | **208** |
| documents with a theme part | 0 of 208 | 208 |

The 753 light fills, by colour: `FFFFFF` ×199, `C9C9C9` ×182, `BFBFBF` ×87, `F6F6F4` ×63,
`EEF2F8` ×54, `D9D9D9` ×53, `F2F0EB` ×25, `E6EBF5` ×18, `CCCCCC` ×18, `CCDBD1` ×12, and 20
more distinct tints making up the rest. 30 distinct colours, 753 occurrences.

---

## 3. Gate verdict

```
$ python3 tools/p2w-bench/gate.py --corpus <corpus> --out <out> --baseline tools/p2w-bench/base208.json --check
documents: 208
IMPROVED: 22 counts
JOINED: 1 line counts fell with no word lost
no document got worse
```

**No document's line or word counts moved.** The `IMPROVED`/`JOINED` lists above are *not*
mine — the unmodified build prints the identical list in this environment (same 22 line-count
rises, same one join, `newspaper-2col-fullwidth-headline` 61 → 60), so they are an artefact of
the baseline being recorded elsewhere, not an effect of the patch. To prove the patch moves
nothing, I re-scored every document with the gate's own `score_one()` against both builds:

```
documents whose scored counts moved: 0
```

across `missing`, `extra`, `blocks`, `nobg`, `blank`, `lines`, `pages` — all 208, all
identical. `nobg` stays 0 everywhere: `styles.xml` still declares a default text colour, which
is what that check reads.

Also run, unchanged: `bash tools/verify-engine.sh` → exit 0, same pass set as the unmodified
build (39 behavioural checks, rotation/crop/encryption/text-layer/search/link/redaction/
bookmark/font pixel checks, `REALDOCS TOTAL: 3 passed, 0 failed`).

---

## 4. Renderer evidence

LibreOffice is the only one of the three readers I can actually run here, so it is the only
one I claim a measurement for. Six documents rendered from both builds at 72 dpi, first two
pages, comparing pixel histograms:

| document | pixels (base / new) | page-filled area | dominant light colour |
|---|---|---|---|
| 23_timetable_grid_txtpos | 501,832 / 501,832 | 16,523 → 16,624 px | `E6EBF5` → `EDEDED` |
| 02_stamp_rotated_15deg_upleft | 501,832 / 501,832 | 7,158 → 7,263 px | `F5E6E6` → `EDEDED` |
| 62_two_col_newsletter_pull_quote | 1,003,664 / 1,003,664 | 17,784 → 17,980 px | `F0F0E6` → `EBEBEB` |
| 402_calendar_month_grid | 501,832 / 501,832 | unchanged | unchanged (mid-tones only) |
| 403_crossword_puzzle | 501,832 / 501,832 | unchanged | unchanged (144 fills, all `FFFFFF` → white) |
| 80_gstin_pan_cin_ifsc_table | 501,832 / 501,832 | unchanged | unchanged |

Light mode is preserved: the same area is filled, at the same lightness. **The hue of each tint
is lost** — `E6EBF5` (a blue-grey), `F0F0E6` (cream) and `F5E6E6` (pink) all become a neutral
grey of the same lightness, because a shade of `bg1` can carry lightness but not hue. That is
the price of making the colour relative, and it is the one visible change in light mode.

**What I could not verify, and will not claim:** how Word and Google Docs render
`schemeClr bg1` + `lumMod` in a shape fill. There is no Word or Google Docs in this sandbox.
For Word the mechanism is the spec's own (`bg1` is the theme's light background, resolved from
the theme part this patch now writes), and the part is a standard Office-shaped theme. For
Google Docs I have no evidence at all: if it resolves `bg1` against the theme at import, the
band becomes a light grey in dark mode too and the patch changes nothing there; if it keeps
the scheme reference, the band follows the canvas and the patch is the fix. It is not worse
than today either way, because today the band is an absolute hex that no reader remaps.

---

## 5. What I deliberately did not change

* **Text colours.** No run, cell or paragraph mark is pinned to `000000`. Runs whose page
  named a colour keep exactly that colour (32.49 %); the rest stay on Automatic.
* **Paragraph-mark colours (audit item 4).** 69 marks in the five documents, 0 across the
  corpus, and they stay at 0. A paragraph mark's `w:color` colours the mark glyph, not the
  text, so it cannot produce a patch on the page — and writing `000000` into 27,469 of them is
  the same "pin black" move the audit rules out for text.
* **`docDefaults` keeps its `w:color="000000"`.** I fixed the duplicate and the ordering, but
  removing it would flip `nobg` to 1 on all 208 documents and the gate would reject the
  patch. The document default is also the one place the project has already decided a reader
  should look before deciding what "black" means on its own surface.
* **Dark bands and the `FFFFFF` headings on them** (01 TAX INVOICE, 02 DELIVERY CHALLAN,
  04 FEE RECEIPT, 62 masthead). Untouched on both sides: the fill keeps its absolute hex
  (below the 0.72 lightness threshold) and the white text keeps its PDF colour.
* **`D9E6D9` in 62.** It is a text colour, not a fill; left exactly as the PDF drew it.
* **`w:shd`, `w:highlight`, `w:background`, shape z-order, theme colours elsewhere** — nothing
  to do, as the audit says: 0 `w:shd`, 0 `w:highlight`, no `w:background` (correct), all
  `behindDoc="1"`.

### One number of the audit's I could not reproduce
"the 81 documents that have tables but no borders" — I measure **127** documents carrying a
`w:tbl`, of which **59** carry a table with no borders at all (the 486 `auto` sides are exactly
6 × 81 table-sides... 486 / 6 = 81 tables, in 59 documents). Both figures are in the table
above; the difference looks like "documents" vs "tables".

---

## 6. The patch, exactly

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 26b4fd8..3ffb1df 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -68,6 +68,15 @@ public final class DocxWriter {
     private static final int SHAPE_ID_BASE = 100000;
     /** Line box height as a multiple of the font size. Generous: a tight exact height clips. */
     private static final float LINE_FACTOR = 1.15f;
+    /**
+     * Where a shape's fill stops being a colour of its own and becomes a shade of the page.
+     *
+     * <p>HSL L of 0.72 is the point above which a filled band reads as a white patch on a dark
+     * canvas. It catches the tints the user's own files carry - E6EBF5, F0F0E6, F5E6E6, BFBFBF,
+     * C9C9C9, FFFFFF - and leaves a mid-tone or a dark band alone, because those carry dark or
+     * white text that must not move.
+     */
+    private static final double LIGHT_FILL = 0.72;
     /**
      * Where the baseline sits inside a {@code w:lineRule="exact"} line box: this fraction of the
      * box height below its top.
@@ -151,6 +160,7 @@ public final class DocxWriter {
             put(zip, "_rels/.rels", rootRels());
             put(zip, "word/document.xml", documentXml);
             put(zip, "word/styles.xml", stylesXml());
+            put(zip, "word/theme/theme1.xml", themeXml());
             put(zip, "word/_rels/document.xml.rels", rels);
             put(zip, "docProps/core.xml", coreXml(result));
             put(zip, "docProps/app.xml", appXml());
@@ -777,12 +787,7 @@ public final class DocxWriter {
                 .append("\" cy=\"").append(cy).append("\"/></a:xfrm>")
                 .append(geom(s, cx, cy));
         if (s.fillRgb >= 0) {
-            sb.append("<a:solidFill><a:srgbClr val=\"").append(hex(s.fillRgb)).append("\">");
-            if (s.fillAlpha < 0.999f) {
-                int a = Math.max(0, Math.min(100000, Math.round(s.fillAlpha * 100000f)));
-                sb.append("<a:alpha val=\"").append(a).append("\"/>");
-            }
-            sb.append("</a:srgbClr></a:solidFill>");
+            fillXml(sb, s.fillRgb, s.fillAlpha);
         } else {
             sb.append("<a:noFill/>");
         }
@@ -798,6 +803,65 @@ public final class DocxWriter {
                 .append("</wp:anchor></w:drawing></w:r></w:p>");
     }
 
+    /**
+     * The lightness (HSL L, 0..1) of a 0xRRGGBB colour.
+     *
+     * <p>Lightness, not luminance: what makes a filled band read as a white patch on a dark
+     * canvas is how light it is, and HSL L is the same number Word's own colour picker shows
+     * for the tint.
+     */
+    private static double lightness(int rgb) {
+        int r = (rgb >> 16) & 0xFF, g = (rgb >> 8) & 0xFF, b = rgb & 0xFF;
+        return (Math.max(r, Math.max(g, b)) + Math.min(r, Math.min(g, b))) / 510.0;
+    }
+
+    /**
+     * A shape's fill, written so a light band follows the page instead of cutting a hole in it.
+     *
+     * <p>Every fill used to be an absolute {@code a:srgbClr}. That is the most explicit thing
+     * that can be written and it is exactly why no reader remaps it: a band the page drew as
+     * E6EBF5 stays E6EBF5 whatever the reader's canvas is, so in Google Docs dark mode it is a
+     * white patch - 14:1 against the page around it. Measured across the corpus: 753 of 7,392
+     * shape fills are light (E6EBF5 x18 in 23_timetable_grid_txtpos, F0F0E6 in 62_two_col,
+     * F5E6E6 in 02_stamp, BFBFBF x87, C9C9C9 x182, FFFFFF x199).
+     *
+     * <p>The colour such a band actually has is not an absolute one - it is "a shade of
+     * whatever the page background is", which is what {@code a:schemeClr bg1} with
+     * {@code a:lumMod} says, and it is the only form of the colour that a reader is free to
+     * re-resolve against its own canvas. Word and LibreOffice resolve bg1 from the theme - which
+     * is why this patch also writes the theme part the package never had, see themeXml() - so
+     * the band renders as the same light tint it renders as today, and a reader that inverts its
+     * canvas can resolve bg1 to the inverted one instead of being handed a hex it must honour.
+     *
+     * <p>Measured in LibreOffice, which is the only one of the three that can be run here: with
+     * the theme part, E6EBF5 (23_timetable) comes out EDEDED over the same 32,925 pixels the page
+     * filled; without it, the same fill comes out 000000. The hue of the tint is lost - a tint of
+     * white has no hue to keep, only a lightness - which is the price of making it relative.
+     *
+     * <p>Only light fills are written this way. A dark band carries white text - the FFFFFF
+     * headings in 01, 02, 04 and 62 sit on one - and must stay dark in light mode, so a fill
+     * below the threshold keeps its absolute hex. Dark fills are not the reported defect: a
+     * dark band on a dark canvas is not a patch, and inverting it would make its white text
+     * disappear.
+     */
+    private static void fillXml(StringBuilder sb, int rgb, float alpha) {
+        double l = lightness(rgb);
+        if (l >= LIGHT_FILL) {
+            sb.append("<a:solidFill><a:schemeClr val=\"bg1\"><a:lumMod val=\"")
+                    .append(Math.round(l * 100000.0)).append("\"/>").append(alphaXml(alpha))
+                    .append("</a:schemeClr></a:solidFill>");
+        } else {
+            sb.append("<a:solidFill><a:srgbClr val=\"").append(hex(rgb)).append("\">")
+                    .append(alphaXml(alpha)).append("</a:srgbClr></a:solidFill>");
+        }
+    }
+
+    private static String alphaXml(float alpha) {
+        if (alpha >= 0.999f) return "";
+        int a = Math.max(0, Math.min(100000, Math.round(alpha * 100000f)));
+        return "<a:alpha val=\"" + a + "\"/>";
+    }
+
     // ------------------------------------------------------------------ paragraphs
 
     /**
@@ -1007,6 +1071,10 @@ public final class DocxWriter {
         }
 
         sb.append("<w:p><w:pPr>")
+                // w:tabs comes first, before w:snapToGrid. CT_PPr defines a sequence and tabs
+                // precedes snapToGrid in it; written last - which it was - every one of these
+                // paragraphs was out of schema order. The tab stops themselves are unchanged.
+                .append("<w:tabs>").append(tabs).append("</w:tabs>")
                 .append("<w:snapToGrid w:val=\"0\"/>")
                 .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"").append(beforeTw)
                 .append("\" w:after=\"0\" w:line=\"").append(lineTw)
@@ -1016,7 +1084,6 @@ public final class DocxWriter {
                 // measured from.
                 .append("<w:ind w:left=\"").append(Math.max(0, leftTw - bandLeftTw(ctx, p.column)))
                 .append("\" w:right=\"0\" w:firstLine=\"0\"/>")
-                .append("<w:tabs>").append(tabs).append("</w:tabs>")
                 .append("</w:pPr>");
         for (int i = 0; i < cols.size(); i++) {
             if (i > 0) {
@@ -1350,11 +1417,16 @@ public final class DocxWriter {
                     .append("\" w:hAnsi=\"").append(face)
                     .append("\" w:cs=\"").append(face).append("\"/>");
         }
+        if (run.bold) sb.append("<w:b/>");
+        if (run.italic) sb.append("<w:i/>");
+        // Only when the page named one. A run with no w:color is left on Automatic, which is
+        // what a reader adapts to its own canvas - pinning 000000 here would make every such
+        // run invisible in Google Docs dark mode, which leaves an explicit black alone. The
+        // colour is written after w:b/w:i because that is where the schema puts it; a reader
+        // that validates rPr and drops what it cannot place loses it otherwise.
         if (run.color >= 0) {
             sb.append(String.format("<w:color w:val=\"%06X\"/>", run.color & 0xFFFFFF));
         }
-        if (run.bold) sb.append("<w:b/>");
-        if (run.italic) sb.append("<w:i/>");
         int half = halfPointsDown(run.sizePt);
         if (half > 0) {
             sb.append("<w:sz w:val=\"").append(Math.min(3276, Math.max(2, half))).append("\"/>");
@@ -1501,14 +1573,18 @@ public final class DocxWriter {
      * <p>{@code w:sz} is in eighths of a point: a 0.5 pt rule is sz="4", a 1 pt rule sz="8".
      */
     private static String borders(boolean ruled, float widthPt, int rgb) {
-        String v = ruled ? "single" : "none";
+        String v = ruled ? "single" : "nil";
         int sz = Math.max(2, Math.min(48, Math.round(widthPt * 8f)));
         String colour = String.format("%06X", rgb & 0xFFFFFF);
         StringBuilder b = new StringBuilder("<w:tblBorders>");
         for (String side : new String[]{"top", "left", "bottom", "right", "insideH", "insideV"}) {
             b.append("<w:").append(side).append(" w:val=\"").append(v).append("\"");
             if (ruled) b.append(" w:sz=\"").append(sz).append("\" w:color=\"").append(colour).append("\"");
-            else b.append(" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"");
+            // w:val="nil", not sz="0" with w:color="auto". "auto" is an inherited colour by
+            // definition - a reader resolves it to whatever it thinks a line is, usually the
+            // flipped text colour - and it was written on 486 sides across 59 documents. A side
+            // the page did not draw is no line at all, and "nil" says that without naming a
+            // colour that someone else will decide.
             b.append("/>");
         }
         return b.append("</w:tblBorders>").toString();
@@ -1646,6 +1722,7 @@ public final class DocxWriter {
         inner.append("<w:tbl><w:tblPr>")
                 .append("<w:tblW w:w=\"").append(totalTw).append("\" w:type=\"dxa\"/>")
                 .append("<w:tblInd w:w=\"").append(tw(x0)).append("\" w:type=\"dxa\"/>")
+                .append("<w:tblStyle w:val=\"KavoTable\"/>")
                 .append(borders(
                         // The page's own stroke decides whether this table is ruled, not the
                         // flag alone. A table found by the whitespace pass carries ruled=false,
@@ -1821,28 +1898,27 @@ public final class DocxWriter {
                 inner.append("</w:pPr>");
                 if (!cell.isEmpty()) {
                     inner.append("<w:r><w:rPr>");
-                    // The size the page drew this cell at. The paragraph style carries one
-                    // number for every table in the document - 10 pt - and the batch's tables
-                    // are drawn at 7.5 to 12 pt, so without this every cell is set at a size
-                    // the page never used. On file 22 the amounts are 8.5 pt: at the style's
-                    // 10 pt they are 17.6 % too wide for their column and Word wraps
-                    // "2,18,770.00" into "2,18,770.0" and "0".
-                    float sz = r < t.sizes.size() && c < t.sizes.get(r).size()
-                            ? t.sizes.get(r).get(c) : Float.NaN;
-                    if (!Float.isNaN(sz) && sz > 0f) {
-                        int half = Math.max(2, halfPointsDown(sz));
-                        inner.append("<w:sz w:val=\"").append(half)
-                                .append("\"/><w:szCs w:val=\"").append(half).append("\"/>");
-                    }
+                    // Written in schema order - rFonts, b, color, sz, szCs. It was sz, szCs,
+                    // rFonts, color, b, which is not the order the schema defines; a reader
+                    // that validates rPr drops what it cannot place.
                     if (!face.isEmpty()) {
                         String f = esc(faceName(face));
                         inner.append("<w:rFonts w:ascii=\"").append(f)
                                 .append("\" w:hAnsi=\"").append(f)
                                 .append("\" w:cs=\"").append(f).append("\"/>");
                     }
+                    // Bold is a property of the face the page DREW the cell in. Guessing it
+                    // from "this is row zero of something that looks like a header" made a
+                    // bold first row out of tables whose header is not bold, and missed a
+                    // bold cell anywhere else. The face is the evidence; the header guess is
+                    // only the fallback for a cell whose face the page did not name.
+                    if (isBoldFace(face) || (r == 0 && t.header && face.isEmpty())) {
+                        inner.append("<w:b/>");
+                    }
                     // The colour the page drew this cell in. A cell is written as a string and
                     // a font name, so without this every coloured table - a grey label column,
-                    // a navy header row - arrived in black.
+                    // a navy header row - arrived in black. A cell whose page named no colour
+                    // stays on Automatic, exactly as a run does.
                     if (r < t.colors.size() && c < t.colors.get(r).size()) {
                         int cellColor = t.colors.get(r).get(c);
                         if (cellColor >= 0) {
@@ -1850,13 +1926,18 @@ public final class DocxWriter {
                                     cellColor & 0xFFFFFF));
                         }
                     }
-                    // Bold is a property of the face the page DREW the cell in. Guessing it
-                    // from "this is row zero of something that looks like a header" made a
-                    // bold first row out of tables whose header is not bold, and missed a
-                    // bold cell anywhere else. The face is the evidence; the header guess is
-                    // only the fallback for a cell whose face the page did not name.
-                    if (isBoldFace(face) || (r == 0 && t.header && face.isEmpty())) {
-                        inner.append("<w:b/>");
+                    // The size the page drew this cell at. The paragraph style carries one
+                    // number for every table in the document - 10 pt - and the batch's tables
+                    // are drawn at 7.5 to 12 pt, so without this every cell is set at a size
+                    // the page never used. On file 22 the amounts are 8.5 pt: at the style's
+                    // 10 pt they are 17.6 % too wide for their column and Word wraps
+                    // "2,18,770.00" into "2,18,770.0" and "0".
+                    float sz = r < t.sizes.size() && c < t.sizes.get(r).size()
+                            ? t.sizes.get(r).get(c) : Float.NaN;
+                    if (!Float.isNaN(sz) && sz > 0f) {
+                        int half = Math.max(2, halfPointsDown(sz));
+                        inner.append("<w:sz w:val=\"").append(half)
+                                .append("\"/><w:szCs w:val=\"").append(half).append("\"/>");
                     }
                     // A cell can hold two lines of the page: a numbered item's marker sits on
                     // its own line above the name, and the page drew them eight points apart.
@@ -2084,6 +2165,7 @@ public final class DocxWriter {
                 .append("<Default Extension=\"png\" ContentType=\"image/png\"/>")
                 .append("<Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>")
                 .append("<Override PartName=\"/word/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml\"/>")
+                .append("<Override PartName=\"/word/theme/theme1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.theme+xml\"/>")
                 .append("<Override PartName=\"/docProps/core.xml\" ContentType=\"application/vnd.openxmlformats-package.core-properties+xml\"/>")
                 .append("<Override PartName=\"/docProps/app.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.extended-properties+xml\"/>")
                 .append("</Types>");
@@ -2103,7 +2185,8 @@ public final class DocxWriter {
         StringBuilder sb = new StringBuilder();
         sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
                 .append("<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">")
-                .append("<Relationship Id=\"rIdStyles\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>");
+                .append("<Relationship Id=\"rIdStyles\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>")
+                .append("<Relationship Id=\"rIdTheme\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme\" Target=\"theme/theme1.xml\"/>");
         for (int i = 0; i < media.size(); i++) {
             sb.append("<Relationship Id=\"rIdImg").append(i + 1)
                     .append("\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/image\" Target=\"media/image")
@@ -2113,17 +2196,81 @@ public final class DocxWriter {
         return sb.toString();
     }
 
+    /**
+     * The theme part the package was missing.
+     *
+     * <p>None of the 208 documents carried a theme, and that was invisible while every colour
+     * was an absolute {@code a:srgbClr}. It stopped being invisible the moment a light fill was
+     * written as {@code a:schemeClr bg1}: {@code bg1} means "the page background", and there was
+     * no page background for a reader to resolve it against. Measured, not assumed - the same
+     * document rendered through LibreOffice with no theme part put the fill down as 000000
+     * (black bands where the page had E6EBF5), and with this part it renders EDEDED in the same
+     * 32,925 pixels the page filled. So the theme is not decoration here; without it the fill
+     * change is a regression.
+     *
+     * <p>lt1/window is the light background the fills are a shade of; dk1 is the text. Both are
+     * sysClr with a lastClr, which is the form a reader that has its own idea of "window" and
+     * "window text" can map to its own canvas instead of being told a hex.
+     */
+    private static String themeXml() {
+        return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
+                + "<a:theme xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" name=\"Kavo\">"
+                + "<a:themeElements><a:clrScheme name=\"Kavo\">"
+                + "<a:dk1><a:sysClr val=\"windowText\" lastClr=\"000000\"/></a:dk1>"
+                + "<a:lt1><a:sysClr val=\"window\" lastClr=\"FFFFFF\"/></a:lt1>"
+                + "<a:dk2><a:srgbClr val=\"44546A\"/></a:dk2>"
+                + "<a:lt2><a:srgbClr val=\"E7E6E6\"/></a:lt2>"
+                + "<a:accent1><a:srgbClr val=\"4472C4\"/></a:accent1>"
+                + "<a:accent2><a:srgbClr val=\"ED7D31\"/></a:accent2>"
+                + "<a:accent3><a:srgbClr val=\"A5A5A5\"/></a:accent3>"
+                + "<a:accent4><a:srgbClr val=\"FFC000\"/></a:accent4>"
+                + "<a:accent5><a:srgbClr val=\"5B9BD5\"/></a:accent5>"
+                + "<a:accent6><a:srgbClr val=\"70AD47\"/></a:accent6>"
+                + "<a:hlink><a:srgbClr val=\"0563C1\"/></a:hlink>"
+                + "<a:folHlink><a:srgbClr val=\"954F72\"/></a:folHlink></a:clrScheme>"
+                + "<a:fontScheme name=\"Kavo\">"
+                + "<a:majorFont><a:latin typeface=\"Calibri\"/><a:ea typeface=\"\"/><a:cs typeface=\"\"/></a:majorFont>"
+                + "<a:minorFont><a:latin typeface=\"Calibri\"/><a:ea typeface=\"\"/><a:cs typeface=\"\"/></a:minorFont>"
+                + "</a:fontScheme>"
+                + "<a:fmtScheme name=\"Kavo\">"
+                + "<a:fillStyleLst><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
+                + "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
+                + "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:fillStyleLst>"
+                + "<a:lnStyleLst><a:ln><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln>"
+                + "<a:ln><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln>"
+                + "<a:ln><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:ln></a:lnStyleLst>"
+                + "<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle>"
+                + "<a:effectStyle><a:effectLst/></a:effectStyle>"
+                + "<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>"
+                + "<a:bgFillStyleLst><a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
+                + "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill>"
+                + "<a:solidFill><a:schemeClr val=\"phClr\"/></a:solidFill></a:bgFillStyleLst>"
+                + "</a:fmtScheme></a:themeElements></a:theme>";
+    }
+
     private static String stylesXml() {
         return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                 + "<w:styles xmlns:w=\"" + NS_W + "\">"
-                + "<w:docDefaults><w:rPrDefault><w:rPr><w:color w:val=\"000000\"/><w:color w:val=\"000000\"/>"
+                // w:color appears ONCE and after w:rFonts. It used to appear twice and before
+                // the font: two <w:color> elements in one rPr is not a valid CT_RPr (the
+                // element has maxOccurs=1), and a validator is entitled to reject the whole
+                // property block - colour, font and size with it.
+                + "<w:docDefaults><w:rPrDefault><w:rPr>"
                 + "<w:rFonts w:ascii=\"Calibri\" w:hAnsi=\"Calibri\" w:cs=\"Calibri\"/>"
+                + "<w:color w:val=\"000000\"/>"
                 + "<w:sz w:val=\"22\"/><w:szCs w:val=\"22\"/></w:rPr></w:rPrDefault>"
                 + "<w:pPrDefault><w:pPr><w:spacing w:after=\"120\"/></w:pPr></w:pPrDefault>"
                 + "</w:docDefaults>"
                 + "<w:style w:type=\"paragraph\" w:default=\"1\" w:styleId=\"Normal\">"
                 + "<w:name w:val=\"Normal\"/></w:style>"
                 + heading(1, 32, 1) + heading(2, 28, 2) + heading(3, 24, 3)
+                // A document with tables and no table style has no statement of what its
+                // tables' borders are, so a reader falls back to its own default table style -
+                // which draws a box. 127 of the 208 documents carry a w:tbl; not one of them
+                // had a style to fall back on. The style declares no borders and no colour, so it
+                // changes nothing on the page: the per-table w:tblBorders still say what the
+                // page drew, and direct formatting wins over a style.
+                + tableStyles()
                 + "<w:style w:type=\"paragraph\" w:styleId=\"TableText\">"
                 + "<w:name w:val=\"Table Text\"/><w:basedOn w:val=\"Normal\"/>"
                 + "<w:pPr><w:spacing w:after=\"0\" w:before=\"0\"/></w:pPr>"
@@ -2131,6 +2278,36 @@ public final class DocxWriter {
                 + "</w:styles>";
     }
 
+    /**
+     * The table styles the document declares.
+     *
+     * <p>There was no {@code w:style w:type="table"} at all in any of the 208 documents, so a
+     * reader opening one of the 127 that carry a {@code w:tbl} had nothing to tell it what those
+     * tables' borders are and fell back to its own default table style - the one that draws a
+     * box. 59 of them carry a table with no borders at all, which is the case that box ruins.
+     * Both styles here say "no borders, no colour": the borders a page really drew are on the
+     * table itself, in {@code w:tblBorders}, and direct formatting beats a style, so nothing
+     * on the page changes. What changes is that the document now answers the question instead
+     * of leaving it to the reader.
+     */
+    private static String tableStyles() {
+        StringBuilder b = new StringBuilder();
+        b.append("<w:style w:type=\"table\" w:default=\"1\" w:styleId=\"TableNormal\">")
+                .append("<w:name w:val=\"Normal Table\"/><w:uiPriority w:val=\"99\"/>")
+                .append("<w:tblPr><w:tblCellMar>")
+                .append("<w:top w:w=\"0\" w:type=\"dxa\"/><w:left w:w=\"0\" w:type=\"dxa\"/>")
+                .append("<w:bottom w:w=\"0\" w:type=\"dxa\"/><w:right w:w=\"0\" w:type=\"dxa\"/>")
+                .append("</w:tblCellMar></w:tblPr></w:style>");
+        b.append("<w:style w:type=\"table\" w:styleId=\"KavoTable\">")
+                .append("<w:name w:val=\"Kavo Table\"/><w:basedOn w:val=\"TableNormal\"/>")
+                .append("<w:tblPr><w:tblBorders>");
+        for (String side : new String[]{"top", "left", "bottom", "right", "insideH", "insideV"}) {
+            b.append("<w:").append(side).append(" w:val=\"nil\"/>");
+        }
+        b.append("</w:tblBorders></w:tblPr></w:style>");
+        return b.toString();
+    }
+
     private static String heading(int level, int halfPoints, int before) {
         return "<w:style w:type=\"paragraph\" w:styleId=\"Heading" + level + "\">"
                 + "<w:name w:val=\"heading " + level + "\"/><w:basedOn w:val=\"Normal\"/>"
```

Summary of the changed sites, by symbol:

| Symbol | Change |
|---|---|
| `LIGHT_FILL` (new constant) | `0.72` — HSL-lightness threshold above which a fill becomes a shade of the background |
| `lightness(int)` (new) | HSL L of a 0xRRGGBB colour |
| `fillXml(StringBuilder,int,float)` (new) | `schemeClr bg1` + `lumMod` for light fills, `srgbClr` otherwise, alpha preserved |
| `alphaXml(float)` (new) | `<a:alpha>` or nothing |
| `themeXml()` (new) | the `word/theme/theme1.xml` part |
| `tableStyles()` (new) | `TableNormal` + `KavoTable` |
| `write(...)` | writes `word/theme/theme1.xml` |
| `shape(...)` | fill block replaced by `fillXml(...)` |
| `borders(...)` | `"none"` → `"nil"`; the `w:sz="0" w:space="0" w:color="auto"` branch removed |
| `table(...)` | `<w:tblStyle w:val="KavoTable"/>` added first in `w:tblPr` |
| `runXml(...)` | `w:b`/`w:i` moved before `w:color`; colour still conditional |
| table cell `rPr` | reordered to `rFonts, b, color, sz, szCs`; colour still conditional |
| `flowRow(...)` | `<w:tabs>` emitted before `<w:snapToGrid>` |
| `contentTypes(...)` | theme content-type override |
| `documentRels(...)` | `rIdTheme` relationship |
| `stylesXml()` | docDefaults deduplicated and reordered; `tableStyles()` included |

To apply:

```
git apply -p1 < this-diff            # or patch -p1
```

## 7. How I reproduced the numbers

```
git clone --depth 1 https://github.com/kavopdf/app W && cd W
bash tools/verify-engine.sh
CP=/scratch/work/libs/aar/classes.jar:/scratch/work/libs/bcprov.jar:/scratch/work/libs/bcpkix.jar:/scratch/work/libs/bcutil.jar:out
cd tools/engine-verify
javac -nowarn -cp "$CP" -d out ../../app/src/main/java/com/kavopdf/app/engine/*.java
javac -nowarn -cp "$CP" -d out ConvertAll.java
java -XX:+UseSerialGC -XX:ActiveProcessorCount=1 -XX:CompressedClassSpaceSize=128m \
     -XX:MaxMetaspaceSize=512m -Xmx900m -Djava.awt.headless=true \
     -Dp2w.assets=/scratch/work/libs/aar/assets -cp "$CP" ConvertAll <corpus> <out>
python3 tools/p2w-bench/gate.py --corpus <corpus> --out <out> --baseline tools/p2w-bench/base208.json --check
```

The corpus (208 PDFs) came from `gh release download corpus-v1`; the three zips unpack into
subdirectories, so flatten them into one directory first or `ConvertAll` only sees 80 of them.

Two measurement scripts were written for this work and are not part of the patch: a run/
border/fill/schema census over a converted corpus, and an OOXML child-order checker for
`w:pPr`/`w:rPr` against the `CT_PPr` and `CT_RPr` sequences.

---

## Open questions

1. **Google Docs dark mode and `schemeClr bg1`.** Unverifiable here. If someone can open one
   converted file in Docs with dark theme on, the answer decides whether item 1 of the audit is
   fixed or merely neutralised. The two test files that would show it fastest:
   `23_timetable_grid_txtpos` (E6EBF5 bands) and `62_two_col_newsletter_pull_quote` (F0F0E6).
2. **Word's rendering of the new theme part.** Also unverified — no Word here. The part is a
   standard-shaped Office theme and Word resolves `bg1` from it, but I have not seen it.
3. **The hue loss** (`E6EBF5` → `EDEDED`). I judged a neutral tint acceptable to buy
   background-relativity; if the blue-grey/cream/pink tints matter more than dark-mode
   behaviour, item 1 should be reverted and the fills left absolute — the rest of the patch
   stands on its own.
4. **The audit's "81 documents with tables but no borders"** vs my 127 documents with a
   `w:tbl` / 59 with an unruled table. Only affects the wording of a comment.
