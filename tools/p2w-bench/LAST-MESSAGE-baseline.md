# P2W Baseline - Run Report

**24 Nov 2026 · 09:48 IST**

> 153 of 212 documents are at or under 1% share@5px in LibreOffice. The corpus is 39.7% closer to the 15 Nov baseline than it started.

This was not a measure phase. The `.txt` table was stale against a newer verifier and a newer engine, so this run rebuilt the corpus from an empty pod — downloaded the release zips, built the engine from the current head of main, converted every PDF to both formats — then re-scored every `.txt` with the current verifier and committed only those tables. The conversion loop and its soffice renders write no beacon, so no fix attempt is recorded here: the engine did not change, it was re-measured with an instrument that now matches it.

## Corpus

| | |
|:--|--:|
| Documents | **212** |
| .docx at or under 1% share@5px (LibreOffice) | **153** |
| .docx still open | **59** |
| .txt clean | **199** |
| .txt failing | **14** |
| Google measured | **190** of 212 |
| Google clean | **35** |

## Against the 15 Nov baseline

| | baseline | now | |
|:--|--:|--:|:--|
| mean share@5 | 6.15 | **3.71** | -39.70% |
| documents improved at all (any fall) | | **65** | |
| regressions | | **0** | none |

