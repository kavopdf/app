# What dominates the SSIM loss — 213 documents, Google render

Read-only analysis of `kavopdf/app` at the cloned HEAD (shallow clone, 27 Nov 2026). No repo file was
modified, no commit, no push, no Java build, no PDF conversion through the pipeline. Every number
below is either quoted with `file:line`, computed from a committed CSV, or measured in this sandbox
from the corpus PDFs that are committed in the repo.

---

## 0. Where the number actually comes from (the question's premise needs one correction)

The "4 at 99%+, 10 at 95%+, median 84.1% over 213 scored" row is **not** `share5`. It is
`ssim_pct` from `benchmarks/PIXEL-SCORES-112-DOCS.csv` (213 data rows + header = 214 lines):

* producer of the row: `tools/p2w-bench/report.py:1453-1457` and the duplicate at `:1468-1472`
* data file: `benchmarks/PIXEL-SCORES-112-DOCS.csv`, column `ssim_pct`, `ssim_method=half-res-stride2`
* the same row is printed verbatim in `tools/p2w-bench/REPORT.md:15` and `LAST-MESSAGE.md:12`

`share5` is a **different metric on a different renderer**. It lives in `benchmarks/RANKING.csv`
(`share1..share10`, `median_pt`, `p90_pt`) and is computed by `benchmarks/p2w.py` from the
**LibreOffice** render (`p2w.py` drives `soffice`; see `SOFFICE_FAIL_LIMIT`, `p2w.py:672`). Its meaning
is "share of ink more than 5 px from where the source put it", and the 99% bar is `share5 <= 1.0`
(`p2w.py:827`). So the file name says 112 but holds 213 documents, and "the share5 table" and "the
SSIM table" are two different tables that happen to be discussed in the same breath.

This matters for the question, because the two disagree in a way that is itself the finding (§4).

---

## 1. Band histogram — 213 scored documents

| SSIM band | documents | share |
|---|---:|---:|
| 99 – 100 | **4** | 1.9 % |
| 95 – 99 | **6** | 2.8 % |
| 90 – 95 | **29** | 13.6 % |
| 80 – 90 | **97** | 45.5 % |
| 70 – 80 | **49** | 23.0 % |
| < 70 | **28** | 13.1 % |
| **total** | **213** | |

median **84.11**, mean **81.41**, sd **10.71**, min **41.02**, max **99.84**.
Quantiles: p01 45.79 · p05 60.82 · p10 65.71 · p25 76.44 · p75 88.77 · p90 92.15 · p95 94.62 · p99 99.09.

175 of 213 documents (82.2 %) sit between 70 and 95. The single most crowded band is 80–90, with 97
documents — more than the two bands below it combined.

## 2. Worst 15 documents

| # | document | SSIM | ink_iou_d1 | pages src→render |
|---:|---|---:|---:|---|
| 1 | Account_Opening_Form_Fillable_filled | 41.02 | 7.90 | 9 → 11 |
| 2 | 041122-Account_Opening_Form | 41.30 | 8.06 | 9 → 11 |
| 3 | itr-computation-with-slab-table | 44.95 | 6.77 | 1 → 1 |
| 4 | very-long-single-column-table | 51.97 | 10.36 | 3 → 3 |
| 5 | boq-tender-bill-of-quantities | 54.54 | 14.49 | 1 → 1 |
| 6 | price-list-2col-dense-right-aligned | 55.90 | 24.45 | 1 → 1 |
| 7 | bank-statement-5-pages | 56.73 | 26.40 | 5 → 5 |
| 8 | newspaper-2col-fullwidth-headline | 58.63 | 57.98 | 1 → 1 |
| 9 | electricity-bill | 59.94 | 28.48 | 1 → 1 |
| 10 | marksheet-university-consolidated | 60.42 | 11.56 | 1 → 1 |
| 11 | table-with-no-header-row | 60.70 | 12.56 | 1 → 1 |
| 12 | mobile-bill | 60.90 | 11.74 | 1 → 1 |
| 13 | insurance-policy-schedule | 61.17 | 13.13 | 1 → 1 |
| 14 | newsletter-3col-header-footer | 61.59 | 60.01 | 1 → 1 |
| 15 | salary-slip-factory-wages | 61.83 | 12.07 | 1 → 1 |

Thirteen of the fifteen are table- or form-dense single pages. Only two have a page-count defect.
Their ink overlap (7–28 %) is low, so these are genuinely broken documents, not measurement noise.

