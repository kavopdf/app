# P2W Fixer - Run Report

**25 Nov 2026 · slot 17:16 → 18:05 IST · 48 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **42** documents clean - a kept attempt is progress inside a class, not a finished document |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `t12_word_invention` - taken from the pending list (19 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `t12_word_invention` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:35 | **kept** | 2/3 |  |
| 18:01 | **lead** | 0/None | annotation /Contents hoist has a second, unguarded door in PdfToWord.pageText(): the annotationRuns loop lacks the drawnByAppearance(apDrawn, ...) guard its sibling form-value loop has. Measured 600_r |

## The txt

| | |
|:--|:--|
| Measured | **22 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **202** (94.8%) |
| Failing at least one check | **11** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t02_position` - 4 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 17:16 → 18:05 · 48 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 33 |
| Longest silence | **18.4 min** — from 17:40:27, after `pending.py: reading the pending gate` |
| Silences over 2 min | 8 |
| Obstacles | 0 cleared · 4 parked, with the evidence to re-open them |
| Still a wall | **does not apply.** `status.py` reads verdict IDLE - "no fixer claim - the slot is free" - so there is no clai |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **1 min** | `#` |
| fix - diagnose and change the engine | **22 min** | `##########` |
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `##` |
| record - attempt, handoff, class rows | **9 min** | `####` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **7 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 16 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 15 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. FIRST ATTEMPT: add the drawnByAppearance(apDrawn, ...) guard to the annotationRuns loop in PdfToWord.pageText() (~line 956) - its sibling loop at line 947 already has it. Measured on one document: 600_reviewed_invoice_with_annotations goes 20 tokens/83 chars -> 7 tokens/30 chars, paragraphs 14 -> 13. Needs the 213-document docx ratchet before it lands. SECOND: the (Authorised signatory) duplication on 041122-Account_Opening_Form and Account_Opening_Form_Fillable_filled is a table-row/paragraph overlap, a different construct, and clearing it closes the last 2 txt documents that are not the annotation one. THIRD: _ensure_scipy() should refuse rather than warn, and p2w.py:1112 must not swallow the scipy.ndimage import - see FINDINGS/SCREEN-HANG-IS-SCIPY-NOT-SOFFICE-25NOV.md.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
