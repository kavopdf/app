# Fixer report - 2026-11-27 19:18

```
# P2W Fixer - Run Report

**27 Nov 2026 · slot 19:18 → 19:41 IST **

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **5600** of 5933 (94.4%) on 142 documents |
| Check-instances still failing | **333** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **48** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; kept change: 1 code commit(s) in this window, first: finding 27NOV relay: the cell-before patch measu vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **37** of the **137** re-measured on this engine - **70** of the 207 scored are still on an older engine, and **5** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **2** run(s) for the 70 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **6** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (61 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 19:39 | **lead** | 0/None | cell-before patch measured in Google on the 3 only-18 documents: 74_balance_sheet 41/42 -> 42/42 (dy 1.5->0.6); bus-timetable 18 fixed but gains 46_text_crossing_rule; 72_bank_statement dy -1.0 -> -3. |

## Why nothing moved, in this run's own words

> The one open question the 18:00 run left was a measurement it could not afford: the cell-before
> patch moves `w:before` exactly as its arithmetic predicts, and the LibreOffice instrument is blind
> to a 1.7-3.2 pt move by construction. This run spent its middle on the Google render that settles it,
> on the three documents the store's census named as "fail 18_displacement and nothing else".
>
> Google answered, and the answer is not one law. `74_balance_sheet_indented_subitems` goes 41/42 ->
> 42/42 with its median dy 1.5 -> 0.6 pt: the branch's own case, and a real CLEAN document.
> `bus-timetable-station-left-times-right` fixes its displacement (4.2 -> 1.1) and gains a failure it
> did not have, `46_text_crossing_rule`: the raised cell now crosses a rule in Google's layout.
> `72_bank_statement_no_rules_right_amounts` moves the wrong way, dy -1.0 -> -3.0.
>
> So the patch is a real defect fix and a wrong class-wide change at the same time. One document
> becomes CLEAN, one trades its failure, one gets worse: a net of -1. Landing it would be the 23 Nov
> mistake with a nicer table, so the engine is unchanged, the three store rows were restored to their
> HEAD measurement (a row measured on `f4ce54f257d15f1c` describes an engine that is not in the tree),
> and the whole measurement is committed as FINDINGS/18-cellbefore-GOOGLE-27NOV-relay.md with the
> predicate the next run should test first: `cellBoxTw * 2 >= rowHeightTw`, which is true of 74 and
> false of both documents this change broke.

## The txt

| | |
|:--|:--|
| Measured | **3.8 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

Two, deployed before the first attempt. Neither is in ROUND.json's agent ledger - they ran as in-turn
delegations, so report.py counts none, and this table is the only record of them.

| agent | question | verdict |
|:--|:--|:--|
| 60_text_column_right_edge | which engine site lets a line stop short of its column's right edge, and how much is it worth | **`:4724`, the `stretchTw` gate**: `w:rpr/w:spacing` is emitted only when the page's own word gaps were inflated, so a narrower resolved face draws every line short in proportion. Ceiling **5** documents (38 fail it on this engine, 5 fail only it). Its falsifier - does Google honour `w:rpr/w:spacing` on import - is unmeasured. |
| 18_displacement targets | how many documents fail 18, how many fail only it, which to Google-measure first | **118 fail, 24 fail only it** (leverage 53.9), 105 table-bearing. Named the three measured here, and confirmed the patch's arithmetic line by line: `-1.70 pt` is table 1 of 74 only, table 2 is `-3.30`. |

## Timing

| | |
|:--|:--|
| Slot window | 19:18 → 19:41 · 22 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 25 |
| Longest silence | **7.1 min** — from 19:24:32, after `pending.py: reading the pending gate` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `######` |
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `##############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
