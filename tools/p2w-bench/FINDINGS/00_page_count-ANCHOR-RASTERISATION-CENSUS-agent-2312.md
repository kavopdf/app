# `00_page_count` — why 23 documents render the wrong number of pages in Google Docs

Read-only analysis of `kavopdf/app` at HEAD `ad233f1` (cloned 23 Nov 2026). No repo file modified,
no Drive probe created, no push. Every number below is either quoted with `file:line` or measured in
this sandbox from the corpus PDFs (`corpus-v1` release, 208 PDFs + `benchmarks/realworld/`'s 2).

---

## 0. Three corrections to the framing, before anything else

1. **The check is named `01_page_count` in the data, not `00_page_count`.** The class name used by
   `ATTEMPTS.json` / `FINDINGS/` is `00_page_count`; the check key written by `verify_google.py` and
   `gverify.py` is `01_page_count` (`tools/p2w-bench/gverify.py:277-285`,
   `benchmarks/gverify-lo/*.json` → `checks.01_page_count`). Same thing, two names.
2. **A refused document is not a scored zero.** `gverify.py:277-285` refuses to score at all when
   `got != want` and writes `{"status":"page_count_refused","pages":got,"want":want}`. `pages` is the
   page count of **Google's exported PDF**, `want` is the page count of the **source PDF**
   (`_pages()`, `gverify.py:150-156`). `passed`/`total` are absent from these records.
3. **The 23-document list is pre-merge and largely unstamped.** 21 of the 23 records carry **no
   `engine` field at all**; only `353_admit_card` and `402_calendar_month_grid` carry one
   (`98be7c3c`). `ATTEMPTS.json` → `00_page_count.last_engine` is `0be925ff` and records a merge
   landed at 16:34 that moved two documents (`361_product_catalogue_grid` 2 pages → 1, measured in
   Google at 41/42; `375_attendance_register` 2 → 1). `361` is still listed as refused in the
   committed `benchmarks/gverify/361_product_catalogue_grid.json`. **So the true current count is
   ≤ 22 and the committed table has not been regenerated.** Any fixer must re-run
   `gverify.py --report` on the new engine before believing "23".

---

## (a) The 23 unscored documents, and the direction of the error

All 23 are **too many pages**. Not one is short. 21 are one-page sources rendered onto two; two are
nine-page sources rendered onto fourteen.

| # | document | Google pages | source pages | Δ | LibreOffice | LO score |
|---:|---|---:|---:|---:|---|---|
| 1 | `041122-Account_Opening_Form` | 14 | 9 | **+5** | 9 → **10** | 27/47 |
| 2 | `Account_Opening_Form_Fillable_filled` | 14 | 9 | **+5** | 9 → **11** | 21/47 |
| 3 | `05_round_company_seal_curved_text` | 2 | 1 | +1 | 1 → 1 | 42/42 |
| 4 | `305_vaccination_certificate` | 2 | 1 | +1 | 1 → 1 | 45/47 |
| 5 | `314_tender_rfp_boq` | 2 | 1 | +1 | 1 → 1 | 46/47 |
| 6 | `320_balance_sheet_statutory` | 2 | 1 | +1 | 1 → 1 | 47/47 |
| 7 | `326_itr_computation` | 2 | 1 | +1 | 1 → 1 | 46/47 |
| 8 | `332_bom_on_drawing` | 2 | 1 | +1 | 1 → 1 | 47/47 |
| 9 | `333_datasheet_spec_tables` | 2 | 1 | +1 | 1 → 1 | 46/47 |
| 10 | `341_shipping_manifest` | 2 | 1 | +1 | 1 → 1 | 47/47 |
| 11 | `350_question_paper` | 2 | 1 | +1 | 1 → 1 | 42/42 |
| 12 | `351_omr_answer_sheet` | 2 | 1 | +1 | 1 → 1 | 42/42 |
| 13 | `353_admit_card` | 2 | 1 | +1 | 1 → 1 | 47/47 |
| 14 | `361_product_catalogue_grid` | 2 | 1 | +1 | 1 → 1 | 42/42 |
| 15 | `390_wide_data_appendix` | 2 | 1 | +1 | 1 → 1 | 46/47 |
| 16 | `401_trifold_brochure` | 2 | 1 | +1 | 1 → 1 | 42/42 |
| 17 | `402_calendar_month_grid` | 2 | 1 | +1 | 1 → 1 | 47/47 |
| 18 | `403_crossword_puzzle` | 2 | 1 | +1 | 1 → 1 | 41/42 |
| 19 | `405_sheet_music_lyrics` | 2 | 1 | +1 | 1 → 1 | 42/42 |
| 20 | `60_page_border` | 2 | 1 | +1 | 1 → 1 | 41/42 |
| 21 | `bank-statement-horizontal-rules-only` | 2 | 1 | +1 | 1 → 1 | 42/42 |
| 22 | `boq-horizontal-rules-only` | 2 | 1 | +1 | 1 → 1 | 42/42 |
| 23 | `price-list-2col-dense-right-aligned` | 2 | 1 | +1 | 1 → 1 | 42/42 |

Source: `benchmarks/gverify/<name>.json` (`status`, `pages`, `want`) and
`benchmarks/gverify-lo/<name>.json` (`checks.01_page_count.source/render`, `passed/total`).

**Two facts this table settles:**

* **The page count is not a shared defect.** LibreOffice renders the source's exact page count on
  **21 of 23**; it is wrong on only the two account-opening forms (9→10 and 9→11). Across the whole
  213-document corpus, exactly **2** documents have a LibreOffice page-count mismatch — the same two.
  So 21 of 23 are *correct in the proxy and wrong only in Google*, and no amount of writer
  page-height arithmetic will explain them. (This supersedes the count in
  `FINDINGS/00_page_count-REFUSALS-ARE-GOOGLE-RASTERISATION-1640-relay.md` §2, which lists 21 of
  **22** and omits `Account_Opening_Form_Fillable_filled`; measured here it is 21 of 23.)
* **14 of the 23 pass every LibreOffice check they have** (`05_round` 42/42, `320` 47/47,
  `332` 47/47, `341` 47/47, `350` 42/42, `351` 42/42, `353` 47/47, `361` 42/42, `401` 42/42,
  `402` 47/47, `405` 42/42, `bank-statement` 42/42, `boq` 42/42, `price-list` 42/42). They are
  *finished documents* that cannot be scored in Google at all because it adds a sheet. That is the
  leverage: for those 14, the page count is the only thing between them and CLEAN.

---

## What the writer actually emits, construct by construct

Every place page height is consumed, with the code line and the renderer behaviour:

| # | construct | where | LibreOffice | Google | evidence |
|---|---|---|---|---|---|
| C1 | `wp:anchor` per page-positioned object (`behindDoc=1`, `wrapNone`, `positionH/V relativeFrom="page"`) | `shapeRun()` `DocxWriter.java:2956-3013` (anchor open tag `:2967-2986`); `anchorShape()` `:5580-5633`; `anchoredPicture()` `:2574-2606` | draws the shape where the paper says; no flow cost | **rasterises each anchor into an image and lays it in the flow** | `…-1640-relay.md` §3-§4 (62 shapes → 46 images p1 + 16 p2; 0 shapes + `w:pgBorders` → 1 page) |
| C2 | `w:line` + `w:lineRule="exact"` on every flow line | `spacing()` `:149-157`; law documented `:78-105`; `HAIRLINE_EM` `:107`; `LINE_MODE` `:133` | advance = `w:before + w:line/20` — exact | advance = `w:before + max((w:line/240)·k·size, 0.069·size)` — **quadratic in size** | `patches/README-2026-11-13.md:80-86` residual table; `18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA.md:136-176` (max residual 0.00004 pt over 15 points) |
| C3 | one `wp:anchor` per shape instead of a section-level page frame | no `w:pgBorders` anywhere in `sectPrXml()` `:2402-2415` | n/a | a `w:pgBorders` costs zero flow; N shapes cost N images | `…-1640-relay.md` §4 |
| C4 | folio emitted as a **table row** | `table()` row loop; the folio rule is `b.y > 0.88 * pageHeightPt && isFolio(p)`, flow-lines only | row is real height → +1 page on both forms | same row, plus C1 | `HYPOTHESES.md:9-14` (measured: our page 8 is that one-character row) |
| C5 | `<wp:inline>` picture in a paragraph with **no `w:pPr`** (inherits `after=120`, `sz=22`) | `picture()` `:2565-2587`, inline emit at `:2569` | image height + 6 pt | image height + inherited mark line + 6 pt | `00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md`; **but see refutation below** |
| C6 | empty carrier paragraph per shape | `SHAPE_PARA_PPR` `:2907-2913`, `flushShapes()` `:2934-2941` | honours `w:line="1" exact` → 0.05 pt | charges a line box | **REFUTED**, see below |
| C7 | table row height `w:trHeight … w:hRule="atLeast"` + `w:cantSplit` | `:6558-6559`, `:2257` | row grows to fit content | normalises `exact`→`atLeast` and does **not** lay the row at `trHeight` | `18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` §1-§3 |
| C8 | section break `w:type w:val="nextPage"` / `w:br w:type="page"` | `:1087-1093`, `breakPage()` `:666-678` | honoured | honoured | not applicable: measured **0** `<w:br w:type="page"/>` in the 16 single-page docs (`BLOCKERS.md:170`) |
| C9 | `w:pgSz` exact + `w:pgMar` all zeros | `sectPrXml()` `:2402-2415` (`w:pgMar … ="0"` at `:2411`) | honoured | honoured — "`w:pgMar` is all zeros and both renderers honour zero. Not the lever." (`18_displacement-page-top-before-DROPPED-105000-f1x.md:58`) | not a page-count cause |

`tools/p2w-bench/google_safe.py:35-62` catalogues what Google ignores (`w:framePr`, `w:drawing`,
`wp:anchor`, `w:w`, letter `w:spacing`, `w:position`, page-top `w:before`). **C2 is not in it** — the
list has a gap that `18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` §3 states explicitly:
"it is a construct Google ignores — which `google_safe.py` does not list (it lists only
`w:position`). **That list has a gap.**" C3, C4 and C5 are also absent from it.

