# RANKING-TXT.csv is not a stale duplicate of RANKING.csv - it is a different table, and the "50 apart" claim is unverified

**24 Nov 2026, fixer slot 14:17.** Answers pending item 6 / agent `18_dB-03`.

## What the two files are

| file | rows | cols | what it scores |
|:--|--:|--:|:--|
| `benchmarks/RANKING.csv` | 212 | 21 | geometry: share1/2/3/5/10, median_pt, p90_pt, max_pt, text_recall, colour/tone/order/font share |
| `tools/p2w-bench/RANKING-TXT.csv` | 213 | 6 | the 12 .txt checks: applicable, passed, failed, abstained, failed_ids |

**They share no score, verdict or pass column.** A score comparison between them is not
computable, so "50 documents apart" cannot be read off these two files at all.

- Overlap on `document`: 212. Only in RANKING.csv: 0. Only in RANKING-TXT.csv: 1 (`416_many_tiny_pages`).
- `RANKING-TXT.csv` is internally consistent: 213 unique ids, `applicable + abstained = 12` on every
  row, `passed + failed = applicable` on every row, `failed_ids` token count = `failed` on every row.
- `RANKING.csv` is not fully consistent: 3 rows carry `signature=clean` with a non-`none` problem
  (ranks 69, 110, 135), 70 rows have a null `colour_share`, and it omits one corpus document.

## What this means for the report

The report should cite `RANKING.csv` for docx numbers and `RANKING-TXT.csv` for .txt numbers.
Neither is a copy of the other. The duplicate claim compares against `txt/RANKING-TXT.csv`, which
was not supplied to this analysis - so it is **unverified**, not refuted.
