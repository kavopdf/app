# `60_text_column_right_edge` — census: 60 documents fail it, 5 fail only it, and the one live construct is honoured by Google but not by our reader

**27 Nov 2026, ~04:50-05:00 IST · census run · clone at `5ef9ea07` (engine fingerprint `d28ca7516c3f9165`)**
**Nothing under `app/` was touched. No file was deleted. Nothing was written to the user's Drive root; every
Drive object used here already existed in the `KavoPDF-Verify` folder `1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA`.**
**This file is the only write.**

---

## Verdict in one paragraph

**60 documents fail `60_text_column_right_edge` in the stored Google results, and 5 of them fail nothing
else — so 5 CLEAN documents are at stake, not 61's worth of anything.** Measured through Google on the
current engine, **three of those five are a genuine underrun** — the same line, same baseline, 58.48 / 60.73 /
65.61 pt short of the source, because the engine declares DejaVu and Google substitutes Arial/Verdana — and
**two are the instrument charging a line it re-grouped**, not an edge that moved: on `342_packing_list` the
charge is +51.88 pt where the same ink moved +1.97 pt, and on `79_inr_indian_digit_grouping_table` +46.85 pt
where the same text moved +1.56 pt. The construct is **live and measured honoured**: a right tab stop puts the
trailing word's right edge at **538.50 pt where the page drew 538.61 — 0.11 pt**, re-measured here from the
arm-B Google Doc. It still wins **0 CLEAN documents today**, because Google's export splits the tabbed line
into two PyMuPDF lines: on the reader at HEAD the body column reads **461.58** (worse than the 473.00 control)
and `17_matched_runs` falls **34 → 13**. The pin family (`w:jc="distribute"` + `w:ind w:right`) is **refuted**
by measurement; the tab family is **supported in the renderer and blocked by the reader and by `17`**.

---

## 0. What was run (every number below comes from one of these)

| # | command | what it produced |
|---|---|---|
| 1 | `python3 -c` over `benchmarks/gverify/*.json` (213 files) | the census: which documents fail `60`, and what else they fail |
| 2 | `bash tools/p2w-bench/corpus-fetch.sh` | `corpus: 213 PDFs, 212 scored in RANKING.csv, 0 missing` |
| 3 | `bash tools/p2w-bench/build-engine.sh` (JDK 17.0.21.1 fetched to `/scratch/work/.p2w-jdk`) | `engine built - ConvertAll ready (41s)`; docx fingerprint `d28ca7516c3f9165` |
| 4 | `java -cp out:libs/… ConvertAll /scratch/work/shard5 /scratch/work/out5` (5 symlinked PDFs) | `done: 5 files, 0 failed`, 6.9 s |
| 5 | `GOOGLEDRIVE_DOWNLOAD_FILE` ×5 + `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` ×5 (`run_program`) | the stored corpus `.docx` and the Google PDF renders of them |
| 6 | `python3 tools/p2w-bench/verify_google.py <src> <google-render> --docx out5/<n>.docx --json …` ×5 | the Google verdict per document, on `d28ca75` |
| 7 | `python3 /scratch/work/edge60.py <src> <render>` (a mirror of `page_lines`/`columns`/`edge`, constants copied) | the actual x positions: source edge, render edge, delta, one-word slack, verdict |
| 8 | `soffice --headless --convert-to pdf` ×5 + the same two tools | the **LibreOffice proxy** numbers, labelled proxy-only throughout |
| 9 | export of `321_auditors_report_nospace` (arm B, tab-only) + `321_auditors_report_ctl` | the construct re-measured: `538.50` vs `538.61`, and `17_matched_runs` `34 → 13` |
| 10 | `python3 /scratch/work/merge_test.py` | the merged-reader variant on the same three PDFs (`540.99` vs `538.61`) |

**Why the stored Google renders are usable for a HEAD build.** The `.docx` in Drive were written on 25 Nov.
I compared `word/document.xml` of the stored `.docx` against the `.docx` this run built: **`313` and `321` are
byte-identical**; `316`, `342` and `79` differ **only** in `w:before` / `w:line` / `w:trHeight` — vertical
spacing. No run text, no `w:sz`, no `w:right`, no alignment, no `w:tabs` differs, so **the horizontal geometry
this check reads is unchanged**, while `18_displacement` (a vertical check) is *not* comparable — which is
exactly where the one discrepancy below comes from.