## 3. Concentrated or uniform? Uniform, and the arithmetic is unambiguous

Deficit accounting against a perfect 100 (total deficit 3,959.6 points, mean 18.59 per document):

| population | share of the total deficit |
|---|---:|
| worst 5 | 6.7 % |
| worst 15 | **16.9 %** |
| worst 28 (all below 70) | 28.0 % |
| worst 50 | 42.9 % |

Counterfactuals (each computed, not estimated):

| if these became perfect | resulting median | resulting mean |
|---|---:|---:|
| worst 15 → 100 | **85.09** | 84.55 |
| worst 50 → 100 | 88.52 | — |
| worst 100 → 100 | 97.43 | — |

**Fixing every one of the worst 15 completely — all of them, to 100 — moves the median from 84.11 to
85.09, one point.** To move the median to 99 at least 107 of the 213 documents must reach 99+; four
do today. The median is set by documents 100–110 in the ranking, i.e. by the 80–90 crowd, not by the
tail. Any per-document fix that lands on the worst 15 is provably moving a number that is not the goal.

## 4. Is the measurement normalised? No — and that is why the two tables disagree

How the render is aligned before comparison (`tools/p2w-bench/pixel-score.py`):

* both sides are rasterised at the **same** DPI, 150 (`DEFAULT_DPI`, `:64`; `render_page`, `:76-84`),
  in greyscale, so a page at the same physical size lands on the same grid;
* `to_canvas` (`:99-116`) pads the smaller page with white **at the top-left corner and explicitly does
  not resample** — the docstring says "NO SCALING" (`:102`);
* SSIM is computed as `ssim(a[::2,::2], b[::2,::2], data_range=255)` — half resolution, stride not
  interpolation (`:161-168`), default skimage window;
* `align` is **off by default** (`score(..., align=False)`, `:202`) and the batch path never turns it on
  (`pixbatch.py:92-93` calls `mod.score(src, render, dpi)` with no `align`), so `best_offset_px` and
  `agree_at_offset` (`:177-200`, `:253-255`) were **never recorded for any corpus document**.

So: no scaling, no crop-to-content, no registration, no per-page normalisation. The number is a raw
grid comparison of two different renderers' rasters.

The consequence is visible in the two tables. `share5` (LibreOffice, ink-within-5-px):

* median `share5` = **0.12 %** over 212 documents
* **152 of 212** documents already pass the 99 % bar (`share5 <= 1.0`) in LibreOffice
* those 152 documents' Google SSIM: **median 84.67, four at 99+, nine at 95+**
* correlation between `share5` and `ssim_pct` over 212 joined documents: **−0.32** (weak)
* the best single correlate of SSIM in `RANKING.csv` is `share1`, the *1-pixel* displacement measure:
  **−0.50**

A document whose ink is within 5 px of the source everywhere (LibreOffice) scores 84.67 % SSIM in
Google. The layout is not what SSIM is measuring; the fine-scale ink agreement is.

## 5. What the loss is actually made of — measured on this box

Using the repo's own computation (150 dpi grey, top-left canvas pad, `ssim(a[::2,::2], b[::2,::2])`),
on the corpus PDFs that are committed in the repo (`benchmarks/realworld/`, `benchmarks/corpus-extra/`):

**(a) Two different rasterisers of the *identical* vector file, zero geometric difference**
(MuPDF 2.1 at 150 dpi vs poppler `pdftoppm` at 150 dpi, `best_offset` = (0,0) on every pair, so no
registration error to recover):

| page | ink coverage | SSIM |
|---|---:|---:|
| 602_bookmarked_annual_report p1 | 0.29 % | **99.72** |
| 602_bookmarked_annual_report p2 | 1.08 % | 98.60 |
| 601_fillable_admission_form p1 | 2.17 % | 96.88 |
| 600_reviewed_invoice p1 | 3.07 % | 97.37 |
| Account_Opening_Form_Fillable_filled p1 | 13.52 % | **86.69** |
| 041122-Account_Opening_Form p1 | 13.35 % | **87.09** |

Same vectors, same positions, same size — and the score falls from 99.7 to 86.7 as the page gets
inkier. Aligning the pair does not help: the best offset is (0,0) and the score does not move. This is
the metric's ceiling for a dense page, and it is not about the document at all.