---

## (b) Ranked constructs, with measured reach

Reach is counted against the 23. "Measured fix" means a page delta was observed in Google, not
inferred. The per-document column is my own measurement of the source PDFs (PyMuPDF): `prims` =
drawing primitives on page 1 — a **lower-bound proxy** for the number of objects C1 emits, not an
anchor count; `Δflow` = Σ(Google advance − pitch) over page 1's text lines, from the C2 law at
k = 1.15 (Arial), i.e. how much *taller* Google's text flow is than LibreOffice's; `frame` = a path
covering ≥90 % of the page in both axes.

| rank | construct | documents reached | measured fix | evidence |
|---:|---|---:|---:|---|
| **1** | **C1 — one `wp:anchor` per page-positioned object** (`shapeRun` `:2956-3013`) | **22 of 23** (all but `350`, whose page 1 carries 1 primitive and 0 anchors) | **1 proven by removing the objects** (`60_page_border` 2→1); 1 more by the landed paragraph merge (`361`) | 1640 §3/§4: 62 anchors → 46 images on p1 + **16 on p2, page 2 has 0 characters**; identical docx with 0 shapes + `w:pgBorders` → **1 page, 689 chars on p1**; LibreOffice 1 page in both |
| **2** | **C3 — the page frame is emitted as N shapes, not as `w:pgBorders`** | **5 of 23** carry a full-page frame: `041122`, `Account_Opening_Form_Fillable_filled`, `332_bom_on_drawing`, `351_omr_answer_sheet`, `60_page_border` | **1** (`60_page_border`, 2→1) | same probe; `sectPrXml()` has no `w:pgBorders` at all |
| **3** | **C2 — `w:line`+`exact` quadratic in size** | **1 of 23** (`405_sheet_music_lyrics`, Δflow **+131.8 pt**); **0** as a page-count cause on the other 22 (their Δflow is **negative**, −19.7 to −304.5 pt) | 0 | law `DocxWriter.java:78-105`; residual table `patches/README-2026-11-13.md:80-86` (+0.124 pt/line at 12 pt, +1.265 at 20 pt); my measurement, table below |
| **4** | **C4 — folio written as a table row** | **2 of 23** (`041122`, `Account_Opening_Form_Fillable_filled`) | measured for the LO half (+1 page each), not for Google | `HYPOTHESES.md:9-14`; the flow-line folio anchor exists and cannot fire on a table row |
| 5 | C5 — inline picture in a `pPr`-less paragraph | **0 of 23** | 0 | **refuted for `350`**: its page 2 carries 8 real characters and its docx carries **1** anchor (`…-1640-relay.md` §3), and the source has no picture to inline at all — `08_image_count` source = 0 and `14_filled_shapes` source = 0 (`gverify-lo/350_question_paper.json`). The construct is real for full-bleed scan pages but no document in this 23 is one |
| — | C6 — empty carrier paragraph per shape | **0** | 0 | **REFUTED**: 18 of 22 have no drawing-only paragraph; adding a trailing empty `<w:p>` to `60_page_border` leaves it at 2 pages (`…-1640-relay.md` §1-§2). The 0.83 pt/paragraph figure is a measurement on a document (108 carriers) that no longer exists in the tree |
| — | C7 — `w:trHeight` / `w:hRule` / `w:cantSplit` | **0** | 0 | **REFUTED twice**: Google normalises `exact`→`atLeast` and lays 18.0/19.0/20.0 on rows written 360/380/… (`GOOGLE-IGNORES-TRHEIGHT-1045` §1-§3); and the wrap-charge build measured over 124 document-measurements: **0 improve, 18 worse** (`HYPOTHESES.md:250-275`) |
| — | column-page shape merge (`columnPage()`→`emitBlock()`) | **1** (`361`) | **LANDED** at 16:34, 361 2→1 at 41/42 | `ATTEMPTS.json` → `00_page_count.history[4]`. **Do not re-propose: already in the tree.** |

