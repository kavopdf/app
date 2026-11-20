# .txt defect classes

Documents measured: **213 of 213** - 167 clean, 46 failing at least one check.

Grouped from `tools/p2w-bench/txt/RANKING-TXT.csv` only. A document's class is the check
that fails it; a document failing several is counted under each and its own row names all
of them. Ranked by how many documents each check holds, because one fix that clears a check
serves every document under it.

Regenerated 20 Nov: it said 64 failing while the ranking said 46, so a fixer reading it was
aiming at a corpus that no longer existed.

## Classes

| check | what it means | documents | share |
|---|---|---:|---:|
| `t13_amount_columns` | amount columns stay right-aligned | **18** | 8% |
| `t12_word_invention` | no word appears that the PDF did not have | **12** | 6% |
| `t01_word_accuracy` | every word is the word the PDF had | **10** | 5% |
| `t08_line_order` | rows appear in the PDF order | **10** | 5% |
| `t02_position` | text sits where the PDF put it | **5** | 2% |
| `t09_page_furniture` |  | **4** | 2% |
| `t07_symbol_counts` |  | **3** | 1% |
| `t03_symbols` |  | **2** | 1% |
| `t06_encoding` |  | **2** | 1% |
