# `60_text_column_right_edge` — 59 documents, 21.13 clean documents, and the price is wrong in both directions

**28 Nov 2026 · read-only analysis · clone `e1a736e3` · nothing under `app/` touched, nothing committed**

---

## 0. Verdict in one paragraph

**The class is real, it is one mechanism, and the check is wrong about 40 % of it.** All **five**
sole-failure documents are a genuine engine defect, reproduced here first-hand from the live Google
render: the body column collapses by **61–79 pt** because the `.docx` declares **DejaVu** and Google
substitutes **Arial**, which is 12–20 % narrower at the same size, and the engine has **no construct
that survives Google** to hold the right edge — its only one, `w:spacing` from `stretchTw()`, is on the
measured-ignored list. Separately, **17 of the 43 documents I could measure are charged on ink that
moved ≤ 3.9 pt**, because `columns()` buckets each side's lines independently by left edge with a hard
10 pt threshold; two of those charges are **+103.36** and **+181.62** pt against real ink movement of
**+2.79** and **+3.29** pt. So the 21.1 is **8.67** of engine defect, **4.17** of instrument defect,
**2.18** that already passes, and **6.11** that this run could not decide.

**The premise of the brief needs one correction before anything else.** This construct does not have
"zero prior investigation". There are **nine** findings named for it in
`tools/p2w-bench/FINDINGS/` (`60_text_column_right_edge-EDGE-IS-THE-FACE-4GOOGLE-1INSTRUMENT-24NOV-agentA.md`,
`-IT-FIRES-UNDER-AND-THE-CAUSE-IS-FONT-SUBSTITUTION-2322-fixer.md`,
`-GOOGLE-HAS-NO-DEJAVU-0830-fixer.md`, `-VERDICT-MIXED-1115-fixer.md`,
`-STALE-ENGINE-REFUTED-ON-ALL-FOUR-2318-fixer.md`, `-SHAPE-ANCHOR-1334-B1.md`, `-B-025500-a3f1.md`,
`60ed60_text_column_right_edge-01.md`) plus four under other names in the top-level `FINDINGS/`
(`60-COLUMN-RIGHT-EDGE-0137-27NOV.md`, `60-COLUMN-RIGHT-EDGE-CENSUS-27NOV-agent.md`,
`RIGHT-TAB-POSITION-60-EDGE-27NOV-fixer.md`, `60-RIGHT-TAB-HONOURED-INSTRUMENT-BLIND-27NOV-fixer.md`).
The grep that found nothing was looking for `column_right` and `60_text` in `FINDINGS/`; the files are
hyphenated and the bulk of them live in `tools/p2w-bench/FINDINGS/`. `DOCS-ROOT-CAUSES-24NOV.md` is
there too, not in `FINDINGS/`. **This report therefore confirms, corrects and prices that record rather
than starting from zero** — and it does the one thing the 27NOV census asked for and nobody had done:
it re-measures the class on a single engine.

---

## 1. What the check actually measures

`tools/p2w-bench/verify_google.py:2830`:

```python
c["60_text_column_right_edge"] = (over, under, over == 0 and under == 0)
```

`source` = pages whose column **overruns** the source's; `render` = pages whose column is **narrower**.

