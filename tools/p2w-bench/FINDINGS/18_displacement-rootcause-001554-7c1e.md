# 18_displacement — ROOT CAUSE: the row top is derived with `LINE_BASE × pitch`, the cell's baseline is written at `before + LINE_BASE × box`, and the two are not inverses

**28 Nov 2026 · diagnosis only, no engine change.** Engine at HEAD `33863086`
(`git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/`). Corpus 213.
Everything below that is called *measured* was measured in this slot with `ConvertOne` + `soffice`
+ PyMuPDF on the repo's own corpus; everything called *recorded* comes from
`benchmarks/gverify/*.json` (Google, engine `a05b20eb05fe0fc8`) and `benchmarks/gverify-lo/*.json`
(LibreOffice, engine `d28ca7516c3f9165`).

---

## 0. The class, counted

From `benchmarks/gverify/` (206 scored): **108 documents fail `18_displacement`**, 18 of them fail
**nothing else**. Splitting against `benchmarks/gverify-lo/`: 49 of the 108 also fail in
LibreOffice, 59 fail only in Google. So the class is not one renderer's opinion of one construct —
any root cause has to be visible in the *declaration*, not only in Google's reading of it.

---

## 1. THE MECHANISM

A table's cell text is placed by two different pieces of arithmetic that must be inverses of each
other and are not.

**(a) The row's TOP EDGE is derived from a baseline by subtracting `LINE_BASE × pitch`.**
`DocxWriter.java:6657-6665`:

```java
float rowTopPagePt = Float.NaN;
if (exactRows) {
    float edgePt = rowEdge[r];
    if (!t.ruled) {                                   // the whitespace / rule-less pass
        float pitchHere = rowEdge[r + 1] - rowEdge[r];
        if (pitchHere > 0.5f && pitchHere < 2000f) edgePt -= LINE_BASE * pitchHere;
    }
    rowTopPagePt = edgePt;
}
```

For a rule-less table `rowEdge` holds the rows' first **baselines** (`PdfToWord.java:7957-7960`;
the same fact is stated at `DocxWriter.java:6619-6622`), so the row's top is *invented* as

    rowTop = firstBaseline − 0.8 × pitch                       (LINE_BASE = 0.8, DocxWriter.java:220)

**(b) The cell's BASELINE is then written `before + LINE_BASE × box` below that top.**
`DocxWriter.java:6912-6924`:

```java
float wantPt = cellBaseY - rowTopPagePt;
...
int beforeTw = (int) Math.round((wantPt - LINE_BASE * boxTw / TWIPS_PER_PT) * TWIPS_PER_PT);
int capTw = ... Math.min(rowHeightTw, contentTwHere) - boxTw;
cellBeforeTw = Math.max(0, Math.min(beforeTw, capTw));
```

and the paragraph the reader gets is `w:before = before`, `w:line = box`, `w:lineRule="exact"`
(`DocxWriter.java:158-160`), whose baseline sits `before + 0.8 × box` under the row top.

**(c) The residual.** A cell that fills its row gets `before + box = pitch` (the cap at :6919-6920
is `contentTw − box`, and `contentTw = pitch − rule`), so the baseline the engine *asks for* is

    wantPt = before + 0.8 × box  =  before + 0.8 × (pitch − before)  =  0.8 × pitch + 0.2 × before

while the top it derived assumed `0.8 × pitch`. **The cell lands `0.2 × before` lower than the row
top arithmetic assumed, and every row of the table inherits the same shift because the pitch itself
is right.** The displaced amount is a CONSTANT, not a ramp:

    displacement = (1 − LINE_BASE) × before = 0.2 × beforeTw / 20   pt, downward

The engine already knows this number. `DocxWriter.java:6936-6940` records the *same* factor on the
fallback branch and says what it costs:

> `// Writing before = rowLineTw - box instead moved every cell 0.2 * row pitch lower`
> `// and 18_median_dy went 64 -> 100 documents.`

The `before` was fixed. The identical `0.2` is still in the row top at :6662.

---

## 2. THE EVIDENCE — two documents, measured, with the source value

`ConvertOne` from HEAD → `soffice --headless --convert-to pdf` → baselines read with PyMuPDF.
The cell's `before`/`box`/`w:trHeight` are read straight out of `word/document.xml`.

### `35_four_typefaces_one_page` — page 1, the marks table, row 1

