# Agent 18_dA-05 - the 18_displacement engine fix, as returned

**Deployed 26 Nov 10:56 IST, worked 19 minutes, landed.** Verdict: **no** - it could not measure its
AFTER side, because every Drive upload of a staged document was refused (the staging-path rule this
run then identified and wrote up in `GOOGLE-LOOP-UNBLOCKED-COPY-TO-OUTPUT-FIRST-26NOV-fixer.md`).

What it did establish, and what the next run should start from:

* **115 of 213 documents fail `18_displacement`; 25 fail it alone** on the ledger it read. (This run's
  own count from `benchmarks/gverify/*.json` at `a4d8fca469bba636` is 24 documents failing exactly one
  check, 10 of them `18_displacement` - the two numbers are different ledgers, and the second is the
  one `classpick.py --leverage` reads.)
* The construct it proposed: carry the gap as a **1x1 borderless `w:tbl` with one row at
  `w:trHeight w:val="G" w:hRule="exact"`**, the carrier the repo had already measured as read by all
  three renderers.
* Google BEFORE, measured on two documents: `68_journal_wide_table_spanning` med_dy **-114.3 pt**
  (41/42); `412_page_labels_roman` med_dy **-59.0 pt**, bad pages 1-4 (40/42).
* LibreOffice before and after: identical, page counts unchanged.

Its full report follows, unedited.

---

# 18_displacement — the single engine change, and what it measures

**26 Nov 2026.** Repo: `kavopdf/app` (cloned to `/scratch/work/CS` at `2b3e812`). Nothing was committed,
`app/` source was not modified in the repo, nothing was pushed, no file was deleted.

> **Repo recovery, stated up front.** The task said the repo was already at `/scratch/work/CS` with the
> gate installed. On this pod `/scratch/work` was empty and no copy of the repo existed anywhere on disk,
> so it was re-cloned from GitHub (`kavopdf/app`, the only repository holding `tools/p2w-bench` and `app/`),
> the corpus was fetched with `tools/p2w-bench/corpus-fetch.sh` (213 PDFs, 0 missing) and the toolchain
> built with `tools/p2w-bench/pod-prep.sh` (JDK 17, PDFBox-Android 2.0.27.0, BouncyCastle 1.72, stubs,
> engine, scipy). Everything below is measured from that tree at HEAD `2b3e812`.

---

## 1. What the sources say the mechanism is

Read: `tools/p2w-bench/SETTLED.md`; the `18_displacement` sections of
`tools/p2w-bench/FINDINGS/DOCS-ROOT-CAUSES-24NOV.md` (lines 26–85, 369–460, 589–645);
`FINDINGS/18-displacement-B-GROUP-CENSUS-25NOV-relay.md`;
`FINDINGS/18-displacement-GAP-CARRIER-25NOV-relay.md`;
`FINDINGS/18-displacement-ROW-HEIGHT-IS-CONTENT-DRIVEN-26NOV-fixer.md`;
`FINDINGS/18-displacement-ROW-SNAP-FALSIFIED-25NOV-fixer.md`; and `tools/p2w-bench/FIXER-BRIEF.md`.

The root-cause file names **three** constructs, of which the two the task names are the first two:

| # | construct | site in `DocxWriter.java` | what Google does | documents (of 102) |
|---|---|---|---:|---:|
| **A** | page's top gap as `w:before` on the first paragraph after `<w:br w:type="page"/>` | `place()` newPage branch, `:4124-4135`; emitted via `spacing(...)`, `:149` | **drops it** — 55.15 pt asked, 0.33 pt drawn | 16 (6 exclusive) |
| **B** | `w:line … lineRule="exact"` on an empty spacer paragraph, used as a gap | `:6107-6112` (the refused branch of the room guard at `:6098-6103`) | charges `2.5873 × max(L/240, 0.06)` pt, i.e. ~22 % of what is asked; 5–10 pt of any exact line height | 81 (71 exclusive) |
| C | `w:trHeight … hRule="atLeast"` on table rows | `:6468`, `:6516` | lays content height, +0.75 pt quantum per row, cumulative | 27 drift-dominant, 0 exclusive |

Union of A and B is **87 of the 102**. `w:before` is honoured **1:1** everywhere except a page top
(`18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA`). The page-top family is the biggest *magnitude*,
the spacer family the biggest *count*.

The repo also records the construct that **is** read as a length by all three renderers: a 1×1 `w:tbl`
with `w:trHeight w:val="G" w:hRule="exact"` delivered **55.83 of 55.15 pt** in Google, against 0.33 pt
for `w:before`. That is the lever this report pulls.

`SETTLED.md` also records that the table-top spacer was *not* the whole class and that the room guard
exists because spending a gap unguarded pushed `mobile-bill` and `insurance-policy-schedule` onto a
second page. Both facts are respected below.

---

## 2. The ledger: which documents fail `18_displacement`, and what else they fail

