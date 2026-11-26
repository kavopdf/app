# 60_text_column_right_edge — the edge is not in the file, and the instrument convicts on a tenth of a point

**27 Nov 2026, 01:37 IST · explore run · clone at `a1efec6` · engine built from `app/src` at that commit**
**Nothing under `app/src/`, `tools/` or `benchmarks/` was touched. This file is the only write.**

## Verdict in one paragraph

**Engine, for the class; instrument, for a measured subset — and both are proven here.** The predicate
measures the right quantity and its arithmetic is sound (a trailing space is 2.25-2.86 pt against a 6.0 pt
tolerance; cell borders are not in the text layer at all; the ink-versus-advance gap is 0.3-1.3 pt). But the
column edge it compares is **not a property the engine writes**: for a left-aligned line `rightTw` stays 0
(`DocxWriter.java:4444`), no `w:jc` is emitted (`:4673-4675`), `w:pgMar right="0"` (`:2448`), so the edge is
whatever the renderer's face makes of the string. Two declared quantities then lose the extent: the size is
**floored to a half-point** (`halfPointsDown`, `:7335`), measured at −1.2 % to −6.4 % of a line's advance on
**26 of the 61 failing documents**, and the face may be **one the renderer does not have** (33 of the 61
declare DejaVu, which Google lacks, and a fallback with Arial/Times metrics is 12-21 % narrower than the face the source used).
Separately, `columns()` (`verify_google.py:2671`) defines the columns **independently on each side** with a
hard 10 pt bucket taken from the bucket's own minimum (`:2692`), so a line that jitters a **tenth of a
point** across that boundary is charged to the wrong column — measured on `purchase-order`, where a line
that moved **0.12 pt** turns a column into **+102.98 pt OVER**. Under a symmetric predicate, 8 of the 15
LibreOffice failures flip to PASS and 2 new ones fire, which is the proof that the correction is not a
check gone blind.

**If both halves land: 6 documents become CLEAN (the 6 that fail `60` alone). The class is worth 24.0
CLEAN in `classpick.py --leverage`.**

## 1. The predicate, in words

`verify_google.py:2646-2790`. For every page of the source PDF and the Google-exported PDF:

1. **Lines.** `page_lines()` (`:2660`) takes every text line with any non-space character, as a bbox from
   `get_text("dict")`. The bbox is the **advance** edge, not the ink edge.
2. **Bands.** A line is *inside* when `y0 >= 0.06·H` and `y1 <= H − 0.06·H` (`BAND`, `:2651`); everything
   else is a header/footer band line. Band lines are kept only if they start within 10 pt of a body column's
   left edge (`:2696`), so a masthead cannot become the column's edge.
3. **Columns.** The inside lines are sorted by left edge and bucketed: a line joins the current bucket when
   `b[0] − bucket[0].left <= 10` (`:2692`). A bucket is a column when it holds at least
   `max(3, 5 % of the page's inside lines)` lines (`COL_MIN_LINES`, `COL_MIN_SHARE`, `:2656-2657`).
4. **The edge.** `edge()` (`:2704`) returns the **widest line's right edge** in that column, plus a slack:
   `min(40.0, median word width of the column)` (`SLACK_CAP`, `:2658`).
