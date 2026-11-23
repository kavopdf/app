# Leverage of a single Google check: which failure, fixed alone, cleans the most documents?

**Data:** `benchmarks/gverify/*.json` in `kavopdf/app` (clone at HEAD, depth 1). Every number below is computed from those committed JSON files only — no builds, no Google Drive calls, no engine changes.

## What the data actually contains

- **213** gverify JSON files on disk, one per document, **213 unique document names** (no duplicates).
- **190** carry a check list (a `failed` array plus `total`/`passed`) and are analysed below.
- **23** carry **no check list** and are **excluded**, not guessed: every one of them has `status: "page_count_refused"` and only `name`, `pages`, `want` (two also carry `engine`). They never reached the 42-check stage, so their failing sets are unknown. All 190 analysed files have `status: "ok"` and `passed + len(failed) == total` holds in all 190 (0 inconsistencies).

**The suite is not uniformly 42 checks.** The `total` field takes three values:

| checks per document (`total`) | documents |
|---|---|
| 42 | 126 |
| 44 | 2 |
| 47 | 62 |

The check-id universe differs by suite: the 42-check set has 26 distinct check ids, the 44-check set adds `28_clipped_at_edge`, `62_table_columns`, `63_table_rows`, the 47-check set adds those plus `34a_span_size_match`, `64_table_span_across`, `65_table_span_down`, `66_table_cell_width`. So "all 42 checks passing" is exactly right for 126 of the 190 documents; for the other 64 "CLEAN" means "all checks in that document's own suite passing" (`failed == []`). The sole-failure metric below is unaffected by this, because it only counts documents with exactly one entry in `failed`.

## Headline numbers

- Documents **already CLEAN** (zero failing checks): **30** of 190 (15.8%).
- Documents failing **exactly one check**: **26** of 190 (13.7%). These are the only documents a single fix can clean.
- Documents failing **two or more** checks: **134**.
- Distinct check ids that fail in at least one document: **33**.

## Answer

**`18_displacement`** (the text-displacement check) **is the answer.** It is the sole failing check in **13 documents**, more than three times the next check, and it also has the largest raw footprint (**101 of 190 documents**, 53.2%). Fixing it alone moves 13 documents from failing to CLEAN — roughly 43% more clean documents than the 30 that are clean today.

## Top 10 checks ranked by documents where it is the SOLE failure (then by total failures)

| # | check id | docs where SOLE failure (fixing it alone → CLEAN) | total docs failing it | sole ÷ total |
|---|---|---|---|---|
| 1 | `18_displacement` | **13** | 101 | 12.9% |
| 2 | `60_text_column_right_edge` | **4** | 56 | 7.1% |
| 3 | `25_invisible_text` | **3** | 48 | 6.2% |
| 4 | `32_stroke_lines` | **2** | 47 | 4.3% |
| 5 | `59_shape_anchor` | **2** | 45 | 4.4% |
| 6 | `17_matched_runs` | **1** | 30 | 3.3% |
| 7 | `47_margins` | **1** | 25 | 4.0% |
| 8 | `04_chars_missing` | **0** | 65 | 0.0% |
| 9 | `05_chars_extra` | **0** | 43 | 0.0% |
| 10 | `45_char_accuracy` | **0** | 37 | 0.0% |

## Full table — all 33 failing checks

| check id | docs failing it | docs where SOLE failure | share of its failures that are the last blocker |
|---|---|---|---|
| `18_displacement` | 101 | 13 | 12.9% |
| `60_text_column_right_edge` | 56 | 4 | 7.1% |
| `25_invisible_text` | 48 | 3 | 6.2% |
| `32_stroke_lines` | 47 | 2 | 4.3% |
| `59_shape_anchor` | 45 | 2 | 4.4% |
| `17_matched_runs` | 30 | 1 | 3.3% |
| `47_margins` | 25 | 1 | 4.0% |
| `04_chars_missing` | 65 | 0 | 0.0% |
| `05_chars_extra` | 43 | 0 | 0.0% |
| `45_char_accuracy` | 37 | 0 | 0.0% |
| `13_text_colours` | 32 | 0 | 0.0% |
| `44_header_footer` | 31 | 0 | 0.0% |
| `27_text_off_page` | 17 | 0 | 0.0% |
| `26_text_overlap` | 16 | 0 | 0.0% |
| `35_rotation` | 12 | 0 | 0.0% |
| `43_within_10pt_x` | 12 | 0 | 0.0% |
| `10_font_sizes` | 6 | 0 | 0.0% |
| `53_embedded_faces` | 4 | 0 | 0.0% |
| `66_table_cell_width` | 4 | 0 | 0.0% |
| `23_line_pitch` | 3 | 0 | 0.0% |
| `62_table_columns` | 3 | 0 | 0.0% |
| `63_table_rows` | 3 | 0 | 0.0% |
| `34a_span_size_match` | 2 | 0 | 0.0% |
| `38_list_markers` | 2 | 0 | 0.0% |
| `28_clipped_at_edge` | 1 | 0 | 0.0% |
| `31_pages_lost_their_text` | 1 | 0 | 0.0% |
| `37_super_subscript` | 1 | 0 | 0.0% |
| `40_link_targets` | 1 | 0 | 0.0% |
| `46_text_crossing_rule` | 1 | 0 | 0.0% |
| `51_field_values` | 1 | 0 | 0.0% |
| `52_outline` | 1 | 0 | 0.0% |
| `64_table_span_across` | 1 | 0 | 0.0% |
| `65_table_span_down` | 1 | 0 | 0.0% |