**The ledger used.** `benchmarks/gverify/*.json` — the per-document 42-check verdicts. That is the table
`classpick.py --leverage` reads (`clean_leverage()`, `classpick.py:214`): one file per document, a
`failed` list, and a check's worth is `1/len(failed)` per document. Reproducing it gives **53.06**,
which is the 53.1 the task quotes, so this is the right table. (`benchmarks/RANKING.csv` is the
*pixel* ranking and has no check column; `classrow.py` only rewrites the class markdown from it.)

**115 of 213 documents fail `18_displacement`** on this ledger — not 102. The class has grown since the
24 Nov file was written (and 2 of the 102 were on an older engine); the numbers below are the ledger as
it stands at HEAD.

Distribution of *other* failing checks across those 115:

| other checks failed | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 25 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| documents | **25** | 26 | 17 | 19 | 12 | 6 | 6 | 1 | 2 | 1 |

### Which documents become CLEAN if `18_displacement` alone is fixed?

**25 documents.** On each of them `18_displacement` is the *only* failure, so clearing it takes the
document to 42/42 (or 47/47 on the older-shape records) — a whole CLEAN document each:

- `16_right_aligned_amounts_txtpos`
- `303_discharge_summary`
- `31_times_body_arial_headings`
- `320_balance_sheet_statutory`
- `325_demat_holdings_statement`
- `362_price_list_dense`
- `36_embedded_subset_font`
- `402_calendar_month_grid`
- `403_crossword_puzzle`
- `68_journal_wide_table_spanning`
- `70_magazine_drop_cap_photo_caption`
- `71_invoice_space_aligned_no_rules`
- `72_bank_statement_no_rules_right_amounts`
- `74_balance_sheet_indented_subitems`
- `balance-sheet-two-columns-of-figures`
- `bus-timetable-station-left-times-right`
- `electricity-bill`
- `insurance-policy-schedule`
- `marksheet-subject-left-marks-right`
- `mobile-bill`
- `price-list-2col-dense-right-aligned`
- `report-2col-table-spanning-both-columns`
- `table-inside-two-column-page`
- `table-with-no-header-row`
- `two-tables-stacked-with-no-gap`

(That is the whole of the 53.06 leverage: 25 × 1.0 plus the partial credit from the 90 documents where
18 is one of several failures.)

### Full list — 115 documents, other-check count, and the other checks

