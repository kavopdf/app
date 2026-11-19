# P2W Fixer - Run Report

**19 Nov 2026 · slot 23:53 → running IST · 32 min**

> **75_merged_header_cell_three_columns** improved — 27.31 → 7.62. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **2** — 2 attempt(s), 1 kept |
| Documents improved, round total | 59 of 213 |
| Corpus improvement vs 15 Nov | **+39.01%** — mean 6.15 → 3.75 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **27** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 00:24 | **kept** | 2/18 | w:vMerge emitted from spanR (DocxWriter) + spanR recorded only on the row a rectangle starts (PdfToWord) + a rectangle spanning rows is a merge only when its text occupies fewer bands than the rows it |
| 23:56 | **error** | 0/18 | IN PROGRESS - 75_merged_header_cell_three_columns: emit w:vMerge from spanR + bucket glyphs by their own baseline band instead of the cell top edge (PdfToWord:7846); baseline 27.31 reproduced on this |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 23:53 → running · 32 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 16 |
| Longest silence | **28.1 min** — from 23:56:48, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **31 min** | `######################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

content-present-partly-displaced, 24 OPEN. Take 75_merged_header_cell_three_columns (27.31, the worst in the class): implement w:vMerge in DocxWriter's table emission from the spanR PdfToWord:7950 already computes, and bucket each glyph by its own baseline band instead of the cell's top edge (7846) - the sibling finding says both are needed and that the band test alone moves Depot to the wrong row. Do not retry dropping fill-only rules from the Edge list (27.31 -> 46.58). Do not apply patches/rowgapok-run-pitch.patch on its old numbers.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
