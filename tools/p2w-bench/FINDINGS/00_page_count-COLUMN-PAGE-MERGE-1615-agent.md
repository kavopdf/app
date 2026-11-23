# 00_page_count / drawing-only paragraph — merge proposal, verified against the tree

**Tree read:** `kavopdf/app` @ `1ba51d99bfe23e66822bc09e9fe920b787084699` ("claim: fixer takes the slot",
23 Nov 2026 09:45 UTC), cloned read-only into `/scratch/work/CS` (that path did not exist in this sandbox;
`gh repo list kavopdf` found the repo and it was cloned there). **Deliverables:** this file +
`agent-a-merge-paragraphs.patch`. **Nothing in the repo was edited, applied, committed or pushed.**

## 0. Headline: the lever in the handoff is already landed at HEAD

The brief asks for a patch that merges a page's drawing-only paragraphs into one, "in
`DocxWriter.shape()`, reported at around line 2726". At HEAD:

* `shape()` is at **line 2893**, not 2726 — the handoff's line number predates the commits it describes.
* **`pageBody()` already does the merge** (lines 1354–1412): a `Shape` block in the page loop is written
  as a bare run into the last paragraph on the page, and shapes with no paragraph to join are collected
  into **one** carrier paragraph per page. `shapeRun()` (2914) is the run writer; `SHAPE_PARA_PPR`
  (2887) is the pPr both spellings use.
