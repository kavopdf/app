# `59_shape_anchor` — root cause, and a patch spec that survives measurement

**Investigation date:** 26 Nov 2026 · **tree:** `kavopdf/app` @ `678248e` (shallow clone) · **engine fingerprint:** `d85db0a9822ddb54` (= `regress.engine_fingerprint()` on HEAD, i.e. the engine the current store was partly measured on) · **corpus:** the real 213-document corpus, fetched with `tools/p2w-bench/corpus-fetch.sh` ("corpus: 213 PDFs, 212 scored in RANKING.csv, 0 missing").

Read-only on the repo: nothing under `/scratch/work/CS` was modified, nothing was committed or pushed. The one code change in this document was made in a **copy** of the tree at `/scratch/work/CS2`, built and measured there.

---

## 0. Verdict in one page

1. **The check is not measuring the shape anchor.** It measures *where the text sits inside a box*, in points, on the **Google Docs export of the .docx** — not on the source PDF, not on a LibreOffice render, and not on the .docx itself.
2. **The engine's shape geometry is not the defect on most of the failing documents.** On 4 of the documents I converted, the `.docx` reproduces the source PDF's drawings essentially exactly (95/95, 12/12, 11/11, 41/43 anchored drawings within 0.75 pt; 0 uncovered source drawings on two of them). A patch to the shape-anchor writer therefore cannot move those documents.
3. **Where 59 is charged, it is charged vertically, never horizontally.** Across the 12 failing documents that carry a stored `displacement` record, `med_dx` is between −0.6 and +0.2 pt while `med_dy` runs from −15.2 to +6.1 pt. That is `18_displacement`'s question asked in a second frame, with a much smaller denominator (`5 %` of *judged* runs, not `5 %` of *all page runs*).
4. **One genuine writer defect was found and fixed-and-measured**: on `04_stamp_180deg_upside_down` the anchored text box declares an extent 9.34 pt taller than the path it draws, and the source's outline is the shorter one. The patch is in `DocxWriter.stampBox`; it changes exactly 1 of 8 documents' geometry and leaves all 8 LibreOffice verdicts identical.
5. **The obvious "fix the line construct" patch is measured and rejected.** `-Dp2w.lineRule=auto` (already in the engine) breaks **10 of 10** documents under the LibreOffice gate, including 4 that pass today. It is not inert and must not ship.
6. **Predicted CLEAN documents flipped by any shape-anchor-only patch: 0.** No document in the 211 scored records has 59 as its sole failure, so clearing it alone cannot make a document clean. The "~15 CLEAN documents" figure is real but is a *leverage* number (sum of `1/len(failed)`) computed over a store that mixes two engines; at HEAD it is **4.38**.

---

## 1. What the check actually measures

### 1.1 The reference is Google's export, not LibreOffice and not the .docx

`tools/p2w-bench/verify_google.py:3` and `:19`:

```
verify_google.py - compare a Google-Docs-rendered PDF against the source PDF.
...
  python3 verify_google.py <source.pdf> <google-export.pdf> [--docx <engine.docx>] [--json out.json]
```

The two PDFs are opened at `verify_google.py:4717-4718` (`src = fitz.open(src_path)`, `gd = fitz.open(gd_path)`). The .docx is used by three checks only (`54_image_dpi`, `53_embedded_faces`, `37_super_subscript`); **59 reads only the two PDFs.** So the object under judgement is:

* **source side** — the corpus PDF, via `_shapes(src_page)` (`verify_google.py:640`);
* **render side** — the PDF that Google Drive produced by exporting a Google Doc created from the engine's .docx, via `_shapes(gd_page)`;
* and the .docx itself is the *cause* of the difference, never the thing measured.

`_shapes()` (`verify_google.py:640-702`) builds the anchor set from three sources: any `page.get_drawings()` rect with `width >= 8 and height >= 8`; **thin rules re-assembled into a face** (a horizontal pair with a vertical rule standing at each end, `:682-700`); and placed images (`page.get_image_rects`). That assembly step is why a table drawn as a rule grid on one side and as a filled cell on the other can still be compared — and it is also where two producers can disagree about which boxes exist.

### 1.2 The three constants and the three verdicts

`verify_google.py:2329-2333`:

```python
ANCHOR_TOL_PT = 3.0        # points, not a fraction of whatever box encloses the run
ANCHOR_RECT_TOL = 2.0      # pt; the two boxes are the same object within this
ANCHOR_BUDGET = 5          # per cent of the page's judged runs, as 18 uses
ANCHOR_WIDTH_TOL = 1.5     # pt; the render reproduced the run's own ink width
lost, moved, unjudged, anchored = 0, 0, 0, 0
```