**The class is mostly, but not entirely, an underrun.** Of the 36 measured documents that still charge,
**24 fire UNDER** (the render's column is short) and **12 fire OVER** — `305`, `332`, `406`, `77`,
`academic-paper-ieee`, `delivery-challan`, `form16`, `gst-invoice-3line-items`,
`marksheet-university`, `purchase-order`, `question-paper`, `text-held-twice`. **All five
sole-failure documents fire UNDER.** The 23NOV finding's statement that the class fires under
(`…-IT-FIRES-UNDER-…-2322-fixer.md`) is true of the five it looked at and of the solo set, not of the
class; and every one of the 12 OVER charges is in the instrument group of §5.

The measurement, at `verify_google.py:2665-2775`:

| piece | value | line |
|---|---|---|
| `page_lines()` | one bbox per ink run, split at any internal span gap ≥ `GUTTER` | `:2665` |
| `GUTTER` | `2.0` pt | `:2666` |
| `BAND` | `0.06` of page height — header/footer lines dropped | `:2659` |
| `columns()` | clusters body lines by left edge, `b[0] - groups[-1][0][0] <= 10` | `:2671` |
| `COL_MIN_LINES` / `COL_MIN_SHARE` | `3` lines / `0.05` of body lines | `:2662-2663` |
| `edge()` | the column's **widest line** x1; slack = **median word width** of the column, capped | `:2704` |
| `SLACK_CAP` | `40.0` pt | `:2664` |
| `RIGHT_OVERRUN` / `RIGHT_UNDERRUN` | `6.0` / `8.0` pt | `:2660-2661` |

So the tolerance on an underrun is **8.0 + min(40, median word width)** pt. On the five solo documents
that tolerance is **27.3 – 48.0 pt** and the charge is **61–79 pt**: there is no reading of the numbers
under which these five are a tolerance artefact.

---

## 2. Every document that fails it — 59 of 213

Store: `benchmarks/gverify/*.json`, 214 files (206 `ok`, 8 `page_count_refused`). **213 of 214 are on one
engine, `a05b20eb05fe0fc8`** (the 214th, on `a4d8fca469bba636`, is not in this class), all stamped
`2026-11-27`. This is the single-engine re-measurement the 27NOV census listed as its own next step
(§6.4 of `60-COLUMN-RIGHT-EDGE-CENSUS-27NOV-agent.md`), and it is why my counts differ from that file's
60.

**59 documents fail `60_text_column_right_edge`.** `benchmarks/DEFECT-CLASSES-GOOGLE.md:25` agrees:
`| 60_text_column_right_edge | 59 | OPEN | 41 | 18 | 59 |`.

The shapes the brief quotes are exact:

* **5** documents fail `60` and nothing else — **`302_radiology_report`, `313_power_of_attorney`,
  `316_contract_with_schedules`, `321_auditors_report`, `370_offer_letter`**.
* **11** documents fail exactly `{18_displacement, 60_text_column_right_edge}`.
* The other 43 fail `60` alongside two to five others.

**Recomputed price.** `1/len(failed)` summed over the 59 = **21.13**, which is the 21.1
`classpick.py --leverage` prints (verified by running it).

**The five solo documents are not the ones the 27NOV census listed.** That file named
`313, 316, 321, 342, 79`. On `a05b20eb05fe0fc8` the set is `302, 313, 316, 321, 370` — `342` and `79`
have left the class and `302` and `370` have joined it. Every conclusion that file drew from "`342` and
`79` are instrument, so 2 of the 5 are not engine" is therefore **stale**, and §4 below replaces it.

### 2.1 Per-document detail

`src x1` / `ren x1` are the check's own `edge()` values on the charged column; `delta` is `ren − src`;
`slack` is the check's one-word tolerance; `same-text delta` is the **independent witness** of §3.
`pages` and `shape` are read from the source PDF.

| # | document | store score | also fails | pages | shape | charged column (left) | source x1 | render x1 | delta | slack | dir | same-text delta | class |
|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---|---:|---|
| 1 | `301_lab_report_panel` | 45/47 | 18_displacement | 1 | table-heavy | 28.00 | 478.29 | 415.82 | -62.47 | 30.29 | UNDER | -62.27 | (a) engine |
| 2 | `302_radiology_report` | 41/42 | none | 1 | two-column | 28.00 | 543.74 | 475.60 | -68.13 | 32.68 | UNDER | -65.65 | (a) engine |
| 3 | `310_court_judgment` | 39/42 | 43_within_10pt_x, 47_margins | 1 | single-column | 56.69 | 538.63 | 476.01 | -62.62 | 18.74 | UNDER | -81.86 | (a) engine |
| 4 | `311_fir_police_form` | 43/47 | 04_chars_missing, 18_displacement, 45_char_accuracy | 1 | table-heavy | 28.00 | 547.95 | 476.62 | -71.33 | 8.61 | UNDER | -68.85 | (a) engine |
| 5 | `312_affidavit_stamp_paper` | 38/42 | 04_chars_missing, 13_text_colours, 17_matched_runs | 1 | table-heavy | 40.00 | 547.47 | 492.52 | -54.95 | 20.40 | UNDER | -68.31 | (a) engine |
| 6 | `313_power_of_attorney` | 41/42 | none | 1 | single-column | 56.69 | 538.63 | 477.66 | -60.97 | 40.00 | UNDER | -58.48 | (a) engine |
| 7 | `314_tender_rfp_boq` | 44/47 | 42_justification_edges, 63_table_rows | 1 | table-heavy | 28.00 | 565.71 | 489.01 | -76.70 | 20.56 | UNDER | -74.21 | (a) engine |
| 8 | `316_contract_with_schedules` | 46/47 | none | 1 | two-column | 56.69 | 538.61 | 475.40 | -63.21 | 19.27 | UNDER | -60.73 | (a) engine |
| 9 | `317_rti_response` | 40/42 | 47_margins | 1 | single-column | 56.69 | 538.61 | 475.39 | -63.21 | 23.94 | UNDER | -79.81 | (a) engine |
| 10 | `321_auditors_report` | 41/42 | none | 1 | single-column | 56.69 | 538.61 | 470.52 | -68.09 | 28.49 | UNDER | -95.18 | (a) engine |
| 11 | `326_itr_computation` | 43/47 | 18_displacement, 59_shape_anchor, 63_table_rows | 1 | table-heavy | 28.00 | 563.98 | 488.03 | -75.95 | 35.62 | UNDER | -73.47 | (a) engine |
| 12 | `335_msds_safety_data_sheet` | 45/47 | 18_displacement | 1 | two-column | 28.00 | 565.44 | 487.83 | -77.61 | 28.76 | UNDER | -75.42 | (a) engine |
| 13 | `370_offer_letter` | 46/47 | none | 1 | two-column | 56.69 | 538.62 | 459.88 | -78.73 | 22.51 | UNDER | -96.03 | (a) engine |
| 14 | `406_passport_mrz_page` | 38/42 | 18_displacement, 26_text_overlap, 59_shape_anchor | 1 | two-column | 40.00 | 358.57 | 421.42 | 62.85 | 40.00 | OVER | 65.33 | (a) engine |
| 15 | `boq-tender-bill-of-quantities` | 45/47 | 18_displacement | 1 | table-heavy | 39.69 | 472.29 | 450.33 | -21.95 | 7.78 | UNDER | -19.25 | (a) engine |
| 16 | `14_stamp_chars_positioned_td` | 36/42 | 04_chars_missing, 13_text_colours, 18_displacement, 45_char_accuracy, 59_shape_anchor | 1 | table-heavy | 259.27 | 475.50 | 338.66 | -136.84 | 13.34 | UNDER | 1.78 | (b) instrument |
| 17 | `25_signature_block_underscores_txtpos` | 38/42 | 04_chars_missing, 18_displacement, 45_char_accuracy | 1 | two-column | 356.00 | 556.00 | 459.99 | -96.01 | 22.63 | UNDER | 1.52 | (b) instrument |
| 18 | `28_value_overflows_cell_txtpos` | 38/42 | 43_within_10pt_x, 47_margins, 59_shape_anchor | 1 | table-heavy |  |  |  |  |  |  |  | passes now |
| 19 | `305_vaccination_certificate` | 41/47 | 04_chars_missing, 13_text_colours, 17_matched_runs, 43_within_10pt_x, 45_char_accuracy | 1 | table-heavy | 93.20 | 109.42 | 137.45 | 28.03 | 10.03 | OVER | 4.86 | (b) instrument |
| 20 | `318_court_summons_form` | 39/47 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 43_within_10pt_x, 45_char_accuracy, 47_margins | 1 | table-heavy | 40.00 | 596.72 | 474.72 | -122.00 | 33.47 | UNDER | 1.05 | (b) instrument |
| 21 | `322_mutual_fund_factsheet` | 39/47 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 26_text_overlap, 44_header_footer, 45_char_accuracy | 1 | table-heavy | 28.00 | 530.40 | 409.80 | -120.60 | 24.11 | UNDER | 3.65 | (b) instrument |
| 22 | `323_credit_card_statement` | 40/47 | 04_chars_missing, 13_text_colours, 17_matched_runs, 18_displacement, 45_char_accuracy, 66_table_cell_width | 1 | table-heavy | 28.00 | 549.12 | 365.33 | -183.78 | 21.79 | UNDER | 9.97 | (b) instrument |
| 23 | `332_bom_on_drawing` | 42/47 | 18_displacement, 26_text_overlap, 47_margins, 59_shape_anchor | 1 | table-heavy | 314.93 | 319.07 | 500.69 | 181.62 | 4.13 | OVER | 4.34 | (b) instrument |
| 24 | `340_bill_of_lading` | 40/42 | 18_displacement |  |  |  |  |  |  |  |  |  | not measured |
| 25 | `342_packing_list` | 45/47 | 18_displacement |  |  |  |  |  |  |  |  |  | not measured |
| 26 | `343_air_waybill` | 40/42 | 18_displacement |  |  |  |  |  |  |  |  |  | not measured |
| 27 | `344_customs_declaration` | 43/47 | 04_chars_missing, 13_text_colours, 18_displacement |  |  |  |  |  |  |  |  |  | not measured |
| 28 | `352_certificate_ornate_border` | 37/42 | 04_chars_missing, 13_text_colours, 17_matched_runs, 45_char_accuracy |  |  |  |  |  |  |  |  |  | not measured |
| 29 | `360_restaurant_menu` | 38/42 | 18_displacement, 43_within_10pt_x, 47_margins |  |  |  |  |  |  |  |  |  | not measured |
| 30 | `363_warranty_card` | 40/42 | 18_displacement |  |  |  |  |  |  |  |  |  | not measured |
| 31 | `365_recipe_card` | 40/42 | 47_margins |  |  |  |  |  |  |  |  |  | not measured |
| 32 | `371_experience_certificate` | 36/42 | 04_chars_missing, 13_text_colours, 17_matched_runs, 45_char_accuracy, 59_shape_anchor |  |  |  |  |  |  |  |  |  | not measured |
| 33 | `373_leave_application_form` | 43/47 | 18_displacement, 23_line_pitch, 59_shape_anchor |  |  |  |  |  |  |  |  |  | not measured |
| 34 | `381_incident_report_timeline` | 43/47 | 04_chars_missing, 18_displacement, 59_shape_anchor |  |  |  |  |  |  |  |  |  | not measured |
| 35 | `383_api_docs_page` | 41/47 | 04_chars_missing, 18_displacement, 47_margins, 59_shape_anchor, 66_table_cell_width |  |  |  |  |  |  |  |  |  | not measured |
| 36 | `38_faux_bold_italic_synthesised` | 39/42 | 04_chars_missing, 46_text_crossing_rule |  |  |  |  |  |  |  |  |  | not measured |
| 37 | `393_spectrum_peak_table` | 44/47 | 18_displacement, 59_shape_anchor |  |  |  |  |  |  |  |  |  | not measured |
| 38 | `56_table_indented_from_margin` | 39/42 | 18_displacement, 59_shape_anchor |  |  |  |  |  |  |  |  |  | not measured |
| 39 | `65_two_col_full_width_figure_caption` | 35/42 | 04_chars_missing, 13_text_colours, 17_matched_runs, 44_header_footer, 45_char_accuracy, 59_shape_anchor |  |  |  |  |  |  |  |  |  | not measured |
| 40 | `77_arabic_rtl_document` | 40/47 | 17_matched_runs, 18_displacement, 26_text_overlap, 43_within_10pt_x, 47_margins, 59_shape_anchor | 1 | table-heavy | 322.60 | 334.02 | 388.60 | 54.58 | 11.42 | OVER | -185.87 | (b) instrument |
| 41 | `79_inr_indian_digit_grouping_table` | 40/42 | 59_shape_anchor | 1 | table-heavy |  |  |  |  |  |  |  | passes now |
| 42 | `academic-paper-ieee-2col-abstract` | 39/47 | 04_chars_missing, 17_matched_runs, 18_displacement, 27_text_off_page, 44_header_footer, 45_char_accuracy, 47_margins | 2 | two-column | 58.28 | 136.00 | 274.53 | 138.54 | 16.65 | OVER |  | undecided |
| 43 | `balance-sheet-and-profit-loss` | 44/47 | 18_displacement, 27_text_off_page | 2 | table-heavy | 446.70 | 552.77 | 464.65 | -88.12 | 22.02 | UNDER | 2.05 | (b) instrument |
| 44 | `delivery-challan` | 42/47 | 04_chars_missing, 13_text_colours, 18_displacement, 26_text_overlap | 1 | table-heavy | 422.76 | 473.53 | 550.74 | 77.21 | 21.61 | OVER | 0.47 | (b) instrument |
| 45 | `form16-part-b` | 43/47 | 04_chars_missing, 18_displacement, 27_text_off_page | 2 | table-heavy | 425.45 | 457.47 | 552.39 | 94.92 | 32.03 | OVER | 2.66 | (b) instrument |
| 46 | `gst-invoice-3line-items` | 45/47 | 18_displacement | 1 | table-heavy | 62.92 | 174.79 | 335.97 | 161.18 | 19.99 | OVER | 1.27 | (b) instrument |
| 47 | `gst-invoice-horizontal-rules-only` | 36/42 | 04_chars_missing, 18_displacement, 26_text_overlap, 44_header_footer, 45_char_accuracy | 1 | table-heavy | 426.22 | 549.92 | 453.37 | -96.55 | 27.19 | UNDER |  | undecided |
| 48 | `landscape-page-inside-portrait-document` | 45/47 | 18_displacement | 3 | single-column |  |  |  |  |  |  |  | passes now |
| 49 | `magazine-2col-pullquote-spanning` | 33/42 | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 43_within_10pt_x, 44_header_footer, 45_char_accuracy, 47_margins | 1 | two-column | 45.35 | 473.33 | 326.16 | -147.16 | 16.86 | UNDER | 2.72 | (b) instrument |
| 50 | `marksheet-subject-left-marks-right` | 44/47 | 18_displacement, 46_text_crossing_rule | 1 | table-heavy |  |  |  |  |  |  |  | passes now |
| 51 | `marksheet-university-consolidated` | 45/47 | 18_displacement | 1 | table-heavy | 488.65 | 502.66 | 541.90 | 39.24 | 14.01 | OVER | 2.96 | (b) instrument |
| 52 | `mutual-fund-statement` | 42/47 | 18_displacement, 25_invisible_text, 27_text_off_page, 66_table_cell_width | 2 | table-heavy |  |  |  |  |  |  |  | passes now |
| 53 | `one-page-rotated-180-degrees` | 40/47 | 04_chars_missing, 18_displacement, 27_text_off_page, 43_within_10pt_x, 62_table_columns, 63_table_rows | 2 | table-heavy | 64.88 | 87.50 | 62.10 | -25.40 | 10.69 | UNDER |  | undecided |
| 54 | `policy-2col-spanning-section-heading` | 34/42 | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 44_header_footer, 45_char_accuracy, 59_shape_anchor | 1 | two-column | 51.02 | 406.07 | 304.16 | -101.91 | 24.01 | UNDER | -1.15 | (b) instrument |
| 55 | `purchase-order` | 45/47 | 26_text_overlap | 1 | table-heavy | 428.30 | 449.71 | 553.07 | 103.36 | 17.51 | OVER | 3.56 | (b) instrument |
| 56 | `question-paper-marks-right-margin` | 40/42 | 18_displacement | 1 | two-column | 56.69 | 376.50 | 503.58 | 127.08 | 6.75 | OVER |  | undecided |
| 57 | `table-across-page-break-repeated-header` | 42/47 | 04_chars_missing, 18_displacement, 27_text_off_page, 44_header_footer | 3 | table-heavy |  |  |  |  |  |  |  | passes now |
| 58 | `text-held-twice-shadow-text` | 44/47 | 13_text_colours, 25_invisible_text | 1 | two-column | 45.35 | 551.99 | 589.58 | 37.59 | 22.04 | OVER | -9.73 | (b) instrument |
| 59 | `very-long-single-column-table` | 42/47 | 04_chars_missing, 18_displacement, 27_text_off_page, 44_header_footer | 3 | table-heavy |  |  |  |  |  |  |  | passes now |

---

## 3. The three places the defect can live — and the counts

I measured **43 of the 59** against the real Google render. Drive holds the `gv-<document>` Google Docs
that `gverify` created and scored; I exported each to PDF
(`GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE`, `application/pdf`), which reproduces the stored verdict
exactly (`source=0 render=1` on all five solo documents). **All 43 renders predate their stored verdict**
(render `modifiedTime` ≤ verdict `at` for 43 of 43), so the render *is* the one the store scored. The
remaining **16** have no `gv-` render in Drive and are marked **not measured** — I did not infer them.

The witness is the decisive instrument: for the charged column, take the widest line on the failing side,
find **the same string** on the other side (restricted to lines within 10 pt of the same left edge), and
measure how far *that text* moved. No clustering, no percentile, no widest-line estimator in the path.

| group | documents | worth (clean docs) | what it means |
|---|---:|---:|---|
| **(a) engine — ink really moved** | **15** | **8.67** | the render's column is short by more than the tolerance on the same text |
| **(b) instrument — the charge is not ink** | **17** | **4.17** | the same text moved ≤ 3.9 pt, inside the tolerance, and the check charged 20–180 pt |
| **passes now** | **7** | **2.18** | the stored verdict is stale relative to the current `verify_google.py` |
| **undecided** | **4** | **0.93** | no witness could be formed (text re-broken, or no charged column) |
| **not measured** | **16** | **5.18** | no render in Drive |
| **total** | **59** | **21.13** | matches the store exactly |

**(a) engine, 15:** `301_lab_report_panel`, `302_radiology_report`, `310_court_judgment`,
`311_fir_police_form`, `312_affidavit_stamp_paper`, `313_power_of_attorney`, `314_tender_rfp_boq`,
`316_contract_with_schedules`, `317_rti_response`, `321_auditors_report`, `326_itr_computation`,
`335_msds_safety_data_sheet`, `370_offer_letter`, `406_passport_mrz_page`,
`boq-tender-bill-of-quantities`.

**(b) instrument, 17:** `14_stamp_chars_positioned_td`, `25_signature_block_underscores_txtpos`,
`305_vaccination_certificate`, `318_court_summons_form`, `322_mutual_fund_factsheet`,
`323_credit_card_statement`, `332_bom_on_drawing`, `77_arabic_rtl_document`,
`balance-sheet-and-profit-loss`, `delivery-challan`, `form16-part-b`, `gst-invoice-3line-items`,
`magazine-2col-pullquote-spanning`, `marksheet-university-consolidated`,
`policy-2col-spanning-section-heading`, `purchase-order`, `text-held-twice-shadow-text`.

**There is no (c).** Not one document in the class is "Google reflowed the column and cannot hold the
edge". The line counts are identical between source and render on every solo document (23/23, 29/29,
26/26, 33/33, 20/20), so Google did not re-break the text at all — it laid each source line down as its
own line and every line simply ended early. The distinction matters: a reflow would be a `(c)`, a
substitution is a face the engine chose, which is `(a)`.