| what | value | where |
|---|---|---|
| source row-1 baseline | **148.80 pt** | `corpus/35_four_typefaces_one_page.pdf` |
| LibreOffice render, same row | **152.50 pt** | HEAD render |
| displacement | **+3.70 pt downward, constant on every row** (row 2: 167.80 → 171.50 = +3.70) | measured |
| the cell's declared `w:before` | **348…368 tw = 18.40 pt** | `w:spacing w:before="368" w:line="12" w:lineRule="exact"` |
| the cell's declared `w:line` (box) | 12 tw = 0.60 pt (the hairline, `hairlinePt()`, :4119) | " |
| `w:trHeight` | 380 tw = 19.00 pt, `hRule="atLeast"` | " |
| **predicted: 0.2 × 18.40** | **3.68 pt** | `(1 − 0.8) × before` |
| predicted row top vs page's row top | 148.80 − 0.8×19.00 = **133.60** vs 148.80 − 18.88 = **129.92** → 3.68 low | :6662 |

3.68 predicted, 3.70 measured; the 0.02 is the twip rounding of `w:before`.

### `71_invoice_space_aligned_no_rules` — page 1, the item table, rows 2-7

| what | value | where |
|---|---|---|
| source baselines, rows 1-2 | **176.00, 194.00 pt** (pitch 18.00) | corpus PDF |
| HEAD LibreOffice render | **181.00, 197.30 pt** | measured |
| displacement rows 2-7 | **+3.30 pt, constant** | measured |
| the cell's declared `w:before` | **348 tw = 17.40 pt** (`w:line="12"` = 0.60) | document.xml |
| `w:trHeight` | 360 tw = 18.00 pt | " |
| **predicted: 0.2 × 17.40** | **3.48 pt** | |

Rows 2-7 land within **0.18 pt** of the prediction. Row 1 carries a further **+1.52 pt** because
its table top comes from the flow (a spacer paragraph, `w:before="169" w:line="11"`), not from
`rowEdge` — a second, additive component that section 4 covers.

### Why this fails a *count* check on a page where the median looks harmless

The check's tolerance is `clamp(0.35 × size, 1.5, 4.5)` pt (`verify_google.py:37-41`). The corpus's
table type is 7.4-9.0 pt, so the tolerance is **2.59-3.15 pt** — under the 3.3-3.7 pt this
mechanism produces. Every run inside the table is out, on every page, while `med_dy` stays near 0
because the flow text above the table is exact (section 3). That is exactly the recorded shape:
`35_four_typefaces_one_page` reads `med_dy −2.8, worst_dy 3.3`; `71_invoice…` reads
`med_dy +2.9, worst_dy 26.3` (the 26.3 is a pairing artefact of the repeated numeric cells —
`FINDINGS/18_dsmall-dy-cluster-of-15-01-ROW-PITCH-RAMP-NOT-CONSTANT-27NOV.md` §3).

### The second, cumulative half: ruled rows are declared a rung short

`DocxWriter.java:6601`:

```java
if (pitchBinds && footRoom && rowHeightTw > ROW_RUNG_UNDER_TW) rowHeightTw -= ROW_RUNG_UNDER_TW;
```

`ROW_RUNG_UNDER_TW = 10` tw = **0.50 pt** (`:54`). A pitch-bound row is therefore declared half a
point under the pitch the page drew, once per row, so the error is *cumulative* rather than
constant. Measured on `table-with-no-header-row`, page 1, against a source row pitch of **18.40 pt
uniform over 26 rows** (the page's own drawn rules: 104.92, 123.32, 141.72, 160.12 …):

| row | source y | HEAD render y | dy |
|---:|---:|---:|---:|
| 1 | 176.00 | 176.48 | +0.48 |
| 2 | 194.40 | 194.38 | −0.02 |
| 3 | 212.80 | 212.28 | −0.52 |
| 4 | 231.20 | 230.18 | −1.02 |
| 5 | 249.60 | 248.08 | −1.52 |
| 27 | — | — | **−12.02** |

**−0.50 pt per row, −12.0 pt by row 27** — the rung, 1:1, 25 times. The rendered pitch is 17.90 pt
against the page's 18.40.

So the class has two signs of the same arithmetic error: a **constant** `(1 − LINE_BASE) × before`
offset on a rule-less table (mechanism a/b/c above) and a **cumulative** `ROW_RUNG_UNDER_TW` ramp on
a ruled one. Both are in the declaration; both are reproduced by LibreOffice alone, which is why 49
of the 108 fail in both renderers.

---

## 3. WHAT I RULED OUT, AND HOW

**Flow (non-table) text placement.** Ruled out by direct measurement, not argument. I reconstructed
the declared baseline chain from `word/document.xml` (`Σ(w:before + w:line)` down the body, baseline
at `boxTop + 0.8 × box`) and compared it with the page's own baselines:

| document | flow line | declared | page drew | error |
|---|---|---:|---:|---:|
| `35_four_typefaces_one_page` | 4 flow lines above the table | 58.02 / 72.04 / 104.02 / 122.03 | 58.00 / 72.00 / 104.00 / 122.00 | ≤ 0.04 pt |
| `71_invoice_space_aligned_no_rules` | 6 flow lines above the table | 62.02 / 76.04 / 108.02 / 123.98 / 153.98 / 162.99 | 62.00 / 76.00 / 108.00 / 124.00 / 154.00 / 163.00 | ≤ 0.04 pt |
| `70_magazine_drop_cap_photo_caption` (no table at all) | 4 heading lines | 52.02 / 92.02 / 110.04 | 52.00 / 92.00 / 110.00 | ≤ 0.04 pt |

**The flow path is exact to 0.04 pt.** Whatever fails `18_displacement` on a flow-only document is
not the flow arithmetic — and `70_magazine_drop_cap_photo_caption` still fails, so its charge is its
4 `<wp:anchor>` boxes, not its paragraphs. This eliminates the `w:line`-exact-vs-Google charge
(`HAIRLINE_EM`, `:113`, `:4119`), `spacing()` (`:149-159`) and `flowLinePt` (`:4133`) as the *class's*
cause: they are right, which is why the flow half of these pages scores clean.

**`LINE_BASE` itself.** Ruled out as the villain and confirmed as the *shared* constant: at 0.8 it is
correct for LibreOffice's exact line box (the header comment at `:208-220` measures it at 0.2 of the
box over 9 box heights and 4 faces). The defect is not the value — it is that the same constant is
applied to a **box** in one place (:6913) and to a **pitch** in another (:6662). No value of
`LINE_BASE` makes both right; only making them the same quantity does.