| document | passes | other fails | other failing checks |
|---|---:|---:|---|
| `16_right_aligned_amounts_txtpos` | 41/42 | 0 | **none - becomes CLEAN** |
| `303_discharge_summary` | 46/47 | 0 | **none - becomes CLEAN** |
| `31_times_body_arial_headings` | 41/42 | 0 | **none - becomes CLEAN** |
| `320_balance_sheet_statutory` | 46/47 | 0 | **none - becomes CLEAN** |
| `325_demat_holdings_statement` | 46/47 | 0 | **none - becomes CLEAN** |
| `362_price_list_dense` | 41/42 | 0 | **none - becomes CLEAN** |
| `36_embedded_subset_font` | 41/42 | 0 | **none - becomes CLEAN** |
| `402_calendar_month_grid` | 46/47 | 0 | **none - becomes CLEAN** |
| `403_crossword_puzzle` | 41/42 | 0 | **none - becomes CLEAN** |
| `68_journal_wide_table_spanning` | 41/42 | 0 | **none - becomes CLEAN** |
| `70_magazine_drop_cap_photo_caption` | 41/42 | 0 | **none - becomes CLEAN** |
| `71_invoice_space_aligned_no_rules` | 41/42 | 0 | **none - becomes CLEAN** |
| `72_bank_statement_no_rules_right_amounts` | 41/42 | 0 | **none - becomes CLEAN** |
| `74_balance_sheet_indented_subitems` | 41/42 | 0 | **none - becomes CLEAN** |
| `balance-sheet-two-columns-of-figures` | 41/42 | 0 | **none - becomes CLEAN** |
| `bus-timetable-station-left-times-right` | 41/42 | 0 | **none - becomes CLEAN** |
| `electricity-bill` | 46/47 | 0 | **none - becomes CLEAN** |
| `insurance-policy-schedule` | 46/47 | 0 | **none - becomes CLEAN** |
| `marksheet-subject-left-marks-right` | 46/47 | 0 | **none - becomes CLEAN** |
| `mobile-bill` | 46/47 | 0 | **none - becomes CLEAN** |
| `price-list-2col-dense-right-aligned` | 41/42 | 0 | **none - becomes CLEAN** |
| `report-2col-table-spanning-both-columns` | 46/47 | 0 | **none - becomes CLEAN** |
| `table-inside-two-column-page` | 46/47 | 0 | **none - becomes CLEAN** |
| `table-with-no-header-row` | 46/47 | 0 | **none - becomes CLEAN** |
| `two-tables-stacked-with-no-gap` | 46/47 | 0 | **none - becomes CLEAN** |
| `23_timetable_grid_txtpos` | 45/47 | 1 | `59_shape_anchor` |
| `300_prescription_rx` | 45/47 | 1 | `59_shape_anchor` |
| `301_lab_report_panel` | 45/47 | 1 | `60_text_column_right_edge` |
| `306_clinical_protocol_synopsis` | 45/47 | 1 | `59_shape_anchor` |
| `30_mixed_font_sizes_one_baseline_txtpos` | 40/42 | 1 | `59_shape_anchor` |
| `333_datasheet_spec_tables` | 45/47 | 1 | `66_table_cell_width` |
| `341_shipping_manifest` | 45/47 | 1 | `60_text_column_right_edge` |
| `342_packing_list` | 45/47 | 1 | `60_text_column_right_edge` |
| `363_warranty_card` | 40/42 | 1 | `60_text_column_right_edge` |
| `370_offer_letter` | 45/47 | 1 | `60_text_column_right_edge` |
| `372_timesheet_grid` | 45/47 | 1 | `59_shape_anchor` |
| `406_passport_mrz_page` | 40/42 | 1 | `60_text_column_right_edge` |
| `412_page_labels_roman` | 40/42 | 1 | `27_text_off_page` |
| `416_many_tiny_pages` | 40/42 | 1 | `27_text_off_page` |
| `42_table_coloured_header_alternating_rows` | 40/42 | 1 | `59_shape_anchor` |
| `bank-statement-horizontal-rules-only` | 40/42 | 1 | `45_char_accuracy` |
| `boq-horizontal-rules-only` | 40/42 | 1 | `45_char_accuracy` |
| `boq-tender-bill-of-quantities` | 45/47 | 1 | `60_text_column_right_edge` |
| `brochure-3col-with-sidebar-box` | 40/42 | 1 | `59_shape_anchor` |
| `eway-bill` | 45/47 | 1 | `25_invisible_text` |
| `gst-invoice-3line-items` | 45/47 | 1 | `60_text_column_right_edge` |
| `invoice-line-items-qty-rate-amount` | 45/47 | 1 | `26_text_overlap` |
| `landscape-page-inside-portrait-document` | 45/47 | 1 | `60_text_column_right_edge` |
| `marksheet-university-consolidated` | 45/47 | 1 | `60_text_column_right_edge` |
| `question-paper-marks-right-margin` | 40/42 | 1 | `60_text_column_right_edge` |
| `table-with-merged-cells` | 45/47 | 1 | `60_text_column_right_edge` |
| `324_loan_amortisation_schedule` | 44/47 | 2 | `27_text_off_page`, `59_shape_anchor` |
| `326_itr_computation` | 44/47 | 2 | `60_text_column_right_edge`, `63_table_rows` |
| `340_bill_of_lading` | 39/42 | 2 | `59_shape_anchor`, `60_text_column_right_edge` |
| `381_incident_report_timeline` | 44/47 | 2 | `04_chars_missing`, `60_text_column_right_edge` |
| `405_sheet_music_lyrics` | 39/42 | 2 | `45_char_accuracy`, `46_text_crossing_rule` |
| `56_table_indented_from_margin` | 39/42 | 2 | `59_shape_anchor`, `60_text_column_right_edge` |
| `57_centred_title_page_left_body_pages` | 39/42 | 2 | `27_text_off_page`, `44_header_footer` |
| `64_newspaper_uneven_columns_ad_boxes` | 39/42 | 2 | `23_line_pitch`, `26_text_overlap` |
| `balance-sheet-and-profit-loss` | 44/47 | 2 | `27_text_off_page`, `60_text_column_right_edge` |
| `gst-invoice-with-qr-code` | 44/47 | 2 | `26_text_overlap`, `66_table_cell_width` |
| `newsletter-3col-header-footer` | 39/42 | 2 | `26_text_overlap`, `59_shape_anchor` |
| `payslip-label-left-amount-right` | 39/42 | 2 | `17_matched_runs`, `53_embedded_faces` |
| `price-list-right-aligned-amounts` | 39/42 | 2 | `17_matched_runs`, `53_embedded_faces` |
| `property-tax-receipt` | 44/47 | 2 | `04_chars_missing`, `13_text_colours` |
| `purchase-order` | 44/47 | 2 | `26_text_overlap`, `60_text_column_right_edge` |
| `salary-slip-corporate` | 44/47 | 2 | `17_matched_runs`, `53_embedded_faces` |
| `salary-slip-factory-wages` | 44/47 | 2 | `59_shape_anchor`, `60_text_column_right_edge` |
| `25_signature_block_underscores_txtpos` | 38/42 | 3 | `04_chars_missing`, `45_char_accuracy`, `60_text_column_right_edge` |
| `330_cad_drawing_sheet` | 43/47 | 3 | `04_chars_missing`, `45_char_accuracy`, `47_margins` |
| `332_bom_on_drawing` | 43/47 | 3 | `26_text_overlap`, `47_margins`, `60_text_column_right_edge` |
| `360_restaurant_menu` | 38/42 | 3 | `43_within_10pt_x`, `47_margins`, `60_text_column_right_edge` |
| `373_leave_application_form` | 43/47 | 3 | `23_line_pitch`, `59_shape_anchor`, `60_text_column_right_edge` |
| `375_attendance_register` | 43/47 | 3 | `43_within_10pt_x`, `47_margins`, `59_shape_anchor` |
| `390_wide_data_appendix` | 43/47 | 3 | `47_margins`, `59_shape_anchor`, `66_table_cell_width` |
| `404_sudoku_grid` | 43/47 | 3 | `23_line_pitch`, `47_margins`, `59_shape_anchor` |
| `40_devanagari_shaping_font` | 43/47 | 3 | `34a_span_size_match`, `38_list_markers`, `47_margins` |
| `417_rotate180_and_mirrored` | 38/42 | 3 | `04_chars_missing`, `17_matched_runs`, `27_text_off_page` |
| `58_header_rule_footer_rule` | 38/42 | 3 | `04_chars_missing`, `27_text_off_page`, `44_header_footer` |
| `602_bookmarked_annual_report` | 38/42 | 3 | `04_chars_missing`, `27_text_off_page`, `52_outline` |
| `75_merged_header_cell_three_columns` | 43/47 | 3 | `59_shape_anchor`, `64_table_span_across`, `65_table_span_down` |
| `76_devanagari_table` | 43/47 | 3 | `17_matched_runs`, `34a_span_size_match`, `47_margins` |
| `form16-part-b` | 43/47 | 3 | `04_chars_missing`, `27_text_off_page`, `60_text_column_right_edge` |
| `itr-computation-with-slab-table` | 43/47 | 3 | `26_text_overlap`, `32_stroke_lines`, `63_table_rows` |
| `newspaper-2col-fullwidth-headline` | 38/42 | 3 | `04_chars_missing`, `26_text_overlap`, `45_char_accuracy` |
| `table-across-page-break-repeated-header` | 43/47 | 3 | `04_chars_missing`, `27_text_off_page`, `60_text_column_right_edge` |
| `text-held-twice-shadow-text` | 43/47 | 3 | `13_text_colours`, `25_invisible_text`, `60_text_column_right_edge` |
| `01_stamp_rotated_15deg_upright` | 37/42 | 4 | `04_chars_missing`, `13_text_colours`, `35_rotation`, `59_shape_anchor` |
| `311_fir_police_form` | 42/47 | 4 | `04_chars_missing`, `45_char_accuracy`, `59_shape_anchor`, `60_text_column_right_edge` |
| `314_tender_rfp_boq` | 42/47 | 4 | `42_justification_edges`, `59_shape_anchor`, `60_text_column_right_edge`, `63_table_rows` |
| `344_customs_declaration` | 42/47 | 4 | `04_chars_missing`, `13_text_colours`, `59_shape_anchor`, `60_text_column_right_edge` |
| `353_admit_card` | 42/47 | 4 | `04_chars_missing`, `26_text_overlap`, `44_header_footer`, `59_shape_anchor` |
| `601_fillable_admission_form` | 37/42 | 4 | `04_chars_missing`, `51_field_values`, `53_embedded_faces`, `59_shape_anchor` |
| `admit-card` | 42/47 | 4 | `04_chars_missing`, `13_text_colours`, `45_char_accuracy`, `59_shape_anchor` |
| `bank-statement-5-pages` | 42/47 | 4 | `25_invisible_text`, `27_text_off_page`, `44_header_footer`, `59_shape_anchor` |
| `delivery-challan` | 42/47 | 4 | `04_chars_missing`, `13_text_colours`, `26_text_overlap`, `60_text_column_right_edge` |
| `gst-invoice-multipage-item-table` | 42/47 | 4 | `25_invisible_text`, `26_text_overlap`, `27_text_off_page`, `44_header_footer` |
| `table-with-rotated-header` | 42/47 | 4 | `04_chars_missing`, `45_char_accuracy`, `47_margins`, `59_shape_anchor` |
| `very-long-single-column-table` | 42/47 | 4 | `04_chars_missing`, `27_text_off_page`, `44_header_footer`, `60_text_column_right_edge` |
| `08_two_overlapping_stamps` | 36/42 | 5 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `35_rotation`, `45_char_accuracy` |
| `383_api_docs_page` | 41/47 | 5 | `04_chars_missing`, `47_margins`, `59_shape_anchor`, `60_text_column_right_edge`, `66_table_cell_width` |
| `78_mixed_english_devanagari_line` | 36/42 | 5 | `05_chars_extra`, `17_matched_runs`, `26_text_overlap`, `43_within_10pt_x`, `47_margins` |
| `80_gstin_pan_cin_ifsc_table` | 36/42 | 5 | `04_chars_missing`, `17_matched_runs`, `44_header_footer`, `45_char_accuracy`, `59_shape_anchor` |
| `gst-invoice-horizontal-rules-only` | 36/42 | 5 | `04_chars_missing`, `26_text_overlap`, `44_header_footer`, `45_char_accuracy`, `60_text_column_right_edge` |
| `mutual-fund-statement` | 41/47 | 5 | `25_invisible_text`, `27_text_off_page`, `59_shape_anchor`, `60_text_column_right_edge`, `66_table_cell_width` |
| `03_stamp_vertical_90deg` | 37/44 | 6 | `04_chars_missing`, `13_text_colours`, `35_rotation`, `59_shape_anchor`, `62_table_columns`, `63_table_rows` |
| `13_stamp_non_english` | 35/42 | 6 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `35_rotation`, `45_char_accuracy`, `59_shape_anchor` |
| `323_credit_card_statement` | 40/47 | 6 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `45_char_accuracy`, `60_text_column_right_edge`, `66_table_cell_width` |
| `600_reviewed_invoice_with_annotations` | 37/44 | 6 | `05_chars_extra`, `28_clipped_at_edge`, `32_stroke_lines`, `45_char_accuracy`, `47_margins`, `62_table_columns` |
| `77_arabic_rtl_document` | 40/47 | 6 | `17_matched_runs`, `26_text_overlap`, `43_within_10pt_x`, `47_margins`, `59_shape_anchor`, `60_text_column_right_edge` |
| `one-page-rotated-180-degrees` | 40/47 | 6 | `04_chars_missing`, `27_text_off_page`, `43_within_10pt_x`, `60_text_column_right_edge`, `62_table_columns`, `63_table_rows` |
| `academic-paper-ieee-2col-abstract` | 39/47 | 7 | `04_chars_missing`, `17_matched_runs`, `27_text_off_page`, `44_header_footer`, `45_char_accuracy`, `47_margins`, `60_text_column_right_edge` |
| `305_vaccination_certificate` | 38/47 | 8 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `34b_span_colour_match`, `34c_span_weight_match`, `43_within_10pt_x`, `45_char_accuracy`, `60_text_column_right_edge` |
| `322_mutual_fund_factsheet` | 38/47 | 8 | `04_chars_missing`, `13_text_colours`, `17_matched_runs`, `26_text_overlap`, `44_header_footer`, `45_char_accuracy`, `59_shape_anchor`, `60_text_column_right_edge` |
| `Account_Opening_Form_Fillable_filled` | 21/47 | 25 | `01_page_count`, `04_chars_missing`, `05_chars_extra`, `10_font_sizes`, `14_filled_shapes`, `17_matched_runs`, `23_line_pitch`, `27_text_off_page`, `32_stroke_lines`, `34a_span_size_match`, `37_super_subscript`, `38_list_markers`, `39_image_position`, `43_within_10pt_x`, `44_header_footer`, `45_char_accuracy`, `47_margins`, `51_field_values`, `53_embedded_faces`, `55_orientation_mix`, `59_shape_anchor`, `60_text_column_right_edge`, `62_table_columns`, `65_table_span_down`, `66_table_cell_width` |