* The repo's own record says so twice, and both are in the tree:
  `tools/p2w-bench/FINDINGS/00_page_count-SHAPE-RUNS-NOT-PARAGRAPHS-LANDED-0730-fixer.md` (measured:
  `301_lab_report_panel` 108 drawing-only paragraphs → 0, Google 2 pages → 1, 39/42; `375_attendance_register`
  456 → 0, 2 pages → 1, 37/42) and
  `tools/p2w-bench/FINDINGS/00_page_count-MERGE-IN-COLUMN-PAGE-MEASURED-IN-GOOGLE.md` ("`pageBody()`
  **already** writes every shape as a bare run … So a re-implementation in `shape()` is a no-op").

So a literal re-implementation in `shape()` would change nothing. What is **still** un-merged is the one
path that reaches `shape()` — the shape blocks of a **column page**, emitted from `columnPage()` — and
that exact patch already exists in the tree as
`tools/p2w-bench/FINDINGS/00_page_count-MERGE-SHAPE-PARAGRAPHS.patch`, measured in Google on one
document (`361_product_catalogue_grid`: 2 pages → 1, 41/42) and **not landed**, because the `.docx`
half of the commit gate (`benchmarks/gate.py`) did not finish inside one call limit.

**My patch is that patch, verified by me** (§4): it applies cleanly to HEAD, compiles the whole engine, and
on a two-column test page collapses 40 paragraphs to 29 while keeping all 12 drawings at identical offsets.

### The handoff's claims, checked

| claim in the handoff | verdict | evidence |
|---|---|---|
| Google rasterises a page-positioned floating shape and keeps the empty paragraph that carries it; ~0.83 pt with `w:line="1"` exact | **measured** (not by me) | `FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md`, table "What is measured, on `301_lab_report_panel`": 89.9 pt for 108 paragraphs, "about 0.83 pt per paragraph", and the one-paragraph deletion moving the block 40.7 → 39.9 pt |
| 301: 108 paragraphs = 89.9 pt against 44.5 pt free ⇒ 2 pages; deleting all 108 ⇒ 1 page at the same text y | **measured** | same file, rows 2 and 4 of its candidate table |
| 22 of 23 refused documents emit all drawing-only paragraphs after the last text paragraph, counts 7…2464 | **measured then, stale now** | 0530 table. At HEAD the same document (`041122`) emits **11** drawing-only paragraphs, not 2464 — my local measurement, §5 |
| the merge is the next lever, `DocxWriter.java:2726`, 88.8 pt vs 89.9 pt needed | **already implemented** at 1354–1412; the residual site is `shape()` via `columnPage()` | code quoted in §1 |

Everything below separates **measured** (a file or a run I can name) from **inferred** (schema knowledge
or code reading).


## 1. Every site that emits a page-positioned / floating drawing with its own paragraph

`grep -n '<w:p><w:pPr>' DocxWriter.java` returns 14 hits; four are page-positioned drawings with their own `<w:p>`:

| # | method | line of the `<w:p>` | per-drawing? | merged at HEAD? |
|---|---|---|---|---|
| A | `shape()` | **2894** | yes, when reached from `columnPage()` | **no** ← the patch |
| B | `anchoredPicture()` | **2580** | yes, one per placed `Picture` | **no** |
| C | `anchorShape()` (text boxes: `anchorBox`, `pinnedBoxes`, `stampBox`) | **5583** | yes, one per anchored line | **no** |
| D | `picture()` inline branch | 2549 | one per picture, **inline** (`wp:inline`) — this one is flow content and must stay in its own paragraph | n/a |
| E | `pageBody()` orphan carrier | 1409–1411 | **one per page** | yes — the landed merge |

### A. `shape()` — 2893–2897 (the site the brief names)

```java
2893    private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
2894        sb.append("<w:p><w:pPr>").append(SHAPE_PARA_PPR).append("</w:pPr>");
2895        shapeRun(sb, s, ctx);
2896        sb.append("</w:p>");
2897    }
```

and its two neighbours, 2887–2912:

```java
2887    private static final String SHAPE_PARA_PPR =
2888            "<w:snapToGrid w:val=\"0\"/>"
2889            + "<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\""
2890            + " w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>"
2891            + "<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr>";
...
2914    private static void shapeRun(StringBuilder sb, Shape s, Ctx ctx) {
2915        int id = SHAPE_ID_BASE + (ctx.shapeSeq++);
2918        long offX = Math.round(s.xPt * EMU_PER_PT);
2919        long offY = Math.round(s.topPt * EMU_PER_PT);
2920        int relHeight = 100000000 + (id & 0xFFFF);
2921        sb.append("<w:r><w:drawing>")
2922                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
2923                .append(" simplePos=\"0\" relativeHeight=\"").append(relHeight).append("\"")
2924                .append(" behindDoc=\"1\" locked=\"0\" layoutInCell=\"1\" allowOverlap=\"1\">")
```

`shape()` has exactly **one** caller — `emitBlock()`, line **2358**:

```java
2342    private static void emitBlock(StringBuilder sb, Object block, Ctx ctx) {
...
2349        } else if (block instanceof Shape) {
2350            Shape s = (Shape) block;
2354            if (s.stampFrame
2355                    && ctx.stampText.containsKey(s.mergedHost == null ? s : s.mergedHost)) {
2356                return;
2357            }
2358            if (!s.consumed) shape(sb, s, ctx);
2359        }
2360    }
```

`emitBlock()` is called from four places: 1394 (the page loop — but `Shape` blocks are intercepted at
1377 *before* it, so `shape()` is unreachable there), 2062 and 2271 (the `before` / `after` bands of a
column page) and 2203 (inside a column cell). **Therefore the only page that can reach `shape()` is one
where `columnPage()` returned true.** That is the whole scope of the patch.

The routing that decides it, `columnPage()` 1984–1992:

```java
1984            float t = blockTop(b), bt = blockBottom(b);
1985            if (home[i] == -2 || t < 0f || bt <= 0f) {
1986                // Positioned rather than flowed - a picture or a drawn shape. It carries its own
1987                // x and y, so it goes after the table and lands where the page put it.
1988                after.add(b);
1989                continue;
1990            }
```

and 2271, the last thing a column page writes:

```java
2271        for (Object b : after) emitBlock(sb, b, ctx);
2272        return true;
```

So on a column page every shape lands **after the table**, one `<w:p>` each — exactly the shape of
failure the 0530 finding describes ("all drawing-only paragraphs after the last text paragraph"), and
exactly why `361_product_catalogue_grid` (a catalogue grid) was the document the patch moved.

### The landed merge, for contrast — `pageBody()` 1354–1412

```java
1354        // It used to get a paragraph of its own, and Google Docs bills every such paragraph the
1355        // line box of its sz=2 run (~0.83 pt) even though w:line="1" exact asks for nothing - so a
1356        // page drawing 108 rules paid ~90 pt of flow for them and rendered a second sheet. The
1357        // shape is anchored to the PAPER (wp:positionH/V relativeFrom="page", wp:wrapNone): it
1358        // does not consult the paragraph it sits in, so the paragraph buys nothing.
1367        StringBuilder pendingShapeRuns = new StringBuilder();
1368        StringBuilder orphanShapeRuns = new StringBuilder();
1377            if (block instanceof Shape) {          // 1377-1393: intercept; 1384 shapeRun(...)
1409        if (orphanShapeRuns.length() > 0) {
1410            sb.append("<w:p><w:pPr>").append(SHAPE_PARA_PPR).append("</w:pPr>")
1411                    .append(orphanShapeRuns).append("</w:p>");
1412        }
```

### B. `anchoredPicture()` — 2574–2607 (unmerged, same construct)

```java
2574    private static void anchoredPicture(StringBuilder sb, Picture p, int id, Ctx ctx) {
2580        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
2581                .append("<w:spacing ... w:line=\"1\" w:lineRule=\"exact\"/>")
2582                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
2583                .append("<w:r><w:drawing>")      // 2584 wp:anchor, 2594 wp:wrapNone
```

Called from `picture()` at 2546 for `p.placed`. `Picture` blocks are **not** intercepted by the
`pageBody()` loop (only `Shape` is), so a page that places N images still pays N line boxes.

### C. `anchorShape()` — 5583+ (unmerged, same construct, largest population)

```java
5583        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
5584                .append("<w:spacing ... w:line=\"1\" w:lineRule=\"exact\"/>")
5585                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
5586                .append("<w:r><w:drawing>")      // 5587 wp:anchor, wrapNone as above
```

This is the writer for every anchored **text box**. `para()` (3059) reaches it whenever a page is in
positioned mode — 3084–3088:

```java
3084        if (ctx.positioned && !anyRotated) {
3085            for (PdfToWord.Box b : p.boxes) {
3086                if (b.runs.isEmpty()) continue;
3087                ctx.cenAnchorPos++;
3088                anchorBox(sb, p, b, ctx);      // -> anchor() 4746 -> anchorShape() 5583
```

so a page written in positioned mode emits **one tiny paragraph per line of text**, each carrying an
anchored text box. The paragraph is not empty of text (the words are inside `w:txbxContent`), but its own
line box is the same `sz=2` / `line=1` exact box — the same 0.83 pt, by the same mechanism.


## 2. How a "drawing-only paragraph" is produced, precisely

A drawing-only paragraph is produced by exactly one code shape (A above):

```xml
<w:p>
  <w:pPr>
    <w:snapToGrid w:val="0"/>
    <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="0" w:after="0"
               w:line="1" w:lineRule="exact"/>
    <w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>
  </w:pPr>
  <w:r><w:drawing><wp:anchor … relativeFrom="page" …><wp:wrapNone/>…</wp:anchor></w:drawing></w:r>
</w:p>
```

* **The `<w:p>` wrapper is written by `shape()` (2894) or by the orphan carrier (1410)**; the run inside
  is written by `shapeRun()` (2914). Nothing else writes a drawing-only paragraph in this writer.
* **The pPr is `SHAPE_PARA_PPR`** (2887–2891) and nothing else: no `w:sectPr`, no `w:pageBreakBefore`,
  no `w:keepNext`, no `w:keepLines`, no `w:ind`, no `w:jc`. `anchorShape()` (5583–5585) and
  `anchoredPicture()` (2580–2582) spell the same three properties out by hand.
* **Several shapes may legally share one `<w:p>`.** *(OOXML schema knowledge, not measured here.)* In
  ECMA-376 `CT_P` contains `EG_PContent`, which allows any number of `w:r` children; `CT_R` allows one or
  more `EG_RunInnerContent` items, of which `w:drawing` is one. Each `w:drawing` holds one `wp:anchor`,
  and each `wp:anchor` carries its own `docPr` id, `relativeHeight`, `positionH`/`positionV` and
  `wrapNone`. There is no "one drawing per paragraph" rule and no "one drawing per run" rule. What the
  merge relies on — a floating anchor with `wrapNone` taking no space in the flow — is the same property
  the landed `pageBody()` merge already relies on, and that one is **measured** (301 and 375, above).
* The one thing I am **inferring** rather than quoting is Google's billing rule itself (0.83 pt per
  paragraph, `w:line="1"` exact not honoured). That comes from the 0530 finding's measurement, and I did
  not re-measure it — no Google round trip was run in this slot.