5. **The comparison.** The source's columns are matched to the render's by nearest left edge within 10 pt
   (`:2760`); a column with no partner is skipped (it is `04/05`'s business). Then, per column:
   * **over** when `rg > rs + 6.0 + slack` (`RIGHT_OVERRUN`, `:2653`)
   * **under** when `rg < rs − 8.0 − slack` (`RIGHT_UNDERRUN`, `:2655`)
   and the check fails if either counter is non-zero (`:2786`). There is also a page-level safety net: two
   lines further right than `source_max + 18 pt` fail the page even when no column caught them (`:2777-2781`).

**So the tolerance is not a fixed number**: it is 6 pt of overrun or 8 pt of underrun **plus one median word
of that column**, which over 1421 columns of the corpus is p50 = 24.0 pt, p75 = 28.3, p90 = 34.0, capped at
40. On `purchase-order` the Rate column's allowance was `6.0 + 17.46 = 23.46 pt` and the charge was 102.98.

## 2. Every document that fails it, with the numbers

**The store does not contain the numbers.** `benchmarks/gverify/*.json` carries `failed: [...]` and nothing
else — the gap `DOCS-ROOT-CAUSES-24NOV.md` already flagged ("storing the pair costs nothing and makes this
class falsifiable") is still open. So the numbers below are **measured by this run**, not read from the
store: the source edge is the source PDF's own text layer, and the "render edge" is the same document
rendered by **LibreOffice from the .docx this engine emitted**, i.e. a renderer that has the face the file
names. The Google side is the store's verdict only (see §6 for why Google could not be re-measured here).

* 213 documents in `benchmarks/gverify`, 205 scored, **61 fail `60_text_column_right_edge`**.
* Of those 61, **46 pass the identical check in LibreOffice and 15 fail there too** — the same 15/56 split
  the 24 Nov investigation measured.
* Declared faces: **33 name DejaVu** (Google has none of them), 28 name Arial/Times New Roman or Noto.
* **26 of the 61 carry a body size that is not on the half-point grid**: 6.8→6.5 in 12 documents,
  7.2→7.0 in 10, 6.6→6.5 in 8, 7.4→7.0 in 7, 6.4→6.0 in 7, 8.4→8.0 in 3, 6.2→6.0 in 2, 8.8→8.5 in 2,
  8.6→8.5 in 2, 9.2→9.0 in 2, 7.6→7.5 in 2, 8.9→8.5 in 1 — every one of them a **narrower** line.

The table is the deciding column of each document (the column with the largest |delta|), sorted by |delta|.
`src` and `ren` are the right edges in points, `slack` the column's one-word allowance, `store` the
`passed/total` in `benchmarks/gverify`.

| document | store | LO | page | col left | src edge | ren edge | delta | slack | declared faces |
|---|---|---|---|---|---|---|---|---|---|
| `323_credit_card_statement` | 40/47 | FAIL | 1 | 28.0 | 549.12 | 357.7 | -191.42 | 21.79 | DejaVuSans |
| `360_restaurant_menu` | 38/42 | FAIL | 1 | 52.0 | 144.12 | 285.7 | 141.58 | 30.77 | DejaVuSans,DejaVuSerif |
| `79_inr_indian_digit_grouping_table` | 41/42 | FAIL | 1 | 132.27 | 289.97 | 149.7 | -140.27 | 17.72 | Arial,Times New Roman |
| `purchase-order` | 44/47 | FAIL | 1 | 428.3 | 449.71 | 552.68 | 102.98 | 17.51 | Arial |
| `77_arabic_rtl_document` | 40/47 | FAIL | 1 | 322.6 | 334.02 | 428.9 | 94.88 | 11.42 | NotoNaskhArabic,NotoSans |
| `gst-invoice-horizontal-rules-only` | 36/42 | FAIL | 1 | 426.22 | 549.92 | 456.46 | -93.46 | 27.19 | Arial |
| `balance-sheet-and-profit-loss` | 45/47 | FAIL | 2 | 446.7 | 552.77 | 464.76 | -88.0 | 22.02 | Arial,Times New Roman |
| `delivery-challan` | 42/47 | FAIL | 1 | 422.76 | 473.53 | 550.94 | 77.41 | 21.61 | Arial |
| `38_faux_bold_italic_synthesised` | 40/42 | FAIL | 1 | 55.41 | 511.58 | 568.37 | 56.79 | 25.66 | Arial,Times New Roman |
| `text-held-twice-shadow-text` | 44/47 | FAIL | 1 | 45.35 | 551.99 | 589.24 | 37.25 | 22.04 | Arial,Times New Roman |
| `one-page-rotated-180-degrees` | 42/47 | FAIL | 2 | 366.88 | 513.28 | 477.06 | -36.22 | 18.1 | Arial,Times New Roman |
| `question-paper-marks-right-margin` | 40/42 | FAIL | 1 | 56.69 | 468.16 | 504.1 | 35.94 | 6.75 | Arial,Times New Roman |
| `318_court_summons_form` | 39/47 | FAIL | 1 | 446.47 | 460.09 | 495.58 | 35.48 | 9.54 | DejaVuSans,DejaVuSerif |
| `28_value_overflows_cell_txtpos` | 38/42 | FAIL | 1 | 86.0 | 404.82 | 433.16 | 28.34 | 21.69 | Arial,Times New Roman |
| `311_fir_police_form` | 42/47 | pass | 1 | 141.0 | 312.51 | 337.46 | 24.95 | 27.83 | DejaVuSans,DejaVuSerif |
| `magazine-2col-pullquote-spanning` | 33/42 | pass | 1 | 45.35 | 473.33 | 450.0 | -23.33 | 16.86 | Arial,Times New Roman |
| `mutual-fund-statement` | 43/47 | pass | 1 | 39.69 | 399.69 | 376.78 | -22.91 | 26.85 | Arial |
| `boq-tender-bill-of-quantities` | 45/47 | FAIL | 1 | 39.69 | 472.29 | 451.54 | -20.74 | 7.78 | Arial,Times New Roman |
| `academic-paper-ieee-2col-abstract` | 40/47 | pass | 1 | 126.2 | 512.52 | 493.98 | -18.54 | 16.31 | Arial,Times New Roman |
| `312_affidavit_stamp_paper` | 38/42 | pass | 1 | 298.42 | 311.9 | 329.21 | 17.3 | 16.65 | DejaVuSans,DejaVuSerif |
| `343_air_waybill` | 40/42 | pass | 1 | 24.0 | 541.07 | 524.1 | -16.98 | 29.68 | DejaVuSans,DejaVuSansMono,DejaVuSe |
| `383_api_docs_page` | 41/47 | pass | 1 | 28.0 | 422.89 | 405.98 | -16.91 | 21.11 | DejaVuSans,DejaVuSansMono |
| `marksheet-subject-left-marks-right` | 45/47 | pass | 1 | 45.35 | 418.78 | 402.47 | -16.32 | 23.84 | Arial |
| `very-long-single-column-table` | 45/47 | pass | 1 | 51.02 | 340.17 | 327.49 | -12.69 | 8.23 | Arial,Times New Roman |
| `table-with-merged-cells` | 45/47 | pass | 1 | 42.52 | 295.38 | 284.3 | -11.08 | 17.2 | Arial,Times New Roman |
| `gst-invoice-3line-items` | 45/47 | pass | 1 | 39.69 | 368.15 | 358.52 | -9.63 | 16.81 | Arial |
| `form16-part-b` | 45/47 | pass | 1 | 42.52 | 241.35 | 231.86 | -9.49 | 14.93 | Arial,Times New Roman |
| `65_two_col_full_width_figure_caption` | 35/42 | pass | 1 | 306.64 | 533.47 | 525.77 | -7.7 | 19.03 | Arial,Times New Roman |
| `371_experience_certificate` | 36/42 | pass | 1 | 383.23 | 396.88 | 391.09 | -5.79 | 8.55 | DejaVuSans,DejaVuSerif |
| `marksheet-university-consolidated` | 45/47 | pass | 1 | 39.69 | 412.37 | 406.78 | -5.59 | 17.76 | Arial,Times New Roman |
| `322_mutual_fund_factsheet` | 38/47 | pass | 1 | 28.0 | 530.4 | 524.86 | -5.54 | 24.11 | DejaVuSans |
| `landscape-page-inside-portrait-document` | 45/47 | pass | 2 | 72.19 | 177.06 | 171.82 | -5.24 | 15.63 | Arial,Times New Roman |
| `policy-2col-spanning-section-heading` | 34/42 | pass | 1 | 51.02 | 406.07 | 400.99 | -5.08 | 24.01 | Arial,Times New Roman |
| `salary-slip-factory-wages` | 44/47 | pass | 1 | 42.52 | 371.57 | 366.62 | -4.95 | 21.61 | Arial |
| `352_certificate_ornate_border` | 37/42 | pass | 1 | 434.29 | 451.08 | 455.99 | 4.91 | 19.64 | DejaVuSans,DejaVuSerif |
| `301_lab_report_panel` | 45/47 | pass | 1 | 170.0 | 230.44 | 233.46 | 3.02 | 25.2 | DejaVuSans,DejaVuSansMono,DejaVuSe |
| `340_bill_of_lading` | 39/42 | pass | 1 | 194.0 | 277.55 | 280.46 | 2.91 | 20.23 | DejaVuSans,DejaVuSansMono,DejaVuSe |
| `365_recipe_card` | 40/42 | pass | 1 | 40.0 | 351.54 | 349.2 | -2.35 | 26.46 | DejaVuSans,DejaVuSerif |
| `305_vaccination_certificate` | 38/47 | pass | 1 | 148.74 | 158.78 | 156.6 | -2.18 | 7.9 | DejaVuSans |
| `310_court_judgment` | 39/42 | pass | 1 | 56.69 | 538.63 | 540.29 | 1.66 | 18.74 | DejaVuSerif |
| `341_shipping_manifest` | 45/47 | pass | 1 | 453.0 | 513.18 | 511.57 | -1.61 | 25.96 | DejaVuSans |
| `14_stamp_chars_positioned_td` | 38/42 | pass | 1 | 259.27 | 475.5 | 473.9 | -1.6 | 13.34 | Arial,Times New Roman |
| `335_msds_safety_data_sheet` | 46/47 | pass | 1 | 241.0 | 298.47 | 297.23 | -1.24 | 5.52 | DejaVuSans,DejaVuSerif |
| `313_power_of_attorney` | 41/42 | pass | 1 | 56.69 | 538.63 | 539.85 | 1.22 | 40.0 | DejaVuSerif |
| `370_offer_letter` | 45/47 | pass | 1 | 56.69 | 538.62 | 537.48 | -1.14 | 22.51 | DejaVuSans,DejaVuSerif |
| `373_leave_application_form` | 43/47 | pass | 1 | 204.0 | 289.3 | 290.32 | 1.01 | 25.48 | DejaVuSans,DejaVuSerif |
| `316_contract_with_schedules` | 46/47 | pass | 1 | 56.69 | 538.61 | 537.79 | -0.83 | 19.27 | DejaVuSans,DejaVuSerif |
| `314_tender_rfp_boq` | 42/47 | pass | 1 | 28.0 | 565.71 | 565.06 | -0.65 | 20.56 | DejaVuSans,DejaVuSerif |
| `321_auditors_report` | 41/42 | pass | 1 | 56.69 | 538.61 | 539.21 | 0.6 | 28.49 | DejaVuSerif |
| `381_incident_report_timeline` | 44/47 | pass | 1 | 28.0 | 561.6 | 561.09 | -0.5 | 21.61 | DejaVuSans,DejaVuSerif |
| `302_radiology_report` | 41/42 | pass | 1 | 28.0 | 543.74 | 543.26 | -0.48 | 32.68 | DejaVuSans,DejaVuSerif |
| `326_itr_computation` | 44/47 | pass | 1 | 28.0 | 563.98 | 563.5 | -0.48 | 35.62 | DejaVuSans,DejaVuSerif |
| `332_bom_on_drawing` | 43/47 | pass | 1 | 314.93 | 319.07 | 319.53 | 0.47 | 4.13 | DejaVuSans |
| `342_packing_list` | 45/47 | pass | 1 | 291.09 | 300.0 | 300.45 | 0.46 | 8.9 | DejaVuSans,DejaVuSansMono,DejaVuSe |
| `393_spectrum_peak_table` | 45/47 | pass | 1 | 42.68 | 63.32 | 63.77 | 0.46 | 4.77 | DejaVuSans |
| `344_customs_declaration` | 42/47 | pass | 1 | 365.96 | 386.0 | 386.45 | 0.45 | 13.86 | DejaVuSans,DejaVuSerif |
| `363_warranty_card` | 40/42 | pass | 1 | 44.0 | 481.45 | 481.15 | -0.3 | 27.79 | DejaVuSans,DejaVuSerif |
| `317_rti_response` | 40/42 | pass | 1 | 56.69 | 538.61 | 538.83 | 0.22 | 23.94 | DejaVuSerif |
| `25_signature_block_underscores_txtpos` | 38/42 | pass | 1 | 313.38 | 330.0 | 330.13 | 0.13 | 16.62 | Arial,Times New Roman |
| `56_table_indented_from_margin` | 39/42 | pass | 1 | 396.62 | 420.0 | 420.13 | 0.13 | 14.88 | Arial,Times New Roman |
| `406_passport_mrz_page` | 40/42 | pass | 1 | 40.0 | 358.57 | 358.47 | -0.1 | 40.0 | DejaVuSans,DejaVuSansMono |

The full per-column table for all 61 documents (every column of every page, both sides) is in the run's
`lo61.json`; the summary is above. Under the shipped predicate exactly one document fails on more than one column on this render
(`360_restaurant_menu`, 2 columns); under the symmetric predicate `one-page-rotated-180-degrees` fails one
column over and one under.

## 3. Three documents measured against the PDF as the independent source

All three are `60`-only or `60`-deciding documents. "declared" is read out of the emitted
`word/document.xml`; "PDF" is the source's own text layer.

### `302_radiology_report` — 1 page, 2 columns, solo-60 in the store, PASSES in LibreOffice

| | left | source edge | LO render edge | delta | slack |
|---|---:|---:|---:|---:|---:|
| body column | 28.00 | **543.74** | 543.26 | **−0.48** | 32.68 |
| right-hand column | 250.00 | **328.73** | 328.72 | −0.01 | 22.48 |

Declared: `w:rFonts` DejaVuSans/DejaVuSerif, `w:sz` 17 among 13/14/15/16/22/24 (8.5 pt is the body size and
the source's own 8.5 — **no floor loss on the body lines**), `w:ind w:left="…" w:right="0"`, no `w:jc`,
`w:pgMar right="0"`, 0 `w:spacing`, 38 paragraphs.
**The file's geometry is exact when the face is present and the store still says FAIL**, and the 26 Nov
right-pin measurement of the same document in Google read `60 = (0, 1, False)`, i.e. **under**. The source
edge is 543.74 and the Google column is short by at least `8.0 + 32.68 = 40.68 pt` — **7.5 % of a 543 pt
line**. No declared size explains that; the face does: DejaVu Serif is 20.9 % wider than Liberation Serif and
12 % wider than Liberation Sans over 299 real line strings of this corpus (measured, §5). Google's actual
fallback for a face it does not have is not measurable from here, but any fallback on Arial/Times metrics
lands in that band, and the 24 Nov substitution experiment measured −57 to −122 pt on the deciding column of
these documents, which is the same order.

### `321_auditors_report` — 1 page, 1 column, solo-60, PASSES in LibreOffice

| | left | source edge | LO render edge | delta | slack |
|---|---:|---:|---:|---:|---:|
| body column | 56.69 | **538.61** | 539.21 | **+0.60** | 28.49 |

Declared: `w:sz` 19 among 19/22 (9.5 pt = the source's 9.5, no floor loss), DejaVuSerif, `w:right="0"`,
no `w:jc`, 34 paragraphs, 10 `w:spacing` runs (the source's own stretch, reproduced). Edge exact in a renderer that has DejaVu Serif; FAIL in Google.

### `purchase-order` — 1 page, 8 columns, fails in LibreOffice AND in Google

| left | source edge | LO render edge | delta | slack | verdict |
|---:|---:|---:|---:|---:|---|
| 42.52 | 329.76 | 321.27 | −8.49 | 7.02 | ok |
| 70.53 | 305.19 | 308.16 | +2.97 | 34.38 | ok |
| 135.56 | 253.05 | 253.52 | +0.47 | 20.62 | ok |
| 326.99 | 343.32 | 343.92 | +0.60 | 12.45 | ok |
| 377.17 | 394.68 | 395.28 | +0.60 | 11.68 | ok |
| **428.30** | **449.71** | **552.68** | **+102.98** | 17.51 | **OVER** |
| 463.55 | 552.75 | 549.10 | −3.66 | 7.78 | ok |
| 518.61 | 552.76 | 552.06 | −0.69 | 31.14 | ok |

Declared: Arial, `w:sz` 12/13/14/17/19/21/24 — 12 (6.0 pt) and 13 (6.5 pt) against source sizes 6.8-7.0, a
**−2.8 % to −4.4 % floor**; `w:right="0"`, no `w:jc`, 126 paragraphs, tables present. **Seven of the eight columns are within 3 pt of the
source.** The eighth is the instrument defect of §4: the Rate column really does end at 449.71 in the render
(measured line by line, every one of its 8 lines ends at 450.26), and the 552.68 is a *different* line
charged to it.

## 4. Where the defect lives — the construct, file:line

### (a) The engine never writes the edge, and loses the extent twice

| what | where | measured effect |
|---|---|---|
| a left-aligned line's right indent is left at zero | `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:4444` (`int rightTw = 0;`), emitted at `:4672`, and no `w:jc` is written for `align == 0` (`:4673-4675`) | 60 of 61 documents declare `w:ind w:right="0"` on every paragraph; 1 declares a non-zero right indent; 9 declare any `w:jc` |
| the page's right margin is zero, so the text area is the whole paper | `DocxWriter.java:2448` (`w:pgMar w:right="0"`) | a line has no right constraint at all; its extent is `x + Σ advance widths in the renderer's face` |
| the size is floored to a half-point | `DocxWriter.java:7335` (`halfPointsDown`), applied at `:3854`, `:4788`, `:7020`, `:7272` | **26 of 61** documents carry a floored body size; 6.4→6.0 is −6.4 % of the line's advance. Measured on `mutual-fund-statement`, the line "NAV is as on 30 September 2026. Returns are calculated on a point-to-point basis and are not indicative of future performance.": source LiberationSans-Italic **6.4 pt, 360.00 pt wide**; declared Arial **6.0 pt**, render **336.98 pt** → **−23.02 pt (−6.4 %)** |
| the face is declared as the source's own, whether or not the target renderer has it | `faceName()`, used at `:4764-4768` | 33 of 61 declare DejaVu; Google has none of them, and its fallback is 12-21 % narrower than the face the source used |

`stretchTw` (`DocxWriter.java:4717-4728`, called at `:4676` for `align == 0`) **already implements the exact
mechanism the fix needs** — it spreads the source's own stretch over the characters as `w:spacing`, capped at
0.30 em per character (`:4726`). The shortfall it is given today is only the source's inter-character
stretch; it does not include the size-floor residual or the declared-face metric gap.

### (b) The instrument convicts wrongly on a tenth of a point — `purchase-order`, proven line by line

`verify_google.py:2692`:

```python
if groups and b[0] - groups[-1][0][0] <= 10:
```

The bucket is measured **from the bucket's own minimum**, and it is built **independently on each side**.
On `purchase-order`:

| side | Rate column anchor | the "For Kastura Home Products Pvt. Ltd." line | distance | in the bucket? |
|---|---:|---:|---:|---|
| source PDF | 428.30 (7 lines, edge 449.71) | left **438.38**, right 552.76 | 10.08 | **no** — 0.08 pt outside |
| LO render | 428.90 (8 lines, edge 552.68) | left **438.50**, right 552.68 | 9.60 | **yes** — 0.40 pt inside |

The line moved **0.12 pt**. The Rate column's edge therefore reads 449.71 on the source side and 552.68 on
the render side, and the check charges **+102.98 pt OVER against an allowance of 23.46 pt**. Nothing about
the document's right edge changed. The same shape is latent on **10 of the 61 documents**: a source line
sitting 9-11 pt from a column anchor and overrunning the column edge by more than 14 pt —
`very-long-single-column-table` (99 such lines), `28_value_overflows_cell_txtpos` (14),
`14_stamp_chars_positioned_td` (11), `gst-invoice-3line-items` (3), `352_certificate_ornate_border` (2),
`marksheet-university-consolidated` (2), `delivery-challan`, `mutual-fund-statement`,
`one-page-rotated-180-degrees`, `purchase-order` (1 each).

**The corrected predicate.** Take the column anchors from the **source** page once, and assign **both** sides'
lines to the nearest anchor (`ASSIGN = 15 pt`): the same line then lands in the same column on both sides
even when its left edge jitters, and the column is a property of the page rather than of the renderer. On the
61 LibreOffice renders:

| predicate | documents failing | which |
|---|---:|---|
| as shipped | **15** | 28_value, 318, 323, 360, 38_faux_bold, 77_arabic, 79_inr, balance-sheet, boq, delivery-challan, gst-invoice-horiz, one-page-rotated, purchase-order, question-paper, text-held-twice |
| symmetric anchors | **9** | 318, 323, 360, 38_faux_bold, boq, **landscape-page (+38.36)**, **marksheet-univ (−46.90)**, one-page-rotated, text-held-twice |

**8 flip to PASS and 2 newly FIRE.** That is the `25_invisible_text` test passed: the corrected rule is not
a rule that can only pass — it convicts two documents the shipped rule lets through, and it still convicts
the seven genuine ones (`323` −191.42, `360` +141.58, `one-page-rotated` ±136, `38_faux_bold` +56.79,
`text-held-twice` +37.25, `318` +27.37, `boq` −20.74). The instruments that must be re-run with it: all 61,
and the (over, under) pair must go into `benchmarks/gverify/*.json` so the class is falsifiable.

### (c) Ruled out, with numbers

| hypothesis | measurement | verdict |
|---|---|---|
| a trailing space inflates the render's edge | the widest line ends in a space on **7 of 61** renders and **0 of 61** sources; the space's advance is **2.25-2.86 pt** against a 6.0 pt overrun tolerance | not the cause |
| a cell border is measured | the check reads `get_text("dict")["blocks"]` lines only; borders are drawings and never enter `page_lines()` | not the cause |
| the ink edge and the advance edge disagree | repo measurement, reproduced in shape: line-bbox right exceeds the rightmost dark pixel by 0.3-1.3 pt, six times inside the tolerance | not the cause |
| Google lays the column differently *for a face it has* | not measurable in this sandbox (§6) | open |

## 5. The proposed rule, and the measurement that backs it

**The rule, stated generally: a line's extent must be carried in the file, not left to the face the renderer
resolves. The engine already writes the line's left edge and its text, and it already knows the line's own
advance width (`b.right − b.x`, from the PDF's own font metrics). Write the size at its half-point and carry
the residual advance as `w:rPr/w:spacing` over the run — the mechanism `stretchTw` already implements — and
declare the metrically closest face the target renderer actually has. Nothing about a column's right edge
needs to be written: if the advance is right, the edge is right.**

Two arms, both measured on real corpus documents, both rendered by LibreOffice with only the declared face
available (which is the situation Google is in for a face it does not have):

**Arm 1 — the size floor (26 of 61 documents).** Correction `W_src·(s_src/s_half − 1)` spread over the run's
characters. No render, no face metrics: both numbers are already in the engine.

| document | worst column delta before | after | spacing added | text layer |
|---|---:|---:|---|---|
| `mutual-fund-statement` | **−22.91** | **−1.97** | median 0.05 pt/char, max 0.20 (max 3.3 % of em) | identical, 204/204 line strings |
| `academic-paper-ieee-2col-abstract` | **−18.54** | **−2.01** | median 0.20 pt/char, max 0.45 (max 6.4 % of em) | identical, 127/127 |
| `marksheet-university-consolidated` | **−5.59** | **−1.97** | median 0.15 pt/char, max 0.20 (max 2.9 % of em) | identical, 119/119 |

**Arm 2 — the absent face (33 of 61 documents).** Metric distance over 299 real line strings, measured with
the fonts themselves:

| source face | vs Liberation (what Arial/TNR resolve to) | vs Noto (in Google's library) |
|---|---:|---:|
| DejaVu Sans | 12.0 % narrower | **7.1 % narrower** (Noto Sans) |
| DejaVu Serif | **20.9 % narrower** | **7.6 % narrower** (Noto Serif) |

Declaring Noto Serif and carrying the 7.6 % residual as `w:spacing`:

| document | worst column delta, engine's own file | re-faced to Noto Serif + carried | pages | line count | text layer |
|---|---:|---:|---|---|---|
| `302_radiology_report` | −0.48 | **+1.42** | 1/1 | 33/33 | identical, 33/33 strings |
| `310_court_judgment` | +1.66 | **+1.05** | 1/1 | 28/28 | identical, 28/28 |
| `321_auditors_report` | +0.60 | **+1.19** | 1/1 | 34/34 | identical, 34/34 |

Spacing cost: median 0.30-0.53 pt/char, worst line 1.35 pt (12.3 % of em). No re-break: the line count and
the page count are unchanged on all three, and every line string survives verbatim — the correction widens
each line to the width the source itself drew, which the source itself fitted on the page, so nothing can
wrap that did not wrap in the source.

**A branch this run measured and refutes — do not ship it.** Re-facing the same documents to **Arial/Times
New Roman** instead (the obvious "name a face Google has" move) needs the full 17-38 % metric gap carried:
**1.0-2.2 pt per character** at 9.5 pt. It lands the edge (302: −0.48 → −0.21, 310: +1.66 → +0.17, 321:
+0.60 → +1.02) and it **destroys the text**: with that much letter-spacing PyMuPDF re-extracts the line as
`P a r t n e r`, `O p i n i o n`, `test in g a sampl e of 60 c on tr acts`, and **7 of 34 line strings on
`321_auditors_report` no longer match the source**. `60` would pass while `04_chars_missing`,
`45_char_accuracy` and the whole `.txt` side went wrong — the definition of a check gone blind. The
Noto arm is the same mechanism at a quarter of the spacing and keeps the text layer intact.

**What the class does NOT need:** `w:ind w:right` and `w:jc="distribute"`. That was built, measured and
reverted on 26 Nov (`FINDINGS/RIGHT-PIN-WRAPS-IN-GOOGLE-INERT-IN-LO-0126-relay.md`): Google moved the edge
by nothing and 28 lines wrapped. The edge is a consequence of the advance width; pinning the frame does not
produce it.

## 6. If this works, these documents become CLEAN

`classpick.py --leverage` prices this check at **24.0 CLEAN documents**, the second biggest prize after
`18_displacement` (52.2). Six documents fail **`60` and nothing else**, so they are the ones a `60`-only fix
can clean:

| document | store | LO today | which arm clears it |
|---|---|---|---|
| `302_radiology_report` | 41/42 | pass (−0.48) | arm 2 — DejaVuSerif, Google lacks it |
| `313_power_of_attorney` | 41/42 | pass (+1.22) | arm 2 — DejaVuSerif |
| `316_contract_with_schedules` | 46/47 | pass (−0.83) | arm 2 — DejaVuSans/Serif |
| `321_auditors_report` | 41/42 | pass (+0.60) | arm 2 — DejaVuSerif |
| `335_msds_safety_data_sheet` | 46/47 | pass (−1.24) | arm 2 — DejaVuSans/Serif |
| `79_inr_indian_digit_grouping_table` | 41/42 | **FAIL (−140.27)** | **arm 3 — the instrument fix**: it PASSES under the symmetric predicate |

**So: 6 documents become CLEAN — 5 from the face arm (measured exact in a renderer that has the face, so
Google is the only unknown) and 1 from the instrument fix (measured on the LibreOffice render).** The other
55 are held by at least one other check (16 by `18_displacement`, 3 by `18` + `59`, 2 by `47_margins`, 2 by
`59`, 1 by `04`+`13`+`45`, …), and the class's 24.0 of leverage is only realised when those land too.

## 7. What this run could NOT measure, and the exact next measurement

**The Google export was not obtainable in this sandbox, so no Google number in this file is new.** The store
holds pass/fail only, and the one path that turns a `.docx` into a Google Doc —
`GOOGLEDRIVE_CREATE_FILE(file_to_upload={s3key})` — needs an `s3key` from the platform `upload` tool, which
is not in this run's tool set; passing a `/scratch` path is refused with *"The file key does not belong to
this project or session"*. Every "Google" statement above is therefore either the store's verdict or a repo
measurement quoted as such. The LibreOffice renders are this run's own.

Three measurements decide whether the proposal ships, and each is one document on the Google loop:

1. **Does Google honour `w:rPr/w:spacing` on .docx import?** This is the single gate: both arms carry the
   advance in it. One document, two arms (with and without the spacing), the same 302 whose Google column is
   already known to be under. If Google drops it, arm 1 and arm 2 are worth nothing in Google and the
   residual belongs to `53_embedded_faces` — and the 24 Nov note *"only `w:spacing` stripped (what Google
   does to the stretch)"* is an assumption about Google, not a measurement of it.
2. **Does Google's font list contain Noto Sans and Noto Serif?** (It should — they are Google's own — but the
   arm 2 claim is worth exactly that.) If it does, arm 2 is the first construct that reproduces a DejaVu
   document's column edge in a renderer without DejaVu, which is what the 24 Nov file called "a wall".
3. **Re-measure all 61 with the symmetric predicate and store `(over, under)` per column.** The store's
   pass/fail-only shape is why two runs reported opposite signs for the same document a day apart.

## 8. How every number here was made (reproducible)

    git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
    bash tools/p2w-bench/corpus-fetch.sh                       # 213 PDFs
    bash tools/p2w-bench/build-engine.sh                       # javac + PDFBox, 36 s
    java -cp out:libs/... ConvertOne <corpus>/<name>.pdf <out> # the .docx this engine emits
    soffice --headless --convert-to pdf --outdir lo out/*.docx # the render with the declared face present
    python3 check60.py <source.pdf> <render.pdf>               # the shipped predicate, per column

The predicate in `check60.py` is `verify_google.py`'s `page_lines`/`columns`/`edge` copied verbatim, with the
constants `BAND=0.06, RIGHT_OVERRUN=6.0, RIGHT_UNDERRUN=8.0, COL_MIN_LINES=3, COL_MIN_SHARE=0.05,
SLACK_CAP=40.0`. `corrected.py` is the symmetric-anchor version. `respace2.py` applies arm 1, `reface.py`
applies arm 2, both to a **copy** of the emitted .docx in `/scratch/work`; nothing in the clone was written.
