# `anchorShape()`'s carrier paragraphs — measured, not assumed

**Agent B.** Repo `kavopdf/app` cloned to `/scratch/work/B/CS` (read-only; the tree is still clean).
All builds and conversions were done in a copy at `/scratch/work/B/build`, so nothing was written
into the clone. Patch: `agent-b-anchorshape.patch`. Corpus: the four zips in `/scratch/input`,
unpacked to `/scratch/work/B/corpus` — **213 PDFs** (211 corpus + `benchmarks/realworld/`'s two
`041122` files, which is where the document named in the brief actually lives; it is *not* in the
zips).

---

## 1. What the code writes

### 1.1 `anchorShape()` — `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`

Two overloads, 5523 and 5538. The body that matters is the second one:

```
5538    private static void anchorShape(StringBuilder sb, Ctx ctx, float pageX, float pageY,
5539            float lx, float ly, float wPt, float hPt, float rotDeg,
5540            String geomXml, String lnXml, String inner,
5541            float lInsPt, float tInsPt, String vert) {
...
5576        int id = ctx.shapeSeq++;
5577        long cx = Math.max(1, Math.round(wPt * EMU_PER_PT));
5578        long cy = Math.max(1, Math.round(hPt * EMU_PER_PT));
5579        long offX = Math.round(offXpt * EMU_PER_PT);
5580        long offY = Math.round(offYpt * EMU_PER_PT);
5581        int relHeight = 251658240 + (id & 0xFFFF);
5582
5583        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
5584                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
5585                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
5586                .append("<w:r><w:drawing>")
```

and it closes at 5632 with

```
5632                .append("</wp:anchor></w:drawing></w:r></w:p>");
5633        ctx.anchorCount++;
```

So, in answer to the three questions asked:

* **What `<w:p>` wrapper.** Literally `<w:p><w:pPr>…</w:pPr><w:r><w:drawing><wp:anchor …>
  … </wp:anchor></w:drawing></w:r></w:p>` — a complete paragraph, one run, one drawing, **per
  anchored text box**. Nothing is buffered; the append is unconditional and the string is closed
  on the same call.
* **Its `pPr`.** `w:snapToGrid val="0"`, `w:spacing` with `before=0 after=0 line=1 lineRule="exact"`
  and both autospacing flags off, and an `rPr` of `w:sz val="2"` / `w:szCs val="2"`. This is
  **byte-identical** to the constant `SHAPE_PARA_PPR` at 2887–2891, which is why the patch below
  can key on one string for both constructs.
* **Where the paragraph break comes from.** The `</w:p>` on line 5632, and from nowhere else. The
  anchor itself is `wp:positionH/V relativeFrom="page"` (5599–5602) with `<wp:wrapNone/>` (5605) and
  `behindDoc="1"` (5597), so the box is placed against the paper and never consults the paragraph
  it sits in.

Callers: `stampBox()` 5352 (a stamp's text box), `para()` 3283 / 3303 / 3309 (a rotated or
positioned line: a ring character, a quarter-turn line, a rotated label) and `anchorBox()` →
`anchor()` 4751 (a label the page drew inside a closed outline). Every one of them lands one
`<w:p>` in the page body per box.

### 1.2 `anchoredPicture()` — 2574

```
2574    private static void anchoredPicture(StringBuilder sb, Picture p, int id, Ctx ctx) {
2575        long cx = Math.max(1, p.widthEmu);
2576        long cy = Math.max(1, p.heightEmu);
2577        long offX = Math.round(p.xPt * EMU_PER_PT);
2578        long offY = Math.round(p.topPt * EMU_PER_PT);
2579        int relHeight = 251658240 + (id & 0xFFFF);
2580        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
2581                .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
2582                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
2583                .append("<w:r><w:drawing>")
```

…closed at 2606 with the same `</wp:anchor></w:drawing></w:r></w:p>`. Same wrapper, same `pPr`,
same paragraph break, same `behindDoc="1"` / `wrapNone` / page-relative offsets. It is a **separate
copy of the same four lines** — the two functions share no helper. Measured: 24 such paragraphs
across the corpus.

