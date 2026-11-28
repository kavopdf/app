# .txt defect classes

Documents measured: **214 of 214** - 208 clean, 6 failing at least one check.

Grouped from `tools/p2w-bench/txt/RANKING-TXT.csv` only. A document's class is the check
that fails it; a document failing several is counted under each and its own row names all
of them. Ranked by how many documents each check holds, because one fix that clears a check
serves every document under it.

## Classes

| check | what it means | documents | status | share |
|---|---|---:|---|---:|
| `t12_word_invention` | the .txt carries no character the source never drew | 4 | OPEN | 2% |
| `t01_word_accuracy` | the source's words survive, 99 % of them | 2 | OPEN | 1% |
| `t06_encoding` | the bytes decode as the UTF-8 the writer declares | 2 | OPEN | 1% |
| `t09_page_furniture` | one copy of each running head per page it belongs to | 2 | OPEN | 1% |
| `t03_symbols` | every character the page DRAWS survives, read from the glyphs | 1 | OPEN | 0% |
| `t07_symbol_counts` | each symbol arrives as many times as the page drew it | 1 | OPEN | 0% |
| `t08_line_order` | lines arrive in the order the page drew them | 1 | OPEN | 0% |

## Documents

| document | class | failed | failing checks | vs baseline |
|---|---|---:|---|---|
| `041122-Account_Opening_Form` | `3 checks` | 3/10 | `t06_encoding`, `t09_page_furniture`, `t12_word_invention` | was 3 |
| `305_vaccination_certificate` | `t08_line_order` | 1/7 | `t08_line_order` | was 1 |
| `600_reviewed_invoice_with_annotations` | `t12_word_invention` | 1/8 | `t12_word_invention` | was 1 |
| `601_fillable_admission_form` | `t01_word_accuracy` | 1/7 | `t01_word_accuracy` | was 1 |
| `Account_Opening_Form_Fillable_filled` | `3 checks` | 3/10 | `t06_encoding`, `t09_page_furniture`, `t12_word_invention` | was 3 |
| `Prakashan_Print_Fidelity_Handbook` | `4 checks` | 4/11 | `t01_word_accuracy`, `t03_symbols`, `t07_symbol_counts`, `t12_word_invention` | was 4 |
