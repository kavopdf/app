# P2W Baseline - Run Report

**24 Nov 2026 · 23:54 IST**

> 153 of 212 documents are at or under 1% share@5px in LibreOffice. The corpus is 39.7% closer to the 15 Nov baseline than it started.


This run was a fix-phase run, so it published no new measurement. It rebuilt the corpus from the corpus-v1 release, compiled the engine from the current head, and re-scored the .txt half from scratch; the re-score reproduced the committed table byte for byte, so no document moved and there was nothing to commit. The .txt row stays open on the documents that still fail their checks, which is the fixer's queue rather than a stale instrument.

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