## 3. Is merging N drawing-only paragraphs into one `<w:p>` safe?

Legal and safe **provided every shape keeps its own `wp:anchor` with unchanged `positionH`/`positionV`/
`extent`, and only the paragraph breaks collapse**. The patch does exactly that: `shapeRun()` is
untouched, so `offX = s.xPt·EMU`, `offY = s.topPt·EMU` (2918–2919), `extent` (2916–2917), `docPr` id
(2915) and `relativeHeight = 100000000 + (id & 0xFFFF)` (2920) are all bit-identical.

Concrete risks, each with the line that decides it:

| risk | what could change | verdict |
|---|---|---|
| **paragraph-mark count** | N marks → 1. A bookmark, comment range or field that pointed at one of the removed marks would dangle. | **No risk in this code**: `shapeRun()` writes only `w:r`/`w:drawing`/`wp:anchor`/`wps:*` (2914–2975) and `SHAPE_PARA_PPR` has no `w:bookmarkStart`, `w:commentRangeStart`, `w:fldChar` or `w:hyperlink`. Nothing outside the drawing refers to the paragraph. |
| **`sectPr` placement** | a section break is a child of `w:pPr`. Collapsing paragraphs could drop one. | **No risk**: neither `SHAPE_PARA_PPR` (2887) nor the two hand-written copies (2580, 5583) contain `w:sectPr`. The body-level `sectPr` is emitted separately and last (1301–1304). |
| **page breaks between them** | a `w:br w:type="page"` in a run, or `w:pageBreakBefore` in pPr, would be lost. | **No risk**: `shapeRun()` writes no `w:br`; `SHAPE_PARA_PPR` has no `w:pageBreakBefore`. |
| **`keepNext` / `keepLines`** | could have kept the shapes on the same page as text. | **No risk**: absent from the pPr (2887–2891). |
| **spacing / line box** | total `w:before + w:line + w:after` goes from N×1 twip to 1×1 twip in the *writer's* model. | **Intended and tiny**: `spacingTw(pg)` (used at 1190/1196 by the budget guard) sees (N−1) fewer twips = (N−1)/20 pt; the Google charge falls by 0.83·(N−1) pt. |
| **z-order** | overlapping shapes could be re-stacked. | **No risk**: `relativeHeight` is per shape (2920) and ids come from `ctx.shapeSeq`, emitted in order; only the enclosing paragraph changes. |
| **`layoutInCell="1"`** | an anchor that was inside a table cell now sitting at body level would change clipping semantics. | **Not reachable in this path**: on a column page a shape has `home[i] == -2` and goes to `after` (1985–1989), never into a cell. The patch's cell guard (see §4) is defensive only. |
| **a cell left with no block** | if a shape *were* the only block in a cell, removing it leaves an empty `<w:tc>`, which is invalid. | **Handled**: the patch adds `|| cellXml[c].indexOf("<w:p") < 0` at the existing filler-paragraph test (2224). |
| **where the carrier sits in the flow** | previously N paragraphs after the table, now 1. Google's break moves. | **This is the fix**, and the only thing whose *effect* must be measured in Google, not in LibreOffice (LibreOffice honours `w:line="1"` exact and shows no change — measured: `FINDINGS/…MERGE-IN-COLUMN-PAGE-MEASURED-IN-GOOGLE.md`, and reproduced by me on the synthetic page, §4). |
| **N = 1** | a page with a single shape must be unchanged. | **Byte-identical**: one paragraph either way, same pPr, same run. |