### 3.1 The five sole-failure documents — all engine

| document | score | pages | shape | charged col left | source x1 | render x1 | charged delta | slack | tolerance | same-text delta | verdict |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| `302_radiology_report` | 41/42 | 1 | two-column | 28.00 | 543.74 | 475.60 | -68.13 | 32.68 | 40.68 | -65.65 | (a) engine |
| `313_power_of_attorney` | 41/42 | 1 | single-column | 56.69 | 538.63 | 477.66 | -60.97 | 40.00 | 48.00 | -58.48 | (a) engine |
| `316_contract_with_schedules` | 46/47 | 1 | two-column | 56.69 | 538.61 | 475.40 | -63.21 | 19.27 | 27.27 | -60.73 | (a) engine |
| `321_auditors_report` | 41/42 | 1 | single-column | 56.69 | 538.61 | 470.52 | -68.09 | 28.49 | 36.49 | -95.18 | (a) engine |
| `370_offer_letter` | 46/47 | 1 | two-column | 56.69 | 538.62 | 459.88 | -78.73 | 22.51 | 30.51 | -96.03 | (a) engine |

`tolerance` = `8.0 + slack`. Every charge is **1.27× to 2.58×** its own tolerance (302: 1.67×,
313: 1.27×, 316: 2.32×, 321: 1.87×, 370: 2.58×), and the independent witness agrees in direction on all
five, and in magnitude to within **2.5 pt** on three of them (302: −65.65 vs −68.13; 313: −58.48 vs
−60.97; 316: −60.73 vs −63.21). On `321` and `370` the witness moves *further* than the charge
(−95.18 vs −68.09, −96.03 vs −78.73) — the render's widest line is not the source's widest line, so the
charge understates those two. The verdict is the same either way.

