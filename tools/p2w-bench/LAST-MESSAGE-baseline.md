# P2W Baseline - Run Report

**25 Nov 2026 · 03:02 IST**

> 153 of 212 documents are at or under 1% share@5px in LibreOffice. The corpus is 39.7% closer to the 15 Nov baseline than it started.

This was a fix-phase run, so it published no new measurement. It rebuilt the corpus and measured every document, then re-scored the whole `.txt` half with the live verifier over those fresh renders; the re-score reproduced the committed table exactly, so no document moved and there was nothing to publish. No engine code was touched.


## Corpus

| | |
|:--|--:|
| Documents | **212** |
| .docx at or under 1% share@5px (LibreOffice) | **153** |
| .docx still open | **59** |
| .txt clean | **199** |
| .txt failing | **14** |
| Google measured | **191** of 212 |
| Google clean | **36** |

## Against the 15 Nov baseline

| | baseline | now | |
|:--|--:|--:|:--|
| mean share@5 | 6.15 | **3.71** | -39.70% |
| documents improved at all (any fall) | | **65** | |
| regressions | | **0** | none |