## 4. The patch

`/scratch/output/agent-a-merge-paragraphs.patch` — **+47 / −5**, `DocxWriter.java` only, **no new
imports** (`StringBuilder` and `Ctx` are already there). It is byte-identical to the repo's own
`tools/p2w-bench/FINDINGS/00_page_count-MERGE-SHAPE-PARAGRAPHS.patch`, which I re-verified rather than
re-derived.

| location | change |
|---|---|
| `Ctx` (~853) | new `final StringBuilder shapeCarrier` |
| `pageBody()` (1359) | `ctx.shapeCarrier.setLength(0)` on entry (the budget guard writes a page up to 3×, each into a fresh `pg`, 1183–1230) and `flushShapes(sb, ctx)` at **both** exits (column exit 1362, normal exit 1427) |
| `columnPage()` (2224) | a cell whose only block was a shape still gets a filler paragraph |
| `shape()` (2910) | appends `shapeRun(...)` to `ctx.shapeCarrier` instead of wrapping it in `<w:p>` |
| `flushShapes()` (new) | writes the carrier as **one** `<w:p>` with `SHAPE_PARA_PPR` — the same string the orphan carrier at 1410 already writes in production — then clears it |

### What I verified, and how

1. **Applies to HEAD**: `git apply --check` against `1ba51d9` — clean, no fuzz, working tree left untouched
   (`git status --porcelain` empty afterwards).