---

## 4. One mechanism, traced end to end: `313_power_of_attorney`

### 4.1 The page's own ink (PyMuPDF, not the check)

`/scratch/work/p2w/corpus/313_power_of_attorney.pdf`, page 1, A4 `595.28 × 841.89`:

* body column left edge **56.69 pt**; its widest line x1 **538.63 pt**
* **8 of the 27 body lines end at exactly 538.6** — the page justified them to a measure of
  **481.94 pt** (`538.63 − 56.69`)
* the text is set in **`AAAAAA+DejaVuSerif` 10.0 pt**

### 4.2 What the engine wrote

The `.docx` Google converted (Drive `313_power_of_attorney.docx`, `1ITwR6O1VRDHjJiOXw9iz-CoDlBsLbvNw`),
`word/document.xml`:

| construct | value | count | engine site |
|---|---|---|---|
| `w:pgSz` | `w:w="11906" w:h="16838"` (A4) | 1 | `DocxWriter.java:2454` region |
| `w:pgMar` | `top=0 right=0 bottom=0 left=0` | 1 | `DocxWriter.java:2454` |
| `w:ind` | `w:left="1134" w:right="0" w:firstLine="0"` | 30 | `flowFromBox`, `DocxWriter.java:4678` |
| `w:jc` | `center` only, on the title | 1 | `DocxWriter.java:4679` |
| `w:tabs` | — | **0** | — |
| `w:rFonts` | `DejaVuSerif` | — | — |