### 1.3 Corrections to the established facts

| claim | what the file says |
|:--|:--|
| `pageBody()` at ~1354–1412 | **1318–1414** (the shape-run logic is 1352–1412; the method opens at 1318) |
| `shape()` at ~2893 | **2893** — correct |
| `anchoredPicture()` at ~2580 | function opens at **2574**; 2580 is its `sb.append("<w:p>…")` |
| `anchorShape()` at ~5583 | opens at **5523 / 5538**; 5583 is the line that writes the `<w:p>` |
| `columnPage()` ~1985-1989 → `emitBlock()` ~2271 | `columnPage()` opens at **1745**; its `emitBlock` calls are **2062** and **2271**; `emitBlock()` itself is **2342** |
| 041122 has 189 of 200 such paragraphs | **189 carrier paragraphs out of 191 drawing-only paragraphs** (the other two: one `anchoredPicture`, one `shape()`). The `2464 drawing-only paragraphs` in `FINDINGS/00_page_count-…-0530-fixer.md` is, on the evidence of the timestamps, a **pre-`SHAPE-RUNS-NOT-PARAGRAPHS`** number — that FINDINGS is dated 04:56–05:55 and the shape-run merge landed at 07:30 — and 2 462 of the 2 464 are gone from the current tree (**inference**; I did not check out the earlier commit) |

---

## 2. Build and measurement

**Build:** plain `javac`, not `tools/p2w-bench/build-engine.sh`. `build-engine.sh` writes `libs/`
and `out/` *inside the clone*, which would leave the tree dirty; the compile itself is the same —
JDK 17.0.21 from Adoptium, PDFBox-Android 2.0.27.0 AAR + BouncyCastle 1.72 jars from Maven Central,
classpath `out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar`,
`javac -d out $(find stubs -name '*.java')` then the engine then `ConvertAll`/`ConvertOne`. 45 s.
`ConvertAll` over all 213 PDFs: 86 s.

**Counter:** a nesting-aware splitter for `<w:p>` (a `w:p` *does* nest — every anchored box carries
`wps:txbxContent`, which holds its own `w:p`), counting top-level paragraphs that contain a
`<w:drawing>` and no `<w:t>` outside it, and attributing them by `wp:docPr name=`.

### 2.1 Per-document counts — 213 documents, before and after the patch

Corpus totals: **1 319** drawing-only paragraphs before, **399** after. Of those, **1 037** came
from `anchorShape()` before and **117** after; **24** from `anchoredPicture()` (untouched by the
patch); **258** from `shape()` reached through `columnPage()`→`emitBlock()` (also untouched — that is
the path the unlanded Google-measured column patch owns).

61 documents carry at least one `anchorShape()` carrier. The twelve largest, `drawing-no-text
paragraphs` and the `anchorShape()` share of them:

| document | drawing-only before | `anchorShape` before | `anchorShape` after | all `<w:p>` before → after |
|:--|--:|--:|--:|--:|
| 041122-Account_Opening_Form | 191 | **189** | 12 | 1262 → 1085 |
| Account_Opening_Form_Fillable_filled | 191 | 189 | 12 | 1271 → 1094 |
| 05_round_company_seal_curved_text | 63 | 63 | 2 | 80 → 19 |
| policy-2col-spanning-section-heading | 62 | 62 | 2 | 68 → 8 |
| academic-paper-ieee-2col-abstract | 51 | 51 | 1 | 138 → 88 |
| 305_vaccination_certificate | 48 | 48 | 2 | 82 → 36 |
| 60_page_border | 47 | 47 | 2 | 62 → 17 |
| magazine-2col-pullquote-spanning | 38 | 37 | 2 | 44 → 9 |
| 69_two_col_legal_numbered_clauses | 36 | 36 | 2 | 48 → 14 |
| 318_court_summons_form | 31 | 31 | 2 | 58 → 29 |
| 312_affidavit_stamp_paper | 28 | 28 | 2 | 52 → 26 |
| 352_certificate_ornate_border | 30 | 28 | 2 | 41 → 15 |

