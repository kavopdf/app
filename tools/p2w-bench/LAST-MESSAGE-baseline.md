# P2W Baseline - Run Report

**28 Nov 2026 · 01:50 IST**

> 155 of 214 documents are at or under 1% share@5px in LibreOffice. The corpus is 40.3% closer to the 15 Nov baseline than it started.
This run was not a measure phase, so it published no new table: it rebuilt the corpus from the release zips, converted every PDF with the engine at HEAD, and re-scored the `.txt` half with the current verifier - 208 clean and 6 failing, unchanged, so there was nothing to commit on that side. It also measured the `.docx` half across the whole corpus, which is the one thing `BLOCKERS.md` has been asking the baseline cron for since 20:43, and the answer is not the one the pipeline wanted: the documents that moved are the ones built out of tables, they moved worse rather than better, and the clean count at or under 1% share@5px falls from 155 to 97. The full row-by-row table this run measured travels with this report as RANKING.csv. I checked the worst of them with my own eyes instead of trusting the number - `table-with-no-header-row`, 0.61 to 47.48 share@5px - and the render shows why: every single-line row is now shorter, so the error accumulates down a long table until its bottom sits tens of pixels from where the source drew it. That is the fixer's last engine commit, 'a single-line cell is written at its row's height', behaving as designed in Google and costing the table-heavy corpus in LibreOffice. So the table was not stamped, nothing was published, and the commit gate still refuses this tree; it is right to, and the fixer owns that change.


## Corpus

| | |
|:--|--:|
| Documents | **214** |
| .docx at or under 1% share@5px (LibreOffice) | **155** |
| .docx still open | **59** |
| .txt clean | **208** |
| .txt failing | **6** |
| Google measured | **206** of 214 |
| Google clean | **46** |

## Against the 15 Nov baseline

| | baseline | now | |
|:--|--:|--:|:--|
| mean share@5 | 6.15 | **3.67** | -40.26% |
| documents improved at all (any fall) | | **65** | |
| regressions | | **0** | none |