**The measure is already correct.** `11906 − 1134 − 0 = 10772` twips = **538.6 pt** — the paragraph's
text area ends exactly where the page's ink ends. The arithmetic that is *wrong* is not the indent; it
is that **nothing makes the line reach it**:

* `rightTw` is `0` for every `align == 0` paragraph. It is only computed at
  `DocxWriter.java:4462-4478`, inside the `align == 1` (centre) and `align == 2` (right) branches.
* `w:jc` is emitted only for `align == 1` and `align == 2` (`DocxWriter.java:4679-4680`). A justified
  source line gets **no** `w:jc`.
* the only stretch the engine emits is `stretchTw(b)` → `w:spacing`, at `DocxWriter.java:4682`
  (call) and `:4723` (definition), whose own docstring says it exists to put "a line the page
  justified back on its measure".

### 4.3 What Google did

Export of `gv-313_power_of_attorney` (`14YHHjFe4FFjM8HCYxfbcxgaHUVP_CwFEvq_UdT6QzjI`):

* body column left **57.00 pt**, widest line x1 **477.66 pt** → **−60.97 pt**
* the **same string**, same baseline: `2. The Attorney shall have the power to …` ends **538.63** in the
  source and **477.66** in the render → **−60.97**; the witness on the next two lines gives **−58.48**
  and **−60.73**
