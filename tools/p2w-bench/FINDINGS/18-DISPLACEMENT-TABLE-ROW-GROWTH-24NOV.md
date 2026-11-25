# `18_displacement` — the real cause, measured

**Repo:** `kavopdf/app` @ `8d5a3eb` (engine source identical to the engine that produced the recorded
verdicts, `b7699196`). Corpus: 213 PDFs via `tools/p2w-bench/corpus-fetch.sh`.
**Engine built** with `tools/p2w-bench/build-engine.sh` (33 s) — used only to *convert*, never modified.
**Renders:** 213 `.docx` produced by `ConvertOne`; 213 LibreOffice PDFs by `soffice`.
**Verdicts** are the recorded Google ones in `benchmarks/gverify/*.json` (130 of 213 carry the check's
own `displacement` detail: `med_dy`, `worst_dy`, `bad_pages`); LibreOffice verdicts from
`benchmarks/gverify-lo/*.json`.
Every number below is from a run in this session unless marked *prior work*.

---

## 1. Hypothesis table

| # | Hypothesis | Verdict | The measurement that decided it |
|---|---|---|---|
| 1 | **MAGNITUDE** — a *large* page-top `w:before` is the cause | **REFUTED** | Max page-top before-gap (body top + after every page break), read from all 213 `.docx`: **fails median 54.9 pt (p10 17.5, p90 63.5, max 239.5)**, **passes median 59.5 pt (p10 23.5, p90 69.5, max 281.5)**. Failing documents carry *smaller* top gaps than passing ones. No threshold separates them; a scan over every cut-off finds nothing better than the rejected presence test. |
| 2 | **PAGE-FILL BUDGET** — the engine over-fills page 1 and pushes content down | **REFUTED** | All 103 failing documents render to the **same page count as the source (103/103)**; page-1 last-line delta (source − render) **median −0.48 pt, p10 −2.29, p90 +0.25**; only **7 of 103** have the render's last line below the source's. Nothing is being pushed off or down by an over-full page. |
| 3 | **THE CHECK ITSELF** — it measures a proxy narrower than "vertical displacement" | **CONFIRMED (in part)** | Reading `verify_google.py:5800-5877`: a page fails if `n_out > max(2, ceil(5%·n))` **or** `n_out == n` **or** `max(|dy|/tol) > 2.0` (TAIL_FACTOR), with `tol = clamp(0.35·size, 1.5, 4.5)` pt. So **one run more than 3.0–9.0 pt out fails the whole page, hence the document**. Corpus evidence: passing documents reach **worst_dy 4.2 pt**, failing ones start at **3.3 pt** — the two populations overlap and the line between them is the tail clause, not a distinct defect. **28 of the 75 measured failures have worst_dy ≤ 9.0 pt**, and **9 have worst_dy ≤ 4.5 pt** (those can only fire on type ≤ 6.4 pt). |
| 4 | **REPEATED TEXT / PAIRING ARTEFACT** | **REFUTED for this class** | (a) The same matcher, run on the *same `.docx`* through LibreOffice, is clean on **92 of the 103** Google failures (LO `worst_dy/tol` median **0.48**, i.e. no displacement at all) — pairing cannot be broken in Google and perfect in LO on identical content. (b) Only **23 % of the out-of-tolerance runs** in the LO renders have text that repeats on their page. (c) My harness reproduces the stored LibreOffice verdict **212/213** (the one exception is the documented "no text layer" case, `15_stamp_on_scanned_page`), so the instrument is behaving. |
| 5 | **TABLE-ROW HEIGHT** — Google lays each row at its own content height, taller than the declared `w:trHeight`; the error accumulates down the table | **CONFIRMED** | See §2. Same `.docx`, same matcher: **Google per-row growth 1.11 pt/row, LibreOffice 0.13 pt/row** (median, 51 single-page table failures); worst |dy| **10.2 pt vs 1.5 pt** (ratio 0.10). **51/51** of those documents imply a Google row height *above* the declared one. |

---

## 2. The most likely cause

**Google Docs lays each table row at a height derived from its own content line box, not at the engine's
declared `w:trHeight`, and the per-row error accumulates down the table. Check 18 charges the far end of
that accumulation.**

