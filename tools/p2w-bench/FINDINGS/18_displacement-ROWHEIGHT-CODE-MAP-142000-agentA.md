# ROWHEIGHT-MAP — how DocxWriter writes table row heights and cell paragraph spacing

Static source read only. No build, no run. Every claim carries `file:line`.
`DocxWriter.java` and `PdfToWord.java` are the copies at `/scratch/input/` (DocxWriter 7431 lines, PdfToWord 10016 lines).

Two method names are used repeatedly below; they are defined here once:

| label | method | declared at |
|:--|:--|:--|
| **`table()`** | `private static void table(StringBuilder sb, PdfToWord.Table t, Ctx ctx)` | `DocxWriter.java:5767` (body ends `DocxWriter.java:6859`) |
| **`columnPage()`** | `private static boolean columnPage(StringBuilder sb, PdfToWord.Page page, Ctx ctx, float pw)` | `DocxWriter.java:1668` (emission at 2159–2161, `return true` at `DocxWriter.java:2195`) |

Constants that every section depends on: `TWIPS_PER_PT = 20.0` (`DocxWriter.java:52`), `LINE_FACTOR = 1.15f` (`DocxWriter.java:73`), `LINE_BASE = 0.8f` (`DocxWriter.java:214`), `AUTO_LINE_EM` default `"1.15"` (`DocxWriter.java:141-142`).

---

## 1. Every place that emits `w:trHeight`, and every place that computes the number

There are exactly **two** emission sites in the file (`grep -n "<w:trHeight"` returns two appends).

### Site A — `table()`, the page's own tables: `w:hRule="atLeast"`

Emission, inside the row loop `for (int r = 0; r < keepRows; r++)` (`DocxWriter.java:6127`):

```
DocxWriter.java:6316            inner.append("<w:tr>");
DocxWriter.java:6317            if (rowTwHere > 0) {
DocxWriter.java:6318                inner.append("<w:trPr><w:trHeight w:val=\"").append(rowHeightTw)
DocxWriter.java:6319                     .append("\" w:hRule=\"atLeast\"/><w:cantSplit/></w:trPr>");
```

`w:val` is `rowHeightTw`; `w:hRule` is the literal `atLeast`; the element is omitted entirely when `rowTwHere <= 0` (`DocxWriter.java:6317`).

The number `rowHeightTw` is built in six stages, all inside the same row iteration:

| # | line(s) | statement | input, and where it came from |
|:--|:--|:--|:--|
| 1 | `5984-5986` | `int rowCount = Math.max(1, t.rows.size()); float extentPt = t.bottom - t.top; int rowTw = extentPt > 0f ? (int) Math.round(extentPt / rowCount * TWIPS_PER_PT) : 0;` | the table's own extent (`t.bottom - t.top`) divided by its row count — the **average** pitch, not a per-row one |
| 2 | `6131-6137` | `int rowTwHere = rowTw;` then, when `exactRows`, `rowTwHere = (int) Math.round(pitchPt * TWIPS_PER_PT)` with `pitchPt = rowEdge[r + 1] - rowEdge[r]` | the **measured** pitch between two of the page's own row edges; `exactRows` is `rowEdge != null && rowEdge.length == t.rows.size() + 1` (`DocxWriter.java:6032`), `rowEdge` is `t.rowEdge` (`DocxWriter.java:6031`) |
| 3 | `6141-6145` | `if (remainTw > 0 && remainTw < rowTwHere) { rowTwHere = remainTw; rowCapTw = remainTw; }` | the space left to the paper's bottom edge, for the one row that straddles it |
| 4 | `6162`, `6163-6164` | `int pitchTwHere = rowTwHere; int contentTwHere = rowTwHere > 0 && ruleTwHere > 0 ? Math.max(1, rowTwHere - ruleTwHere) : rowTwHere;` | `ruleTwHere` is the row's own stroke, `(szAbove + szBelow) * TWIPS_PER_PT / 16.0` (`DocxWriter.java:6149`), from the drawn side widths `sideSz[0/2/4]` (`DocxWriter.java:6111-6113`) |
| 5 | `6167-6195` | `cellLineHere` / `naturalLineHere` from `contentTwHere`, then `rowParts`/`nlParts`/`wrapParts` from the `'\n'` count in the cell string (`6178`) and `wrapsAt(cv, q, r, t, colTw, cols)` (`6189`); `int baseLineTw = rowParts > 1 ? naturalLineHere : cellLineHere;` | the model's cell strings and the column widths |
| 6 | `6204-6219` | `int rowLineTw = baseLineTw;` then per cell `if (sz > 0f) rowLineTw = Math.max(rowLineTw, (int) Math.round(sz * 1.25f * TWIPS_PER_PT));` | `sz` is `t.sizes.get(r).get(q)` (`DocxWriter.java:6217-6218`) — the point size the page drew that cell's text at |
| 7 | `6226-6232` | `int typeFloorTw = rowLineTw;` … `int rowHeightTw = Math.max(rowTwHere, rowLineTw);` … `rowHeightTw = Math.max(typeFloorTw, twScale(rowHeightTw, ctx.squeeze));` | the pitch floor from stage 2/3, the line box from stage 6, and the page squeeze |
| 8 | `6260-6276` | `rowHeightTw = Math.max(rowHeightTw, paraContentTw + ruleTwHere);` (guarded by `if (paraContentTw > 0)`) | `paraContentTw` is the max over columns of `cellParasTw(t, r, q, recutTopPt, rowLineTw)` (`DocxWriter.java:6264-6267`), which sums the cell's `w:before` + `w:line` (`DocxWriter.java:6909-6928`); it runs **only for `t.recut` tables** (`DocxWriter.java:6264`), under `if (paraContentTw > 0)` (`DocxWriter.java:6270`) |

So the number written at `DocxWriter.java:6318` is, in words: `max(page pitch (measured or averaged), line box, and — for a re-cut table only — the cell's summed paragraph content plus the rule)`, then held at its type floor through the squeeze.

### Site B — `columnPage()`, the layout-column table: `w:hRule="exact"`

```
DocxWriter.java:2159            sb.append("<w:tr><w:trPr><w:cantSplit/>")
DocxWriter.java:2160                    .append("<w:trHeight w:val=\"").append(rowTw)
DocxWriter.java:2161                    .append("\" w:hRule=\"exact\"/></w:trPr>");
```

`w:val` is `rowTw`, computed immediately above:

```
DocxWriter.java:2142                cellTw[c] = flowTwOf(cellXml[c]) + ctx.wrapDebtTotalTw;
DocxWriter.java:2144            int rowTw = 1;
DocxWriter.java:2145            for (int c = 0; c < n; c++) rowTw = Math.max(rowTw, cellTw[c]);
```

Input: the cell's **written XML**, summed by `flowTwOf(CharSequence)` (`DocxWriter.java:2207`) as every `w:before` plus every `w:line` of the cell's paragraphs (nested-table `w:trHeight` substituted inside a nested `w:tbl`), plus the wrap debt `ctx.wrapDebtTotalTw`. This is the only place a row height is derived from written cell content rather than from the page's geometry. An empty cell contributes `w:line="1"` (`DocxWriter.java:2133-2136`).

### Nothing else writes a row height

`grep -n "trHeight" DocxWriter.java` matches only these two appends plus comments; `PdfToWord.java` contains no `w:trHeight` emission (the writer is the only XML emitter). A nested table inside a cell is emitted by the same `table()` path, so Site A covers it.

---

## 2. The page-budget accounting

The brief's name is right. The variable is **`writtenRowsTw`**, declared at `DocxWriter.java:6116` inside `table()`:

```
DocxWriter.java:6114        // The height this table is really written at: the sum of the row heights below. It is
DocxWriter.java:6115        // what the page budget must read (see the flow charge after the loop).
DocxWriter.java:6116        int writtenRowsTw = 0;
```