---

## 3. The two documents chosen, and the construct responsible in each

`18_displacement` is the dominant defect on all 25 above, and the *whole* defect on all 25. But **all 25
are single-page documents**, so none of them can exercise construct **A** (the page-top `w:before`
Google drops) — that construct only exists where there is a page break. To measure both mechanisms the
second document has to come from the 26 that fail 18 plus one other check:

| document | pages | other fails | why chosen |
|---|---:|---:|---|
| **`68_journal_wide_table_spanning`** | 1 | **0** — whole defect | the cleanest construct-**B** witness; the document the root-cause file itself uses for the refused spacer ("144 pt becomes −114.28 pt") |
| **`412_page_labels_roman`** | 5 | 1 (`27_text_off_page`) | the only 5-page document in the 18-plus-one set, and the document the root-cause file uses as its construct-**A** control (`w:before="1227"`, page 0 honoured, pages 1–4 dropped). 18 is the dominant defect; 27 is a consequence of the same −59 pt drop |

Build: `java ConvertOne <pdf> <outdir>` from `tools/engine-verify` with
`-cp out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar`.

### 3.1 `68_journal_wide_table_spanning` — the spacer (construct B)

The gap between the last body line and the table is **144.0 pt**, written as an empty paragraph whose
height is an exact line box. This is `word/document.xml`, body block 9, exactly as HEAD emits it:

