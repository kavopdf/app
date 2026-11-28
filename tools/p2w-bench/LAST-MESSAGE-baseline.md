# P2W Baseline - Run Report

**28 Nov 2026 · 06:50 IST**

> 98 of 214 documents are at or under 1% share@5px in LibreOffice. The corpus is -24.3% closer to the 15 Nov baseline than it started.

This run started from an empty pod: it downloaded the corpus, converted every document with the current engine, measured the whole set, and refreshed the .txt table against the same build. The census and the ranking were published from that measurement, and the ratchet compared it against the committed baseline before anything was committed.

## Corpus

| | |
|:--|--:|
| Documents | **214** |
| .docx at or under 1% share@5px (LibreOffice) | **98** |
| .docx still open | **116** |
| .txt clean | **208** |
| .txt failing | **6** |
| Google measured | **206** of 214 |
| Google clean | **48** |

## Against the 15 Nov baseline

| | baseline | now | |
|:--|--:|--:|:--|
| mean share@5 | 6.15 | **7.64** | +24.29% |
| documents improved at all (any fall) | | **47** | |
| regressions | | **84** | LOOK |

Regressions are a defect, not a result:

* `360_restaurant_menu` 34.43 -> 50.18
* `table-with-no-header-row` 0.61 -> 47.48
* `boq-tender-bill-of-quantities` 7.10 -> 41.95
* `very-long-single-column-table` 6.87 -> 41.14
* `electricity-bill` 16.24 -> 36.78
* `balance-sheet-and-profit-loss` 6.20 -> 36.69
* `salary-slip-factory-wages` 18.09 -> 35.15
* `03_stamp_vertical_90deg` 16.98 -> 34.38
* `table-across-page-break-repeated-header` 9.41 -> 33.52
* `mobile-bill` 18.48 -> 30.09