**(b) A face substitution at *identical* positions, sizes and colours** (same strings, same baselines,
10 pt / 13.2 pt leading, 9.3 % ink, built with PyMuPDF):

| face pair | SSIM |
|---|---:|
| DejaVu Serif → Liberation Serif | **65.07** |
| DejaVu Sans → Liberation Sans | **65.74** |
| DejaVu Sans Mono → Liberation Mono (0.325 % advance difference) | **74.17** |

**(c) Pure registration error, same face, same text** (9.3 % ink):

| perturbation | SSIM |
|---|---:|
| identical | 100.00 |
| shift 1 px x | 84.43 |
| shift 1 px y | 84.62 |
| shift 1 px x + y | 75.05 |
| shift 2 px x | 66.66 |
| leading +0.2 pt over 48 lines | 60.50 |
| leading +1.0 pt over 48 lines | 55.43 |

The corpus median of 84.11 sits exactly where a one-pixel misregistration puts a text page (84.4), and
between the "different rasteriser" floor (87) and the "substituted face" cost (65–74).

---

## 6. The single systemic construct most likely to be capping the median

**Google Docs has none of the faces these PDFs are set in, so it substitutes, and a substitute face has
different advances — every line is a different width and everything downstream of it moves.** This is
stated by the repo's own tooling, as the reason `grender.py` exists at all:

> "LibreOffice has DejaVu Serif, Liberation Serif and Liberation Sans installed, so it draws every one
> of these PDFs in the face they were set in. Google Docs has none of them. It substitutes, and a
> substitute face has different advances, so the line is a different width and everything downstream of
> it moves." — `tools/p2w-bench/grender.py:4-9`

with the measured illustration at `grender.py:11-13` (same engine, same source):
`310_court_judgment` 1.39 % LibreOffice vs **16.28 %** Google; `01_stamp_rotated_15deg` 2.09 % vs **14.14 %**.

This is corpus-wide by construction — it applies to every document with text, not to a class — and it
is the only construct in the tree that does. Supporting evidence:

* `FINDINGS/47_margins-DEJAVU-MONO-GOOGLE-SUBSTITUTES-VERDANA-081500-f1x.md` — DejaVu Sans Mono →
  **Verdana** in the exported PDF, a monospace column grid destroyed; 21 corpus documents draw a
  monospaced face. The rename that fixes it (DejaVuSansMono → Courier New) is metric-identical to
  0.325 % and still moves the LibreOffice `share5` enough that `regress.py` refuses it — the face is
  load-bearing on both sides.
* `benchmarks/GOOGLE-VS-LIBREOFFICE.md` — 205 documents, same instrument, same engine: LibreOffice 135
  clean, Google 47. Google is the stricter renderer on 22 of 38 checks, and the Google-only failures
  cluster on exactly the constructs a substitute face perturbs (`17_matched_runs` 29, `43_within_10pt_x`
  13, `10_font_sizes` 6, `23_line_pitch` 3, `60_text_column_right_edge` 61).
* `benchmarks/PIXEL-SCORES-GOOGLE-VS-LO.csv` — the same six documents through both renderers:
  LibreOffice SSIM mean **91.65** (max 97.63), Google mean **84.18**; the gap is **mean 7.47, median
  7.79, range 2.34–13.78** points for identical content. Two of the six are explicitly flagged
  `google_doc_content_identical_to_current_engine = YES` and still lose 9.24 and 2.34 points.

Two other constructs are real but cannot be the median's cause, and the numbers say why:

* **Google rasterises anchored text boxes on import** (`DocxWriter.java:2956-3013` `shapeRun`,
  `:5580-5633` `anchorShape`; census `FINDINGS/00_page_count-ANCHOR-RASTERISATION-CENSUS-agent-2312.md:87`).
  Reach is **31–37 documents / 9,702 characters** (`FINDINGS/DOCS-ROOT-CAUSES-24NOV.md:679`), so it can
  explain the `04_chars_missing` class and the worst tail, not 209 documents.
* **Google's table row height** — 1.11 pt/row in Google against 0.13 pt/row in LibreOffice
  (`FINDINGS/BLOCKERS-AND-WHAT-IS-LEFT-25NOV.md:46`) — explains why 13 of the worst 15 are table-dense,
  but it is a per-table accumulation, not a corpus-wide constant.

