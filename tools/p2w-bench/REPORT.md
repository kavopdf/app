# Fixer report - 2026-11-18 17:20

```
# P2W Fixer — Run Report

**18 Nov 2026 · slot 16:52 → 17:19 IST · 27 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 3 of 212 |
| Corpus improvement vs 15 Nov | **+8.24%** — mean 6.15 → 5.64 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-missing-partly-replaced` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:00 | **reverted** | 0/16 | MEASURED AND REVERTED: the run-size-from-sizePt patch (the one SETTLED called 'the best single change available' after it took 360_restaurant_menu 34.43 -> 1.31) does NOT reproduce on the current engi |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Session | 16:52 → 17:19 · **27 min** |
| Slot window | 16:52 → 17:19 · 27 min |
| Before the claim | 0 min - pod setup, cloning and retries |
| Tool beats | 15 |
| Longest silence | **18.4 min** — from 17:00:38, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 2 |
| Obstacles | 16 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **8 min** | `#######` |
| record - attempt, handoff, class rows | **19 min** | `###############` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `itr-computation-with-slab-table` | 68.82 | 50.80 | -18.02 |
| `newsletter-3col-header-footer` | 3.45 | 3.13 | -0.32 |

## Next run

Do 416_many_tiny_pages FIRST and alone: seed its render (soffice --convert-to pdf on out/416_many_tiny_pages.docx takes ~250 s and does succeed), write pre/416_many_tiny_pages.pdf.src with the docx's size:mtime stamp so conv() uses the cache, then spend one whole call on measure_doc_chunked with chunk=100 budget=270 - or add per-window caching under dist2/<doc>.w<N>.json first, which is the real fix, because without it the document is unmeasurable at 300 pages by construction. Do NOT re-test run-size-from-sizePt (refuted on this engine 18 Nov 17:05, SETTLED.md corrected). Do NOT re-implement the anchor rule or the cell-baseline fallback. The class content-partly-lost-and-displaced is down to one document above the line, itr-computation-with-slab-table at 50.80; its remaining defects are listed in order in FINDINGS/itr-slab-the-squeeze-is-not-the-defect-1645.md and the first two are both refuted, so the third - the footer ROW of table 3 emitted between rows the page draws around it - is the only one left standing, and it is a row-ordering question in DocxWriter.table(), not a flow one.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