* the render's face is **`CAAAAA+ArialMT` 10.0 pt** where the source drew **`DejaVuSerif` 10.0 pt**
* the same line's width in the two faces: **481.93 → 423.14**, a ratio of **0.878**; across the 30
  matched lines of this document the ratio is **p10 0.848 / median 0.871**

**The mechanism, in one sentence:** the engine declares `DejaVuSerif`, Google has no such family and
substitutes Arial at 12–13 % narrower advances, and because the line is one paragraph with no `w:jc`
and no tab, its right end is whatever Arial's advances add up to — so the column's widest line lands
61 pt short of the measure the `.docx` already declares.

The same trace holds on the other four: `316` −63.21 (ratio 0.873), `321` −68.09, `370` −78.73,
`302` −68.13 (its body is ragged, not justified: 543.74 / 536.62 / 529.04 / 498.35, so there the
justification is not even in play and the whole deficit is the face).

---

## 5. The instrument defect, with its own numbers

### 5.1 `purchase-order` — +103.36 pt charged, +2.79 pt of ink

* charged column: left **428.30**, 7 source lines / 8 render lines, `src_edge` **449.71**,
  `ren_edge` **553.07**, delta **+103.36**, slack 17.51 → OVER
* the page's own widest body line: source **552.76** (`For Kastura Home Products Pvt. Ltd.`, x0 438.38),
  render **555.55** (same string, x0 438.75) → **+2.79 pt**, well inside `RIGHT_OVERRUN = 6.0`
* **the source's widest line is not in the source's bucket.** Its left edge is `438.38`; the bucket seed
  is `428.30`; `438.38 − 428.30 = 10.08 > 10`, so it is excluded on the source side. In the render the
  same line sits at `438.75` and `438.75 − 428.30 = 10.45` — but the render's bucket is seeded from its
  own first line, and it **is** included there. The check then compares the source's *narrow* cluster
  against the render's *wide* one.

`verify_google.py:2671` is the whole cause:

```python
for b in sorted(inside, key=lambda b: b[0]):
    if groups and b[0] - groups[-1][0][0] <= 10:
```

A hard 10 pt threshold on left edges, applied to each side **independently**, with no correspondence
test between the two sides. A 0.37 pt shift in a left edge — which is all a substitute face does — moves
a line across the boundary and the check compares two different sets of lines.

### 5.2 `332_bom_on_drawing` — +181.62 pt charged, +3.29 pt of ink