**041122 is confirmed: 189 carrier paragraphs**, and they are not one block — they fold into
**12** paragraphs across its 9 pages.

---

## 3. The patch

`agent-b-anchorshape.patch` — 108 added lines, one file, no other change. It applies cleanly to a
fresh clone (`git apply --check` → clean).

It is a **post-pass on the page buffer**, `collapseAnchorParas(pg)`, called at 1187 and 1241 in
`documentXml` — immediately after `pageBody()` and, at 1241, **before** `spacingTw(pg)`, so the
budget guard sees the collapsed page and not the old one. A page buffer, not the document, because
the guard measures per page and because a merge may not cross a page boundary.

What it does: walk the page for `ANCHOR_PARA_OPEN` (`"<w:p><w:pPr>" + SHAPE_PARA_PPR +
"</w:pPr>"`); if the paragraph's body is **nothing but** complete `<w:r><w:drawing>…</w:drawing></w:r>`
runs, every one of them named `KavoPDF text `, then keep absorbing following siblings that open with
the same prefix and pass the same test; write the first paragraph's pPr, all the runs in the order
they were written, and one `</w:p>`.

**What it refuses to touch**, on purpose: a carrier whose body holds a `w:t`, a bookmark, a field,
or a nested paragraph; and any two carriers with *anything* between them at body level
(`bookmarkStart`, `sectPr`, a table, a flow paragraph, a page break) — the adjacency test is a
literal string comparison of the next 100-odd bytes, so any intervening element ends the run.

### 3.1 Verification — the anchors are untouched

Every `wp:anchor` in every document, reduced to `(attributes, positionH offset, positionV offset,
extent cx, extent cy, docPr id, docPr name, a:xfrm rot, text-run count)` **in document order**,
before vs after, all 213 documents:

```
checked 213 documents; 0 differ in their anchor list; 0 problems
```

`posOffset`, `cx`/`cy`, `relativeHeight`, `behindDoc`, `wrapNone`, `docPr id`, rotation and order
are therefore identical, byte for byte, everywhere.

### 3.2 Verification — the merge is the *only* change

Taking each patched `document.xml` and mechanically re-splitting every merged carrier paragraph back
into one paragraph per run reproduces the unpatched `document.xml` **byte for byte** in **211 of 213**
documents. The two exceptions are `041122-Account_Opening_Form` and its `_Fillable_filled` twin, and
the difference is one number on one ordinary text paragraph: `w:before="831"` → `w:before="832"`
(+1 twip = 0.05 pt). That is not the merge leaking; it is the budget guard re-spending a twip it no
longer pays (see §4).

---

## 4. What the merge changes in flow terms

### 4.1 The engine's own model: measured

`spacingTw()` (449–484) is the page's height model, and it charges a carrier paragraph its
`w:before` (0) plus its `w:line` (**1** twip, from line 5584). So the engine charges **1 twip =
0.05 pt per carrier paragraph** — that is the whole of it, and it is read off the code and
confirmed by the deltas below (removed paragraphs × 1 twip, minus what the guard re-spends).

Porting `spacingTw` exactly and summing per document, base vs patched:

* **914 twips = 45.7 pt** of flow removed across the whole 213-document corpus.
* `041122`: 101 283 → 101 107 twips, **−176 twips = −8.8 pt** for 177 removed paragraphs over
  9 pages (≈ 1 pt per page).
* `05_round_company_seal_curved_text` −61 tw = −3.05 pt; `policy-2col-spanning-section-heading`
  −60 tw = −3.0 pt; `academic-paper-ieee-2col-abstract` −50 tw = −2.5 pt.

So: **920 paragraph marks removed × 0.05 pt measured = 46 pt of the engine's model**, corpus-wide.

### 4.2 The renderer cost: measured, and it is zero in LibreOffice

`041122` renders **10 pages in LibreOffice 7.4.7.2 against a 9-page source**, both before and after.
Rendering all 38 documents whose paragraph count changed, before and after:

* **0 of 38 change page count.** (`041122` 10→10, `05_round` 1→1, `60_page_border` 1→1,
  `305_vaccination` 1→1, `401_trifold_brochure` 1→1.)
