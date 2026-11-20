# 47 — The table-cell emission path, and how it expresses a line's horizontal position

**Scope:** read-only. No repository file was modified; no build, no benchmark run.

**Provenance note.** `/scratch/work/CS` did not exist in this sandbox (empty `/scratch/work`, `/scratch/repos`, `/scratch/input`). The engine was obtained by cloning the only accessible source of it, `kavopdf/app`, into `/scratch/work/CS`. The clone matches the tree the task describes: `flowFromBox` is at 4154 with its body at 4159–4188, the `w:ind`/`w:jc` emission is at 4385–4390 (the diff's "4391–4392" context), `w:pgMar` zero constant at 2268–2269, and `tools/p2w-bench/FINDINGS/47_margins-indent-space-construct-133500.diff` is present and **not applied** (its context lines match the working file exactly). All line numbers below are that tree.

Paths used throughout:

- `W` = `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (7385 lines)
- `P` = `app/src/main/java/com/kavopdf/app/engine/PdfToWord.java` (10015 lines)

---

## 0. The answer in one paragraph

A paragraph inside a real table cell is **never** built by `flowFromBox`. It is built by one of exactly two cell emitters inside `table()` (`W:5721`): an inline `w:p` at `W:6603–6691` for a single-paragraph cell, and `cellParaXml()` (`W:6891–6932`) for a cell holding two or more paragraphs. Both write `<w:ind w:left>` only, from `insetTw()` = *measured ink x − the cell's written left edge* (`W:7040–7055`), never `w:jc`, and they receive **no `Box`** — but they do not need one, because the ink x is already in the model as `Table.cellX` (filled from `visibleX()` / `glyphFirstX()`) and `CellPara.x` (filled from `visibleX()`). Crucially, **every** table-cell text builder in `PdfToWord` already `.trim()`s the text (`P:8347`, `P:8378`, `P:9029`, `P:9420`), so a run inside `w:tc` cannot begin with ASCII spaces in the first place. The cell path is therefore already the construct the flowFromBox patch introduced — it strips (trims) upstream and pins the ink as `w:ind w:left`. That is the concrete reason a flowFromBox-side patch leaves those documents' `.docx` byte-identical.

---

## 1. Which method builds the `w:p` — the three `w:tc` emitters

There are exactly three places in the whole writer that emit `</w:tc>`: `W:2119`, `W:6691`, `W:6931`. They belong to two table writers.

```
block dispatch                         emitBlock (W:2219)
  Para            -> para()            (W:2874)  -> flowRow / flowFromBox / anchorBox / lineParagraph
  Table           -> table()           (W:5721)  -> per cell: inline w:p  OR  cellParaXml()
  Picture/Shape   -> picture()/shape()

page layout dispatch                   columnPage (W:1622)   [multi-column page written AS a layout table]
  -> <w:tbl> W:2029 -> per cell: emitBlock() W:2080 -> para() -> flowFromBox() ...
  -> <w:tc> W:2117
```

`emitBlock` — the only place a `Para` and a `Table` are told apart (`W:2219–2237`):

```java
2219    private static void emitBlock(StringBuilder sb, Object block, Ctx ctx) {
2220        if (block instanceof PdfToWord.Para) {
2221            para(sb, (PdfToWord.Para) block, ctx);
2222        } else if (block instanceof PdfToWord.Table) {
2223            table(sb, (PdfToWord.Table) block, ctx);
2224        } else if (block instanceof Picture) {
```

So the answer to **"which method builds the w:p for a space-led paragraph in a table cell"** splits by which table it is:

| cell kind | enclosing method | builds the `w:p` | line ref |
|---|---|---|---|
| real table, cell holds **1** paragraph (the common case) | `table()` `W:5721` | **inline**, no separate method | `W:6603–6691` |
| real table, cell holds **≥2** paragraphs | `table()` → `cellParaXml()` | `cellParaXml` | `W:6891–6932` (called at `W:6594`) |
| multi-column page layout table | `columnPage()` `W:1622` → `emitBlock` `W:2080` → `para()` `W:2874` | `flowFromBox()` (or `anchorBox`) | `W:4154` / `W:2619` |

The real-table emitters are the ones that differ from `flowFromBox`. The `columnPage` cell is *not* a different path — it is literally `flowFromBox` with `ctx.inColumn = true`, which is why `flowFromBox` has an `inColumn` branch at `W:4168`.

### 1a. `table()`'s cell locals — the cell string and its inset (`W:6294`, `W:6307`)

```java
6294                String cell = (vCont || c >= row.size()) ? "" : row.get(c);
6295                String face = r < t.fonts.size() && c < t.fonts.get(r).size()
6296                        ? t.fonts.get(r).get(c) : "";
...
6302                // How far into its own box this cell's text was drawn. A cell's text does not
6303                // start at its border: the page padded it, centred it or right-aligned it, and
6304                // in a right-aligned column the distance changes row by row. Word's cell margin
6305                // is one number for the whole cell, so the offset goes on the paragraph, which
6306                // is per cell and is what w:ind means.
6307                int insetTw = insetTw(t, r, c, x0, edgeTw[c]);
```

### 1b. The single-paragraph cell `w:p` — `W:6603–6691` (this is the path a space-led cell line takes)

```java
6603                inner.append("</w:tcPr>")
6604                        .append("<w:p><w:pPr><w:pStyle w:val=\"TableText\"/>")
6605                        .append("<w:snapToGrid w:val=\"0\"/>")
6606                        .append(spacing(cellBeforeTw, cellBoxTw, cellSz, autoCellBoxes(), false));
6607                if (insetTw > 0) inner.append("<w:ind w:left=\"").append(insetTw).append("\"/>");
6608                inner.append("</w:pPr>");
6609                if (!cell.isEmpty()) {
6610                    inner.append("<w:r><w:rPr>");
...
6669                    String[] parts = cell.split("\n");
6670                    for (int q = 0; q < parts.length; q++) {
6671                        if (q > 0) {
...
6681                            if (!parts[q - 1].isEmpty() && !parts[q - 1].endsWith(" ")) {
6682                                inner.append("<w:t xml:space=\"preserve\"> </w:t>");
6683                            }
6684                            inner.append("<w:br/>");
6685                        }
6686                        inner.append("<w:t xml:space=\"preserve\">").append(esc(parts[q]))
6687                                .append("</w:t>");
6688                    }
6689                    inner.append("</w:r>");
6690                }
6691                inner.append("</w:p></w:tc>");
```

Note: `xml:space="preserve"` is on every `w:t`, so *if* `cell` began with spaces they would survive to the render — but `cell` cannot (see §3).

### 1c. The multi-paragraph branch that calls `cellParaXml` — `W:6563–6602`

```java
6563                java.util.List<PdfToWord.Table.CellPara> cps = t.parasAt(r, c);
6564                if (cps.size() >= 2) {
6565                    int box0 = paraBoxTw(cps, 0, rowLineTw);
...
6583                    inner.append("<w:vAlign w:val=\"top\"/></w:tcPr>");
6584                    for (int q = 0; q < cps.size(); q++) {
6585                        PdfToWord.Table.CellPara cp = cps.get(q);
...
6589                        int boxTw = paraBoxTw(cps, q, rowLineTw);
6590                        int beforeTw = q == 0 ? before0 : paraBeforeTw(cps, q, rowLineTw);
6591                        stackTw += (q == 0 ? 0 : beforeTw) + boxTw;
6592                        int pInset = Float.isNaN(cp.indentPt) ? insetTw
6593                                : (int) Math.max(0L, Math.round(cp.indentPt * TWIPS_PER_PT));
6594                        cellParaXml(inner, cp, beforeTw, boxTw, pInset, cellSz);
6595                    }
```

### 1d. `cellParaXml()` — `W:6891–6932`

```java
6891    private static void cellParaXml(StringBuilder inner, PdfToWord.Table.CellPara cp,
6892                                    int beforeTw, int boxTw, int insetTw, float cellSz) {
6893        float sz = cp.size > 0f ? cp.size : cellSz;
6894        inner.append("<w:p><w:pPr><w:pStyle w:val=\"TableText\"/>")
6895                .append("<w:snapToGrid w:val=\"0\"/>")
6896                .append(spacing(beforeTw, boxTw, sz, autoCellBoxes(), false));
6897        if (insetTw > 0) inner.append("<w:ind w:left=\"").append(insetTw).append("\"/>");
6898        inner.append("</w:pPr>");
6899        if (!cp.text.isEmpty()) {
6900            inner.append("<w:r><w:rPr>");
...
6918            String[] parts = cp.text.split("\n");
6919            for (int q = 0; q < parts.length; q++) {
6920                if (q > 0) {
...
6924                    inner.append("<w:br/>");
6925                }
6926                inner.append("<w:t xml:space=\"preserve\">").append(esc(parts[q]))
6927                        .append("</w:t>");
6928            }
6929            inner.append("</w:r>");
6930        }
6931        inner.append("</w:p>");
6932    }
```

### 1e. `insetTw()` — where the cell's horizontal number actually comes from (`W:7040–7055`)

```java
7040    /**
7041     * How far into the cell, in twips, this cell's text was drawn.
7042     *
7043     * <p>Zero when the page did not record where the text went, or when the glyphs put it left
7044     * of the cell's own left edge - in both cases the border is the safer answer.
7045     */
7046    private static int insetTw(PdfToWord.Table t, int r, int c, float x0, long edgeTw) {
7047        if (r >= t.cellX.size()) return 0;
7048        List<Float> xs = t.cellX.get(r);
7049        if (c >= xs.size()) return 0;
7050        Float textX = xs.get(c);
7051        if (textX == null || textX.isNaN()) return 0;
7052        double leftPt = x0 + edgeTw / TWIPS_PER_PT;
7053        int tw = (int) Math.round((textX - leftPt) * TWIPS_PER_PT);
7054        return Math.max(0, tw);
7055    }
```

`edgeTw[]` is the **written** cell edge, accumulated from the emitted `w:gridCol` widths (`W:5926–5930`), and `x0` is `t.colX[0]` (`W:5733`) written as `w:tblInd` (`W:5899–5901`). So `insetTw` is *already* `(ink x − written cell left edge)` in twips — the exact quantity `(inkX − b.x)` stands for on the flow path.

---

## 2. `flowFromBox` for comparison — `W:4159–4189` and `W:4381–4397`

```java
4159        int leftTw = (int) Math.max(0L, Math.round(b.x * TWIPS_PER_PT));
4160        int rightTw = 0;
...
4168        if (ctx.inColumn) {
4169            // Inside a column cell the cell IS the column: it is exactly as wide as the band the
4170            // page drew, so a centred line is centred by w:jc against zero indents, and a
4171            // right-aligned one is measured from the cell's right edge rather than the paper's.
4172            if (p.align == 1) {
4173                leftTw = 0;
4174            } else if (p.align == 2) {
4175                leftTw = 0;
4176                rightTw = (int) Math.max(0L,
4177                        Math.round((ctx.cellRightPt - b.right) * TWIPS_PER_PT));
4178            }
4179        } else if (p.align == 1) {
4180            float centre = (b.x + b.right) / 2f;
4181            if (Math.abs(centre - ctx.pageWidthPt / 2f) > 2f) {
4182                rightTw = (int) Math.max(0L, Math.round((ctx.pageWidthPt - b.right) * TWIPS_PER_PT));
4183            } else {
4184                leftTw = 0;
4185            }
4186        } else if (p.align == 2) {
4187            leftTw = 0;
4188            rightTw = (int) Math.max(0L, Math.round((ctx.pageWidthPt - b.right) * TWIPS_PER_PT));
4189        }
```

```java
4381        sb.append("<w:p><w:pPr>");
4382        if (p.heading > 0) {
4383            sb.append("<w:pStyle w:val=\"Heading").append(Math.min(p.heading, 3)).append("\"/>");
4384        }
4385        sb.append("<w:snapToGrid w:val=\"0\"/>")
4386                .append(spacing(beforeTw, lineTw, b.size, autoFlowLines(), ctx.newPage))
4387                .append("<w:ind w:left=\"").append(Math.max(0, leftTw - bandLeftTw(ctx, p.column)))
4388                .append("\" w:right=\"").append(rightTw).append("\" w:firstLine=\"0\"/>");
4389        if (p.align == 1) sb.append("<w:jc w:val=\"center\"/>");
4390        else if (p.align == 2) sb.append("<w:jc w:val=\"right\"/>");
4391        sb.append("</w:pPr>");
4392        int spacingTw = p.align == 0 ? stretchTw(b) : 0;
4393        for (PdfToWord.Run run : b.runs) {
4394            if (run.text.isEmpty()) continue;
4395            runXml(sb, run, p.heading > 0, spacingTw);
4396        }
4397        sb.append("</w:p>");
```

`bandLeftTw` (`W:2276–2288`) is what makes a column-cell line cell-relative: `if (ctx.inColumn) return round(ctx.cellLeftPt * TWIPS_PER_PT)`.

---

## 3. Where the leading spaces go — they are removed *before* the writer sees them

This is the load-bearing finding, and it is why the cell documents came out byte-identical.

Every table-cell text builder in `PdfToWord` trims:

**`glyphText()`** — the ruled-table cell string, `P:8343–8349`:

```java
8343        String[] parts = sb.toString().split("\n", -1);
8344        StringBuilder outSb = new StringBuilder(sb.length());
8345        for (String part : parts) {
8346            if (outSb.length() > 0) outSb.append('\n');
8347            outSb.append(logicalOrder(part.trim()));
8348        }
8349        return outSb.toString().trim();
```

Used at `P:8032` (`String str = glyphText(buckets.get(r).get(c));` → `row.add(str)` at `P:8034`), which is what `table()` reads as `row.get(c)` at `W:6294`.

**`parasOfLines()`** — the multi-paragraph cell model, `P:8377–8389`:

```java
8377        for (Line ln : sorted) {
8378            String piece = ln.text == null ? "" : ln.text.trim();
8379            if (piece.isEmpty()) continue;
8380            if (cur != null && Math.abs(ln.y - curY) <= 2f) {
8381                cur.text = cur.text.isEmpty() ? piece : cur.text + " " + piece;
8382                if (!Float.isNaN(ln.right) && ln.right > cur.right) cur.right = ln.right;
8383                continue;
8384            }
8385            cur = new Table.CellPara(piece, fontOf(ln.glyphs), sizeOf(ln.glyphs),
8386                    colourOfLine(ln.glyphs), boldOf(ln.glyphs), italicOf(ln.glyphs),
8387                    visibleX(ln.glyphs, ln.x), ln.right, ln.y);
```

Line 8387 is the point that matters for question (3): **`CellPara.x` is `visibleX(...)`, i.e. the ink left edge, already.**

**The whitespace-table pass**, `P:9022–9038`:

```java
9022            for (Line line : lines) {
9023                float cx = (line.x + line.right) / 2f;
9024                int r = band(ys, line.y);
9025                int c = band(xs, cx);
9026                if (r < 0 || c < 0) continue;
9027                pieces.get(r).get(c).add(line);
9028                cells[r][c] = cells[r][c] == null
9029                        ? line.text.trim() : cells[r][c] + " " + line.text.trim();
...
9037                if (Float.isNaN(firstX[r][c])) firstX[r][c] = visibleX(line.glyphs, line.x);
9038                if (Float.isNaN(firstY[r][c])) firstY[r][c] = line.y;
9039            }
```

and `firstX` is what becomes `t.cellX` at `P:9113`. The re-cut pass is the same shape (`P:9420` `String piece = cell.text.trim();`).

And the two helpers both mean "ink x", `P:8089–8101` and `P:8141–8154`:

```java
8089    private static Float glyphFirstX(List<Glyph> gs) {
8090        if (gs == null || gs.isEmpty()) return Float.NaN;
8091        List<Glyph> sorted = new ArrayList<>(gs);
...
8099        for (Glyph g : sorted) if (visible(g)) return g.x;
8100        return sorted.get(0).x;
8101    }

8141    private static boolean visible(Glyph g) {
8142        return g != null && g.text != null && !g.text.trim().isEmpty();
8143    }
8149    private static float visibleX(List<Glyph> gs, float fallback) {
8150        if (gs == null) return fallback;
8151        float best = Float.MAX_VALUE;
8152        for (Glyph g : gs) if (visible(g) && g.x < best) best = g.x;
8153        return best == Float.MAX_VALUE ? fallback : best;
8154    }
```

By contrast the flow path keeps them: `PdfToWord.Box.text()` (`P:158–162`) concatenates `run.text` with no trim, which is why `flowFromBox` sees a run beginning with N spaces at all.

---

## 4. The precise difference, side by side

| | `flowFromBox` (`W:4154`) | `table()` inline cell `w:p` (`W:6603`) | `cellParaXml` (`W:6891`) |
|---|---|---|---|
| input object | `PdfToWord.Box b` (+ `Para p`) | none — `(r, c)`, `t`, `cell` string | `PdfToWord.Table.CellPara cp` |
| left position expressed as | `w:ind w:left = b.x*TW − bandLeftTw(...)` | `w:ind w:left = insetTw` (= `cellX − written cell edge`), **emitted only if > 0** | same as the cell path, via the `insetTw` argument (or `cp.indentPt`) |
| `w:jc` | `center` / `right` for `p.align` 1/2 (`W:4389–4390`) | **never emitted** | **never emitted** |
| `w:right` | written (`W:4387`) | not written | not written |
| `w:firstLine` | `0` | not written | not written |
| coordinate frame | page edge, minus `cellLeftPt` when `ctx.inColumn` | the cell's own written left edge | the cell's own written left edge |
| leading spaces in the run text | **present** (`Box.text()` does not trim) | **impossible** (trimmed at `P:8347`/`P:9029`/`P:9420`) | **impossible** (trimmed at `P:8378`) |
| alignment at all | delegated to `w:jc` for centred/right | nothing: a cell line has no alignment, its position is entirely `w:ind` | same |
| `pStyle` | `Heading1..3` when `p.heading > 0`, else none | always `TableText` | always `TableText` |
| run construction | `runXml(sb, run, …)` per `Run` in `b.runs`, several runs allowed | **one** `w:r`, one `w:rPr` for the whole cell | **one** `w:r`, one `w:rPr` for the whole cell |

So the difference is not "spaces vs indent" — it is **one paragraph per line with per-line ink x (`flowFromBox`) versus one paragraph per cell with a single cell-level ink x (the cell emitters)**, plus the fact that the cell emitters delegate *alignment* to nothing at all: a cell line has no `w:jc`, so a right-aligned cell value is expressed as a large positive `w:ind w:left` (`insetTw`), not as `w:jc="right"`. That is a genuine structural difference and it is why `insetTw` is clamped at `≥ 0` (`W:7054`) and re-clamped against the column width at `W:6342`/`W:6365`.

---

## 5. Direct answers

### (1) Which method builds the `w:p` for a space-led paragraph in a table cell

For a real table (`PdfToWord.Table`, dispatched at `W:2222–2223`): **`table()` (`W:5721`)** builds it — inline at `W:6603–6691` when the cell holds one paragraph, or through **`cellParaXml()` (`W:6891–6932`)** when `t.parasAt(r, c).size() >= 2` (`W:6563–6594`).

For a multi-column page written as a layout table: **`columnPage()` (`W:1622`)** emits the `w:tbl` (`W:2029`) and `w:tc` (`W:2117`), and the cell's paragraphs go through `emitBlock` (`W:2080`) → `para()` (`W:2874`) → **`flowFromBox()`** — i.e. the already-patched path, with `ctx.inColumn = true` (`W:2055`) and `bandLeftTw` returning `cellLeftPt` (`W:2277`).

The honest qualification: in a real table cell the premise ("text begins with N ASCII space characters") cannot hold, because the text is trimmed in the model (§3).

### (2) What `w:ind` / `w:jc` / alignment values are written

- `w:ind w:left` = `insetTw` twips, **only when `insetTw > 0`** (`W:6607`, `W:6897`); no `w:ind` element at all otherwise. No `w:right`, no `w:firstLine`, no `w:hanging`.
- `w:jc`: **never** written in either cell emitter. `w:jc` appears in exactly two places in the file, `W:4389–4390` (`flowFromBox`) and `W:4409–4410` (`flowParagraph`).
- The paragraph carries `w:pStyle w:val="TableText"`, `w:snapToGrid w:val="0"`, and `spacing(before, box, size, autoCellBoxes(), false)`; the cell's `w:vAlign` is `top` for the multi-paragraph branch (`W:6583`) and comes from the default path otherwise.
- `insetTw` is `max(0, round((cellX[r][c] − (x0 + edgeTw[c]/TW)) * TW))` (`W:7046–7055`), where `cellX` is the ink x (`visibleX`/`glyphFirstX`) and `x0 + edgeTw[c]/TW` is the cell's **written** left edge. It is then clamped to the cell's width (`W:6342`) and again so the text fits (`W:6365`).

### (3) Does that method have access to the box/line object carrying the ink left edge?

- `table()`'s inline emitter and `cellParaXml()`: **no `Box`, no `Line`, no `Para`** — they are handed only `(r, c)`, the `Table`, and a `CellPara`. But they do not need one: the ink left edge is already in the model twice over — `Table.cellX[r][c]` (filled from `visibleX()` at `P:9037`/`P:9113` and from `glyphFirstX()` at `P:8037`) and `CellPara.x` (filled from `visibleX(ln.glyphs, ln.x)` at `P:8387`). `insetTw()` already consumes exactly that number.
- `flowFromBox()` (`W:4154`): **yes** — it has `b`, and after the FINDINGS diff it has `b.inkX` (the diff declares `PdfToWord.Box.inkX` and sets it from `visibleX(ln.glyphs, ln.x)` at the two box-building sites the diff touches — the `flowFromBox` box builder and the re-cut box builder; those are diff line numbers, not file line numbers).
- `anchorBox()` (`W:2619`) → `lineParagraph()` (`W:3559`): **yes**, it has `b` — and this is where a space-led line really does keep its spaces *and* lose its indent: `lineParagraph` hard-writes `<w:ind w:left="0" w:right="0" w:firstLine="0"/>` (`W:3569`) because "the anchor already put this line at its x", and `anchorBox` anchors at `b.x` (`W:2641`), the left edge of the first *space*, while `lineParagraph` emits `b.runs` verbatim (`W:3577–3580`).

### (4) The minimal change to strip the spaces and emit `(inkX − box.x)` as `w:ind w:left` "there"

Because the cell emitters already trim and already emit the ink offset, the change requested for them is a **no-op**: `cellParaXml`'s `insetTw` and `table()`'s `insetTw` *are* `(ink x − cell left edge)`, and there are no spaces left to strip. Two genuine residues remain, and these are where the same construct is actually missing:

**(a) The per-paragraph inset inside a multi-line cell.** The cell's `w:ind` is one number for the whole cell: `W:6592–6593` falls back to the *cell's* `insetTw` for every paragraph whose `indentPt` is NaN — and `indentPt` is only ever set by the column-row re-cut (`P:8640` `p.indentPt = p.x - t.colX[c];`, `P:8733` `for (Table.CellPara p : ps) p.indentPt = p.x - cellLeft;`). So in an ordinary multi-paragraph cell, paragraphs 2..n are written at the first line's indent. Minimal change, three lines, in `table()` at `W:6592`:

```java
int pInset = Float.isNaN(cp.indentPt)
        ? insetTw
        : (int) Math.max(0L, Math.round(cp.indentPt * TWIPS_PER_PT));
// ->
double cellLeftPt = x0 + edgeTw[c] / TWIPS_PER_PT;          // the written cell edge, as insetTw() uses
int pInset = Float.isNaN(cp.x)
        ? insetTw
        : (int) Math.max(0L, Math.round((cp.x - cellLeftPt) * TWIPS_PER_PT));
```

`cp.x` is already `visibleX(...)` (`P:8387`), so this is the cell analogue of the FINDINGS patch with no model change and no new field: the ink is pinned per paragraph instead of per cell. (The same one-liner in the `parasOfGlyphs` path is unnecessary — `P:8422` also passes `glyphFirstX(band)`.)

**(b) The anchored path — `anchorBox` + `lineParagraph`.** This is the one that still carries leading ASCII spaces into a run *and* writes `w:ind w:left="0"`, so its indent is `0 + N × space advance of the substitute face`, exactly the defect the FINDINGS patch removed from `flowFromBox`. Minimal change, two small edits, and no new model field (the diff's `Box.inkX` is required):

```java
// W:3569, lineParagraph — the spaces are the indent, so they are not text:
//   keep "<w:ind w:left=\"0\" .../>" (the anchor carries the position),
//   and strip the leading ASCII spaces off the first run it emits.
int strip = 0;
for (int i = 0; i < ...) // count leading ' ' across the leading runs of b.runs
// and at W:2641, anchorBox — anchor at the ink, not at the first space:
2641        anchor(sb, ctx, b.x, b.y - ASCENT * b.size, wPt, hPt, inner.toString(), 0f, -1, 0.6f);
//   ->
            float ax = Float.isNaN(b.inkX) ? b.x : b.inkX;     // (inkX − b.x) becomes the anchor's x
            anchor(sb, ctx, ax, b.y - ASCENT * b.size, wPt, hPt, inner.toString(), 0f, -1, 0.6f);
```

`(inkX − b.x)` is not written as `w:ind` on that path because the anchor already places the line absolutely; the equivalent statement there is "move the anchor to `inkX` and drop the spaces from the run", which is the same arithmetic with the same inputs.

---

## 6. What is proven, what is not

Proven by reading (each claim has a line number above): the three `w:tc` emitters and their enclosing methods; that `w:jc` never appears in a cell; that `insetTw` is ink-relative and measured from the *written* cell edge; that `Table.cellX` and `CellPara.x` both carry `visibleX`; that all four cell text builders trim; that `Box.text()` does not.

Not proven here: which of these writers produced the space-led lines in the 10 documents that stayed byte-identical. That needs a run of the benchmark (explicitly out of scope for this task). The code reading says the cell emitters cannot produce a space-led run, so those documents' space-led lines are most likely reaching `anchorBox`/`lineParagraph`, `flowFromBox` with `p.align != 0` or `b.inkX` NaN (the patch's own guard, `p.align == 0 && !b.rotated && !b.ring && !Float.isNaN(b.inkX)`), or a paragraph-merge inside `para()`. Those three are the places to instrument next.
