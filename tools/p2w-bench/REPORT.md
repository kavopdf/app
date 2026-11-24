# Fixer report - 2026-11-24 17:54

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 17:54 → running IST · 0 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **35** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (27 still open), not a new class |

## The txt

| | |
|:--|:--|
| Measured | **2 min ago** |
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
| Slot window | 17:54 → running · 0 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 6 |
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

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. 1. CORPUS FIRST, AND IT COSTS 16 s: `bash tools/p2w-bench/corpus-fetch.sh` puts all 213 PDFs on a fresh pod (212 scored in RANKING.csv, 0 missing). Measured 24 Nov 16:05 IST. Without it every gate reports 'corpus : could not be built (3) - no corpus PDFs found' and still prints PASS, so a run can believe it cleared a gate that read nothing. Run this before anything else. 2. DO NOT SPEND A CORPUS PASS ON THE UNIFORM-PITCH SNAP. Measured in Google on 24 Nov: the patch rewrites the w:trHeight values on 11 of the 13 sole-failure documents and both probes stayed 41/42 failing 18_displacement (72_bank_statement_no_rules_right_amounts, 17 of 18 rows rewritten; bus-timetable-station-left-times-right, 33 of 33). 0 of 13 moved. See FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-INERT-ON-THE-13-1120-fixer.md. The 42/42 on 362_price_list_dense stands and is a different table. 3. screen.py CANNOT SCREEN ON A FRESH POD. It converts, then hangs in 'prerender ... soffice batches of 12' past 280 s on two consecutive calls, because soffice is broken on a fresh pod. Fix the prerender or make it optional; until then the only number that comes back is Google's, at about 4 minutes per document (upload -> CREATE_FILE as a Google Doc in KavoPDF-Verify (id 1WpTvoWqJ9VymwDSzaMAVa0enZSwcUesB) -> EXPORT pdf -> gverify.py --collect). 4. A full --force pass is ~38 min conversion + ~15-20 min measurement on this 1.05-core pod, and parallelism is worth 1.0x. The remaining lever for landing anything is a cache that outlives the pod. 5. Next class: 60_text_column_right_edge is worth 19.8 clean documents and 5 documents fail only it - the second-largest single-check leverage, and nothing has been measured against it.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
