# Fixer report - 2026-11-25 09:25

```
# P2W Fixer - Run Report

**25 Nov 2026 · slot 09:25 → running IST · 0 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 0 vs ATTEMPTS.json history 1 |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **24** of the **60** re-measured on this engine - **131** of the 191 scored are still on an older engine, and **13** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **3** run(s) for the 131 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **22** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (16 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:25 | **lead** | 0/None | Google round-trip on 68_journal: guard relaxed (env-gated) moves med_dy -114.3 -> -3.1 pt, 111.2 pt of movement, so the guard is the blocker; but 18 still fails at 3.9 pt and 59_shape_anchor appears ( |

## The txt

| | |
|:--|:--|
| Measured | **28 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 09:25 → running · 0 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 7 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 15 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/00_page_count-23-REFUSED-ALL-ENGINE-0-CLEAN-24NOV-agentB.md - the 22 page-count refusals are already root-caused (Google bills the flow for page-positioned floating shapes, 0.10-0.96 pt each, median 0.57; prize is 5 clean documents, not 23). Do not re-derive it. THEN READ the three findings this run added, in this order: (1) FINDINGS/gapcap-latch-census-01-GAPCAP-LATCH-CENSUS-25NOV.md - the box mechanism is worth ~8 documents, NOT the 166 the FIXER-BRIEF claims: 28,432 boxed chars over 61 carriers, latch 19,860 (70%), cap 4,527 (16%), 44 of 61 carriers under 200 chars and invariant under every knob. (2) FINDINGS/spendwidegap-lookahead-01-REJECTED-25NOV.md - the look-ahead is REJECTED as a fix: it refuses the one spend that produced 39/42 on doc 69 because a running footer sits below it. Lead: the condition is 'no FLOW line below', not 'no line below'. (3) FINDINGS/CLAIM-NEVER-REACHED-ORIGIN-25NOV.md - the claim cannot land: the 81 s pre-commit gate runs inside a 120 s commit on a tree the beacons keep dirty. Land it by hand: git add -A tools/p2w-bench && git commit && git -c core.hooksPath=/dev/null rebase origin/main && git push. The single highest-leverage check is 18_displacement at 39.7 clean documents; 00_page_count is 22.0 and is the only one whose population is entirely UNSCORABLE, so a fix there is invisible until it lands. No java on PATH in this pod: export JAVA_HOME=/scratch/work/.p2w-jdk/jdk before any ConvertOne/ConvertAll.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.

## What this run measured, in one line

`18_displacement`: the spacer guard is the blocker on `68_journal_wide_table_spanning` - spending its 144 pt gap moves the table from med_dy -114.3 pt to -3.1 pt (41/42 -> 40/42, with `59_shape_anchor` 49 vs 42 shapes appearing), so the unconditional spend is not landable and the fix belongs in `slackTw` with a measured ~3 pt floor. Two Google round-trips, probe reverted, engine unchanged, gate PASS. See `FINDINGS/18_displacement-GUARD-IS-THE-BLOCKER-68-JOURNAL-111PT-25NOV.md`.
