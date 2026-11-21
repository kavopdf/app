# Why the "rule carrier" patch makes documents worse in the LibreOffice proxy

**Question.** `tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch` replaces every PDF
rule (a thin filled rectangle, emitted as a floating `<w:drawing>`) with a floating 1×1 `<w:tbl>`
whose single cell border draws the rule. Measured 2026-11-21 04:00 over the 213-document corpus:
52 documents better, 54 worse, `regress.py --check` refused. Two explanations are on the table:

* **H1** (last run's explanation, `tools/p2w-bench/FINDINGS/32_stroke_lines-CARRIER-54-REGRESSIONS-0400-f1x.md`):
  the carrier table is **nested inside a table cell** (`w:tc`), so it displaces that cell's flow.
* **H2** (from a code read of the patch): carrier tables are **always body-level**, and the damage
  comes from **multiple floating tables per page** stacking/displacing body flow, so displacement
  should scale with **carriers per page**.

**Verdict up front: H1 is falsified. H2's mechanism survives; H2's scaling claim does not.**
Every carrier in every document measured sits at `tc-depth 0` with `w:body` as its parent — there is
no nested carrier anywhere in the output. What the measurements do show is that the regressed
documents **overflow the page**: 7 of 8 regressed documents render to 2–3 pages where the source has
1, while none of the 14 unchanged documents gains a page. That is body-flow displacement, H2's
mechanism. But the magnitude does **not** scale with carriers per page: across the 8 regressed
documents the correlation between carrier count and regression is ~0 (Pearson −0.19, p = 0.66), and a
2-carrier document regressed by +13.80 while eleven 2–3-carrier documents did not move at all.

---

## Method (all numbers below were measured in this run, 22 Nov 2026, IST)

| step | what was run |
|:--|:--|
| clone | `git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS` (nothing pushed, nothing committed, no tracked file edited) |
| HEAD engine | `bash tools/p2w-bench/build-engine.sh` in `CS` — "engine built - ConvertAll ready (36s)" |
| patched engine | `cp -a CS CS-patched && git apply tools/p2w-bench/patches/rule-carrier-horizontal-only-2008.patch` (applies cleanly: `DocxWriter.java | 193 ++++`), same build, 34 s |
| corpus | the 4 release zips (`p2w-all-groups`, `p2w-batch-1`, `pdf-to-word-test-corpus-v3`, `p2w-round2-additions`) + `benchmarks/corpus-extra` + `benchmarks/realworld` → **213 PDFs**, as `p2w.py:corpus()` builds it |
| convert | `ConvertOne <pdf> <outdir>`, **one JVM per document**, classpath exactly as `p2w.py:docx()` builds it |
| score | `p2w.soffice_pdf(docx, out)` then `p2w.measure_doc(source.pdf, render.pdf)`; score is **`share@5px`** (higher = worse), the axis `PIPELINE.md` ranks by. scipy present (exact EDT), not the dilation ladder |
| tc-depth | `word/document.xml` parsed with lxml: for every `<w:tbl>` carrying a `<w:tblpPr>`, count `w:tc` ancestors and record the parent element |
| carriers/page | `w:tblpY` (twips) ÷ `w:pgSz/@w:h` (= 16838 twips, every document), +1. All 22 documents measured are **single-page sources**, so carriers/page equals the carrier count; the per-page split is reported for completeness, not as a second independent variable |

Documents measured: **22** — the 7 regressed documents named in the 04:00 finding, 4 further
documents screened from `benchmarks/RANKING-BASELINE.csv` (changed by the patch, `fails_32`, one page,
score 0.1–1.0), and 11 documents the finding called "unchanged or better". `share@5px` deltas
reproduce the 04:00 numbers to within rounding on every document that appears in both runs
(e.g. `08_two_overlapping_stamps` patched **77.23** vs 77.23 in the finding; `50_invoice_coloured_total_row`
patched **84.13** vs 84.13; `product-catalogue-code-left-price-right` **85.32** vs 85.32;
`02_stamp_rotated_15deg_upleft` **69.22** vs 69.22; `315_gazette_notification` **15.90** vs 15.87).
HEAD reads `50_invoice_coloured_total_row` at **0.24** where the finding quotes 0.00 — same direction,
2.4 tenths of a point apart; every other HEAD value agrees with its baseline to the digit.

---

## H1 test — tc-depth of every carrier table

| document | carriers | max tc-depth | parent of every carrier | non-carrier tables |
|:--|--:|--:|:--|--:|
| product-catalogue-code-left-price-right | 21 | **0** | `w:body` ×21 | 1 |
| 50_invoice_coloured_total_row | 10 | **0** | `w:body` ×10 | 2 |
| 08_two_overlapping_stamps | 9 | **0** | `w:body` ×9 | 1 |
| 02_stamp_rotated_15deg_upleft | 16 | **0** | `w:body` ×16 | 2 |
| 79_inr_indian_digit_grouping_table | 8 | **0** | `w:body` ×8 | 1 |
| 03_stamp_vertical_90deg | 19 | **0** | `w:body` ×19 | 2 |
| price-list-right-aligned-amounts | 41 | **0** | `w:body` ×41 | 1 |
| 315_gazette_notification | 2 | **0** | `w:body` ×2 | 1 |
| 17 / 18 / 19 / 24 / 27 / 37 / 45 / 47 / 49 / 53 / 70 / 74 (12 docs) | 2 each | **0** | `w:body` ×2 | 0–2 |
| 334_patent_document, gst-invoice-with-qr-code | 3 each | **0** | `w:body` ×3 | 0–1 |

**22 of 22 documents: max tc-depth = 0. Every one of the 156 carrier tables counted in this run has
zero `w:tc` ancestors and `w:body` as its direct parent.** Not one carrier table is nested inside a
table cell, and no carrier table has a `w:tbl` ancestor either. The "nested floating table displaces
the cell's flow" mechanism cannot be operating, because the construct it names is not in the output.

The reason is visible in the patch itself: `shape()` now calls `ruleCarrier()`, which appends a bare
`<w:tbl>` to the block buffer at the point the shape's block was being emitted, and the patch's own
comment says "a `w:tbl` is not a legal child of a `w:p`, so this is written where a block goes
(`emitBlock`), never inside a paragraph". The document that produced H1 conflated two different
things: *the shape's box sitting on a table's grid line* (which is true of `315_gazette_notification`,
whose rules are drawn over a table) with *the carrier being emitted inside a `w:tc`* (which never
happens).

---

## H2 test — carriers per page vs regression magnitude

`share@5px` delta = patched − HEAD, in points of share (positive = worse). Page counts are the
LibreOffice render's, from the same `p2w.soffice_pdf` output that was scored.

| document | carriers | max tc-depth | carriers/page | delta | head → patched share@5 | rendered pages (src → patched) |
|:--|--:|--:|--:|--:|:--|:--|
| product-catalogue-code-left-price-right | 21 | 0 | 21 | **+85.26** | 0.06 → 85.32 | 1 → **3** |
| 50_invoice_coloured_total_row | 10 | 0 | 10 | **+83.89** | 0.24 → 84.13 | 1 → **2** |
| 08_two_overlapping_stamps | 9 | 0 | 9 | **+76.91** | 0.32 → 77.23 | 1 → **2** |
| 02_stamp_rotated_15deg_upleft | 16 | 0 | 16 | **+68.86** | 0.36 → 69.22 | 1 → **2** |
| 79_inr_indian_digit_grouping_table | 8 | 0 | 8 | **+32.04** | 0.52 → 32.56 | 1 → **2** |
| 03_stamp_vertical_90deg | 19 | 0 | 19 | **+31.32** | 17.84 → 49.16 | 1 → **2** |
| price-list-right-aligned-amounts | 41 | 0 | 41 | **+15.57** | 0.78 → 16.35 | 1 → **2** |
| 315_gazette_notification | 2 | 0 | 2 | **+13.80** | 2.10 → 15.90 | 1 → 1 |
| 17_three_column_widths_txtpos | 2 | 0 | 2 | 0.00 | 0.02 → 0.02 | 1 → 1 |
| 18_centred_heading_left_body_txtpos | 2 | 0 | 2 | 0.00 | 0.00 → 0.00 | 1 → 1 |
| 19_hanging_indent_txtpos | 2 | 0 | 2 | 0.00 | 0.00 → 0.00 | 1 → 1 |
| 24_address_block_indents_txtpos | 2 | 0 | 2 | 0.00 | 0.00 → 0.00 | 1 → 1 |
| 27_two_column_left_short_txtpos | 2 | 0 | 2 | 0.00 | 0.68 → 0.68 | 1 → 1 |
| 37_font_not_embedded_substitution | 2 | 0 | 2 | 0.00 | 0.56 → 0.56 | 1 → 1 |
| 45_coloured_callout_box | 2 | 0 | 2 | 0.00 | 0.07 → 0.07 | 1 → 1 |
| 47_grey_body_black_headings | 2 | 0 | 2 | 0.00 | 0.00 → 0.00 | 1 → 1 |
| 49_coloured_background_block_paragraph | 2 | 0 | 2 | 0.00 | 0.00 → 0.00 | 1 → 1 |
| 53_single_space_body_15_headings | 2 | 0 | 2 | 0.00 | 0.00 → 0.00 | 1 → 1 |
| 70_magazine_drop_cap_photo_caption | 2 | 0 | 2 | 0.00 | 0.66 → 0.66 | 1 → 1 |
| 74_balance_sheet_indented_subitems | 2 | 0 | 2 | 0.00 | 0.00 → 0.00 | 1 → 1 |
| 334_patent_document | 3 | 0 | 3 | 0.00 | 0.01 → 0.01 | 1 → 1 |
| gst-invoice-with-qr-code | 3 | 0 | 3 | 0.00 | 0.12 → 0.12 | 1 → 1 |

### Correlation (n = 22, carriers/page vs delta)

| population | Pearson r | p | Spearman ρ | p |
|:--|--:|--:|--:|--:|
| all 22 documents | **0.491** | 0.021 | **0.829** | <0.001 |
| the 8 regressed documents only | **−0.186** | 0.659 | **0.190** | 0.651 |

The whole-document correlation is carried by the **zero / non-zero split**, not by a dose–response:
eleven documents with 2–3 carriers sit at exactly 0.00 delta, and the only reason ρ is high is that
the large-carrier documents are the non-zero ones. Once you look only at documents that actually
regressed, **carrier count explains nothing** (r = −0.19): 41 carriers gave +15.57 while 10 carriers
gave +83.89, and the 2-carrier `315_gazette_notification` gave +13.80.

### What the mechanism actually is: page overflow, not stacking per se

The render's page count is the discriminating measurement, and it splits the population perfectly:

* **7 of the 8 regressed documents gained a page** in the LibreOffice render (1 → 2, and
  `product-catalogue-code-left-price-right` 1 → 3). Their `share@5px` signature is `content-loss`
  because page 1 is now largely empty and the ink that should be on it has been pushed onto a page
  the source does not have — `product-catalogue-code-left-price-right` falls to `text_recall` 6.59 %
  with 4 939 of our 33 904 ink pixels left on page 1.
* **0 of the 14 unchanged documents gained a page.**
* `315_gazette_notification` is the exception in both tables: it regressed **+13.80 while staying on
  one page** (`max_pt` 17.76, `invent5` 9.71 — ink moved inside the page, not off it). Its two
  carriers sit over an existing table, which is exactly the "the shape's box coincides with a cell or
  row edge" case the 04:00 finding pointed at — a different sub-mechanism from the overflow, and the
  one that H1's author was reaching for, mis-stated as nesting.

So the surviving mechanism is H2's *body-level flow displacement*: each carrier is a body-level block,
and enough of them push the body's flow past the page's bottom. What the data rejects is H2's
*proportional* form — displacement does not scale with carriers per page. There is a threshold
(every document with ≥ 8 carriers overflowed; every document with 2–3 carriers and no pre-existing
table did not), and above the threshold the magnitude is set by something else: the number of body
blocks that get pushed off page 1, which is a property of where the carriers sit in the flow, not of
how many there are.

---

## Control — documents that IMPROVED under the patch

**Not measured: no improved document was found.** Fifteen candidate documents were converted and
scored on both engines specifically to obtain three improvers, and **every one of them came back at
delta 0.00** (the eleven 2-carrier documents, `334_patent_document`, `gst-invoice-with-qr-code`,
`70_magazine_drop_cap_photo_caption`, `27_two_column_left_short_txtpos`). This is consistent with
`benchmarks/RANKING-BASELINE.csv`: the documents this patch changes are overwhelmingly already at
`share@5px` 0.00 in the proxy, so in the LibreOffice proxy there is little headroom to improve — the
52 "better" documents of the 04:00 run were not reproduced here, and the run's 20-minute budget did
not stretch to locating them. **Any statement about improvers' carriers per page would be
estimation, so it is not made.**

The control that *is* measured is stronger for the question at hand, because it holds carriers per
page fixed: **`315_gazette_notification` regressed +13.80 with 2 carriers, while eleven other
documents with 2 carriers moved by exactly 0.00.** Carriers-per-page alone therefore neither
predicts nor sizes a regression. If improvers were later shown to carry many carriers per page, that
would weaken H2 further — it would not rescue H1, which is dead on the XML alone.

---

## Verdict

**H1 does not survive.** The construct it names — a carrier table nested inside a `w:tc` — does not
exist in the patched output: across 22 documents and 156 carrier tables, **max tc-depth is 0 in every
document and every carrier's parent is `w:body`**. There is no nesting to displace a cell's flow, and
the patch's own comment states that a `w:tbl` is written at block level because it is not a legal
child of a `w:p`. The 04:00 finding inferred nesting from "a document with 21 carriers is not a page
with 21 rules"; the count is real, the nesting is not.

**H2 survives on mechanism, not on its scaling claim.** The carriers are body-level, and the damage
is body-flow displacement — proven by the page counts: **7 of 8 regressed documents overflow from 1
page to 2–3 pages, and 0 of 14 unchanged documents do.** But the regression does not scale with
carriers per page: ρ = 0.829 across all 22 documents collapses to ρ = 0.19 (r = −0.19, p = 0.66) once
the zero-delta documents are removed, and a 2-carrier document regressed as hard as a 41-carrier one
did not. The relationship is a threshold plus a flow-position term, not a dose–response in carrier
count. `315_gazette_notification` regressing on a single page at 2 carriers shows a second,
independent sub-mechanism: a carrier laid over an existing table displaces ink inside the page.

**What would overturn this.**
1. *Against the falsification of H1:* any patched `.docx` in which a `<w:tbl>` carrying `<w:tblpPr>`
   has a `w:tc` ancestor. One such document, reproducibly, reopens H1 — the measurement here is a
   direct structural read of the emitted XML, so it is falsifiable by a single counter-example.
2. *Against H2's mechanism:* a regressed document that keeps the source's page count and shows no
   `invent5`/`max_pt` movement (i.e. the ink neither leaves the page nor moves within it). The one
   such case found here (`315_gazette_notification`) is an in-page displacement, not a counter-example,
   but a regressed document with *neither* symptom would be.
3. *Against H2's threshold:* an improved or unchanged document carrying ≥ 8 carriers per page, or a
   regressed document with a single carrier that gains a page. The improver arm of this test is the
   one measurement still missing — the 52 improved documents of the 04:00 run were not located inside
   this run's budget.

## Files

    /scratch/work/deltas.json      per-document head/patched share@1/5/10, text_recall, signature
    /scratch/work/h1.json          per-document carrier count, tc-depth histogram, parents, per-page split
    /scratch/work/rows.json        the joined table above
    /scratch/work/CS                HEAD clone, built; /scratch/work/CS-patched  patched copy, built
    /scratch/work/dx-head, dx-patched   ConvertOne output, one JVM per document
    /scratch/work/render/head, render/patched   LibreOffice renders that were scored