---

## 1. (a) Every document that fails `60_text_column_right_edge` — 60 of 213

Store: `benchmarks/gverify/*.json`, 213 files (205 `ok`, 8 `page_count_refused`). **60 fail `60`**; **5 fail
nothing else**. Engines are mixed: 37 rows on `74a152e7d3fb3d26`, 17 on `a4d8fca469bba636`, 6 on
`025fe9deda5ac7b1` — and `FINDINGS/GOOGLE-REGRESSION-16-OF-16-ON-a4d8fca-27NOV.md` records that `a4d8fca`
fails more checks than `025fe9d` on 16 of 16 documents, so the store is not one engine's verdict.

| # | document | store score | other checks it also fails | engine |
|---|---|---|---|---|
| 1 | `313_power_of_attorney` | 41/42 | **none — solo** | `74a152e7d3fb3d26` |
| 2 | `316_contract_with_schedules` | 46/47 | **none — solo** | `74a152e7d3fb3d26` |
| 3 | `321_auditors_report` | 41/42 | **none — solo** | `74a152e7d3fb3d26` |
| 4 | `342_packing_list` | 46/47 | **none — solo** | `74a152e7d3fb3d26` |
| 5 | `79_inr_indian_digit_grouping_table` | 41/42 | **none — solo** | `a4d8fca469bba636` |
| 6 | `301_lab_report_panel` | 45/47 | `18_displacement` | `74a152e7d3fb3d26` |
| 7 | `302_radiology_report` | 40/42 | `18_displacement` | `74a152e7d3fb3d26` |
| 8 | `317_rti_response` | 40/42 | `47_margins` | `74a152e7d3fb3d26` |
| 9 | `335_msds_safety_data_sheet` | 45/47 | `18_displacement` | `74a152e7d3fb3d26` |
| 10 | `340_bill_of_lading` | 40/42 | `18_displacement` | `74a152e7d3fb3d26` |
| 11 | `341_shipping_manifest` | 45/47 | `18_displacement` | `74a152e7d3fb3d26` |
| 12 | `343_air_waybill` | 40/42 | `18_displacement` | `74a152e7d3fb3d26` |
| 13 | `363_warranty_card` | 40/42 | `18_displacement` | `74a152e7d3fb3d26` |
| 14 | `370_offer_letter` | 45/47 | `18_displacement` | `74a152e7d3fb3d26` |
| 15 | `balance-sheet-and-profit-loss` | 45/47 | `18_displacement` | `025fe9deda5ac7b1` |
| 16 | `boq-tender-bill-of-quantities` | 45/47 | `18_displacement` | `a4d8fca469bba636` |
| 17 | `form16-part-b` | 45/47 | `18_displacement` | `025fe9deda5ac7b1` |
| 18 | `gst-invoice-3line-items` | 45/47 | `18_displacement` | `a4d8fca469bba636` |
| 19 | `landscape-page-inside-portrait-document` | 45/47 | `18_displacement` | `a4d8fca469bba636` |
| 20 | `marksheet-university-consolidated` | 45/47 | `18_displacement` | `a4d8fca469bba636` |
| 21 | `question-paper-marks-right-margin` | 40/42 | `18_displacement` | `a4d8fca469bba636` |
| 22 | `table-with-merged-cells` | 45/47 | `18_displacement` | `a4d8fca469bba636` |
| 23 | `very-long-single-column-table` | 45/47 | `18_displacement` | `025fe9deda5ac7b1` |
| 24 | `310_court_judgment` | 39/42 | `43_within_10pt_x`, `47_margins` | `74a152e7d3fb3d26` |
| 25 | `314_tender_rfp_boq` | 44/47 | `42_justification_edges`, `63_table_rows` | `74a152e7d3fb3d26` |
| 26 | `365_recipe_card` | 39/42 | `18_displacement`, `47_margins` | `74a152e7d3fb3d26` |
| 27 | `393_spectrum_peak_table` | 44/47 | `18_displacement`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 28 | `406_passport_mrz_page` | 39/42 | `18_displacement`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 29 | `56_table_indented_from_margin` | 39/42 | `18_displacement`, `59_shape_anchor` | `a4d8fca469bba636` |
| 30 | `purchase-order` | 44/47 | `18_displacement`, `26_text_overlap` | `a4d8fca469bba636` |
| 31 | `salary-slip-factory-wages` | 44/47 | `18_displacement`, `59_shape_anchor` | `a4d8fca469bba636` |
| 32 | `text-held-twice-shadow-text` | 44/47 | `13_text_colours`, `25_invisible_text` | `a4d8fca469bba636` |
| 33 | `25_signature_block_underscores_txtpos` | 38/42 | `04_chars_missing`, `18_displacement`, `45_char_accuracy` | `74a152e7d3fb3d26` |
| 34 | `28_value_overflows_cell_txtpos` | 38/42 | `43_within_10pt_x`, `47_margins`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 35 | `311_fir_police_form` | 43/47 | `04_chars_missing`, `18_displacement`, `45_char_accuracy` | `74a152e7d3fb3d26` |
| 36 | `312_affidavit_stamp_paper` | 38/42 | `04_chars_missing`, `13_text_colours`, `17_matched_runs` | `74a152e7d3fb3d26` |
| 37 | `326_itr_computation` | 43/47 | `18_displacement`, `59_shape_anchor`, `63_table_rows` | `74a152e7d3fb3d26` |
| 38 | `344_customs_declaration` | 43/47 | `04_chars_missing`, `13_text_colours`, `18_displacement` | `74a152e7d3fb3d26` |
| 39 | `360_restaurant_menu` | 38/42 | `18_displacement`, `43_within_10pt_x`, `47_margins` | `74a152e7d3fb3d26` |
| 40 | `373_leave_application_form` | 43/47 | `18_displacement`, `23_line_pitch`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 41 | `381_incident_report_timeline` | 43/47 | `04_chars_missing`, `18_displacement`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 42 | `38_faux_bold_italic_synthesised` | 38/42 | `04_chars_missing`, `18_displacement`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 43 | `mutual-fund-statement` | 43/47 | `18_displacement`, `59_shape_anchor`, `66_table_cell_width` | `025fe9deda5ac7b1` |
| 44 | `332_bom_on_drawing` | 42/47 | `18_displacement`, `26_text_overlap`, `47_margins`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 45 | `352_certificate_ornate_border` | 37/42 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `45_char_accuracy` | `74a152e7d3fb3d26` |
| 46 | `383_api_docs_page` | 42/47 | `04_chars_missing`, `18_displacement`, `47_margins`, `66_table_cell_width` | `74a152e7d3fb3d26` |
| 47 | `delivery-challan` | 42/47 | `04_chars_missing`, `13_text_colours`, `18_displacement`, `26_text_overlap` | `a4d8fca469bba636` |
| 48 | `one-page-rotated-180-degrees` | 42/47 | `18_displacement`, `43_within_10pt_x`, `62_table_columns`, `63_table_rows` | `025fe9deda5ac7b1` |
| 49 | `14_stamp_chars_positioned_td` | 36/42 | `04_chars_missing`, `13_text_colours`, `18_displacement`, `45_char_accuracy`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 50 | `305_vaccination_certificate` | 41/47 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `43_within_10pt_x`, `45_char_accuracy` | `74a152e7d3fb3d26` |
| 51 | `371_experience_certificate` | 36/42 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `45_char_accuracy`, `59_shape_anchor` | `74a152e7d3fb3d26` |
| 52 | `gst-invoice-horizontal-rules-only` | 36/42 | `04_chars_missing`, `18_displacement`, `26_text_overlap`, `44_header_footer`, `45_char_accuracy` | `a4d8fca469bba636` |
| 53 | `323_credit_card_statement` | 40/47 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `18_displacement`, `45_char_accuracy`, `66_table_cell_width` | `74a152e7d3fb3d26` |
| 54 | `65_two_col_full_width_figure_caption` | 35/42 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `44_header_footer`, `45_char_accuracy`, `59_shape_anchor` | `a4d8fca469bba636` |
| 55 | `77_arabic_rtl_document` | 40/47 | `17_matched_runs`, `18_displacement`, `26_text_overlap`, `43_within_10pt_x`, `47_margins`, `59_shape_anchor` | `a4d8fca469bba636` |
| 56 | `academic-paper-ieee-2col-abstract` | 40/47 | `04_chars_missing`, `17_matched_runs`, `18_displacement`, `44_header_footer`, `45_char_accuracy`, `47_margins` | `025fe9deda5ac7b1` |
| 57 | `318_court_summons_form` | 39/47 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `18_displacement`, `43_within_10pt_x`, `45_char_accuracy`, `47_margins` | `74a152e7d3fb3d26` |
| 58 | `322_mutual_fund_factsheet` | 39/47 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `18_displacement`, `26_text_overlap`, `44_header_footer`, `45_char_accuracy` | `74a152e7d3fb3d26` |
| 59 | `policy-2col-spanning-section-heading` | 34/42 | `04_chars_missing`, `10_font_sizes`, `13_text_colours`, `17_matched_runs`, `44_header_footer`, `45_char_accuracy`, `59_shape_anchor` | `a4d8fca469bba636` |
| 60 | `magazine-2col-pullquote-spanning` | 33/42 | `04_chars_missing`, `10_font_sizes`, `13_text_colours`, `17_matched_runs`, `43_within_10pt_x`, `44_header_footer`, `45_char_accuracy`, `47_margins` | `a4d8fca469bba636` |