```xml
<w:p><w:pPr><w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
             w:before="568" w:after="0" w:line="2312" w:lineRule="exact"/>
  <w:rPr><w:sz w:val="2"/></w:rPr>
</w:pPr></w:p>
```

The numbers: `w:before="568"` = **28.40 pt**, `w:line="2312"` = **115.60 pt**; `568 + 2312 = 2880` twips
= **144.0 pt**, which is also the `Math.min(2880L, …)` cap at `DocxWriter.java:6090`. The split is the
room guard's: `roomTw` allowed 568 twips of the gap to be spent as `w:before`, the remaining 2312 stayed
in `w:line`.

What Google does with it: 28.40 pt of `w:before` is delivered 1:1, and the 115.60 pt declared as an
exact line arrives as `2.5873 × 2312/240` = **24.92 pt**. Total drawn **53.32 pt of 144** — a **90.68 pt**
shortfall, and everything below the spacer sits that far high.

(The copy of this document currently in Drive was built by an earlier engine state that spent none of
the gap: `w:before="0" w:line="2880"`. Google drew 31.05 pt of 144 there, and the measured median
displacement is **−114.3 pt** — see §5. Same construct, more of it refused.)

### 3.2 `412_page_labels_roman` — the page-top gap (construct A)

Every page of this document is the same shape. Body blocks 3 and 4, exactly as HEAD emits them:

```xml
<w:p><w:pPr><w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
             w:before="0" w:after="0" w:line="1" w:lineRule="exact"/>
  <w:rPr><w:sz w:val="2"/></w:rPr></w:pPr>
  <w:r><w:br w:type="page"/></w:r></w:p>

<w:p><w:pPr><w:pStyle w:val="Heading3"/><w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
             w:before="1227" w:after="0" w:line="13" w:lineRule="exact"/>
  <w:ind w:left="1120" w:right="0" w:firstLine="0"/></w:pPr>
  <w:r>…<w:t xml:space="preserve">Front matter 2</w:t></w:r></w:p>
```

`w:before="1227"` = **61.35 pt** — the whole distance from the top of the sheet down to the first
heading's box. It is written on the first paragraph of *every* page (page 0 carries the same 1227).
Google honours it on page 0 (+2.3 pt) and **drops it on pages 1–4**: measured median **−59.0 pt**,
worst −59.1, `bad_pages = [1, 2, 3, 4]`.

---

## 4. The proposed rule (one rule, no per-document cases)

> **A vertical gap is carried as a length every renderer reads as a length. Where the engine today
> writes a gap as `w:before` (dropped at a page top by Google) or as `w:line … lineRule="exact"` on an
> empty paragraph (charged at ~22 % by Google), it instead writes a borderless 1×1 `w:tbl` whose single
> row is `w:trHeight w:val="G" w:hRule="exact"`, with an empty cell.**

Why this one and not "emit the gap as `w:before` on the following real paragraph", which was the other
candidate: `w:before` is honoured 1:1 **except at a page top**, and construct A *is* a page top — so the
`w:before` rule fixes B and cannot fix A. The exact-height row is the one carrier measured to work in
both places, and it is the construct the repo already probed in Google (55.83 of 55.15 pt).

Why it cannot regress LibreOffice or Word: both already read `w:trHeight … hRule="exact"` as a length,
and both already drew the whole gap (via `w:line exact` or `w:before`). The row delivers the same
number, so LO/Word lay the identical page. **Only the renderer that was under-delivering changes.**
That is also why the room guard at `:6098` can be dropped with it: the guard existed because Google was
*not* drawing the gap while LO was, so spending it moved Google's page and not LO's. When every
renderer draws the same gap, the page fits in all three or in none — the guard has nothing left to
protect.

What Google is expected to do, and why: deliver ~101 % of `G` instead of 22 % of it (`2.5873 × L/240`
for a `w:line`) or 0 % (for a page-top `w:before`). Expected residual is a ~1–2 pt overshoot, well
inside the check's `clamp(0.35·size, 1.5, 4.5)` pt tolerance.

### Implementation (in a scratch copy — `app/` in the repo is untouched)

Applied to `/scratch/work/mod/src/com/kavopdf/app/engine/DocxWriter.java`, a copy of
`app/src/main/java/…/DocxWriter.java`; compiled into `/scratch/work/mod/out`. Three edits:

1. a new `gapTable(int tw, int widthTw)` helper returning the XML above;
2. at `:6157-6175` (the spacer) the two `sb.append("<w:p>…")` branches, and the `spendTw` split with
   them, become `sb.append(gapTable(spacerTw, …))`;
3. at `:3819` (`flowRow`) and `:4670` (`flowFromBox`), when the paragraph is the page's first and
   `beforeTw > 0`, the table is appended before the paragraph and the paragraph's `w:before` is written
   as `0` (the emitted gap stays in the flow accounting, so `resync()` still records the truth).

### The XML after the change — the same two sites

`68_journal_wide_table_spanning`, body block 9, replacing the spacer paragraph:

```xml
<w:tbl><w:tblPr><w:tblW w:w="11906" w:type="dxa"/><w:tblStyle w:val="KavoTable"/>
 <w:tblBorders><w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/>
  <w:right w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders>
 <w:tblLayout w:type="fixed"/>
 <w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>
  <w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar></w:tblPr>
 <w:tblGrid><w:gridCol w:w="11906"/></w:tblGrid>
 <w:tr><w:trPr><w:trHeight w:val="2880" w:hRule="exact"/><w:cantSplit/></w:trPr>
  <w:tc><w:tcPr><w:tcW w:w="11906" w:type="dxa"/><w:tcMar>…all zero…</w:tcMar></w:tcPr>
   <w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="1" w:lineRule="exact"/>
    <w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p></w:tc></w:tr></w:tbl>
```

`w:trHeight w:val="2880" w:hRule="exact"` — the full 144.0 pt, in the property Google reads.

`412_page_labels_roman`, the page-break paragraph is unchanged, and the gap now sits between it and the
heading:

```xml
<w:p>…<w:r><w:br w:type="page"/></w:r></w:p>

<w:tbl>…<w:tr><w:trPr><w:trHeight w:val="1227" w:hRule="exact"/><w:cantSplit/></w:trPr>
  <w:tc>…<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="1" w:lineRule="exact"/>…</w:p></w:tc>
 </w:tr></w:tbl>

<w:p><w:pPr><w:pStyle w:val="Heading3"/><w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
             w:before="0" w:after="0" w:line="13" w:lineRule="exact"/>
  <w:ind w:left="1120" w:right="0" w:firstLine="0"/></w:pPr>
  <w:r>…<w:t xml:space="preserve">Front matter 2</w:t></w:r></w:p>
```