## Documents where a check is the sole failure (exact names)

Only seven checks ever appear as a last blocker, in 26 documents total:

**`18_displacement`** — 13 document(s):

- `16_right_aligned_amounts_txtpos` (suite of 42 checks)
- `31_times_body_arial_headings` (suite of 42 checks)
- `362_price_list_dense` (suite of 42 checks)
- `36_embedded_subset_font` (suite of 42 checks)
- `68_journal_wide_table_spanning` (suite of 42 checks)
- `71_invoice_space_aligned_no_rules` (suite of 42 checks)
- `72_bank_statement_no_rules_right_amounts` (suite of 42 checks)
- `balance-sheet-two-columns-of-figures` (suite of 42 checks)
- `bus-timetable-station-left-times-right` (suite of 42 checks)
- `insurance-policy-schedule` (suite of 47 checks)
- `mobile-bill` (suite of 47 checks)
- `table-with-no-header-row` (suite of 47 checks)
- `two-tables-stacked-with-no-gap` (suite of 47 checks)

**`60_text_column_right_edge`** — 4 document(s):

- `302_radiology_report` (suite of 42 checks)
- `313_power_of_attorney` (suite of 42 checks)
- `316_contract_with_schedules` (suite of 47 checks)
- `321_auditors_report` (suite of 42 checks)

**`25_invisible_text`** — 3 document(s):

- `10_stamp_as_image` (suite of 42 checks)
- `50_invoice_coloured_total_row` (suite of 42 checks)
- `63_three_column_brochure` (suite of 42 checks)

**`32_stroke_lines`** — 2 document(s):

- `407_id_card_front_back` (suite of 42 checks)
- `49_coloured_background_block_paragraph` (suite of 42 checks)

**`59_shape_anchor`** — 2 document(s):

- `48_form_coloured_border_coloured_values` (suite of 42 checks)
- `52_one_cm_margin_wide_body` (suite of 42 checks)

**`17_matched_runs`** — 1 document(s):

- `391_survey_questionnaire_grid` (suite of 42 checks)

**`47_margins`** — 1 document(s):

- `392_statistical_console_output` (suite of 42 checks)

## Cross-check: any check sole-failing in 3 or more documents?

Yes — three of them, and only three:

| check id | count | documents |
|---|---|---|
| `18_displacement` | 13 | `16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings`, `362_price_list_dense`, `36_embedded_subset_font`, `68_journal_wide_table_spanning`, `71_invoice_space_aligned_no_rules`, `72_bank_statement_no_rules_right_amounts`, `balance-sheet-two-columns-of-figures`, `bus-timetable-station-left-times-right`, `insurance-policy-schedule`, `mobile-bill`, `table-with-no-header-row`, `two-tables-stacked-with-no-gap` |
| `60_text_column_right_edge` | 4 | `302_radiology_report`, `313_power_of_attorney`, `316_contract_with_schedules`, `321_auditors_report` |
| `25_invisible_text` | 3 | `10_stamp_as_image`, `50_invoice_coloured_total_row`, `63_three_column_brochure` |

Everything else tops out at 2 (`32_stroke_lines`, `59_shape_anchor`), 1 (`17_matched_runs`, `47_margins`) or 0. Note that `04_chars_missing` (65 failures), `05_chars_extra` (43) and `45_char_accuracy` (37) are the second, third and fourth most common failures overall yet are **never** a last blocker — they are always accompanied by at least one other failure, so fixing them cleans nothing on its own.

## Conclusion

`18_displacement` is the single highest-leverage failing Google check in this dataset. It fails in 101 of the 190 measurable documents and is the **only** failing check in 13 of them — `16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings`, `362_price_list_dense`, `36_embedded_subset_font`, `68_journal_wide_table_spanning`, `71_invoice_space_aligned_no_rules`, `72_bank_statement_no_rules_right_amounts`, `balance-sheet-two-columns-of-figures`, `bus-timetable-station-left-times-right`, `insurance-policy-schedule`, `mobile-bill`, `table-with-no-header-row` and `two-tables-stacked-with-no-gap` — so a single fix to text displacement would take the clean-document count from 30 to 43 (+43%) without touching any other check. The pattern in the names is unambiguous: the last-blocker set is dominated by **column- and space-aligned tabular layouts** — right-aligned money columns, price lists, timetables, schedules, borderless tables — which is the class of document most sensitive to horizontal position drift, and it explains why the next check down, `60_text_column_right_edge` (4 sole), is also about the right edge of a text column. The next-best single fix delivers under a third as much: `60_text_column_right_edge` cleans 4, `25_invisible_text` 3, `32_stroke_lines` and `59_shape_anchor` 2 each. Two caveats bound this result. First, the leverage is narrow, not broad: 88 of the 101 documents failing `18_displacement` fail something else too, so the remaining 134 multi-failure documents need at least two fixes each regardless of ordering. Second, 23 of the 213 committed JSONs carry no check list at all (`page_count_refused`) and are excluded here; if any of those would have been single-`18_displacement` failures the count above is a floor, but their failing sets are not recorded and were not guessed.