* Span-level comparison of the rendered PDFs: **33 of 38 identical**; the other five move text
  **vertically only, never horizontally**, by at most 2.1 pt (`041122`), 0.2 pt
  (`323_credit_card_statement`), 0.1 pt (three documents). The largest movers are ordinary flowed
  text on `041122` page 10, not anchored boxes — the page's flow re-spends the twips it no longer
  pays. Anchored box text moves at most 0.1 pt.

**LibreOffice does not charge this paragraph.** It honours `w:line="1" w:lineRule="exact"`, so the
carrier costs it ≈0.05 pt and collapsing them buys nothing there. That is the honest result of the
one renderer I can run.

### 4.3 The Google figure — borrowed, not mine

I cannot run the Google round trip, so I have no Google measurement of my own and I am **not**
claiming one. The repository's own number, from
`tools/p2w-bench/FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md`:

> "the whole trailing block costs **89.9 pt** — about **0.83 pt per paragraph**, the line box of a
> `w:sz=2` run under `w:line="1" w:lineRule="exact"` (2.25 pt × 0.35), not the 0.1552 pt the exact
> line asks for. Measured directly: deleting one of the 108 moved the page-2 block from 40.7 →
> 39.9 pt."

**That 0.83 pt is a borrowed number from that FINDINGS file, measured by an earlier agent on
`301_lab_report_panel` in Google Docs. It is not my measurement and it is not measured on
`041122`.** If it transfers, 177 removed carriers on `041122` are worth ≈147 pt in Google — 17 % of
one 842 pt sheet, spread over nine. The same figure at 920 paragraphs corpus-wide would be ≈764 pt.

---

## 5. Risks

**`relativeHeight` ordering.** Every carrier carries `relativeHeight = 251658240 + (id & 0xFFFF)`
(5581), with `id` from `ctx.shapeSeq++` (5576). The merge does not touch `id`, `shapeSeq` or the
attribute — verified by §3.1, which compares the whole `wp:anchor` open tag including
`relativeHeight`. Because ids are allocated in document order and the merge preserves document
order, the relative stacking of any two boxes is unchanged. **Inference, marked as such:** the
z-order among `behindDoc="1"` objects is resolved by `relativeHeight`, so preserving the attribute
and the order preserves the z-order.

**`behindDoc` / z-order against page text.** All `anchorShape` boxes are `behindDoc="1"`
(5597, with the comment at 5589–5596 explaining that a stamp is a mark *on* the paper). Merging two
of them into one paragraph cannot change that: both are still `behindDoc="1"`, still page-anchored,
still `wrapNone`. What changes is only how many paragraph marks separate them.

**A shape anchored to the paragraph it is being merged into.** This is the risk the brief is right
to name, and the code answers it directly: `wp:positionH relativeFrom="page"` /
`wp:positionV relativeFrom="page"` (5599–5602) with `<wp:wrapNone/>` (5605). A page-relative,
`wrapNone` anchor does not consult the paragraph, which is the same argument `pageBody()` already
relies on at 1352–1363 to write a `Shape` as a bare run appended to a paragraph that already
exists. Nothing in this patch asserts that argument beyond what the file already asserts; if the
premise were false, the landed shape-run merge would already be wrong.

**Bookmarks and fields.** Cannot be inside a carrier: the body test requires *only* complete
drawing runs, so a `w:bookmarkStart`, `w:fldChar` or `w:t` in the body fails the test and the
paragraph is left alone. A bookmark *between* two carriers is at body level, so the next bytes are
not `ANCHOR_PARA_OPEN` and the run ends there. Both are structural consequences of the code, not
hopes.

**`sectPr`.** `sectPr` is the last child of `w:body` (1303) and a `w:sectPr` inside a `w:pPr` marks a
section break. Neither can be inside a carrier (the `pPr` is exactly `SHAPE_PARA_PPR`), and a
body-level `sectPr` between carriers would break the adjacency test. A merge can therefore never
cross a section boundary.