It is charged **once per kept row**, at the top of the row's own iteration:

```
DocxWriter.java:6233            // The budget is charged what the renderer will LAY OUT, which is the content plus
DocxWriter.java:6234            // the rule - not the content alone. Charging the content alone under-measures every
DocxWriter.java:6235            // ruled table by one rule a row, and this is the number the flow after the table is
DocxWriter.java:6236            // placed from.
DocxWriter.java:6237            writtenRowsTw += Math.max(0, Math.max(pitchTwHere,
DocxWriter.java:6238                    Math.max(rowTwHere, rowLineTw) + ruleTwHere));
```

and handed to the page's flow after the table:

```
DocxWriter.java:6781        ctx.flowTw += (writtenRowsTw > 0
DocxWriter.java:6782                ? twScale(writtenRowsTw, ctx.squeeze)
DocxWriter.java:6783                : twScale((int) Math.round(Math.max(0f, extentPt) * TWIPS_PER_PT), ctx.squeeze))
DocxWriter.java:6784                + (carrier ? carrierTw : 0);
```

**Exactly what is charged per row** — three terms, and the answer to the brief's "declared? content? both?" is *neither of the two as stated*:

1. `pitchTwHere` (`DocxWriter.java:6162`), i.e. the declared pitch (`rowTwHere`, stages 2–3 of §1) — the declared term.
2. `max(rowTwHere, rowLineTw) + ruleTwHere` — the height the row is **written** at (§1 stage 7), **plus** the row's own stroke. `rowLineTw` is a single **line box**, floored by `sz * 1.25f` per cell (`DocxWriter.java:6219`), not the cell's summed content.
3. Nothing else. In particular:
   - **Cell paragraph content is not charged.** The charge has no term for the cell's `w:before`/`w:line` sum; `spacingTw()` deliberately ignores them for the page (`DocxWriter.java:470-475`: *"A cell's line is not the page's height: the row it sits in already carries that height as its own w:trHeight, and counting both charges a table twice"*), and `writtenRowsTw` carries no equivalent.
   - **The re-cut content floor is not charged either.** `writtenRowsTw` is accumulated at `DocxWriter.java:6237-6238`, which is **before** the `paraContentTw` floor at `DocxWriter.java:6260-6276` raises `rowHeightTw`. For a `t.recut` table the written `w:trHeight` can therefore exceed what the budget was charged.
   - The per-page post-write measurement sums `w:trHeight` per row and flow `w:before`/`w:line` outside tables only (`spacingTw`, `DocxWriter.java:449`, `476-478`; used at `DocxWriter.java:1169`, `1221`, `1268`), so it agrees with `writtenRowsTw` in shape but is taken off the written XML rather than the model.

**Consequence for the brief's premise.** The budget does *not* charge the bare declared value. Where `t.sizes` holds a positive size for any cell of the row, the charge is at least `1.25 × size + ruleTwHere` (`DocxWriter.java:6219` → `6238`). Where `t.sizes` holds `NaN`, `0` or no entry, `sz > 0f` is false (`DocxWriter.java:6219`) and `rowLineTw` falls back to `baseLineTw` (`DocxWriter.java:6195`), which is derived from the row pitch alone — **there the charge is the bare declared value, and the size term is absent entirely**. Which of the two applies to a given document is not determinable from source; it depends on whether the pass that built that table recorded `t.sizes`.

---

## 3. The floor question: what would have to change for `max(declared, 1.15 × size)`

### What the source has today

- The `1.15` constant exists in this file twice, and **neither is the row floor**: `LINE_FACTOR = 1.15f` (`DocxWriter.java:73`, consumed by `flowLinePt` at `DocxWriter.java:3889`) and `AUTO_LINE_EM` default `"1.15"` (`DocxWriter.java:141-142`, consumed by `spacing()` at `DocxWriter.java:155-157`).
- The **row** floor is `1.25`, not `1.15`:

```
DocxWriter.java:6217                float sz = r < t.sizes.size() && q < t.sizes.get(r).size()
DocxWriter.java:6218                        && t.sizes.get(r).get(q) != null ? t.sizes.get(r).get(q) : 0f;
DocxWriter.java:6219                if (sz > 0f) rowLineTw = Math.max(rowLineTw, (int) Math.round(sz * 1.25f * TWIPS_PER_PT));
```

- That floor reaches **both** the written declaration (`DocxWriter.java:6228`, `rowHeightTw = Math.max(rowTwHere, rowLineTw)`) and the budget (`DocxWriter.java:6238`).

### The variable holding the row's font size

**There is no row-level font-size variable in scope at `DocxWriter.java:6237`.** The only size in scope is the loop-local `float sz` at `DocxWriter.java:6217-6218`, one value **per cell** (`q` indexes columns of `row`), and the max is folded straight into `rowLineTw` at `DocxWriter.java:6219`. `rowLineTw` is therefore the only carrier of "the row's largest size", and it carries it already multiplied by 1.25.

`t.sizes` is one size per cell, not per run: `public final List<List<Float>> sizes` (`PdfToWord.java:516`), documented as *"The point size each cell's text was drawn at … `Float#NaN` where the pass did not measure it"* (`PdfToWord.java:507-514`), and the model's cell description states *"Every cell carries the FIRST line's style only"* (`PdfToWord.java:317-320`). So **the size of the largest *run* in the row is not determinable in `table()`'s scope** — the nearest available quantity is the largest per-**cell** size, which is what `DocxWriter.java:6217-6219` already takes.

### Exact lines that would have to change

1. `DocxWriter.java:6205-6220` — hoist a row-scope variable (e.g. `float rowMaxSz = 0f;` before the loop, `if (sz > rowMaxSz) rowMaxSz = sz;` after `DocxWriter.java:6218`). Without it the size is gone by line 6237.
2. `DocxWriter.java:6237-6238` — add the floor to the charged expression (the only line pair that decides what the budget pays per row).
3. `DocxWriter.java:6219` — **only if the written declaration is also meant to move.** Changing `1.25f` here changes `rowHeightTw` at `DocxWriter.java:6228`, i.e. the XML, not just the budget.
4. `DocxWriter.java:6195` / `6204` — the fallback path for a row with no recorded size; no size is available there to multiply, so the floor cannot be computed on that path without new data (see "not determinable" below).

**Not determinable from source:** whether the `1.15 × size` floor is *reachable* for a row whose `t.sizes` entry is `NaN`. `PdfToWord.java:507-514` says the field is `NaN` "where the pass did not measure it", and no other per-cell size field exists in `Table` (`PdfToWord.java:307-330`, `505-525`). Plumbing would have to come from the passes that populate `sizes` (`PdfToWord.java:8051`, `8708`, `8768`, `9122`, `9469`, `9642`, `9662`), which is outside `DocxWriter`.

---

## 4. Every `<w:spacing ... w:before=...>` inside a table cell paragraph

The element is emitted by exactly one function, and reached by exactly two call sites for cell paragraphs.

**The emitter** — `spacing(int beforeTw, int lineTw, float size, boolean auto, boolean pageFirst)` (`DocxWriter.java:149`):

```
DocxWriter.java:150        if (!auto) {
DocxWriter.java:151            return "<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\""
DocxWriter.java:152                    + beforeTw + "\" w:after=\"0\" w:line=\"" + lineTw
DocxWriter.java:153                    + "\" w:lineRule=\"exact\"/>";
DocxWriter.java:154        }
DocxWriter.java:155        int boxTw = (int) Math.round(AUTO_LINE_EM * Math.max(1f, size) * TWIPS_PER_PT);
DocxWriter.java:156        long b = (long) beforeTw + lineTw - boxTw;
...
DocxWriter.java:165        if (pageFirst) b += Math.round((1f - LINE_BASE) * (boxTw - lineTw));
DocxWriter.java:166        if (b < 0) { b = 0; autoFloorHits++; }
DocxWriter.java:167        return "<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\""
DocxWriter.java:168                + b + "\" w:after=\"0\" w:line=\"240\" w:lineRule=\"auto\"/>";
```