**`worst_dy` as a signal.** Ruled out as evidence (not as a verdict). `71`'s `worst_dy 26.3` and
`table-with-no-header-row`'s 101.4 are the greedy pairing in `verify_google.py:5626-5645` claiming
the nearest *unused* copy of a repeated numeric string, not a displacement. Any fit to `worst_dy`
alone is fitting noise. `med_dy` is a *dilution* of the table offset by the clean flow lines above
it, so a small `med_dy` with a failing count clause is the signature of this mechanism, not
evidence against it.

**Page-level constructs.** Ruled out for these two documents: both are single-page, both have
`w:pgMar` all zero and a page-top gap that the flow spends correctly (measured exact, table above).
The 48-67 pt UNIFORM PAGE SHIFT pages in
`FINDINGS/18_displacement-dy-shape-101323-4fa7.md` are a *different* sub-population and are not
explained by this finding — see §5.

---

## 4. A SECOND, ADDITIVE COMPONENT I DID NOT CLOSE

`71_invoice_space_aligned_no_rules` row 1 sits **+5.00** where rows 2-7 sit **+3.30**. The extra
**1.52 pt** is above the table, not in it: the gap from the last flow line to the table's top is
carried by an empty spacer paragraph

```xml
<w:spacing w:before="169" w:after="0" w:line="11" w:lineRule="exact"/>   <!-- 8.45 + 0.55 = 9.00 pt -->
```

and the declared table top is 9.00 pt below the previous paragraph's box while the page's table top
is 7.48 pt below it. The engine's `SPACER_SPEND_FRAC = 0.70` (`:58`) splits the gap 70 % into
`w:before` (1:1 in both renderers) and 30 % into `w:line` (Google charges 21.6 % of it — `:57`), so
this component is *renderer-dependent* and is the one place in the class where Google and
LibreOffice disagree by construction. It is worth **0.30 × gap × 0.784 ≈ 0.24 × gap** — 1-6 pt on
this corpus — and it is the same site as the recorded 27 Nov sub-class
(`HYPOTHESES.md:39-56`, `FINDINGS/18-displacement-RULED-ROW-PITCH-IS-GOOGLE-ONLY-27NOV-fixer.md`).
I measured its *existence* on `71` (+1.52 pt) and did not derive its full law; that is the one open
piece of this finding.

---

## 5. WHAT WOULD PROVE ME WRONG

One document, one rebuild, one measurement — and it is falsifiable in a single number.

**Test.** Take `35_four_typefaces_one_page`. In the table's cell paragraphs set
`w:before = 0` and `w:line = <the row's pitch, 380 tw>` with `w:lineRule="exact"`, leaving
`w:trHeight` at 380. Nothing else changes. Then `before + 0.8 × box = 0.8 × 19.00 = 15.20`, which is
*exactly* the quantity `:6662` subtracted to invent the row top — so `rowTop` and the cell's baseline
become inverses by construction.

    predicted by this finding : row-1 baseline moves 152.50 -> 148.80, dy = 0.00, 18_displacement PASS
    refuted if                : dy stays 3.70 (then :6662 is not the site and the offset is elsewhere)