The branches, from the check's own header (`:2322-2328`):

```
  lost      the text is in the render and NO shape encloses it - the outline went
  unjudged  the render's enclosing box is a different object; the fraction would
            be measured against the wrong rectangle, so it is not compared
  moved     the SAME box on both sides, and the text sits > ANCHOR_TOL_PT off it
  A page fails on the same budget 18_displacement uses, not on one stray run.
```

The measurement itself, `verify_google.py:2519-2530`:

```python
gxl = min(gruns[j]["xink"] for j in js)
dx = (gxl - gb.x0) - (sruns[i]["xink"] - sb.x0)
dy = (gy - gb.y0) - (sy - sb.y0)
...
if abs(dx) <= ANCHOR_TOL_PT and abs(dy) <= ANCHOR_TOL_PT:
    anchored += 1
```

So: for every source run, find the smallest shape in `_shapes(source)` whose interior contains the run's centre (`_smallest_holding`, `:731`), find the render run with the same text (`_match`, `:2336`), find the render's smallest shape containing it, and compare **the run's offset from the box's top-left corner on each side**. Agreement within 3.0 pt is `anchored`. Disagreement is a conviction only where `_same_box` holds — four corners within 2.0 pt (`:2367-2369`) — otherwise the run is `unjudged`, unless the text has not moved on the page while a box of the source's size exists somewhere (`_box_moved`, `:2426`), which scores `moved` with `hard_out` set.

The page fails on `verify_google.py:2576-2578`:

```python
if n_judged and (n_out > max(2, -(-n_judged * ANCHOR_BUDGET // 100))
                 or n_out == n_judged or hard_out):
    anchor_bad_pages.append(si)
```

and the document's row is `:2585`:

```python
c["59_shape_anchor"] = (anchored + lost + moved + unjudged, anchored, not anchor_bad_pages)
```

Note the two properties that matter for everything below:

* **`hard_out` is a tripwire, not a budget.** One run in the `_box_moved` branch fails the page regardless of `n_judged`.
* **The denominator is the runs the check could judge**, not the page's runs. `18_displacement` uses the same 5 % but divides by *every* run on the page (`verify_google.py:5864`, tolerance `min(max(0.35 * size, 1.5), 4.5)`; `:5893` `n_out > max(2, -(-len(ds) * 5 // 100))`). On a page with 900 runs, 6 runs out is 0.7 %; on the 12-60 runs 59 can judge, 6 runs out is 10-50 %.

---

## 2. The failing documents — count, names, derivation

### 2.1 Derivation

`benchmarks/gverify/` holds one JSON per document: `{name, engine, passed, total, failed[], displacement{...}, status}`. `classpick.clean_leverage()` (`tools/p2w-bench/classpick.py:224-270`) scores each check `1.0 / len(failed)` per document — that is the "worth ~N CLEAN documents" number. Running it on this tree:

```
18_displacement              54.74
60_text_column_right_edge    22.90
59_shape_anchor              14.98      <-- the "~15 CLEAN documents"
04_chars_missing             11.69
```

**The store mixes two engines, and that is the first correction this investigation makes.** 213 files, of which 211 carry a `failed` list and 2 are `page_count_refused`:

| engine | records | note |
|---|---:|---|
| `981ff1fa35e2cf67` | 153 | superseded (98 carry no `status`, an older record format) |
| `d85db0a9822ddb54` | 60 | **= HEAD's `regress.engine_fingerprint()`** |

| slice | documents failing 59 | 59 leverage |
|---|---:|---:|
| whole store (what `classpick` reads) | **50** | **14.98** |
| HEAD engine only | **17** | **4.38** |

Both numbers are true of what they measure; only the second is a statement about the code that exists today.

### 2.2 The 17 documents failing 59 on the HEAD engine

| document | checks failed | also fails 18? |
|---|---|---:|
| `01_stamp_rotated_15deg_upright` | 5 | yes |
| `02_stamp_rotated_15deg_upleft` | 5 | yes |
| `03_stamp_vertical_90deg` | 7 | yes |
| `04_stamp_180deg_upside_down` | 5 | yes |
| `09_stamp_font_not_embedded` | 4 | no |
| `13_stamp_non_english` | 7 | yes |
| `15_stamp_on_scanned_page` | 9 | no |
| `23_timetable_grid_txtpos` | 2 | yes |
| `28_value_overflows_cell_txtpos` | 4 | no |
| `300_prescription_rx` | 2 | yes |
| `306_clinical_protocol_synopsis` | 2 | yes |
| `30_mixed_font_sizes_one_baseline_txtpos` | 2 | yes |
| `314_tender_rfp_boq` | 5 | yes |
| `318_court_summons_form` | 8 | no |
| `322_mutual_fund_factsheet` | 9 | yes |
| `324_loan_amortisation_schedule` | 3 | yes |
| `331_pid_diagram` | 9 | no |

