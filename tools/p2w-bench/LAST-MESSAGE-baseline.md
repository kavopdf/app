# P2W Baseline - Run Report

**25 Nov 2026 · 20:40 IST**

> 154 of 213 documents are at or under 1% share@5px in LibreOffice. The corpus is 40.0% closer to the 15 Nov baseline than it started.

This run did the non-measure refresh and nothing more, because the phase is `fix` and not `measure`. From an empty corpus it rebuilt the corpus, re-rendered every document through LibreOffice and re-scored the `.txt` half against the current engine and verifier. That re-score reproduced the committed table exactly, so there was no `.txt` change to publish and the round was neither advanced nor ranked; the fix slot was left alone. What the fixer should know: the LibreOffice prerender is the bottleneck and its batches kept coming back empty inside the render budget, so the pass rate is set by retries rather than by comparison work - clearing the stale single-instance IPC lock in `/tmp` before a pass is what unstuck it. The very long multi-page document remains exempt by design and is named in `EXEMPT.json`, not dropped. And `precommit.sh` cannot pass at HEAD: `check-regressions` flags files that later commits deliberately replaced and nobody has waived them, so any commit from this tree needs that looked at first.

## Corpus

| | |
|:--|--:|
| Documents | **213** |
| .docx at or under 1% share@5px (LibreOffice) | **154** |
| .docx still open | **59** |
| .txt clean | **204** |
| .txt failing | **9** |
| Google measured | **213** of 213 |
| Google clean | **42** |

## Against the 15 Nov baseline

| | baseline | now | |
|:--|--:|--:|:--|
| mean share@5 | 6.15 | **3.69** | -39.98% |
| documents improved at all (any fall) | | **65** | |
| regressions | | **0** | none |