### The C2 measurement that splits the class

Σ over page 1's text lines of `max((pitch·20/240)·1.15·size, 0.069·size)` minus Σ pitch, measured
from each source PDF:

| document | median size | median pitch | Δflow (pt) |
|---|---:|---:|---:|
| `405_sheet_music_lyrics` | 7.5 | 22.0 | **+131.8** |
| `402_calendar_month_grid` | 9.5 | 28.0 | −19.7 |
| `401_trifold_brochure` | 8.0 | 14.0 | −33.7 |
| `305_vaccination_certificate` | 7.5 | 3.8 | −59.9 |
| `60_page_border` | 6.2 | 4.4 | −62.0 |
| `05_round_company_seal_curved_text` | 7.0 | 3.9 | −86.1 |
| `361_product_catalogue_grid` | 7.0 | 18.0 | −89.9 |
| `314_tender_rfp_boq` | 8.0 | 15.0 | −96.4 |
| `326_itr_computation` | 8.0 | 15.0 | −100.8 |
| `320_balance_sheet_statutory` | 7.5 | 14.0 | −105.9 |
| `353_admit_card` | 7.0 | 11.0 | −112.5 |
| `351_omr_answer_sheet` | 5.5 | 14.0 | −122.4 |
| `333_datasheet_spec_tables` | 7.2 | 14.0 | −132.8 |
| `390_wide_data_appendix` | 5.4 | 13.0 | −133.3 |
| `341_shipping_manifest` | 6.2 | 13.0 | −145.2 |
| `350_question_paper` | 8.0 | 16.0 | −187.2 |
| `price-list-2col-dense-right-aligned` | 8.0 | 16.4 | −189.4 |
| `403_crossword_puzzle` | 5.0 | 22.0 | −195.2 |
| `332_bom_on_drawing` | 6.5 | 15.0 | −233.0 |
| `boq-horizontal-rules-only` | 7.0 | 18.4 | −263.4 |
| `Account_Opening_Form_Fillable_filled` | 6.0 | 14.7 | −272.2 |
| `bank-statement-horizontal-rules-only` | 6.6 | 18.4 | −277.4 |
| `041122-Account_Opening_Form` | 6.0 | 14.7 | −304.5 |