2. **Compiles**: applied to a *copy* of the clone (`/scratch/work/CS-verify`), then the full engine built
   the way `tools/p2w-bench/build-engine.sh` builds it — `javac 17` (Adoptium 17.0.21.1), stubs + all 11
   files of `app/src/main/java/com/kavopdf/app/engine` + `ConvertOne`, against pdfbox-android 2.0.27.0 and
   bouncycastle 1.72: **exit 0, 0 errors**, `DocxWriter.class` produced. (The unpatched tree was compiled
   the same way as a control, also clean.)
3. **Exercised, and geometry preserved** — a two-column test page (2×14 text lines, 12 rules) converted
   with both engines:

   | | base | patched |
   |---|---:|---:|
   | `<w:p>` elements | 40 | **29** |
   | `<w:drawing>` elements | 12 | 12 |
   | `wp:anchor` (posOffsetH, posOffsetV, cx, cy) | 12 | **12, all identical, in order** |
   | `word/document.xml` well-formed (lxml) | yes | **yes** |
   | LibreOffice page count | 1 | 1 |

   11 paragraphs collapsed = 12 shapes − 1 carrier ⇒ 11 × 0.83 ≈ **9.1 pt** of Google flow saved on that
   page. *(Synthetic page, LibreOffice only — it proves the code path runs and the drawings do not move;
   it does not prove a Google page count.)*
4. **Blast radius on the real PDFs I have**: five corpus documents exist in this sandbox
   (`041122-Account_Opening_Form`, `Account_Opening_Form_Fillable_filled`, `600_reviewed_invoice`,
   `601_fillable_admission_form`, `602_bookmarked_annual_report`). Their `document.xml` is **byte-identical**
   between base and patched — the patch is a no-op on all five, because none of them is a column page with
   shapes. The 21 documents it changed in the repo's own measurement are not among the five I can build here.


## 5. The documents refused on page count

Source: `benchmarks/gverify/*.json` (213 files, Google) joined to `benchmarks/RANKING.csv` (share@5px, the
LibreOffice pixel proxy) and `benchmarks/gverify-lo/*.json` (LibreOffice, the only per-check detail that
exists for a refused document).

