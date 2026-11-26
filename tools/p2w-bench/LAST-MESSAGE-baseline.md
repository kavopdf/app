# P2W Baseline - Run Report

**26 Nov 2026 · 13:54 IST**

> 154 of 213 documents are at or under 1% share@5px in LibreOffice. The corpus is 40.6% closer to the 15 Nov baseline than it started.

This run was not a measure phase, so it published no new table: it rebuilt the corpus from the release zips, converted every PDF, and re-scored every `.txt` with the current verifier. Nothing moved between clean and failing, so the `.txt` half was already current and there was nothing to commit. One document re-measured deterministically at a worse position score than its published row, with engine sources byte-identical to the published commit; this run did not establish the cause, so it left the published table alone rather than overwrite it with a regression it cannot explain. The conversion loop and the LibreOffice renders write no beacon.

## Corpus

| | |
|:--|--:|
| Documents | **213** |
| .docx at or under 1% share@5px (LibreOffice) | **154** |
| .docx still open | **59** |
| .txt clean | **205** |
| .txt failing | **8** |
| Google measured | **207** of 213 |
| Google clean | **42** |

## Against the 15 Nov baseline

| | baseline | now | |
|:--|--:|--:|:--|
| mean share@5 | 6.15 | **3.65** | -40.60% |
| documents improved at all (any fall) | | **65** | |
| regressions | | **0** | none |

