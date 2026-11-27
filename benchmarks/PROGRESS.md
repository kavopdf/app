# Progress - one row per day

Written by `tools/p2w-bench/progress.py`, which the watchdog runs. Each row is the committed state of
the corpus on that date; nothing here is typed by hand.

`docx open` is the number of documents whose share@5px is above 1.0 in RANKING.csv. `txt failing` is
the number whose .txt fails a check. `google` is how many documents have been measured through Google's
own renderer, and `google clean` how many of those pass all 42 checks.

A row that does not move is the signal: it means a day of the pipeline produced no change, and the
watchdog's job is to find out why.

| date | docx open | txt failing | google | google clean | note |
|---|---:|---:|---:|---:|---|
| 2026-11-19 | 65 | 47 | 84 | 7 |  |
| 2026-11-20 | 60 | 46 | 192 | 7 |  |
| 2026-11-21 | 59 | 23 | 192 | 6 | amended: was docx 59, txt 27, google 192/6 |
| 2026-11-22 | 59 | 16 | 192 | 23 |  |
| 2026-11-23 | 59 | 14 | 190 | 30 | amended: was docx 59, txt 16, google 190/28 |
| 2026-11-24 | 59 | 14 | 190 | 35 | amended: was docx 59, txt 14, google 190/29 |
| 2026-11-25 | 59 | 9 | 213 | 42 | amended: was docx 59, txt 11, google 213/42 |
| 2026-11-26 | 60 | 8 | 205 | 47 | amended: was docx 59, txt 8, google 208/42 |
| 2026-11-27 | 59 | 8 | 212 | 42 | amended: was docx 59, txt 8, google 205/42 |