**The answer to "does fixing 60 alone make any document CLEAN": yes, exactly 5** — rows 1-5. Every other one of
the 55 is two or more checks away, and the check it most often shares a failure with is `18_displacement`
(43 of the 55), then `04_chars_missing` (20), `59_shape_anchor` (16), `13_text_colours` (14),
`45_char_accuracy` (14), `17_matched_runs` (12), `47_margins` (11).

**On "42/42" meaning clean.** `all_check_ids()` (`verify_google.py:6432`) knows **47** checks at HEAD
(`--list-checks | wc -l` → `47`), and a row's `total` is what that document was *given*. The five solo
documents split 3 × 42 and 2 × 47. The three 42s are **not** a stale catalogue: `313`, `321` and `79` have no
tables, and the five checks they were not given are exactly the table block
`62_table_columns, 63_table_rows, 64_table_span_across, 65_table_span_down, 66_table_cell_width` (measured by
diffing each document's `checks` keys against `--list-checks`). `316` and `342` were given all 47. So all five
are clean on every check that applies to them.

---

## 2. (b) The measured defect on the five solo documents

All five converted from HEAD (`d28ca7516c3f9165`), scored against their Google render. The predicate is
`verify_google.py:2660-2786`: the edge is the **widest line of a left-edge cluster**, the tolerance is
`RIGHT_OVERRUN = 6.0` / `RIGHT_UNDERRUN = 8.0` (`:2654-2655`) plus **one word of that column**, capped at
`SLACK_CAP = 40.0` (`:2658`).

| document | Google verdict on HEAD | charged line (source) | source x1 | Google x1 | delta | one-word slack | allowed | result |
|---|---|---:|---:|---:|---:|---:|---|
| `313_power_of_attorney` | **41/42, `60` only** | `2. The Attorney shall have the power to execute and register any lease deed…` | 538.63 | **480.14** | **−58.48** | 40.00 | 48.00 | UNDER by 10.48 |
| `316_contract_with_schedules` | **46/47, `60` only** | `2.1 The Client shall pay the charges set out in Schedule C…` | 538.61 | **477.88** | **−60.73** | 19.27 | 27.27 | UNDER by 33.46 |
| `321_auditors_report` | **41/42, `60` only** | `4. We draw attention to Note 27 to the financial statements…` | 538.61 | **473.00** | **−65.61** | 28.49 | 36.49 | UNDER by 29.12 |
| `342_packing_list` | **45/47, `60` + `18`** (see note) | `300.00` (source) vs `300.00 120x100x15` (render, one line) | 489.99 | **541.87** | **+51.88** | 24.49 | 30.49 | OVER by 21.39 |
| `79_inr_indian_digit_grouping_table` | **41/42, `60` only** | source column's widest: `11,79,136.00`; render's: `Verified: R. Sundaram` | 372.37 | **419.22** | **+46.85** | 40.00 | 46.00 | OVER by 0.85 |

**Three of the five are one defect, and it is a face substitution, not a rounding.** The charged line is the
*same string on the same baseline* in both PDFs, and it simply stops short:

* `313`: source `DejaVuSerif 10.0` → Google `ArialMT 10.0`. Line ends **480.14** where the page drew **538.63**.
* `316`: source `DejaVuSans 8.0` → Google `Verdana 8.0`; source `DejaVuSerif 9.5` → Google `ArialMT 9.5`.
  Body line ends **477.88** where the page drew **538.61**.
* `321`: source `DejaVuSerif 9.5` → Google `ArialMT 9.5`. Line ends **473.00** where the page drew **538.61**.

That is the mechanism the four findings describe and this run confirms in the render: **the engine writes no
right edge.** Measured in the `.docx` this run built: `313` has 30 `<w:p>`, **31** `w:right="0"`, **1** `w:jc`,
**0** `<w:tabs>`; `321` has 34 paragraphs, **35** `w:right="0"`, **1** `w:jc`, **0** `<w:tabs>`; `316` has 43
paragraphs, **28** `w:right="0"`, **0** `w:jc`, **0** `<w:tabs>`; every page carries
`<w:pgMar w:top="0" w:right="0" w:bottom="0" w:left="0" …/>`. Current sites: `DocxWriter.java:4450`
(`int rightTw = 0;`), `:2454` (the `w:pgMar` line), `:4679-4680` (`w:jc` only for `align == 1` / `align == 2`).
**The line numbers quoted in the 26-27 Nov findings for these sites (`:4444`, `:2448`, `:4673-4675`) have
drifted by ~6 lines; these are the lines in `5ef9ea07`.**

**Two of the five are not an edge that moved — they are the reader charging a line it re-grouped.** Both are
*overruns*, and on the ink itself there is no overrun at all:

* **`342_packing_list`.** The source draws two PyMuPDF lines on one baseline (`y0 = 175.18`):
  `300.00` at **465.51 → 489.99** and `120x100x15` at **496.00 → 539.90**. Google's export puts the same two
  words on **one** line (`y0 = 176.29`), `300.00 120x100x15` at **465.75 → 541.87**. The check compares the
  render's one line (541.87) with the source's widest *line in that cluster* (489.99) and charges **+51.88**.
  The same ink, measured word for word, moved **+1.97 pt** (`120x100x15`: 539.90 → 541.87; `300.00`:
  489.99 → 490.54, **+0.55**). Inside the 6.0 pt overrun tolerance.
* **`79_inr_indian_digit_grouping_table`.** The charge compares two *different lines*: the source's cluster at
  left 323.10 is widest at `11,79,136.00` → **372.37**, while the render's cluster at the same left holds
  `Verified: R. Sundaram` → **419.22**. That text is at **x0 = 336.00 in both PDFs** and ends
  **417.66** (source) vs **419.22** (render) — **+1.56 pt**, well inside the 6.0 pt tolerance. The 46.85 is
  the clustering, not the line.

*Note on `342`.* The store says `342` fails `60` only; on HEAD it reads **45/47 with `18_displacement` too**.
That extra failure is the vertical difference between the stored `.docx` (25 Nov) and HEAD (`w:before`,
`w:line`, `w:trHeight` all differ), i.e. an artefact of scoring a HEAD `.docx` against a 25-Nov render, not a
statement about `342` on its own engine. `313`, `321` are byte-identical and `79` reads the same solo `60` as
the store, so only `342`'s `18` is affected.

**LibreOffice proxy — proxy-only, and it is blind to four of the five.** `soffice --headless --convert-to pdf`
on the same five `.docx`, scored with the same verifier:

| document | LO proxy checks | LO proxy `60` | LO delta on the body column |
|---|---|---|---|
| `313_power_of_attorney` | **42/42 PASS** | `(0,0,True)` | +1.22 |
| `316_contract_with_schedules` | **47/47 PASS** | `(0,0,True)` | −0.83 |
| `321_auditors_report` | **42/42 PASS** | `(0,0,True)` | +0.60 |
| `342_packing_list` | **47/47 PASS** | `(0,0,True)` | −0.10 |
| `79_inr_indian_digit_grouping_table` | 41/42 FAIL | `(0,1,False)` | −140.27 (on a *different* column than Google charges) |

**Every LibreOffice number above is proxy-only.** The proxy says 42/42 and 47/47 on four documents that Google
fails by 58-66 pt; it fails `79` on a column Google passes and passes the column Google fails. No conclusion
about this class may be drawn from it.

---

## 3. (c) What the four prior FINDINGS already contain

Order of the record: **25 Nov** `RIGHT-PIN-WRAPS` → **26 Nov** `60-COLUMN-RIGHT-EDGE-0137` → **27 Nov 02:33**
`RIGHT-TAB-POSITION` → **27 Nov 03:57** `RIGHT-TAB-HONOURED` (latest).

### Refuted — with the measurement

1. **`RIGHT-PIN-WRAPS-IN-GOOGLE-INERT-IN-LO-0126-relay.md` (25 Nov) — refuted `w:jc="distribute"` +
   `w:ind w:right`, measured on `302_radiology_report`, Google, both arms on one build.** The pin did not move
   the edge — `60` read `(0,1,False)` in **both** arms — and it **wrapped 28 lines** (`26_text_overlap`
   `wrap: 28` against 2 in the control), with `17_matched_runs` **33 → 21** and the score **41/42 → 39/42**.
   In LibreOffice both arms were identical, 42/42, 33/33, 0 overlaps — the change is invisible to the proxy.
   The refutation is of *this implementation*: "pinning to the source ink edge is a *compression* on these
   lines, and `distribute` cannot compress — it re-breaks."
2. **`60-COLUMN-RIGHT-EDGE-0137-27NOV.md` (26 Nov) — refuted the `w:spacing` advance carry**, the proposal it
   inherited: `w:spacing` is measured to do nothing in Google (380.1 → 380.1,
   `GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md`) and is on `google_safe.py`'s `IGNORED` list, so the gate refuses
   a corpus that gains it. The same file also measured the **instrument** side: `columns()`
   (`verify_google.py:2671`) buckets lines by left edge within 10 pt and `edge()` (`:2704`) takes the widest
   line, which is what produces the `purchase-order` `+102.98` charge on a line that moved **0.12 pt** — the
   same shape I measured on `342` (+51.88 charged / +1.97 real) and `79` (+46.85 charged / +1.56 real).
3. **`RIGHT-TAB-POSITION-60-EDGE-27NOV-fixer.md` (27 Nov 02:33) — proposed the right tab stop and left the
   right-tab question open.** Its own §"Open questions" #1: "**Does Google honour `w:tab w:val="right"`** …
   The left flavour is measured to 0.00 pt; the right flavour … **no Google measurement**." It predicted
   **5 become CLEAN** and named them `302, 313, 316, 321, 335`. **The census corrects that list**: `302` and
   `335` fail `18_displacement` as well in the store, and the five solo documents are `313, 316, 321, 342, 79`.

### Supported — with the measurement

4. **`60-RIGHT-TAB-HONOURED-INSTRUMENT-BLIND-27NOV-fixer.md` (27 Nov 03:57) — supported: Google honours a
   right tab stop.** Measured on `321`: the trailing word's right edge landed at **538.50** where the source
   drew **538.61** — **0.11 pt** — and the baseline was identical (`84.73` both pieces), so it did not wrap.
   The run still read 40/42 because `page_lines()` (`verify_google.py:2660`) takes **one bbox per PyMuPDF
   `line`**, and PyMuPDF splits a tabbed line at the jump: the fragments form one-line clusters dropped by
   `COL_MIN_LINES = 3` (`:2656`), the real column's widest line falls back to 239.54, and `17_matched_runs`
   (`:5799`, `matched >= ceil(0.9 * len(s_runs))`) loses the pairs. On a **merged** reader (same `bottom`
   within 1.0 pt, gap < 200 pt) `60` **PASSES** and only `17` fails.

### What I re-measured on the construct myself, and it holds — and it still wins nothing

I exported the arm-B Google Doc (`321_auditors_report_nospace`) and the control, and ran both through the
repo's own verifier at HEAD and through my mirror of the check:

| render | lines seen | body-column widest x1 | `60` | `17_matched_runs` | total |
|---|---:|---:|---|---|---:|
| source `321` | 34 | **538.61** | — | 34 source runs | — |
| Google **control** | 34 | **473.00** (−65.61) | `(0,1,False)` FAIL | 34/34 PASS | 41/42 |
| Google **arm B (tab only)** | **62** | **461.58** (−77.04) | `(0,1,False)` FAIL | **13/34 FAIL** | 40/42 |
| arm B, **merged-reader variant** (`merge_test.py`) | 34 | **540.99** (+2.38) | would PASS | still 13/34 | — |

And the construct's own ink, read from the exported PDF: the trailing word lands at **538.50** (`ArialMT 9.5`)
where the source drew **538.61** — **−0.11 pt**, confirming the prior finding independently.

**So the honest state of the construct: live in the renderer, dead in the pipeline.** As the reader stands the
tab makes `60` *worse* (473.00 → 461.58) and adds a `17_matched_runs` failure, so it wins **0** of the 5
CLEAN documents. With the reader fixed it passes `60` and still fails `17`, which is one failure swapped for
another — still 0 CLEAN. `17` is the binding constraint, and it is a run-splitting artefact of Google's export
of a `<w:tab/>`, not an edge.

---

## 4. So: how many CLEAN documents does fixing `60` alone win

* **5** by the store's own accounting (`313`, `316`, `321`, `342`, `79`) — the number the class is worth as a
  *class*.
* **3** of those five are an engine defect (a genuine underrun of 58.48 / 60.73 / 65.61 pt caused by face
  substitution), so an engine-side fix can reach at most **3**.
* **2** of the five (`342`, `79`) are charged by the reader's line grouping and column bucketing; their ink is
  within **1.97** and **1.56** pt. No engine construct reaches them, because there is nothing to move. They
  need `verify_google.py`, which is outside an engine brief.
* **0** of those 3 are won *today* by the only construct with a measurement behind it, because the right tab
  stop costs `17_matched_runs`.

The prior finding's "23.5" and "5" figures are both still consistent with this: 23.5 is a mixed-engine
`classpick.py` number, 5 is the engine-side ceiling on the class, and this census adds that **only 3 of the 5
are engine-reachable and the one live construct currently wins none of them.**

---

## 5. What this file does not claim

* No `app/` change was made or proposed as shipped. The engine was built from unmodified `5ef9ea07` and
  converted 5 documents.
* The three Google renders used for the delta are **of the 25-Nov `.docx`**, not of a fresh upload: this
  sandbox cannot put new bytes in Drive (`GOOGLEDRIVE_UPLOAD_FILE` requires an `s3key` from a platform upload
  action, and a `/scratch` path is refused — "The file key does not belong to this project or session"). For
  `313` and `321` the `.docx` is **byte-identical** to HEAD's, and for `316`/`342`/`79` the difference is
  confined to `w:before`/`w:line`/`w:trHeight`, so the **horizontal** numbers are sound and the vertical ones
  (`18`) are not — which is exactly the one discrepancy reported above.
* The 60-row census is the **stored** verdicts, on three different engines; it is not a re-measurement of 60
  documents. `313`, `316`, `321`, `79` were re-measured here on HEAD and read the same solo `60`.
* Every LibreOffice figure is **proxy-only** and the proxy is blind to four of the five.

## 6. What the next run should do, in order

1. **`17_matched_runs` is the binding constraint on this class, not `60`.** The tab places the edge to 0.11 pt
   and `17` throws the document away. Either the piece matcher lets one source run be satisfied by consecutive
   render pieces on one baseline, or the trailing word is placed without a tab.
2. **Then `page_lines()` (`verify_google.py:2660`)** — one bbox per PyMuPDF line means a tabbed line is read as
   two, `60` reads *worse* on a render that is right to 0.11 pt, and every line-counting check sees double.
   This is a reader change and needs a corpus pass, not a document.
3. **Re-check `342` and `79` before working them.** Their charges are 20-30× the ink movement; the same
   predicate on the same line passes both. Two of the five CLEAN documents are instrument, not engine.
4. **Re-measure the 60 census rows on one engine** before quoting the class size — 37 of the 60 were measured
   on `74a152e7d3fb3d26`, 17 on `a4d8fca469bba636` (which regresses 16 of 16 against `025fe9d`), 6 on
   `025fe9deda5ac7b1`.

## Open questions

1. **Whether the tab construct can be made to keep `17_matched_runs`** — not measured by anyone. The piece
   matcher's rule at `verify_google.py:5799` is `matched >= ceil(0.9 * len(s_runs))`, and Google's export
   splits a tabbed run into two; whether a per-baseline concatenation rule would recover 34/34 is unmeasured.
2. **Whether `316` and `342` pass all 47 on their own store engine** — `342`'s `18` failure here is an artefact
   of the 25-Nov render, so its true state on `74a152e7d3fb3d26` is the store's word, not a measurement of mine.
3. **A fresh Google upload of the HEAD `.docx` for `316`, `342`, `79`** — blocked in this sandbox (no
   `s3key`), so those three were measured against the 25-Nov renders.