**This is the single most discriminating measurement in the analysis.** On 22 of 23 documents
Google's *text* flow is shorter than LibreOffice's — by up to 304 pt, a third of the sheet — yet
Google renders **more** pages. A per-line drift therefore cannot be the cause; something must add a
discrete block of flow on top of the text, and the only measured candidate is C1: N rasterised
images, each with its own box in the flow. `60_page_border` is the arithmetic: 46 images fit
alongside 654 pt of text on an 842 pt sheet (~4 pt each), the 16 remaining overflow.

`405_sheet_music_lyrics` is the one document where C2 is a page-count cause in its own right
(+131.8 pt), and it is also a C1 document (306 primitives).

### Not explained by any of the above

**`350_question_paper`.** Measured: 1 drawing primitive, 0 anchors, 1 stroke line, 0 images, 0
anchored runs (`gverify-lo/350_question_paper.json`), Google's text flow 187 pt *shorter* than
LibreOffice's, 4.6 pt of slack below the last ink — and yet 2 pages, with page 2 carrying 8 real
characters (`…-1640-relay.md` §3). Something adds ≥190 pt that neither C1, C2, C5, C6 nor C7
accounts for. **Not measured.** Do not spend a slot on it until a Google probe of its docx names
the construct.

---

## (c) The one patch to apply