* **12 of 17 also fail `18_displacement`.** On those, 59 is asking 18's question in a second frame.
* **5 fail 59 without failing 18** (`09`, `15`, `28`, `318`, `331`) — these are the only documents where 59 could carry an independent charge.
* **0 documents have 59 as their only failure.** Four have exactly `{18_displacement, 59_shape_anchor}`: `23_timetable_grid_txtpos`, `300_prescription_rx`, `306_clinical_protocol_synopsis`, `30_mixed_font_sizes_one_baseline_txtpos`.
* Therefore: **clearing 59 alone flips 0 documents to CLEAN. Clearing 18 + 59 flips 4.**

---

## 3. What is *not* the construct — measured, not argued

I converted the documents with the HEAD engine (`ConvertOne`, from `tools/engine-verify/`), unzipped `word/document.xml`, parsed every `wp:anchor` into `(posOffset x, posOffset y, extent cx, extent cy)` in points, and matched each against the source PDF's `page.get_drawings()` rects at 0.75 pt on all four edges.

| document | source drawings | `_shapes` (all pages) | docx `wp:anchor` | anchored drawings reproduced within 0.75 pt | source drawings with no counterpart |
|---|---:|---:|---:|---:|---:|
| `306_clinical_protocol_synopsis` | 95 | 21 | 95 | **95 / 95** | **0** |
| `30_mixed_font_sizes_one_baseline_txtpos` | 12 | 2 | 12 | **12 / 12** | **0** |
| `28_value_overflows_cell_txtpos` | 11 | 2 | 11 | **11 / 11** | **0** |
| `23_timetable_grid_txtpos` | 26 | 9 | 11 | 11 / 11 | 15 (rule grid → one frame + cell fills) |
| `300_prescription_rx` | 229 | 14 | 43 | 41 / 43 | 191 (signature strokes merged into 2 bounding shapes) |
| `318_court_summons_form` | 20 | 7 | 51 | 20 / 51 | 0 (31 extra: one box per glyph of curved text) |
| `324_loan_amortisation_schedule` | — | 253 | **1483** | — | — |

**Every drawing in every file is the same construct**, without exception:

```xml
<w:drawing><wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0"
  relativeHeight="100034468" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">
  <wp:simplePos x="0" y="0"/>
  <wp:positionH relativeFrom="page"><wp:posOffset>353060</wp:posOffset></wp:positionH>
  <wp:positionV relativeFrom="page"><wp:posOffset>797560</wp:posOffset></wp:positionV>
  <wp:extent cx="9985880" cy="220980"/>
  <wp:effectExtent l="0" t="0" r="0" b="0"/>
  <wp:wrapNone/>
  <wp:docPr id="100004" name="Shape 100004"/>
  ...
```

(from `306_clinical_protocol_synopsis.docx`, the row band `27.80, 62.80, 786.29 × 17.40` pt, against the source face `28.00, 63.00, 785.89 × 17.00`). Emitted by `DocxWriter.shapeRun` (`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:3015-3040`). All shapes on a page are collected into **one** carrier paragraph (`flushShapes`, `:2993-2996`) precisely because Google charges flow for the paragraph each shape is written in — the comment at `:2975-2981` records that measurement (`FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md`).

**Conclusion.** `positionH/V relativeFrom="page"` + `wrapNone` + `behindDoc="1"` is a construct that reproduces the source geometry to sub-0.75 pt in the .docx and that LibreOffice renders back to 47/47 PASS on the four `{18,59}` documents. A patch to this construct cannot change 306, 30_mixed or 28, because on those documents the construct is already producing the source's own rectangles.

---

## 4. The construct that is wrong — three documents

### 4.1 `04_stamp_180deg_upside_down` — the anchored box declares an extent 9.34 pt taller than the path it draws

**Source PDF, page 1** (`page.get_drawings()`, the stamp):

```
[300.0, 386.4, 481.79, 450.0]   w=181.79 h=63.60  fill=None stroke=(0.45,0.03,0.10) type=s n_items=1
[303.0, 389.4, 478.79, 447.0]   w=175.79 h=57.60  fill=None stroke=(0.45,0.03,0.10) type=s n_items=1
```

**Emitted .docx** — one anchored text box carrying both rules as two closed sub-paths:

```xml
<wp:anchor ... behindDoc="1" ...>
  <wp:positionH relativeFrom="page"><wp:posOffset>3810000</wp:posOffset></wp:positionH>
  <wp:positionV relativeFrom="page"><wp:posOffset>4907280</wp:posOffset></wp:positionV>
  <wp:extent cx="2308752" cy="926338"/>            <!-- 181.79 x 72.94 pt -->
  <wp:wrapNone/>
  <wp:docPr id="1" name="KavoPDF text 1"/>
  <a:graphic><a:graphicData uri="...wordprocessingShape"><wps:wsp>
    <wps:cNvSpPr txBox="1"/><wps:spPr>
      <a:xfrm><a:off x="0" y="0"/><a:ext cx="2308752" cy="926338"/></a:xfrm>
      <a:custGeom><a:pathLst><a:path w="2308752" h="926338">
        <a:moveTo><a:pt x="2308752" y="0"/></a:moveTo>
        <a:lnTo><a:pt x="0" y="0"/></a:lnTo>
        <a:lnTo><a:pt x="0" y="807720"/></a:lnTo>       <!-- 63.60 pt, not 72.94 -->
        <a:lnTo><a:pt x="2308752" y="807720"/></a:lnTo>
        <a:close/>
        <a:moveTo><a:pt x="2270652" y="38100"/></a:moveTo> ... <a:close/>
```

Measured off the XML: the path's own points span **x 0..2308752, y 0..807720 = 181.79 × 63.60 pt**, which is the source's outer rect to the twip. The declared frame is **`cy="926338"` = 72.94 pt**. **The box is 9.34 pt taller than the outline it draws**, and the box is the thing `_same_box` compares (2.0 pt) and the thing `_box_moved` measures the size of.