The engine's row declarations are *correct*: measured across the corpus, `declared row height / source
row pitch` = **1.00 (median)** in both failing and passing documents (fails p10 0.98/p90 1.25;
passes p10 1.00/p90 8.14 — the high tail is rows whose source pitch my banding mis-measured). The error
is added by the renderer, which is why no `.docx` construct separates the class: a 40-feature scan over
all 213 `.docx` (row heights, `hRule`, `cantSplit`, `gridSpan`, `vMerge`, `vAlign`, `tcMar`, spacer
paragraphs, page breaks, fonts, drawings, text boxes, exact/auto line rules, section margins) found **no
feature better than sensitivity 0.82 / specificity 0.70** (`cantSplit` count — a proxy for "row-heavy
table"), i.e. no better than the `w:before` construct that was already rejected.

### Evidence, same document, two renderers

For the 51 single-page, table-bearing Google failures that carry the check's own detail:

| renderer | worst \|dy\| on the page | per-row growth | docs with growth > 0.3 pt/row |
|---|---:|---:|---:|
| Google Docs (recorded) | **10.2 pt** (median) | **1.11 pt/row** | 48 / 51 |
| LibreOffice (same `.docx`) | **1.5 pt** (median) | **0.13 pt/row** | — |

39 of those 51 are **below 3.0 pt** in LibreOffice. Nothing in the file changed between the two columns.

The implied Google row height — `declared_row_pt + worst_dy / rows` — is **above the declared value on
51 of 51** documents, median **18.82 pt** against a declared median of 18.0 pt. That is the signature of
a one-directional per-row growth, not of a page shift.

The magnitudes agree with the observed distribution: median failing table has **12 rows**, growth
**1.11 pt/row** → **13.3 pt**, against an observed **worst_dy median of 13.0 pt**.

### Why the class looks the way it does

* **"One page out" is not a page-1 effect.** 65 of the 75 measured failures fail on exactly one page —
  but 86 of the 103 failing documents are *single-page* documents. One page is simply the only page.
* **`med_dy` near zero with a large `worst_dy`** (34 of 75 have |med_dy| ≤ 4.5 pt) is what a ramp
  through a table looks like: the page as a whole is registered, the two ends of the table are not.
* **Table presence is necessary but not sufficient**: 91 of 103 failures carry table rows, but so do 52
  of 110 passes. The passes are *short* tables — the same per-row error over fewer rows stays inside the
  check's absolute tolerance (e.g. `393_spectrum_peak_table`, 4 rows, 0.90 pt/row, worst 3.6 pt, passes;
  `362_price_list_dense`, 29 rows, 0.09 pt/row, worst 2.6 pt, passes because its declared pitch already
  matches Google's row height). **The verdict is a function of (per-row error × rows) crossing an
  absolute threshold** — which is why the class cannot be described by any single construct's presence.

### Extremes (from the recorded Google detail)

| document | worst_dy | med_dy | bad pages | rows | per-row growth |
|---|---:|---:|---:|---:|---:|
| `very-long-single-column-table` | 656.7 | −7.4 | 3 | 99 | 6.63 |
| `table-across-page-break-repeated-header` | 403.9 | −34.7 | 3 | 45 | 8.98 |
| `80_gstin_pan_cin_ifsc_table` | 237.1 | −34.6 | 1 | 20 | 11.86 |
| `601_fillable_admission_form` | 230.4 | +27.3 | 1 | 0 (no table) | — |
| `56_table_indented_from_margin` | 143.6 | −35.6 | 1 | 9 | 15.96 |
| … | | | | | |
| `70_magazine_drop_cap_photo_caption` | 3.3 | +2.9 | 1 | 0 | — |
| `payslip-label-left-amount-right` | 3.4 | +0.1 | 1 | 21 | 0.16 |
| `brochure-3col-with-sidebar-box` | 3.4 | +0.1 | 1 | 2 | 1.70 |

---

## 3. How many of the 103 it explains

Attribution over all 103 (single-page + ≥4 table rows ⇒ table-row; multi-page with page breaks ⇒
page-break; the rest classified individually):

| mechanism | documents | note |
|---|---:|---|
| **table-row height accumulation** (≥4 rows, single page) | **75** | 52 carry Google detail; 49/52 show >0.3 pt/row growth |
| short tables (1–3 rows) | 6 | same mechanism, too few rows to cross the threshold on its own; each is a per-document outlier |
| **multi-page / page-break** (`w:before` after a page break) | **16** | the construct *already proven* by prior work; my numbers are consistent with it — e.g. `412_page_labels_roman` med_dy −59.0 pt against a 61.35 pt after-break gap, `416_many_tiny_pages` −87.2 pt against 89.5 pt, `602_bookmarked_annual_report` −67.6 pt against 69.5 pt |
| unclassified (no table, single page, no spacer) | 6 | `31_times_body_arial_headings`, `601_fillable_admission_form`, `70_magazine_drop_cap_photo_caption`, `78_mixed_english_devanagari_line`, `bank-statement-horizontal-rules-only`, `gst-invoice-horizontal-rules-only` |

So the row-height cause explains **75 of 103 outright, 81 with the short tables**, and the remaining
**16 are the page-break construct** the repo had already proved for pages 2..N. Six documents are left
unexplained by either.

---

## 4. What would settle it

The one thing this session could not do is read **per-run `dy` inside the Google export**, because the
Drive upload tool cannot read a file from the sandbox (`s3key` must belong to the calling project) and
the only public artifacts repo (`Onyx-Node/kavopdf-render-probe`) is read-only to me (push → 403).

The settling measurement is one Google round trip per document on 10 of the 51 table failures:

1. `ConvertOne` → upload the `.docx` → `GOOGLEDRIVE_CREATE_FILE` as `application/vnd.google-apps.document`
   → export PDF (the route `grender.py` documents), then `dy.py` on the pair.
2. **Prediction if the row-height cause is right:** `dy` is a monotone ramp *within the table body*,
   near zero at the table's first row and growing linearly with row index; the runs outside the table are
   registered; and the row pitch in the export is `declared + ~1 pt` while the source's is `declared`.
3. **Falsifier:** if `dy` jumps at a single row and returns to ~0 below it, or if the ramp starts at the
   table's *top* with the first row already out by the full amount (the shape prior work measured at
   −10.16 pt on `table-with-no-header-row`), the cause is the block's leading position, not accumulation,
   and this diagnosis is wrong.

A cheaper partial check, needing no Drive: rebuild with the row pitch emitted as `pitch − 0.5 pt` (a
*diagnosis* build, not a fix) and re-render through LibreOffice — LO must stay clean while the implied
Google row height moves; that only shows the construct reaches the output, which is already known.

---

## 5. Where the check itself looks wrong

1. **A single run decides a document.** `TAIL_FACTOR = 2.0` means one run >2×tolerance (3.0–9.0 pt,
   depending on type size) fails the page regardless of the 5 % budget. 28 of 75 measured failures sit
   entirely inside 9 pt; 9 sit inside 4.5 pt.
2. **The pass/fail line falls inside a continuous distribution.** Passing documents reach 4.2 pt of
   worst displacement; failing ones start at 3.3 pt. There is no gap, so "103 documents fail" is a
   statement about where the threshold sits on an accumulation curve, not about a population of defects.
3. **The per-page 5 % budget is a ruler for page length inside a table.** Because the error is
   proportional to the number of rows, a 12-row table fails and a 4-row table with a *larger* per-row
   error passes (`393_spectrum_peak_table`: 0.90 pt/row, passes at 3.6 pt). The check's own comment
   argues the budget must be per page to avoid being "a ruler for document length"; in the table case it
   is a ruler for table length instead.
4. **The count it reports is not the fault it means.** `18_displacement` reports `bad_pages` — the
   number of pages whose tail clause tripped. On this corpus that number is 1 for 65 of 75 failures,
   which reads as "one page is wrong" when the truth is "the table on that page accumulates ~1 pt per
   row".
5. **LibreOffice and Google disagree on 92 of the 103.** Any fix validated on the LO proxy is not
   measuring this class at all.

---

## Method notes / limitations

* I could not produce new Google renders (see §4). Every Google number above is the recorded
  `displacement` detail in `benchmarks/gverify/*.json` (75 of the 103 failures, 55 of the 110 passes);
  every LibreOffice number is from my own conversion and my own run of the check's matcher.
* My per-page harness re-implements the check's three clauses on top of `verify_google.py`'s own
  `runs()`/pairing (spying on `extra_checks`, as `dy.py` does) and reproduces the stored LO verdict on
  212/213 documents.
* `per-row growth` = `worst_dy / table rows`. It is an upper bound on the per-row error (the worst run
  need not be the last row), which is why the median matters and single documents do not.
* The 3 geometric outliers named in the brief (+194.68, +101.90, +27.00 pt) were not re-examined; the
  656.7 pt document here (`very-long-single-column-table`, 99 rows, 3 pages) is a different one and is
  consistent with the same accumulation mechanism at 6.63 pt/row.