* **213 documents: 190 `ok`, 23 `page_count_refused`.** No `ok` document fails a page-count check (count 0,
  over all 190 `failed` lists).
* **A refused row carries no check list** — the JSON is only `{name, status, pages, want}`, because
  `gverify` will not score checks against a different page count. The per-check data below is the
  LibreOffice proxy, not a Google result. The check set is 42 on some runs and 47 on others.

| document | pages / want | share5 | LO proxy | LO checks failing |
|---|---:|---:|---:|---|
| `041122-Account_Opening_Form` | 14 / 9 | 98.65 | 27/47 | 01_page_count, 04_chars_missing, 05_chars_extra, 10_font_sizes … |
| `Account_Opening_Form_Fillable_filled` | 14 / 9 | 97.62 | 21/47 | 01_page_count, 04_chars_missing, 05_chars_extra, 10_font_sizes … |
| `price-list-2col-dense-right-aligned` | 2 / 1 | 2.69 | 42/42 | — |
| `326_itr_computation` | 2 / 1 | 0.63 | 46/47 | 63_table_rows |
| `05_round_company_seal_curved_text` | 2 / 1 | 0.19 | 42/42 | — |
| `boq-horizontal-rules-only` | 2 / 1 | 0.13 | 42/42 | — |
| `350_question_paper` | 2 / 1 | 0.11 | 42/42 | — |
| `bank-statement-horizontal-rules-only` | 2 / 1 | 0.10 | 42/42 | — |
| `333_datasheet_spec_tables` | 2 / 1 | 0.07 | 46/47 | 66_table_cell_width |
| `60_page_border` | 2 / 1 | 0.06 | 41/42 | 17_matched_runs |
| `390_wide_data_appendix` | 2 / 1 | 0.03 | 46/47 | 66_table_cell_width |
| `401_trifold_brochure` | 2 / 1 | 0.03 | 42/42 | — |
| `314_tender_rfp_boq` | 2 / 1 | 0.00 | 46/47 | 63_table_rows |
| `305_vaccination_certificate` | 2 / 1 | 0.00 | 45/47 | 17_matched_runs, 59_shape_anchor |
| `403_crossword_puzzle` | 2 / 1 | 0.00 | 41/42 | 14_filled_shapes |
| `320_balance_sheet_statutory` | 2 / 1 | 0.00 | 47/47 | — |
| `332_bom_on_drawing` | 2 / 1 | 0.00 | 47/47 | — |
| `341_shipping_manifest` | 2 / 1 | 0.00 | 47/47 | — |
| `351_omr_answer_sheet` | 2 / 1 | 0.00 | 42/42 | — |
| `353_admit_card` | 2 / 1 | 0.00 | 47/47 | — |
| `361_product_catalogue_grid` | 2 / 1 | 0.00 | 42/42 | — |
| `402_calendar_month_grid` | 2 / 1 | 0.00 | 47/47 | — |
| `405_sheet_music_lyrics` | 2 / 1 | 0.00 | 42/42 | — |

### How many would the merge plausibly turn CLEAN?

**None can be claimed clean on evidence, and I would predict 0–3 at best.** The reason is that the four
documents of this class that have actually been re-measured in Google after a merge came out *measurable
and near-clean*, not clean:

| document | merge applied | Google pages | Google checks |
|---|---|---:|---|
| `301_lab_report_panel` | landed (`pageBody`) | 2 → **1** | refused → **39/42** |
| `375_attendance_register` | landed (`pageBody`) | 2 → **1** | 35/42 → **37/42** |
| `361_product_catalogue_grid` | **this patch** | 2 → **1** | refused → **41/42** (only `25_invisible_text`) |
| `401_trifold_brochure` | this patch | 2 → **2** | still refused (20 × 0.83 = 16.6 pt saved against ~0 pt of slack) |