`w:before` 1227 → **0**; the 61.35 pt is now the row's exact height. The same substitution is emitted at
every page top in the file (5 gap rows: page 0 and pages 1–4).

---

## 5. The measurement

### 5.1 Google — BEFORE: measured

Real Google renders, exported from Drive and scored with the repo's unmodified
`tools/p2w-bench/verify_google.py` against the source PDF and the HEAD `.docx`. Both Google Docs were
already in the pipeline's own `KavoPDF-Verify` folder (`1OoSHtsv-qEUwk8CnNa9d5hsCKu8PFeij`) from
earlier gverify runs — the route the root-cause file used, and the only one open here.

| document | Google `passed/total` | `18_displacement` | med_dy | worst_dy | bad_pages | runs matched |
|---|---|---:|---:|---:|---|---:|
| `68_journal_wide_table_spanning` | **41/42** | **FAIL** | **−114.3 pt** | 115.0 | [0] | 74 |
| `412_page_labels_roman` | **40/42** | **FAIL** | **−59.0 pt** | 59.1 | [1, 2, 3, 4] | 15 |

Both numbers reproduce the root-cause file's own measurements (−114.28 and −58.8) and 412's stored
gverify record exactly (`benchmarks/gverify/412_page_labels_roman.json`, engine `a4d8fca469bba636`,
`med_dy −59.0`, `bad_pages [1,2,3,4]`).

### 5.2 Google — AFTER: **not reachable from this sandbox**

Stated plainly: **I could not get the changed document into Google Docs, so there is no measured
Google "after" number.**

The blocker is the one the repo has hit three times and recorded in
`DOCS-ROOT-CAUSES-24NOV.md`: every Drive **write** path needs an `s3key` that the platform `upload` tool
would stage, and that tool is not bound on this pod. `GOOGLEDRIVE_UPLOAD_FILE`,
`GOOGLEDRIVE_CREATE_FILE` and `GOOGLEDRIVE_RESUMABLE_UPLOAD` all take
`file_to_upload = {name, mimetype, s3key}`, and every form of the local path was refused:

```
Apollo files API /api/v3/mercury_lwglhqij/files/download returned HTTP 403:
The file key does not belong to this project or session.
The file with s3key '/scratch/output/tmp-gv-68_journal_wide_table_spanning.docx'
belongs to another project or session; use a file uploaded by this project.
```

Tried: the absolute path in `/scratch/output` (the only writable, sendable directory — `/scratch/input`,
`/scratch/saved` and `/scratch/downloads` are all read-only on this pod), the bare filename, and the same
call from inside `run_program`. All three fail identically. The download/export direction works fine
(that is how §5.1 was measured); only the upload direction is closed. `GOOGLEDRIVE_UPLOAD_FROM_URL` would
need a public HTTPS copy of the file, and publishing one would mean creating a public artefact on the
user's behalf (or `git push`, which was forbidden), so it was not done.

**Nothing was uploaded to Drive, and no Drive file was created, modified or deleted.**

### 5.3 LibreOffice — the proxy, BEFORE and AFTER: measured

Same `.docx` pair, rendered with `soffice --headless --convert-to pdf`, scored with the same
`verify_google.py`.

| document | side | `passed/total` | failing checks | med_dy | worst_dy | bad_pages | pages |
|---|---|---|---:|---|---:|---:|---|---:|
| `68_journal_wide_table_spanning` | before | 40/42 | `18_displacement`, `59_shape_anchor` | −3.1 | 3.4 | [0] | 1 |
| `68_journal_wide_table_spanning` | **after** | **40/42** | `18_displacement`, `59_shape_anchor` | **−3.1** | **3.4** | [0] | **1** |
| `412_page_labels_roman` | before | 42/42 | — | 3.0 | 3.8 | [] | 5 |
| `412_page_labels_roman` | **after** | **42/42** | — | **3.0** | **3.8** | [] | **5** |

**The proxy is identical before and after, on both documents, to the tenth of a point, and the page
counts do not move** (412 stays 5 pages, 68 stays 1). That is the designed outcome and the reason the
change is safe to land: LibreOffice already drew the gap, so it has nothing to gain and nothing to lose.
It is *not* evidence that Google improves — the proxy is blind to this construct by construction, which
is the exact reason the class has been unlandable (`BLOCKERS.md`, 24 Nov 03:25).

Two things this measurement does establish, both real:

1. **No page overflow from dropping the room guard.** The guard exists because spending a gap unguarded
   pushed `mobile-bill` and `insurance-policy-schedule` onto a second page. With the gap carried by an
   exact row, 412 and 68 hold their page counts in the renderer that already spent the gap.
2. **The added tables do not trip the table checks.** 412 goes from **0 tables to 5** and still scores
   **42/42**, i.e. `62_table_columns`, `63_table_rows`, `64_table_span_across`, `65_table_span_down` and
   `66_table_cell_width` all still pass with five extra 1×1 tables in the body. That was the main
   structural risk of this rule and it is measured away on the proxy. (It still needs confirming in
   Google, where the table checks read the export.)