Why: `DocxWriter.stampBox` (`DocxWriter.java:5360-5534`) sets the box from the **union of the text lines' boxes and the frame** — `:5475` `float bw = ux1 - ux0, bh = uy1 - uy0;` after `:5466-5474` extends `uy1` to `max(ly[i] + lpt[i])`. On a 180° document the stamp's lines come back mirrored (`stampBox`'s `mirrored(b)` branch, `:5385-5388`, rewrites `py = ctx.pageHeightPt - b.y`), and one line's box then reaches 9.34 pt below the drawn rule. The frame — the object the page actually drew — is the shorter one.

This is the **only** document of the eight I converted where the declared box differs from the path; on `01`, `05`, `06`, `08`, `09` the path bbox and `wp:extent` agree exactly (e.g. `01`: path bbox 205.95 × 104.68 = extent 2615570 × 1329377 EMU).

Note the second-order charge on this document: the box's text lives in `wps:txbx` inside a `behindDoc="1"` anchor, and `DocxWriter.java:405-412` records the measured consequence —

```
Google Docs does not read the text of a floating drawing. A wps:txbx inside a
wp:anchor with behindDoc comes back from Drive as pixels with no text layer,
so every character in it is missing from the export, while LibreOffice keeps all of them.
```

`04` fails `04_chars_missing` as well as 59 for exactly this reason. Fixing the extent does not put the text back.

### 4.2 `306_clinical_protocol_synopsis` — nothing wrong with the box; the text is 6.1 pt low

**Source `_shapes` (first six of 21), page 1:**

```
  0.00   0.00 841.89  34.00   (841.89 x 34.00)     page band
 28.00  46.00 813.89  63.00   (785.89 x 17.00)     row band
 28.00  63.00 813.89  80.00   (785.89 x 17.00)
 28.00  80.00 813.89  97.00   (785.89 x 17.00)
 28.00  97.00 813.89 114.00   (785.89 x 17.00)
 28.00 114.00 813.89 131.00   (785.89 x 17.00)
```

**Emitted .docx:** 95 anchored drawings, **all 95 reproduced within 0.75 pt, 0 source drawings uncovered** (table in §3). The anchor quoted at the top of §3 is row band #1.

**Stored Google measurement** (`benchmarks/gverify/306_clinical_protocol_synopsis.json`):

```
displacement: med_dy 6.1, worst_dy 88.0, med_dx 0.2, bad_pages [0], runs_matched 75
```

Horizontal is exact (`med_dx = +0.2 pt`); vertical is 6.1 pt at the median and 88 pt at worst. The text is not where the source put it **inside boxes that are in the right place**. The construct that carries every line's vertical position is not the shape at all — it is the paragraph's own spacing, e.g. `306`'s first three paragraphs:

```xml
<w:spacing ... w:before="0"   w:after="0" w:line="13" w:lineRule="exact"/>   <!-- Heading1 -->
<w:spacing ... w:before="209" w:after="0" w:line="10" w:lineRule="exact"/>
<w:spacing ... w:before="377" w:after="0" w:line="1"  w:lineRule="exact"/>   <!-- shape carrier -->
```

`w:line` + `w:lineRule="exact"`, emitted by `DocxWriter.spacing()` (`DocxWriter.java:148-172`). The engine's own javadoc for the alternative mode states the mechanism and names it (`DocxWriter.java:104-113`):

```
 *   <li>{@code w:line = 1.38*size} + {@code lineRule="exact"} - the hairline above. Word and
 *       LibreOffice honour it exactly; Google Docs does not implement "exact" and reads
 *       {@code w:line} as 240ths of the face's line height, so it charges
 *       {@code (1.38*size/240) * r * size} - quadratic in the type size.</li>
```

A flow whose every line is priced by a different rule drifts cumulatively: `+6.1` pt median with a `+88` pt tail is the shape of that, not of a per-run scatter. **So on 306 the 59 conviction is `18_displacement`'s subject** — text displaced inside a correctly reproduced outline. 306 fails both.

### 4.3 `28_value_overflows_cell_txtpos` — the .docx is exact, the text is within 2.3 pt, and 59 still fails

**Source drawings 11, docx anchors 11, 11/11 reproduced within 0.75 pt, 0 uncovered.** Stored measurement:

```
displacement: med_dy 1.6, worst_dy 2.3, med_dx -0.1, bad_pages [], runs_matched 45
```

`worst_dy = 2.3` is the **maximum absolute vertical baseline error over all 45 matched runs** (`verify_google.py:5794`, computed from every matched pair at `:5782-5785`). So no run on this page is more than 2.3 pt from its source baseline — under `ANCHOR_TOL_PT = 3.0`, and well under 18's own tolerance for its text sizes. And the .docx carries the source's boxes exactly.

Nothing on this page moved, in either document the engine produced. 59 nevertheless fails it. The only exits left in the check are the ones that do not read a distance at all:

* `lost` (`:2485`) — the run's text is in the render but no shape encloses it;
* the `_box_moved` branch (`:2557-2566`) — `dtx`/`dty` within 3.0 pt **and** a shape of the source box's size exists somewhere on the render, which scores `moved` with **`hard_out = 1`** and fails the page on one run;
* `unjudged` counted into the source total (`:2585`).

`_box_moved` (`:2426-2445`) is a size-and-count test with **no position term** — its own docstring says so, and it returns True for a box that never moved:

```python
def _box_moved(a, gshapes, sshapes):
    if _class_count(a, gshapes) == 0:
        return False
    return _class_count(a, gshapes) >= _class_count(a, sshapes)
```

On a Google export, a table the .docx draws as anchored cell rectangles comes back as Google's own rule grid; `_shapes` then assembles different faces, `_same_box` is False, the text is where it was, and a box of the source's size still exists → `moved`, `hard_out`, page fails. **This is a check-side charge, not an engine defect.** It is the same hole `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md:466-508` named ("`_box_moved` has no position term … returns True, i.e. 'the outline moved' is reported with the outline unmoved"), and `_same_object`/`_face`/`_held` (`:2373`, `:2389`, `:2404`), written to close it, are **defined and never called** — I confirmed that at HEAD: the only references in the whole file are the three definitions and `_face`/`_held` inside `_same_object`'s own body (`:2416`, `:2418`).

### 4.4 Supporting cases (same three channels, no new one)

* **`09_stamp_font_not_embedded`** — 59 fails, 18 passes (`worst_dy 3.4`, `med_dy 1.1`). Both concentric stamp rules are present in the .docx as two sub-paths of one `a:custGeom` (`path bbox 115.03 × 82.43 = extent`, exactly the source's outer rect), so the outline did not go. With a 3.4 pt worst case against a 3.0 pt tolerance and ~21 matched runs, this is the small-denominator arithmetic: a handful of runs over 3 pt is >5 % of what 59 can judge and <1 % of the page.
* **`23_timetable_grid_txtpos`** — 59 and 18. The .docx keeps 11 of 26 source drawings and replaces the 7 row rules + 9 vertical rules with **one frame rect + 8 cell fills**. That is a genuine change of primitive on the *source* side's assembled faces, and 18 also reports `med_dy −15.2` on it — so both candidates are live here and this document cannot discriminate between them without a Google render.
* **`300_prescription_rx`** — 59 and 18, `med_dy −9.2`, `med_dx −0.1`. 191 of 229 source drawings (signature strokes) are replaced by two bounding shapes (52 × 52 and 130 × 44 pt), i.e. the primitive population changes again.
* **`318_court_summons_form`** — 59 fails, 18 passes (`worst_dy 2.5`). 51 anchors against 20 source drawings: the engine emits **one 7-10 pt box per glyph** for curved text, which `_shapes` will pick up as many small boxes the source does not have. `331_pid_diagram` shows the same signature at the limit: `runs_matched = 1`.
* **`324_loan_amortisation_schedule`** — 1483 anchors against 253 source shapes on 7 pages: one floating drawing per rule.

---

## 5. Patch spec

### P1 — RECOMMENDED. `DocxWriter.stampBox`: declare the box the path draws, not the text frame's union.

**File / function:** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, `stampBox(...)`, line **5475** (`float bw = ux1 - ux0, bh = uy1 - uy0;`), consumed at `:5502-5534` (`local`, `geomXml`, `anchorShape(sb, ctx, bx0, by0, 0f, 0f, bw, bh, ...)`).

**Change:** after `cmds` is built (`:5502-5512`), clamp `bw`/`bh` to the bounding box of the points actually in the path:

```java
float px0 = 0f, py0 = 0f, px1 = -1f, py1 = -1f;
for (float[] c : cmds) {
    if ((int) c[0] == 3) continue;              // 3 == close
    if (px1 < 0f) { px0 = px1 = c[1]; py0 = py1 = c[2]; }
    px0 = Math.min(px0, c[1]); px1 = Math.max(px1, c[1]);
    py0 = Math.min(py0, c[2]); py1 = Math.max(py1, c[2]);
}
if (px1 > px0 && py1 > py0) { bw = Math.min(bw, px1); bh = Math.min(bh, py1); }
```

The box origin (`bx0`, `by0`) and every text line's local coordinate are untouched — only the bottom/right edge moves, and only inwards, so no line's `w:before`/`w:ind` changes. `bodyPr` is `wrap="none"` with `<a:noAutofit/>` (`:5807-5812`), so a line that now reaches past the box spills instead of being clipped or re-wrapped.

**Why this is the right shape of fix for 59:** the check compares `_same_box` (four corners, 2.0 pt) and `_class_count` (width and height, 2.0 pt) of *the box the render draws*. A box declared 9.34 pt taller than its own outline is a different rectangle from the source's at every tolerance in the check, and it is the one place in this investigation where the engine, not the check, produced the wrong number.

### P2 — REJECTED, MEASURED. Do not default `p2w.lineRule=auto`.

The obvious patch for the vertical half of 59 is to ship the `auto` construct the engine already has (`DocxWriter.java:113-131`, `spacing()` `:149-172`). It is not inert. Measured below.

### P3 — out of scope of the engine, but it is where 4 of the 17 documents actually live.

`_box_moved` needs a position term (or `_same_object` needs to be called). That is an instrument change in `tools/p2w-bench/verify_google.py`, not a writer change, and it should not be bundled into an engine patch: the repo's own gate compares against LibreOffice, which cannot see it either.

---

## 6. Is P1 inert on the documents that pass today? — evidence

**Method.** Full copy of the tree at `/scratch/work/CS2`, the four-line clamp above applied to `DocxWriter.java` only, `javac` into the existing `out/`; then `ConvertOne` with the HEAD build and with the patched build on 8 documents — 5 stamp documents (4 failing 59, plus `05`, `06`, `08` as controls), `23` and `306`; LibreOffice render of both sets; `verify_google.py <source> <lo render> --docx <docx>` on both.

**Result — the geometry changes on exactly one document:**

| document | HEAD text box (x, y, w, h) | patched | source outline |
|---|---|---|---|
| `04_stamp_180deg_upside_down` | 300.00, 386.40, 181.79 × **72.94** | 300.00, 386.40, 181.79 × **63.60** | `[300.0, 386.4, 481.79, 450.0]` = 181.79 × 63.60 |
| `01_stamp_rotated_15deg_upright` | 164.24, 436.06, 205.95 × 104.68 | unchanged | path bbox identical |
| `05_round_company_seal_curved_text` | 63 boxes, e.g. 181.83, 586.51, 8.03 × 8.05 | unchanged | — |
| `06_rect_paid_stamp_red_transparent` | 133.97, 334.84, 147.62 × 114.13 | unchanged | — |
| `08_two_overlapping_stamps` | 3 boxes, all as HEAD | unchanged | — |
| `09_stamp_font_not_embedded` | 164.90, 426.98, 115.03 × 82.43 | unchanged | — |
| `23`, `306` | no text boxes at all | unchanged | — |

**Result — the LibreOffice verdicts are identical, document for document:**

| document | HEAD | patched |
|---|---|---|
| `01_stamp_rotated_15deg_upright` | 41/42, fails `35_rotation` | 41/42, fails `35_rotation` |
| `04_stamp_180deg_upside_down` | 41/42, fails `35_rotation` | 41/42, fails `35_rotation` |
| `05_round_company_seal_curved_text` | 42/42 PASS | 42/42 PASS |
| `06_rect_paid_stamp_red_transparent` | 41/42, fails `35_rotation` | 41/42, fails `35_rotation` |
| `08_two_overlapping_stamps` | 41/42, fails `35_rotation` | 41/42, fails `35_rotation` |
| `09_stamp_font_not_embedded` | 41/42, fails `35_rotation` | 41/42, fails `35_rotation` |
| `23_timetable_grid_txtpos` | 47/47 PASS | 47/47 PASS |
| `306_clinical_protocol_synopsis` | 47/47 PASS | 47/47 PASS |

8 of 8 identical, including the one whose XML changed. **No regression under the gate the repo actually runs, and no gain** — which is what "inert on the LibreOffice proxy" means, and it is the only inertness this environment can establish. (It also shows the stamp documents fail `35_rotation` under LibreOffice as well, so the rotated-CTM drop is visible on both renderers.)

---

## 7. Is P2 inert? — measured, and it is not

Same method, `-Dp2w.lineRule=auto` on 10 documents (6 failing 59, 4 passing controls), LibreOffice render, full 42/47 checks:

| document | HEAD (`exact`, LO) | `auto` (LO) |
|---|---|---|
| `23_timetable_grid_txtpos` | **47/47 PASS** | 45/47 — `18_displacement` render=1, `59_shape_anchor` 56→0 |
| `300_prescription_rx` | **47/47 PASS** | 45/47 — `18_displacement`, `59` 39→10 |
| `303_discharge_summary` (control) | **47/47 PASS** | 45/47 — `18_displacement`, `59` 22→20 |
| `306_clinical_protocol_synopsis` | **47/47 PASS** | 45/47 — `18_displacement`, `59` 74→70 |
| `30_mixed_font_sizes_one_baseline_txtpos` | **42/42 PASS** | 39/42 — `18_displacement`, `59` 12→0 |
| `314_tender_rfp_boq` | 46/47 (`63_table_rows`) | 44/47 — `18_displacement`, `59` 68→64 |
| `320_balance_sheet_statutory` (control) | **47/47 PASS** | 46/47 — `18_displacement` |
| `351_omr_answer_sheet` (control) | **42/42 PASS** | 40/42 — `18_displacement`, `59` 66→0 |
| `48_form_coloured_border_coloured_values` (control) | **42/42 PASS** | 40/42 — `18_displacement`, `59` 24→0 |
| `52_one_cm_margin_wide_body` (control) | **42/42 PASS** | 40/42 — `18_displacement`, `59` 18→0 |

**10 of 10 break, 4 of them documents that pass today.** Every one gains `18_displacement` with `render = 1` (the whole page is judged displaced) and 59's `render` collapses toward 0. Whatever the `auto` transform does to the advance, it does not preserve it across a page under LibreOffice, so it cannot be shipped as a Google fix — and shipping it would take the corpus down, not up.

---

## 8. Predicted document count flipped

| patch | documents whose verdict can move | predicted CLEAN flips | basis |
|---|---|---|---|
| **P1** (box = path bbox) | 1 of the 8 measured (`04`); among the 17 failing-59 documents, 1 (`04`) | **0** | measured: 04 still fails `04_chars_missing`, `13_text_colours`, `18_displacement`, `35_rotation` |
| **P2** (`lineRule=auto`) | all 10 measured | **negative** | measured: 10/10 break, 4 of them from PASS |
| 18 + 59 together (for context) | 4 | **4** | `23`, `300`, `306`, `30_mixed` fail exactly `{18_displacement, 59_shape_anchor}` |
| 59 alone, any patch | 17 | **0** | no document has 59 as its sole failure |

**The honest headline: `59_shape_anchor` is worth 14.98 clean documents as a leverage number and 0 clean documents as a patch target.** It is a second reading of `18_displacement`'s displacement on 12 of its 17 HEAD documents, a reading of `04_chars_missing`'s dropped text box on the stamp documents, and a check-side artefact (`_box_moved`, `hard_out`) on at least `28`. The engine work that moves 59 is the work that moves 18 and 04.

---

## 9. What I could not measure, and exactly what I would measure

**Not determinable in this environment: the Google side of any of these documents.** The Google loop needs a local file staged into an S3 key (`GOOGLEDRIVE_CREATE_FILE` → `file_to_upload.s3key`), and the platform `upload` tool that produces that key is not bound in this sandbox. I confirmed this empirically: passing a `/scratch/work/...` path as `s3key` returns `403 … The file key does not belong to this project or session`. So every Google number in this document is either (a) the committed record in `benchmarks/gverify/*.json`, dated 25 Nov 2026, or (b) derived from the .docx and the source PDF, both of which I measured myself. `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md` records the same wall for three earlier investigations.

Consequences, stated plainly:

* I can prove the **box** on `04` was 9.34 pt wrong and that the patch corrects it to the source's own 63.60 pt.
* I **cannot** claim the patch clears 59 on `04`; `04`'s text is inside a `behindDoc` text box that Google rasterises without a text layer, so the runs will land in `lost` regardless. **Predicted: no change to 04's 59 verdict.**
* I **cannot** attribute `23`'s and `300`'s 59 charge between "text displaced" and "primitive population changed". Both are present and both are measurable in the .docx; only a render separates them.

**The three commands that would settle it** (one Google round trip per document, ~1 minute each, nothing left in Drive):

```
# for each of 23, 300, 306, 30_mixed, 04, 28, 09, 318, 331:
upload the .docx -> create Google Doc -> export PDF -> delete the Doc
python3 tools/p2w-bench/verify_google.py /scratch/work/p2w/corpus/<doc>.pdf <google-export>.pdf \
        --docx /scratch/work/p2w/out/<doc>.docx --json /scratch/work/<doc>.json
```

and, for the branch each conviction took, a **copy** of the instrument with one `print` added at `verify_google.py:2528` (the `anchored` exit), `:2485` (`lost`), `:2561` (`moved` via `_box_moved`) and `:2507`/`:2566` (`unjudged`), reporting per run: text, `dx`, `dy`, `sb`, `gb`, and which exit fired. That is the single measurement that turns §4.2 and §4.3 from "the only exits left" into "this exit, this many runs". The prior run that instrumented the same way (`FINDINGS/59_shape_anchor-IS-RIGHT-THE-THREE-SOLO-DOCS-ARE-3PT-LOW-0150-relay.md`) found every conviction on its three documents took the **same-box** branch with `dx ≈ 0.6–1.0` and `dy ≈ 3.2–3.9` — i.e. vertical, which is what the stored `med_dx`/`med_dy` in this store say independently.

**Also worth measuring before shipping P1:** the two `324`-class documents (1483 and 2966 anchored drawings on 7 pages). `_shapes` on the render side will see one shape per rule; whether Google keeps all of them is unknown, and that is the population `_class_count` compares.

---

## 10. Reproduction

```bash
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
bash tools/p2w-bench/corpus-fetch.sh          # 213 PDFs -> /scratch/work/p2w/corpus
bash tools/p2w-bench/build-engine.sh          # javac + PDFBox-android; 36 s

# convert (from tools/engine-verify, so the AFM assets resolve)
java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne /scratch/work/p2w/corpus/306_clinical_protocol_synopsis.pdf /scratch/work/conv

# shape geometry: docx anchors vs source drawings
python3 - <<'EOF'   # full script used for §3 is /scratch/work/cmp2.py
...
EOF

# the LibreOffice arm of every measurement above
soffice --headless --convert-to pdf --outdir lo conv/*.docx
python3 tools/p2w-bench/verify_google.py <source.pdf> lo/<doc>.pdf --docx conv/<doc>.docx
```

The census in §2 was computed from `benchmarks/gverify/*.json` with `classpick.clean_leverage()` for the leverage column and with a group-by on the `engine` field for the HEAD/legacy split.

---

## Open questions

1. **Which exit fires on each conviction** — `anchored`-adjacent `dx/dy`, `lost`, `_box_moved`/`hard_out`, or `unjudged` — per document. Requires one Google export per document (blocked: no `upload` tool in this sandbox).
2. **Whether `04`'s 59 charge survives P1.** My prediction is that it does not change, because the text in that box has no text layer in Google's export; but that is an inference from `DocxWriter.java:405-412`, not a measurement.
3. **Whether Google preserves all 1483/2966 anchored drawings on `324`-class documents**, which decides whether `_class_count` is comparing like populations there.
4. **What Google's single-line ratio `r` actually is** for the faces it substitutes — the one number that would let the `auto` construct be written correctly instead of with `AUTO_LINE_EM = 1.15` (`DocxWriter.java:141-142`). P2 was rejected in its current form; the construct is not rejected in principle.