The docx's own geometry is not the problem, and this is the measurement that makes the verdict safe:
median `dy` **0.02 pt**, IQR 0.11 pt, slope 0.0004 pt per pt of page over 18,327 lines in 213 documents
(`FINDINGS/Y-ERROR-EMPIRICAL-213-DOCS-AND-RECONCILIATION-24NOV.md`, table at :10-15, slope at :17-22), and
`share5` median 0.12 % with 152/212 documents already inside the 99 % bar in LibreOffice. The document
is right; the renderer Google uses to draw it is a different one.

---

## 7. Is 99 % reachable for the bulk? Only for a subset, and the reason is the instrument

Reachable today, by the data:

* **Sparse documents.** The four at 99+ are the emptiest pages in the corpus — established in
  `FINDINGS/PIXEL-SSIM-IS-INFLATED-BY-WHITE-SPACE-25NOV.md`: `413_tagged_pdf_actualtext` SSIM 99.2 on an
  ink overlap of 37.3 %, `412_page_labels_roman` 98.4 on 13.1 %. My measurement reproduces the mechanism
  from the other direction: a 0.29 %-ink page scores 99.72 between two different rasterisers, a 13 %-ink
  page scores 87.
* **Nothing else.** Not one document in the corpus is above 99.1 except those, and the highest score any
  document reaches through a *friendly* renderer with *identical content* is 97.63
  (`PIXEL-SCORES-GOOGLE-VS-LO.csv`, `01_stamp_rotated_15deg_upright`).

Not reachable for the bulk, for three separate reasons, each measured:

1. **The metric's floor on a dense page is ~87** even for byte-identical vector content (§5a). A dense
   document cannot reach 99 under this instrument no matter what the pipeline emits, because two
   independent rasterisations of the same page do not agree to 1 part in 100 at 150 dpi, half
   resolution, over a whole page of thin strokes.
2. **A substituted face costs 35 points at identical geometry** (§5b), and Google substitutes on
   essentially every document (`grender.py:4-9`).
3. **The comparison is unregistered and unscaled** (§4), so the ~1 px of grid disagreement that two
   renderers always produce is charged to the document at ~15 points (§5c).

Therefore: closing checks cannot reach the goal, because the goal as measured is not a property of the
document. 213 documents at 99 %+ would require either (i) the Google render to be produced from the
same glyph outlines at the same sub-pixel positions as the source raster — i.e. no substitution, which
Google does not offer — or (ii) the instrument to change: register before comparing (`--align` already
exists, `pixel-score.py:177-200`), compare at full resolution, and mask the score to ink rather than
letting white space carry it. Option (ii) is a measurement change and would be honest only if it is
declared as a change of standard; option (i) is not in the engine's gift.

The one pipeline-side lever that would move the bulk is the one the tree already names as the route to
stop rasterising text — emitting a multi-column band as one paragraph with tab stops
(`FINDINGS/Y-ERROR-EMPIRICAL...:68-71`, route (c), `PATCHES/route-c-col-rows.patch`, not landed). It is
worth doing for correctness; it will not take the median to 99.

---

## 8. What could not be established from committed artefacts

* **Per-document ink coverage.** The `PIXEL-SCORES-112-DOCS.csv` schema is
  `document, pages_src, pages_render, ink_iou_d1_pct, ssim_pct, agree_pct, ssim_method, defects` — no
  coverage column. So "SSIM is a function of ink density" is demonstrated on the 5 corpus PDFs that are
  committed, not on all 213. The corpus itself (213 PDFs) and the 213 Google renders are not in the
  repo (`grender.py:43` caches to `/scratch/work`), so the corpus could not be re-scored here.
* **Whether a constant offset exists in the corpus renders.** `best_offset_px` was never recorded
  (`pixbatch.py:92-93`). The cheap settling test: re-score 10 documents with `pixel-score.py --align`
  and read the offset. My two-renderer control returned (0,0), which suggests the offset is not the
  issue — but that is 5 pages, not the corpus.
* **The SSIM of the Google render against a *re-rendered* source** (same engine on both sides) is not
  recorded anywhere, so the size of the "different renderer" term on the real corpus is inferred from
  the 6-document `PIXEL-SCORES-GOOGLE-VS-LO.csv`, not measured over 213.
* **`ssim_method` is a hard-coded string** (`pixbatch.py:105` writes `"half-res-stride2"` on every row
  regardless of what the scorer did), so the column is a label, not evidence that every row was scored
  the same way. The scorer's code path is single, so the label is probably true — it is not proof.