A second, independent falsifier: **compute, for all 108 failing documents, `0.2 ×` the first cell's
`w:before` from `word/document.xml` and correlate it with the recorded Google `med_dy`/count.** This
finding predicts a positive correlation and, specifically, that every *rule-less*-table document
fails exactly when `0.2 × before > clamp(0.35 × size, 1.5, 4.5)` — i.e. when
`before > 5 × 0.35 × size = 1.75 × size`. On the two documents above: `18.40 / 9.0 = 2.04` (fails)
and `17.40 / 9.0 = 1.93` (fails); a table whose cell `before` is under `1.75 × size` should pass
`18_displacement` while still being displaced. If that ratio does not separate the 108 from the 98
that pass, the mechanism is real but not the class's root cause.

A third: **the rung predicts a ramp.** For every document failing 18 with ruled rows, the per-row
`dy` must step by −0.50 pt and the total by `0.50 × (rows − 1)`. On `table-with-no-header-row` that
is −12.0 over 25 rows and it measured −12.02. Any ruled-table document whose per-row step is not
0.50 pt falsifies the rung as its cause.

---

## 6. WHAT THE MECHANISM PREDICTS (other classes)

A root cause has to predict documents that have not been looked at. This one does:

1. **`18_displacement` splits into two disjoint sub-populations, and the split is already visible in
   the store.** Constant-offset documents (`med_dy` small, `worst_dy` ≈ 2-4, one page, count clause
   failing) are rule-less tables with a tall `before`. Ramp documents (`worst_dy` large, dy growing
   with page depth) are ruled tables. Predicts: the 49 that fail in both renderers are predominantly
   the rule-less/constant kind, and the 59 that fail only in Google are the ruled/spacer kind —
   because only the spacer component is renderer-dependent.
2. **`46_text_crossing_rule`.** The row top being 0.2 × before too low is the *same* quantity that
   puts a cell's text across the rule above it when `before` is small and the row is tight. The
   engine's own note at `:6601` records this trade ("take ten twips off and the rule the page drew
   moves up through the text"). Predicts: 46 and 18 are anti-correlated in `before` — a document
   fails one or the other, never neither, when a table's rows are pitch-bound.
3. **`23_line_pitch` and `07_table_rows`.** `w:trHeight` is written from `rowHeightTw`, which the
   rung and `rowLineTw` both modify (`:6598-6601`). Any document whose rows are pitch-bound carries
   a declared pitch 0.50 pt under the page's — which is what `23_line_pitch` measures directly and
   what `07_table_rows` sees as a row count that changes when a page overflows. Predicts: those two
   classes' open documents are a subset of the ruled-table population.
4. **`43_within_10pt_x` / `60_text_column_right_edge`** are *not* predicted by this mechanism — it is
   purely vertical, `med_dx` is −0.5…+0.5 on every document in the class. If a fix to this closes
   any horizontal check, this finding is wrong about the axis.
5. **`59_shape_anchor`.** Independent corroboration that the class is arithmetic and not rendering:
   my HEAD render of `35_four_typefaces_one_page` scores **40/42 in LibreOffice** (`18_displacement`
   *and* `59_shape_anchor`), where the store's row for engine `d28ca7516c3f9165` is **42/42**. Two
   engine commits sit between them (`8fb4f503` the rung, `33863086` the single-line cell), so the
   `cellPlaced` branch at `:6912-6924` is now firing where the self-consistent fallback at
   `:6936-6941` used to — the regression and the root cause are the same lines.

---

## 7. NOT MEASURED, AND WHY

- **No Google render was regenerated.** `benchmarks/gverify/` holds 214 summary JSONs and
  `gverify/gd` is empty; the Google side of every number above is the *recorded* `med_dy/worst_dy`
  for engine `a05b20eb05fe0fc8`, not a render I made. The `+3.70` and `+3.30` are LibreOffice, and
  the claim that they are the same displacement Google charges rests on (i) 49 of the 108 failing in
  both renderers and (ii) the mechanism living in the declaration, which both renderers read.
- **The spacer law (§4) is measured on one document only** (+1.52 pt on `71` row 1). Its dependence
  on the gap and on `SPACER_SPEND_FRAC` is derived from the file's own comments (`:57-58`), not
  measured across a range.
- **The `0.2 × before` correlation was not run over the corpus.** §5 gives it as the falsifier rather
  than as a result, because converting and rendering 108 documents did not fit this slot.
