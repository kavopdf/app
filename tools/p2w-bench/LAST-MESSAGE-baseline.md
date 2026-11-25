# P2W Baseline - Run Report

**25 Nov 2026 · 17:06 IST**

> 154 of 213 documents are at or under 1% share@5px in LibreOffice. The corpus is 40.0% closer to the 15 Nov baseline than it started.

This run was not the measure phase, so nothing here is a fresh publication: the fixer holds the round. What it did do was build the corpus from the release zips, convert every PDF, and measure the whole corpus with the current engine, then re-score the whole .txt half with the current verifier. Both halves reproduce the committed tables document for document - no .docx moved and no .txt row moved - which is exactly the check this run exists to make. The conversion loop and the soffice renders write no beacon, so this paragraph is the only record that they ran.

## Corpus

| | |
|:--|--:|
| Documents | **213** |
| .docx at or under 1% share@5px (LibreOffice) | **154** |
| .docx still open | **59** |
| .txt clean | **202** |
| .txt failing | **11** |
| Google measured | **213** of 213 |
| Google clean | **42** |

## Against the 15 Nov baseline

| | baseline | now | |
|:--|--:|--:|:--|
| mean share@5 | 6.15 | **3.69** | -39.98% |
| documents improved at all (any fall) | | **65** | |
| regressions | | **0** | none |