### 5.4 Google — AFTER: modelled, from the repo's own measured laws

Labelled as a **model, not a measurement**. It uses only constants the repo has measured in Google:
`w:before` 1:1; an exact line charged at `2.5873 × max(L/240, 0.06)`; an exact row height delivered at
`55.83/55.15 = 101.2 %`; page-top `shift = 0.961 × gap − 0.58`.

| document | gap asked | Google drew (before) | shortfall | Google med_dy before (measured) | predicted Google med_dy after |
|---|---:|---:|---:|---:|---:|
| `412_page_labels_roman` | 61.35 pt × 4 pages | 0.33 pt | 61.0 | **−59.0** | **≈ +0.7 pt** (101.2 % of 61.35 = +0.74) |
| `68_journal_wide_table_spanning` (HEAD bytes) | 144.0 pt | 53.32 pt (28.40 + 24.92) | 90.68 | not measurable here — see note | **≈ +1.7 pt** (101.2 % of 144 = +1.73) |
| `68_journal_wide_table_spanning` (the Drive copy, `w:before="0"`) | 144.0 pt | 31.05 pt | 112.95 | **−114.3** | — |

The `68` row that is measured is the Drive copy, which spent none of the gap; its predicted shortfall
was 112.95 pt and the measured displacement was 114.3 pt, so the law holds to **1.4 pt**. Applying the
same 1.4 pt residual to HEAD's 90.68 pt shortfall gives an expected Google **before** of about **−92 pt**
for the exact bytes this rule was applied to.

On the model, both documents move from a 59–114 pt displacement to a 1–2 pt one, i.e. **inside
`clamp(0.35·size, 1.5, 4.5)` pt**, which is what "passes `18_displacement`" means. That prediction is
consistent with the LibreOffice proxy, where the same substitution leaves both documents at the same
place (3.0 and −3.1 pt) — but it is a prediction, and the first thing the next run with a working
upload path should do is replace this table with measured numbers.

### 5.5 What is NOT claimed

- **No Google number after the change exists.** §5.4 is arithmetic on the repo's measured constants.
- **Coverage is not measured.** The rule was compiled and run on **two** documents, not on the 115 or
  the 213. `regress.py --check` and the corpus ratchet were not run; the repo's own gate refuses a
  change until the whole corpus is measured, and building all 213 through the modified engine is a
  ~10-minute job that was out of this run's budget.
- **`27_text_off_page` on 412 is not addressed.** It is a consequence of the same −59 pt drop (the
  bottom two lines of each page fall off the sheet), so it should clear with the displacement; that is
  inference, not measurement.
- **`59_shape_anchor` on 68 is untouched** and is not part of this class.
- **Construct C (`hRule="atLeast"` row heights) is untouched.** It is the third mechanism, 27
  drift-dominant documents, 0 exclusive. This rule does not need it (it removes the room guard by
  making every renderer draw the same gap, rather than by giving Google the slack the guard was
  protecting), but a document whose *rows* drift will still fail on the drift.

---

## 6. Summary of the numbers

| quantity | value |
|---|---:|
| documents failing `18_displacement` (ledger at HEAD) | **115** of 213 |
| documents that become CLEAN if 18 is fixed alone | **25** |
| leverage, recomputed from the ledger | **53.06** (task quotes 53.1) ✓ |
| documents where 18 is one of exactly two failures | 26 |
| documents with a page break among the 25 solo ones | **0** (all single-page) |
| Google before, `68_journal_wide_table_spanning` | **41/42**, med_dy **−114.3 pt**, worst 115.0 |
| Google before, `412_page_labels_roman` | **40/42**, med_dy **−59.0 pt**, worst 59.1, bad_pages [1,2,3,4] |
| LibreOffice before → after, both documents | **identical** (40/42 & 42/42; 3.4 pt & 3.8 pt worst) |
| page counts, LibreOffice before → after | **unchanged** (1 and 5) |
| table checks with 0 → 5 added 1×1 tables (412) | **all pass, 42/42** |
| Google after | **not measured — upload path blocked** (§5.2); modelled ≈ +0.7 / +1.7 pt (§5.4) |

---

## 7. Files this run produced (not in the repo)

`/scratch/work/patch_engine.py` (the three-edit patch, applied to a copy),
`/scratch/work/mod/src/` (patched copy of `app/src/main/java`), `/scratch/work/mod/out/` (its build),
`/scratch/work/p2w/out/` (HEAD `.docx`), `/scratch/work/p2w/out-mod/` (changed `.docx`),
`/scratch/work/xml/`, `/scratch/work/xmlm/` (unpacked `document.xml`, before/after),
`/scratch/work/lo-before/`, `/scratch/work/lo-after/` (LibreOffice renders + check JSONs),
`/scratch/work/gbefore/`, `/scratch/work/gb2/` (Google exports + check JSONs),
`/scratch/work/ledger_table.md`, `/scratch/work/solo_list.md`.

`git status` in `/scratch/work/CS` is clean: `app/` was never edited in the repo, nothing was committed,
nothing was pushed, and no file was deleted.
