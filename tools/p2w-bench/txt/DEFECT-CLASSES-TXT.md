# .txt defect classes

Documents measured: **213 of 213** - 167 clean, 46 failing at least one check.

Grouped from `tools/p2w-bench/txt/RANKING-TXT.csv` only. A document's class is the check
that fails it; a document failing several is counted under each and its own row names all
of them. Ranked by how many documents each check holds, because one fix that clears a check
serves every document under it.

## Classes

| check | what it means | documents | share |
|---|---|---:|---:|
| `t13_amount_columns` | amount columns stay right-aligned | 18 | 8% |
| `t12_word_invention` | the .txt carries no word the source never drew | 12 | 6% |
| `t01_word_accuracy` | the source's words survive, 99 % of them | 10 | 5% |
| `t08_line_order` | lines arrive in the order the page drew them | 10 | 5% |
| `t02_position` | a line's x survives as its leading spaces | 5 | 2% |
| `t09_page_furniture` | one copy of each running head per page it belongs to | 4 | 2% |
| `t07_symbol_counts` | each symbol arrives as many times as the page drew it | 3 | 1% |
| `t03_symbols` | every character the page DRAWS survives, read from the glyphs | 2 | 1% |
| `t06_encoding` | the bytes decode as the UTF-8 the writer declares | 2 | 1% |

## Documents

| document | class | failed | failing checks | vs baseline |
|---|---|---:|---|---|
| `01_stamp_rotated_15deg_upright` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `041122-Account_Opening_Form` | `7 checks` | 7/10 | `t01_word_accuracy`, `t03_symbols`, `t06_encoding`, `t07_symbol_counts`, `t08_line_order`, `t09_page_furniture`, `t12_word_invention` | was 7 |
| `05_round_company_seal_curved_text` | `t12_word_invention` | 1/9 | `t12_word_invention` | was 1 |
| `09_stamp_font_not_embedded` | `t08_line_order` | 1/9 | `t08_line_order` | was 1 |
| `10_stamp_as_image` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `12_stamp_across_page_break` | `t12_word_invention` | 1/10 | `t12_word_invention` | was 1 |
| `22_invoice_four_columns_txtpos` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `29_dot_leaders_txtpos` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `305_vaccination_certificate` | `t08_line_order` | 1/7 | `t08_line_order` | was 1 |
| `311_fir_police_form` | `t12_word_invention` | 1/7 | `t12_word_invention` | was 1 |
| `324_loan_amortisation_schedule` | `t09_page_furniture` | 1/10 | `t09_page_furniture` | was 1 |
| `330_cad_drawing_sheet` | `t08_line_order` | 1/7 | `t08_line_order` | was 1 |
| `332_bom_on_drawing` | `t02_position` | 1/8 | `t02_position` | was 1 |
| `334_patent_document` | `t02_position` | 1/7 | `t02_position` | was 1 |
| `362_price_list_dense` | `t13_amount_columns` | 1/8 | `t13_amount_columns` | was 1 |
| `38_faux_bold_italic_synthesised` | `t01_word_accuracy + t07_symbol_counts` | 2/9 | `t01_word_accuracy`, `t07_symbol_counts` | was 2 |
| `391_survey_questionnaire_grid` | `t01_word_accuracy + t12_word_invention` | 2/7 | `t01_word_accuracy`, `t12_word_invention` | was 2 |
| `392_statistical_console_output` | `t12_word_invention` | 1/7 | `t12_word_invention` | was 1 |
| `39_small_caps_letter_spacing` | `t01_word_accuracy + t12_word_invention` | 2/9 | `t01_word_accuracy`, `t12_word_invention` | was 2 |
| `400_comic_page_speech_bubbles` | `t08_line_order` | 1/7 | `t08_line_order` | was 1 |
| `406_passport_mrz_page` | `t01_word_accuracy + t12_word_invention` | 2/7 | `t01_word_accuracy`, `t12_word_invention` | was 2 |
| `411_nested_xobject_transforms` | `t01_word_accuracy` | 1/4 | `t01_word_accuracy` | was 1 |
| `46_chart_coloured_labels_body_text` | `t08_line_order` | 1/9 | `t08_line_order` | was 1 |
| `600_reviewed_invoice_with_annotations` | `t12_word_invention` | 1/8 | `t12_word_invention` | was 1 |
| `601_fillable_admission_form` | `t01_word_accuracy` | 1/7 | `t01_word_accuracy` | was 1 |
| `65_two_col_full_width_figure_caption` | `t08_line_order` | 1/9 | `t08_line_order` | was 1 |
| `70_magazine_drop_cap_photo_caption` | `t08_line_order` | 1/9 | `t08_line_order` | was 1 |
| `72_bank_statement_no_rules_right_amounts` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `74_balance_sheet_indented_subitems` | `t02_position + t13_amount_columns` | 2/10 | `t02_position`, `t13_amount_columns` | was 2 |
| `77_arabic_rtl_document` | `t01_word_accuracy + t12_word_invention` | 2/9 | `t01_word_accuracy`, `t12_word_invention` | was 2 |
| `79_inr_indian_digit_grouping_table` | `t01_word_accuracy` | 1/10 | `t01_word_accuracy` | was 1 |
| `Account_Opening_Form_Fillable_filled` | `7 checks` | 7/10 | `t01_word_accuracy`, `t03_symbols`, `t06_encoding`, `t07_symbol_counts`, `t08_line_order`, `t09_page_furniture`, `t12_word_invention` | was 7 |
| `balance-sheet-and-profit-loss` | `t13_amount_columns` | 1/11 | `t13_amount_columns` | was 1 |
| `balance-sheet-two-columns-of-figures` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `bank-statement-horizontal-rules-only` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `electricity-bill` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `form16-part-b` | `t13_amount_columns` | 1/11 | `t13_amount_columns` | was 1 |
| `gst-invoice-3line-items` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `gst-invoice-horizontal-rules-only` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `gst-invoice-multipage-item-table` | `t09_page_furniture + t13_amount_columns` | 2/12 | `t09_page_furniture`, `t13_amount_columns` | was 2 |
| `itr-computation-with-slab-table` | `t08_line_order + t13_amount_columns` | 2/10 | `t08_line_order`, `t13_amount_columns` | was 2 |
| `journal-2col-with-footnotes` | `t12_word_invention` | 1/9 | `t12_word_invention` | was 1 |
| `one-page-rotated-180-degrees` | `t02_position` | 1/10 | `t02_position` | was 1 |
| `payslip-label-left-amount-right` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
| `price-list-2col-dense-right-aligned` | `t02_position` | 1/10 | `t02_position` | was 1 |
| `purchase-order` | `t13_amount_columns` | 1/10 | `t13_amount_columns` | was 1 |