**Do two anchored text boxes in one paragraph keep their own wrap settings?** Yes, trivially — and
this is the one place where the answer is stronger than "probably". `anchorShape` writes
`<wp:wrapNone/>` unconditionally (5605): there is no per-box wrap setting to lose, because every box
this function writes has the same one. `wp:anchor`'s wrap element is a child of each `wp:anchor`
(5604–5605), and each `wp:anchor` is untouched, so even a future per-box wrap would survive the
merge — the patch moves `</w:p>`/`<w:p><w:pPr>` bytes and never enters a `wp:anchor`.

**OOXML legality of several drawings in one paragraph.** `CT_P` is `pPr?` followed by `EG_PContent`
with `minOccurs="0" maxOccurs="unbounded"`; `CT_R` is `EG_RPr?` followed by `EG_RunInnerContent`
with `maxOccurs="unbounded"`, and `EG_RunInnerContent` admits `drawing`. A paragraph of N runs, each
a `w:drawing`, is what the content model describes. (Source: the ECMA-376 `CT_P` / `CT_R` schema
excerpt reproduced at python-docx.readthedocs.io, *CT_P*, dev/analysis/schema/ct_p.html.)

**The residual risk I would actually watch.** `18_displacement` (`tools/p2w-bench/verify_google.py`,
THRESHOLDS block) calls a run "out" when it is further than `clamp(0.35*size, 1.5, 4.5)` pt from its
source baseline. The largest displacement I measured is **2.1 pt**, on `041122` page 10 — inside the
tolerance for 10 pt text (3.5 pt) but **above the 1.5 pt floor** for small text. A document whose
moved runs are set below ~4.3 pt could flip that check. I did not run `gverify`, so this is a risk
stated from the threshold, not an observed failure.

---

## 6. Verdict

**Is it worth a fixer slot? Not on its own — and no document can be claimed CLEAN on evidence.**

The reasons, in the order they matter:

1. **Nothing in this corpus gets better in the only renderer I can measure.** 0 of 38 documents
   change page count in LibreOffice; 33 of 38 are pixel-identical; the other five move text by
   ≤2.1 pt vertically and not at all horizontally. The engine's own flow model gains 45.7 pt across
   the whole corpus — 8.8 pt on `041122`, ≈1 pt per page. That is not a page.
2. **The 0.83 pt/paragraph that would make this matter is Google's, and it is borrowed.** It is a
   real measurement, but it was made by an earlier agent on `301_lab_report_panel`, in a document
   whose drawing-only paragraphs were shapes, not anchored text boxes. I have no Google measurement
   of a carrier paragraph and I am not going to invent one.
3. **The class it could help has already been emptied by the shape merge.** Of the 23
   `page_count_refused` documents listed in `FINDINGS/00_page_count-…-0530-fixer.md`, **17 now have
   zero drawing-only paragraphs of any kind** in the current tree. The survivors with
   `anchorShape` carriers are `041122` and its fillable twin (189 each), `05_round_company_seal`
   (63), `305_vaccination_certificate` (48), `60_page_border` (47) and `401_trifold_brochure` (5) —
   six documents, not twenty-three. (`361_product_catalogue_grid`'s 85 remaining carriers are
   `shape()` through the column path, which this patch deliberately does not touch.)
4. **It is cheap and provably safe.** 920 paragraph marks removed on 38 documents; 213/213 documents
   keep every anchor attribute and every anchor's document order; 211/213 documents are
   byte-identical once the merge is undone. If it is going to be done at all, this is the shape of
   the change.

**So: ship it bundled, do not spend a slot on it alone.** It costs nothing to carry alongside the
unlanded column-page patch, which touches the same `SHAPE_PARA_PPR` carrier in the same page body
and would otherwise leave the writer with two different rules for the same paragraph. If a slot is
spent, the thing to buy with it is a Google round trip on the six documents in point 3 — because
`041122` is a 9-page source that LibreOffice already renders as **10**, so its carrier paragraphs
are demonstrably not the only thing wrong with it, and the borrowed 147 pt would not by itself make
it a 9-page document either.

**Documents expected to become CLEAN: 0 claimed.** Not "0 measured" — 0 that I can claim on
evidence, because the claim needs a Google render and I have none.
