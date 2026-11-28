# P2W Fixer - Run Report

**28 Nov 2026 · slot 04:58 → 05:42 IST · 43 min**

> **2 document(s)** improved this run, but the run did not commit benchmarks/RANKING.csv, so the report cannot name them.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 3 vs ATTEMPTS.json history 2; subagents: 4 deployed vs no FINDINGS filename carries 18prize-01, 61rank-02 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **2** — 3 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (61 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:39 | **kept** | 2/None | instrument fix: page_lines() split a Google table row at its cell gutters; 2 documents CLEAN (salary-slip-factory-wages, table-with-merged-cells), 10 more pass 60, 0 pass->fail in a 62-document census |
| 05:41 | **error** | 0/None | spacer-gap model (shift=0.961*gap-0.58) refuted at a05b20eb05fe0fc8: measured 0.2288, r=1.0000; page-break leg binary at -59.03 pt regardless of gap; the inverse correction moves the probe 0.29 pt and |

## Why nothing moved, in this run's own words

> **Something did move: two documents, measured through Google.** This section is here because the tool
> asks for the reasoning, not because the run was empty.
>
> **The choice, and its reason.** `classpick.py --leverage` prices `18_displacement` at 46.6 clean
> documents and `60_text_column_right_edge` at 23.63. I took `60` and not `18`, and the reason was not that
> `60` looked easier: `60`'s population was exact: 62 documents, one mechanism, one file, and a census of all 62 could be
> measured inside the slot. `18`'s 108 failing documents split across at least three sub-constructs - a
> rigid offset (12), a per-run tail (6) and the page-break drop (18 multi-page) - so no single mechanism was
> established for it and an attempt would have been a guess at which one. **Before the attempt I asked which
> documents become CLEAN if this works: two.** Both did.
>
> **And a correction to my own reasoning.** I first wrote that `18`'s 46.6 was untrustworthy because it
> disagreed with the store's 108 failing / 18 alone. It does not disagree: 46.6 is `sum(1/len(failed))` over
> the 108 and reproduces exactly, and the same is true of `60`'s 23.63. **`--leverage` is a ranking, never a
> yield** - the document count behind 46.6 is 18 solo plus 28 solo-plus-one, and behind 23.63 it was 2. I
> recorded the wrong reason and am correcting it rather than leaving it to mislead the next run.
>
> **What the attempt was.** `60` reads the bbox of a MuPDF "line" object as a column's right edge. Google's
> PDF export puts a whole table row in one such object, so the check read the right-hand cell's edge as the
> left-hand column's overrun. The engine writes no right edge at all (`w:pgMar w:right="0"` on 62 of 62), so
> this was never an engine defect. The fix splits a line at its cell gutters. Threshold measured, not tuned:
> the 0.5-2 pt band is empty over 5,843 gaps.
>
> **Proved wrong first.** The before column is an independent script that reimplements the shipped
> predicate and the split side by side, not the file I edited. It FAILs all three probe documents on the
> shipped predicate and passes them on the split; the patched `gverify` then scores the same export PDFs
> 47/47 on two of them. Census of all 62: 0 pass->fail, because a split can only shrink a box.
>
> **The second attempt was a refutation, and that is the run's other product.** The corpus's `18_displacement`
> spacer model (`shift = 0.961*gap - 0.58`) was taken on an engine two revisions old. Re-taken here it is
> `0.2288`, and the page-break leg is binary (a flat -59.03 pt at every gap value), so the proposed inverse
> correction is worth **zero documents**. That is a run not spent later. The lead it leaves is different and
> better: the displacement accumulates up the page (`dy = -8.44 - 0.027*y`), which is `w:lineRule="exact"`
> clipping one line at a time, and the engine already has a mode switch for it that was measured at the same
> magnitude and **never taken to a verdict**.
>
> **What stopped this run was not the clock.** The pipeline rotated to `measure` while I was writing up and
> `--claim-fixer` now refuses. The kept change was committed, measured and pushed before that happened
> (`620dc85e`, `30121a9a`).

## The txt

| | |
|:--|:--|
| Measured | **15 min ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `60_tA-01` | which engine construct sets a body line's right edge | 08:04 | - | not recorded |
| `18prize-01` | which documents would become CLEAN if 18_displacemen | 04:05 | 04:12 | 7 min |
| `61rank-02` | among the 61 genuine losses, which single Google che | 04:31 | 04:32 | 1 min |
| `18_dB-01` | test the 0.961 spacer model at the current engine an | 05:40 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 04:58 → 05:42 · 43 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 53 |
| Longest silence | **20.1 min** — from 05:07:43, after `pending.py: reading the pending gate` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| build - compiling the engine | **4 min** | `##` |
| fix - diagnose and change the engine | **4 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **24 min** | `##############` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **2 min** | `#` |

The unattributed row is 5 distinct beat(s) that matched no phase. They said:

- `applying instrument fix to 60_text_column_right_edge`
- `60_text_column_right_edge -> kept`
- `heartbeat before any claim: attempt 2: 18_displacement per-line drift`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