Cell call sites:

| site | line | what it writes |
|:--|:--|:--|
| single-`w:p` cell, `table()` | `DocxWriter.java:6651-6652` | `.append(spacing(cellBeforeTw, cellBoxTw, cellSz, autoCellBoxes(), false))` |
| per-paragraph, `cellParaXml()` | `DocxWriter.java:6941-6942` | `.append(spacing(beforeTw, boxTw, sz, autoCellBoxes(), false))` — called from `DocxWriter.java:6640`, once per `CellPara` |
| empty cell of a `columnPage()` table | `DocxWriter.java:2134-2135` | literal `w:before="0" w:after="0" w:line="1" w:lineRule="exact"` |

Non-cell `w:before` sites, for completeness (these are paragraphs in the flow, not in a cell): the table spacer at `DocxWriter.java:5871-5874` (before the table) and the carrier at `DocxWriter.java:6770-6773` (after it), both `w:before="0"`; flow paragraphs at `DocxWriter.java:3581` and `4432`.

### A cell with several `w:p` versus a cell with one `w:p`

The branch is `cps.size() >= 2` at `DocxWriter.java:6610`, where `cps = t.parasAt(r, c)` (`DocxWriter.java:6609`):

**(a) Several `w:p` — the model carries the page's own lines** (`DocxWriter.java:6610-6646`):

```
DocxWriter.java:6630                    for (int q = 0; q < cps.size(); q++) {
DocxWriter.java:6635                        int boxTw = paraBoxTw(cps, q, rowLineTw);
DocxWriter.java:6636                        int beforeTw = q == 0 ? before0 : paraBeforeTw(cps, q, rowLineTw);
DocxWriter.java:6637                        stackTw += (q == 0 ? 0 : beforeTw) + boxTw;
DocxWriter.java:6640                        cellParaXml(inner, cp, beforeTw, boxTw, pInset, cellSz);
DocxWriter.java:6641                    }
```

**Yes — `w:before` is written on the 2nd..nth paragraph**, from `paraBeforeTw` (`DocxWriter.java:6898-6906`):

```
DocxWriter.java:6900        int boxPrev = paraBoxTw(cps, q - 1, rowLineTw);
DocxWriter.java:6901        int boxHere = paraBoxTw(cps, q, rowLineTw);
DocxWriter.java:6902        float dy = cps.get(q).baseY - cps.get(q - 1).baseY;
DocxWriter.java:6903        long want = Math.round(dy * TWIPS_PER_PT)
DocxWriter.java:6904                - Math.round(0.2f * boxPrev) - Math.round(LINE_BASE * boxHere);
DocxWriter.java:6905        return (int) Math.max(0L, want);
```

It is the page's own inter-baseline gap, floored at 0 (`DocxWriter.java:6905`). It is **0 only when the leading is already the box** (`DocxWriter.java:6903-6904` cancel); where the page drew a paragraph gap it is positive and every line below the first is placed by it.

**(b) One `w:p` — a cell whose string holds `'\n'`** (`DocxWriter.java:6715-6735`):

```
DocxWriter.java:6715                    String[] parts = cell.split("\n");
DocxWriter.java:6716                    for (int q = 0; q < parts.length; q++) {
DocxWriter.java:6717                        if (q > 0) {
...
DocxWriter.java:6730                            inner.append("<w:br/>");
DocxWriter.java:6731                        }
```

The lines are `<w:br/>` inside **one run of one `w:p`**; there is no 2nd..nth paragraph, so **no `w:before` exists on those lines at all**. The single `w:before` for the whole cell is `cellBeforeTw` at `DocxWriter.java:6652`. The same shape is used by `cellParaXml` for a `CellPara` whose own text contains `'\n'` (`DocxWriter.java:6964-6974`).