Charged column left **314.93**, `src_edge` **319.07**, `ren_edge` **500.69** → **+181.62** with slack
4.13. The page's own widest body line: source **715.00**, render **718.29** → **+3.29 pt**. The source's
widest line is at x0 700.53, nowhere near the bucket at 314.93; the render's line at 314.81 that ends at
500.69 is `Item` (`Item` ends at 325.35 in the source — the witness's **+4.34**).

### 5.3 How much of the class this is

**17 of 43 measured documents (40 %)** are charged this way, worth **4.17 clean documents**. Fixing only
the instrument would take the class from 21.13 to **16.96**.

### 5.4 A fix I tried and it failed — recorded so nobody repeats it

Replacing the render's clustering with an **assignment** (each render line joins the source column it
overlaps most) flips **15** documents to pass and **regresses 6** — `28_value_overflows_cell_txtpos`,
`landscape-page-inside-portrait-document`, `marksheet-subject-left-marks-right`,
`mutual-fund-statement`, `table-across-page-break-repeated-header`, `very-long-single-column-table`
(`/scratch/work/assign60.py`, results in `assign60.json`). Overlap assignment pulls a neighbouring
column's lines into the bucket and inflates the render edge. **The bucketing defect is proven; a
replacement bucketing is not yet designed.** A fix that tracks the *same text* across sides would pass
the 17 and keep the 15 failing, but it fails exactly where a legitimate re-break occurs — which is what
the one-word slack exists to cover.

### 5.5 The store is stale against the current check

**7 of the 43 stored-failing documents pass on the render that was scored** — `28_value_overflows_cell_txtpos`,
`79_inr_indian_digit_grouping_table`, `landscape-page-inside-portrait-document`,
`marksheet-subject-left-marks-right`, `mutual-fund-statement`,
`table-across-page-break-repeated-header`, `very-long-single-column-table` (worth 2.18). Since all 43
renders predate their verdicts, the change is in `verify_google.py`, not in the renders: the
`page_lines()` `GUTTER` split (`:2665`) landed after the store was written, and its own docstring
records the census — *"52 unchanged, 10 over -> pass, 1 over -> under"* at engine `a05b20eb05fe0fc8`.
**The 21.1 is therefore computed from verdicts the current instrument no longer returns.**

---

## 6. The engine change, and what it is worth

### 6.1 What will not work, each with the measurement that refutes it

| construct | result | source |
|---|---|---|
| `w:ind w:right` = `pageWidth − b.right` alone | the edge does not move; the paragraph is one line that already fits, so a smaller measure cannot pull it right | §4.2 arithmetic; `RIGHT-PIN-WRAPS-…-0126-relay.md` |
| `w:jc="distribute"` + that indent | `60` read `(0,1,False)` in **both** arms, 28 lines wrapped, `17_matched_runs` 33→21, score 41/42→39/42 — on `302_radiology_report`, one build, Google | `RIGHT-PIN-WRAPS-IN-GOOGLE-INERT-IN-LO-0126-relay.md` |
| `w:jc="both"` on these paragraphs | a one-line paragraph's only line is its last line; `both` leaves it ragged | WordprocessingML semantics; the engine's own paragraph-per-line structure (§4.2, 30 paragraphs / 30 `w:ind` for 29 body lines) |
| `w:w` (character scaling) | **measured-ignored by Google**, four ways | `google_safe.py:74-77` → `FINDINGS/GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md` |
| `w:spacing` (what `stretchTw()` already emits) | **measured-ignored by Google**, 380.1 → 380.1 | `google_safe.py:78-80`, `DocxWriter.java:4723` |
| family swap `DejaVuSerif→Georgia`, `DejaVuSans→Verdana` | recovers **38 of the 58 pt** on `316` (480.1 → 518.1) and **still fails**: the deciding column moved the wrong way (480.1 → 471.8) | `…-IT-FIRES-UNDER-…-2322-fixer.md` |

### 6.2 The change that does hold the edge in Google

**A right tab stop at the measure.** Measured live on `321_auditors_report`: the trailing word's right
edge landed at **538.50** where the page drew **538.61** — **0.11 pt** — on the identical baseline
(`84.73` both pieces), so it did not wrap
(`60-RIGHT-TAB-HONOURED-INSTRUMENT-BLIND-27NOV-fixer.md`).

The engine already emits exactly this construct, gated to table rows:

```java
// DocxWriter.java:3806-3812
if (last && b.right > ctx.pageWidthPt - 2f && (b.right - frameX) > clear) {
    int posTw = (int) Math.round((b.right - frameX) * TWIPS_PER_PT);
    tabs.append("<w:tab w:val=\"right\" w:pos=\"").append(posTw).append("\"/>");
```

**The named engine change:** in `flowFromBox` (`DocxWriter.java:4443`), for `align == 0`, non-rotated,
not `inColumn`, where the line is a full-measure line (`b.right` equals the column's own right edge —
on `313`, 8 of 27 lines at 538.6), emit `<w:tabs><w:tab w:val="right" w:pos="9639"/></w:tabs>` and a
`<w:tab/>` before the last word.

**The twips, before and after (`313`, `b.x = 56.69`, `b.right = 538.63`):**