**Why this one and not the bigger one.** The widest construct (C1, 22 of 23) has no measured
*reduction* that is safe: coalescing N anchors into one `wpg:wgp` group puts a page-sized union bbox
into the flow as a single image, which is predicted to overflow *worse*, and nothing in the repo has
measured a group in Google. C3, by contrast, is the only page-count fix in this class with a
**measured** Google delta, and the 1640 finding named it as "the shape of the fix for every
border/frame document" and did not build it.

**File:** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`
**Functions:** `sectPrXml(float,float,int,float)` at `:2402-2415`; its body-sectPr call site at
`:1317-1319`; `pageBody()` shape loop at `:1394-1412`.

**Change 1 — a Ctx flag.** Add beside `int pageSeq;` (`:967`):

```java
/** True when this page's furniture is a closed frame, emitted as w:pgBorders instead of N shapes. */
boolean pageFrame;
```

**Change 2 — detect the frame and skip its shape** (in `pageBody()`'s shape branch, `:1394-1412`,
immediately after `if (sh.consumed) continue;`):

```java
// A page frame is the one piece of furniture that is a SECTION property, not an object:
// w:pgBorders costs Google no flow at all, while each anchored edge costs it an image
// (~4 pt measured on 60_page_border: 46 images fit beside 654 pt of text, 16 do not, and
// page 2 carries 0 characters). Measured: same docx, 62 shapes -> 2 pages; 0 shapes +
// w:pgBorders -> 1 page, 689 characters on page 1. FINDINGS/00_page_count-REFUSALS-ARE-
// GOOGLE-RASTERISATION-1640-relay.md §4.
if (!ctx.pageFrame && sh.lineRgb >= 0 && sh.fillRgb < 0
        && sh.wPt >= 0.90f * ctx.pageWidthPt && sh.hPt >= 0.90f * ctx.pageHeightPt) {
    ctx.pageFrame = true;
    continue;
}
```

**Change 3 — emit it** in `sectPrXml(float wPt, float hPt, int cols, float gapPt)`, after the
`colsXml` term at `:2413`:

```java
+ (frame ? "<w:pgBorders w:offsetFrom=\"page\">"
        + "<w:top w:val=\"single\" w:sz=\"8\" w:space=\"24\" w:color=\"auto\"/>"
        + "<w:left w:val=\"single\" w:sz=\"8\" w:space=\"24\" w:color=\"auto\"/>"
        + "<w:bottom w:val=\"single\" w:sz=\"8\" w:space=\"24\" w:color=\"auto\"/>"
        + "<w:right w:val=\"single\" w:sz=\"8\" w:space=\"24\" w:color=\"auto\"/>"
        + "</w:pgBorders>" : "")