`361` is the closest thing to a win in the class and it is one check short. The likeliest closers are the
13 whose LibreOffice proxy is already perfect (`320`, `332`, `341`, `353`, `402` at 47/47; `05`, `350`,
`351`, `361`, `401`, `405`, `bank-statement`, `boq`, `price-list` at 42/42) — but the one of them measured
in Google after the merge (`361`) still failed `25_invisible_text`, a Google-only check the proxy cannot
see. So: **the merge's value here is that these documents become scorable at all** (each is currently 0 of
42 known checks), with 2–5 further checks then visible, not that they go clean.

Two of the 23 are explicitly **not** explained by this mechanism:

* `350_question_paper` — 1 drawing-only paragraph (0530 finding); still refused.
* `041122` / `Account_Opening_Form_Fillable_filled` — 14 pages against 9. At HEAD their built `.docx`
  carries **11** drawing-only paragraphs and **200** `sz=2`/`line=1`-exact paragraphs in total (189 of
  them anchored text boxes) ⇒ 200 × 0.83 ≈ **166 pt ≈ 0.2 page** against a **5-page** gap. Merging the
  shape paragraphs cannot close that. *(Measured by me: `ConvertOne` on
  `benchmarks/realworld/041122-Account_Opening_Form.pdf`, then lxml over `word/document.xml`: 1451 `w:p`,
  2653 `wp:anchor`, 200 tiny paragraphs.)*

I could not map each of the 23 to "is a column page" — the corpus PDFs (`/scratch/work/p2w/corpus`) are
not present in this sandbox and only 5 real PDFs are in the tree. **The patch can only change documents
whose page is routed through `columnPage()`** (§1), so the per-document attribution needs the corpus and a
`ConvertAll` run.


## 6. The residual levers, in order of size

One construct, three floating emitters (A, B, C): the merge is landed for A's `pageBody()` path, unlanded for A's column-page path (this patch), and not applied at all to B or C.

1. **`anchorShape()` / text boxes (5583)** — the largest: **189 of the 200** tiny paragraphs on `041122`.
   Every line of a positioned page is one. They could join the same carrier; the care needed is that
   `anchorShape` also writes `w:txbxContent` inside the drawing, so only the wrapper may move.
2. **`anchoredPicture()` (2580)** — one per placed image; `Picture` blocks are not intercepted by the
   `pageBody()` loop, and a placed picture's anchor is also `relativeFrom="page"` + `wrapNone`.
3. **`w:tcBorders` / `w:tblBorders` through the table writer** — the second lever named by the 0530
   finding for `32_stroke_lines` and `05_chars_extra` (one construct, three check families).

Each of these is a strictly larger edit than the patch here and needs its own Google measurement; the
LibreOffice proxy cannot see any of it (measured: no LibreOffice page count moved on any document, in the
repo's record or in mine).


## 7. What would falsify this

* A document whose LibreOffice page count goes **up** with this patch (none did — 21/21 in the repo's
  measurement; the 5 I could build are byte-identical).
* A Google render where a shape moved or a `<w:drawing>` disappeared (12/12 anchors kept their exact
  offsets on my synthetic column page; the repo measured 361 the same way).
* A document that still refuses at HEAD *because* of drawing-only paragraphs on a non-column page.

## Open questions

1. **The corpus PDFs are absent from this sandbox** (`/scratch/work/p2w/corpus` does not exist; only 5 real
   PDFs ship in the tree). I therefore could not (a) run `ConvertAll` over the 23 refused documents to
   count their drawing-only paragraphs at HEAD, or (b) say which of them are column pages and are
   therefore touched by the patch. That attribution is the one measurement I could not make.
2. **No Google round trip was run** — no Drive upload/export in this slot, so every Google number in this
   report is quoted from the repo's FINDINGS, and my own measurements are LibreOffice + XML only.
3. **The commit gate is still the blocker, not the evidence**: `benchmarks/gate.py --budget 250` has to
   rewrite `RANKING.csv` and `STATE.json` on the patched engine before the engine and its table can be
   committed together. I did not run it (it outlives one call and writes into the repo).