So the answer to the brief's question depends on which representation the cell got: **written** on 2nd..nth `w:p` in form (a) (`DocxWriter.java:6636` → `6942`), and **not written at all** in form (b), because those lines are not paragraphs. A cell the renderer wraps (counted by `wrapsAt` at `DocxWriter.java:6189`, folded into `rowParts` at `DocxWriter.java:6193`) is form (b): one `w:p`, continuation lines are renderer line boxes.

---

## 5. Patch plan

Line numbers are for the files as given. **Caveat:** `18-row-pitch-net-of-rule-and-subpoint-grid.patch` inserts 26 lines at its `DocxWriter.java` hunk `@@ -6313,10 +6313,36 @@` (patch file lines 5-42), i.e. immediately after `DocxWriter.java:6315`. If that patch is applied first, **every line after 6315 in `table()` shifts by +26** — including `6318`, `6636`, `6781`, `6924`, `6942`. The hunk's old-side context matches the file as given (`inner.append("<w:tr>");` at 6316), so the patch does apply cleanly to it.

### (a) Charge the budget the `1.15 × size` floor

**Step 1** — carry the row's largest size out of the per-cell loop. At `DocxWriter.java:6205` (before `for (int q = ...)`) add `float rowMaxSz = 0f;`, and after `DocxWriter.java:6218` add `if (sz > rowMaxSz) rowMaxSz = sz;`. Leave `DocxWriter.java:6219` untouched so the **written** declaration keeps its current 1.25 em floor.

**Step 2** — charge it. Replace `DocxWriter.java:6237-6238` with a form that adds the floor as a fourth term:

```
int lineBoxFloorTw = (int) Math.round(rowMaxSz * LINE_FACTOR * TWIPS_PER_PT);
writtenRowsTw += Math.max(0, Math.max(pitchTwHere,
        Math.max(Math.max(rowTwHere, rowLineTw), lineBoxFloorTw) + ruleTwHere));
```

`LINE_FACTOR` is already `1.15f` (`DocxWriter.java:73`) and is the same constant the flow uses, so no new magic number is introduced. This touches **only** the budget: `rowHeightTw` (`DocxWriter.java:6228`) and the emission (`DocxWriter.java:6318`) are unchanged, so the XML and therefore the rendered document do not move on this half of the patch.

**Risk 1 — the change is a no-op wherever a size exists.** `rowLineTw` at `DocxWriter.java:6238` is already ≥ `1.25 × sz` (`DocxWriter.java:6219`), which is strictly greater than `1.15 × sz`, so the new term only ever binds where `rowMaxSz == 0f` — and there it contributes 0. The patch as written cannot change any number unless Step 1 is fed a size the row does not have today. Stated plainly: **on the `t.sizes == NaN` path there is no size to multiply, so this half of the patch cannot make the budget match Google's floor; it only makes the code express the floor.**

**Step 2-alt** — if the intent is to make the *declared* floor 1.15 as well (which is what actually changes a laid pitch), change `1.25f` → `LINE_FACTOR` at `DocxWriter.java:6219`. That is one character-class change and it moves `rowHeightTw` at `DocxWriter.java:6228`, i.e. the `w:trHeight` at `DocxWriter.java:6318`, for every table whose cells carry a size. Risk: it lowers every declaration that the 1.25 floor was raising, so `18_displacement` and `23_line_pitch` both move on every such table — and it changes which rows satisfy the `rowExact` predicate of the pending patch (`rowHeightTw == rowTwHere`, patch file line 26), silently widening or narrowing that patch's reach.

**Risk 2 — the budget shrinks.** `writtenRowsTw` is added to `ctx.flowTw` at `DocxWriter.java:6781-6784`; a larger charge per row reaches the fitter, whose answer to an overrun is the global squeeze (`DocxWriter.java:1146-1219`, note at `DocxWriter.java:6038-6044`). Charging more per row can therefore move *every* gap on *every* page of a dense document, which is a corpus-wide change, not a table-local one.

### (b) `w:before="0"` on continuation paragraphs of a wrapped cell