| | today | with the change |
|---|---:|---:|
| `w:ind w:left` | `1134` | `1134` (unchanged) |
| `w:ind w:right` | `0` | `0` (unchanged — the measure is already right) |
| `w:pgMar w:right` | `0` | `0` (unchanged) |
| paragraph measure | `10772` tw = 538.6 pt | `10772` tw = 538.6 pt |
| tab stop | **none** | `<w:tab w:val="right" w:pos="9639"/>` = 481.95 pt from the indent |
| render's widest line | **477.66** (−60.97) | **538.6** (measured 0.11 pt on `321`) |

**Expected effect: 5.0 clean documents** — the five sole-failure documents — **and 0 today**, because
the same measurement that places the edge costs `17_matched_runs`: on `321` the export splits the tabbed
line into two PyMuPDF lines, the column's widest line falls back to `239.54`, `60` reads **worse**
(473.00 → 461.58), and `17_matched_runs` falls **34 → 13**. One failure is swapped for another. **`17`
is the binding constraint on this class, not `60`.** Beyond the five solo documents the same change
cannot win anything until `18_displacement` and the other co-failures are also clear.

**Honest caveat on the construct itself.** A right tab moves the last word to the edge and leaves the
gap before it — it fixes the *measured* edge, not the raggedness. The render still will not look
justified. Only re-breaking the block to the measure with `w:jc="both"` would, and that changes line
counts, which is `23_line_pitch` and `17_matched_runs` territory.

---

## 7. What this run did and did not do

**Did.** Fetched the full 214-document corpus (`corpus-fetch.sh`: *"corpus: 214 PDFs, 213 scored in
RANKING.csv, 0 missing"*). Exported 43 live Google renders from Drive and re-ran the shipped verifier on
them, reproducing `source=0 render=1` on all five solo documents. Read the `.docx` Google actually
converted (4 of the 5 solo documents) and traced `w:ind`/`w:pgMar`/`w:pgSz`/`w:jc`/`w:tabs` in it.
Measured the ink on both sides with PyMuPDF, independently of the check. Re-ran `classpick.py --leverage`
and reproduced 21.1. Wrote a mirror of `page_lines`/`columns`/`edge` with the constants copied verbatim
(`/scratch/work/probe60.py`).

**Did not — and this bounds every claim above.** **No live Google round trip of a modified `.docx`.**
`GOOGLEDRIVE_CREATE_FILE` requires `file_to_upload.s3key`, and the download path returns only a
`workspace_path`; a `/scratch` path is refused. So the right-tab change in §6.2 is **named and
arithmetically specified but not re-measured by me** — its 0.11 pt and its `17` cost are the 27NOV
run's measurements, and I say so. No engine build was made and no `app/` file was changed. The 16
documents with no render in Drive are unmeasured, not classified.

---

## 8. What to do, in order

1. **Re-run `gverify` over the class on the current `verify_google.py`.** 7 of 43 already pass; the 21.1
   is priced against a check that no longer returns those verdicts. That is 2.18 clean documents of
   pure bookkeeping.
2. **Fix the bucketing in `columns()` (`verify_google.py:2671`)** — it is worth **4.17 clean documents**
   and needs no Google round trip, only a re-measurement. A replacement that assigns lines to columns by
   a correspondence test rather than two independent 10 pt chains. My overlap variant is refuted (§5.4);
   start from that failure.
3. **Then the engine, and only with `17` fixed first.** The right tab is the one construct measured to
   place the edge (0.11 pt); it is worth **5.0 clean documents** and nets **0** while `17_matched_runs`
   rejects a tab-split line.
4. **Do not spend another run on `w:jc="distribute"`, `w:w` or `w:spacing`.** All three are refuted by
   measurement, two of them on Google's own ignored list.

---

## Open questions

1. **Whether `17_matched_runs` can accept a tab-split line.** Unmeasured by anyone. Its rule is
   `matched >= ceil(0.9 * len(s_runs))` (`verify_google.py:5799`) and Google's export splits a tabbed
   run in two; whether a per-baseline concatenation recovers 34/34 is not known. This gates the whole
   engine half of the class.
2. **Whether Google honours docx font embedding** (`fontTable.xml` `w:embedRegular`), which would remove
   the substitution instead of compensating for it. Unmeasured — the 23NOV run named it as option 1 and
   never tested it.
3. **What family matches DejaVu Serif to within 1 %.** The 23NOV swap used Georgia and recovered 38 of
   58 pt; no local advance-width comparison against the source PDF was ever run, which is the cheap
   measurement that would pick the family.
4. **A fresh Google render for the 16 unmeasured documents** — `340, 342, 343, 344, 352, 360, 363, 365,
   371, 373, 381, 383, 38, 393, 56, 65` — worth 5.18 clean documents and unclassified here.
5. **Whether the 4 undecided documents** (`academic-paper-ieee-2col-abstract`,
   `gst-invoice-horizontal-rules-only`, `one-page-rotated-180-degrees`,
   `question-paper-marks-right-margin`) are engine or instrument; the witness could not be formed
   because the render re-broke the line or no column was charged.