```

with a `boolean frame` parameter threaded from the call site at `:1318`
(`sectPrXml(secW, secH, secCols, secGap, ctx.pageFrame)`). **Gate the whole thing on a single-page
document** (`ctx.pageSeq <= 1`) so the body `sectPr` is the only section and no per-page section
break is introduced — the two nine-page account forms are out of scope for this patch and are
documented as needing C4 as well.

**Expected page delta.** `60_page_border` **2 → 1** (measured, `…-1640-relay.md` §4, same text, 689
characters on page 1). Same delta predicted for the other four frame documents — `332_bom_on_drawing`,
`351_omr_answer_sheet`, `041122`, `Account_Opening_Form_Fillable_filled` — where it is **not
measured**; for the two account forms it removes one of their five extra pages at most.

**The one question this patch must answer before it is kept, and it is cheap.** The 1640 probe did
not establish that Google *draws* the `w:pgBorders` frame: "the only drawing in either export is a
single rect at [0.0, 0.0, 595.5, 842.2] — the full page — in both variants". So measure, in the same
Google round trip, **both** (i) page count == source and (ii) ink exists near all four page edges
(four segments at ~24 twips inset). If the count is 1 and the frame is drawn, keep it. If the count
is 1 and the frame is gone, `32_stroke_lines` / `14_filled_shapes` will newly fail and the document
has traded one defect for another — in that case the fallback is **4 composite shapes per page (one
per edge) instead of N**, which keeps the frame and cuts 62 objects to 4.

**Watch on the corpus run.** `01_page_count` (target), `32_stroke_lines`, `14_filled_shapes`,
`27_text_off_page`, `47_margins`. Any document whose score drops without its page count moving is a
frame Google dropped; revert it for that document rather than the whole class.

---

## Attempts already made at this class — what is refuted

From `tools/p2w-bench/ATTEMPTS.json` → `00_page_count` (5 attempts, `status: OPEN`, `last_engine
0be925ff`) and `FINDINGS/`:

| attempt | date | outcome | verdict |
|---|---|---|---|
| inline-picture paragraph carries the line (`350`) | 23 Nov 05:09 | lead, 0 moved | **refuted for 350** by 1640 §3 (page 2 has 8 characters, docx has 1 anchor, source has 0 images). Patch never compiled. |
| empty carrier paragraph costs ~0.83 pt (`301_lab_report_panel`) | 23 Nov 05:30 | corrected to a lead, 0 moved | **REFUTED**: 18 of 22 documents have no carrier paragraph at all, and `60_page_border` — the document that best shows the fault — has none; adding a trailing empty `<w:p>` changes nothing (2 pages before and after). |
| shape paragraphs → runs in the existing paragraph | 23 Nov 08:11 | kept | **landed**; it is why `SHAPE_PARA_PPR`/`flushShapes()` exist. It does not change the object count, so it cannot fix the page count. |
| column-page shape merge (`columnPage()`→`emitBlock()`) | 23 Nov 11:28 → 16:34 | partial, 2 moved | **LANDED.** 361 2→1 at 41/42 (Google), 375 2→1, 35/42→37/42. Do not re-propose. |
| deleting all shapes → 1 page | 23 Nov (probe) | diagnostic | proves the cause, is not a fix (it deletes the page furniture). |

Also refuted in adjacent work and not to be re-derived: table row heights / wrap charge
(`HYPOTHESES.md:250-275`, 124 document-measurements, 0 improve, 18 worse), `w:hRule="exact"`
(`GOOGLE-IGNORES-TRHEIGHT-1045` §1), `w:before` inside a row (§2), `w:pgMar` as the page-top lever
(`18_displacement-page-top-before-DROPPED-105000-f1x.md:58`), and the "split the box / constant
`w:line`" family for C2, which keeps the pitch but drops **every baseline by 0.2 × box** and
measured `300_prescription_rx` 55/58 → 53/58 (`patches/README-2026-11-13.md:106-130`).

---

## Two instrument defects a fixer will hit

1. `regress.py` skips `page_count_refused` in both readers, so **scored → refused is invisible** and
   the gate prints PASS. Four documents were scored on 22 Nov and refused on 23 Nov this way
   (`FINDINGS/00_page_count-FOUR-DOCS-LOST-A-PAGE-0625-agent.md`; `BLOCKERS.md:227`).
2. `benchmarks/gverify/` still carries the pre-merge refusal for `361`, and 21 of the 23 records have
   no `engine` stamp, so `gverify.py --report` cannot attribute them to HEAD. Re-measure before
   quoting 23.