**Step 1** — the only line that decides it: `DocxWriter.java:6636`. Change

```
int beforeTw = q == 0 ? before0 : paraBeforeTw(cps, q, rowLineTw);
```

to

```
int beforeTw = q == 0 ? before0 : 0;
```

`cellParaXml` (`DocxWriter.java:6940-6942`) then writes `w:before="0"` for every paragraph after the first, in both spacing modes (`DocxWriter.java:151-153` and `155-167`).

**Step 2** — keep the model's own content sum in step, or a re-cut table's row height will disagree with its XML. `cellParasTw` adds the same quantity at `DocxWriter.java:6923-6926`:

```
DocxWriter.java:6923        for (int q = 1; q < cps.size(); q++) {
DocxWriter.java:6924            total += paraBeforeTw(cps, q, rowLineTw);
DocxWriter.java:6925            total += paraBoxTw(cps, q, rowLineTw);
DocxWriter.java:6926        }
```

Drop line `6924` (or gate both call sites on one flag). This matters only for `t.recut` tables, where `paraContentTw` reaches `rowHeightTw` at `DocxWriter.java:6276`.

**Step 3** — leave `paraBeforeTw` (`DocxWriter.java:6898-6906`) itself alone unless both callers are changed; deleting its body would leave `cellParasTw` compiling against a changed contract.

**Risk 1 — it moves text, by design.** `beforeTw` on `q >= 1` is the page's measured inter-baseline gap (`DocxWriter.java:6902-6905`). Zeroing it lifts every continuation line by that gap; `stackTw` (`DocxWriter.java:6637`) and the recut floor (`DocxWriter.java:6924`) shrink with it. Where the page's leading already equals the box, `paraBeforeTw` returns 0 and nothing moves — so the change is confined to cells the page drew with a real paragraph gap, which are exactly the cells the per-line model exists for (`PdfToWord.java:317-330`).

**Risk 2 — it does not reach the case the brief names.** A *wrapped* cell (one the renderer wraps, `rowParts > 1` via `wrapsAt`, `DocxWriter.java:6189-6193`) is written as a single `w:p` (`DocxWriter.java:6651-6652`) with `<w:br/>` between lines (`DocxWriter.java:6715-6734`). It has **no continuation paragraph**, so there is nothing on which to write `w:before="0"`. For those cells the pitch is decided by the renderer's line box and by `w:trHeight` — i.e. by the floor in §3, not by this half of the patch.

**Risk 3 — the auto construct can still add a box.** In `LINE_MODE == 2` (`autoCellBoxes()`, `DocxWriter.java:146`), `spacing()` writes `w:line="240" w:lineRule="auto"` and `w:before = beforeTw + lineTw - boxTw` (`DocxWriter.java:155-166`). With `beforeTw = 0` the emitted `w:before` is `lineTw - boxTw`, floored at 0 (`DocxWriter.java:166`) and counted in `autoFloorHits` (`DocxWriter.java:144`, `DocxWriter.java:172`). Zeroing the input does **not** guarantee `w:before="0"` in that mode.

---

## Not determinable from source

- Whether any given corpus document's tables carry positive `t.sizes` entries, and therefore whether the existing `1.25 × size` floor at `DocxWriter.java:6219` is active on it. The field is documented as `Float#NaN` "where the pass did not measure it" (`PdfToWord.java:507-514`); which passes populate it for which table shapes is spread over `PdfToWord.java:8051`, `8708`, `8768`, `9122`, `9469`, `9642`, `9662` and is not decidable without running the passes.
- The size of the largest **run** in a row: no per-run size is stored on `Table` in `DocxWriter`'s scope; `t.sizes` is per cell (`PdfToWord.java:516`).
- Which of Site A / Site B produced the rows on the 16 `18_displacement` documents: `columnPage()` is entered only for a page accepted as a multi-column layout (`DocxWriter.java:1668`; refusals at `DocxWriter.java:1678`, `1950`, `1971`), and the decision is made at run time, not in the source.
