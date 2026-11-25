# .txt defect classes

Documents measured: **213 of 213** - 202 clean, 11 failing at least one check.

Grouped from `tools/p2w-bench/txt/RANKING-TXT.csv` only. A document's class is the check
that fails it; a document failing several is counted under each and its own row names all
of them. Ranked by how many documents each check holds, because one fix that clears a check
serves every document under it.

## Classes

| check | what it means | documents | status | share |
|---|---|---:|---|---:|
| `t02_position` | a line's x survives as its leading spaces | 4 | OPEN | 2% |
| `t01_word_accuracy` | the source's words survive, 99 % of them | 3 | OPEN | 1% |
| `t12_word_invention` | the .txt carries no character the source never drew | 3 | OPEN | 1% |
| `t06_encoding` | the bytes decode as the UTF-8 the writer declares | 2 | OPEN | 1% |
| `t08_line_order` | lines arrive in the order the page drew them | 2 | OPEN | 1% |
| `t09_page_furniture` | one copy of each running head per page it belongs to | 2 | OPEN | 1% |

## Documents

| document | class | failed | failing checks | vs baseline |
|---|---|---:|---|---|
| `041122-Account_Opening_Form` | `3 checks` | 3/10 | `t06_encoding`, `t09_page_furniture`, `t12_word_invention` | was 3 |
| `305_vaccination_certificate` | `t08_line_order` | 1/7 | `t08_line_order` | was 1 |
| `332_bom_on_drawing` | `t02_position` | 1/8 | `t02_position` | was 1 |
| `334_patent_document` | `t02_position` | 1/7 | `t02_position` | was 1 |
| `39_small_caps_letter_spacing` | `t01_word_accuracy + t08_line_order` | 2/9 | `t01_word_accuracy`, `t08_line_order` | was 2 |
| `600_reviewed_invoice_with_annotations` | `t12_word_invention` | 1/8 | `t12_word_invention` | was 1 |
| `601_fillable_admission_form` | `t01_word_accuracy` | 1/7 | `t01_word_accuracy` | was 1 |
| `74_balance_sheet_indented_subitems` | `t02_position` | 1/10 | `t02_position` | was 1 |
| `77_arabic_rtl_document` | `t01_word_accuracy` | 1/9 | `t01_word_accuracy` | was 1 |
| `Account_Opening_Form_Fillable_filled` | `3 checks` | 3/10 | `t06_encoding`, `t09_page_furniture`, `t12_word_invention` | was 3 |
| `price-list-2col-dense-right-aligned` | `t02_position` | 1/10 | `t02_position` | was 1 |
