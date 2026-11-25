# P2W Fixer - Run Report

**26 Nov 2026 · slot 02:28 → running IST · 1h 03m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **0** of 0 (0.0%) on 0 documents |
| Check-instances still failing | **0** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **42** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; subagents: 2 deployed vs no FINDINGS file for 60_tA-02, 04_cB-01 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **could not be read** - 0 of 213 scored were read as current, which is a failed read and not a measurement. No count is stated rather than a zero |
| Who re-measures them | the **:20 gverify** cron, once the read works |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (24 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 03:31 | **lead** | 0/25 | pgMar-top patch committed (b6bfcb7b). Full corpus re-measured on the patched engine: RANKING.csv byte-identical, 212 of 212 unchanged, 0 worse - the LibreOffice proxy is blind to this construct by con |

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `60_tA-02` | which emitted construct makes Google compute a diffe | 02:35 | 03:31 | 56 min |
| `04_cB-01` | does the check open the .docx at all, and what is th | 02:35 | 03:31 | 56 min |

## Timing

| | |
|:--|:--|
| Slot window | 02:28 → running · 1h 03m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 38 |
| Longest silence | **13.7 min** — from 03:15:00, after `lastmessage.py: running a tool for its numbers` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **43 min** | `#################` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **7 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run


---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 03:31 | **lead** | 0/25 | pgMar-top patch committed (b6bfcb7b). Full corpus re-measured on the patched engine: RANKING.csv byte-identical, 212 of 212 unchanged, 0 worse - the LibreOffice proxy is blind to this construct by con |

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `60_tA-02` | which emitted construct makes Google compute a diffe | 02:35 | 03:31 | 56 min |
| `04_cB-01` | does the check open the .docx at all, and what is th | 02:35 | 03:31 | 56 min |

## Timing

| | |
|:--|:--|
| Slot window | 02:28 → running · 1h 03m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 38 |
| Longest silence | **13.7 min** — from 03:15:00, after `lastmessage.py: running a tool for its numbers` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **43 min** | `#################` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| other - not attributed to a tool | **7 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run


---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 03:31 | **lead** | 0/25 | pgMar-top patch committed (b6bfcb7b). Full corpus re-measured on the patched engine: RANKING.csv byte-identical, 212 of 212 unchanged, 0 worse - the LibreOffice proxy is blind to this construct by con |

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 02:28 → running · 1h 02m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 36 |
| Longest silence | **13.7 min** — from 03:15:00, after `lastmessage.py: running a tool for its numbers` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **43 min** | `#################` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| other - not attributed to a tool | **7 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run


---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 21:15 | **lead** | 0/25 | Full corpus re-measured on the pgMar-top engine (213 converted, 212 scored). `RANKING.csv` byte-identical on all 212 rows, 0 worse, 0 better - the LibreOffice proxy cannot see this construct by construction. |
| 21:56 | **kept** | - | `18-displacement-PGMAR-TOP-CARRIES-THE-PAGE-GAP.patch` committed as `b6bfcb7b` through the real pre-commit hook (PASS). |

## The class I chose, and why

`18_displacement` - worth **54.8 CLEAN documents** in `classpick.py --leverage`, the largest single
prize in the table, and 25 of the 213 documents fail it and nothing else. It is not a research job
this time: `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md` root-caused it as three constructs, and the 01:25 run
had already applied and measured construct 2 end to end, then left it uncommitted for one reason - a
pre-existing 3-document regression in the committed engine. That regression is gone: `regress.py
--check` and `measure_gate.py` both passed on the tree I inherited, so the only thing standing
between the patch and the repo was the full corpus pass, and that is what this slot bought.

## What was measured

| | result |
|:--|:--|
| Corpus converted on the patched engine | **213 of 213**, 0 failed |
| Corpus scored | **212 of 212** |
| `benchmarks/RANKING.csv` vs the committed baseline | **byte-identical** - every column, all 212 rows |
| Documents worse | **0** |
| Documents better in the proxy | **0** - expected: `w:pgMar w:top` is honoured by Google, not by the proxy's page-top rule |
| The construct actually moved (independent read of the emitted XML) | `w:pgMar w:top` = 1103 / 1790 / 1390 / 230 / 1040 twips on `bank-statement-5-pages`, `416_many_tiny_pages`, `602_bookmarked_annual_report`, `324_loan_amortisation_schedule`, `mobile-bill`. At HEAD the writer emitted a literal `w:top="0"` |
| Gate | `regress.py --check` **PASS**, run by the installed hook at commit time |
| Google side | **not re-measured this run.** The 01:25 run measured this exact construct live on 5 documents: 9 check-instances fixed, 1 document clean, 0 new failures |

## Two agents, both landed

| | finding |
|:--|:--|
| A - `60_text_column_right_edge` (worth 22.9) | `FINDINGS/60-text-column-right-edge-ROOTCAUSE-2110-agentA.md`. The `under` half (35 docs, 27 on a DejaVu face) is font substitution: the right edge is written nowhere (`w:pgMar` right 0, `w:ind w:right` 0), so the edge is the resolved face's advance, and Liberation is 0.887 of DejaVu Sans. Patch spec in §7 (`stretchTw` + `faceRatio`), inert on the 124 non-DejaVu documents, predicted +18 to +27 documents. The `over` half (20 docs, 19 of them table documents) is **not** root-caused. |
| B - `04_chars_missing` (worth 11.9) | `FINDINGS/04-chars-missing-CHECK-IS-BLIND-TO-TEXTBOXES-2110-agentB.md`. The check compares the source PDF against Google's export and **never opens the .docx**; on 40 of 44 documents the "loss" equals, to the character, the text sitting inside `<w:txbxContent>`. The earlier lead's numbers were wrong (59 failures, not 65; 0 fail only `04`) and its example now passes. A minimal attribution fix would flip 40 documents and cannot newly fail any. |

## Verdict

**One kept engine change, and it is the one the pipeline has been refusing to land for two runs.**
`w:pgMar w:top` now carries the page-top gap that Google drops when it is written as the first
paragraph's `w:before`. It is an exact identity in the proxy (212 of 212 unchanged, every column),
which is why the gate can pass it at all, and it is the second of the three constructs that
`DOCS-ROOT-CAUSES-24NOV.md` says explain 94 of the 102 `18_displacement` failures.

Two honest limits. First, the Google-side gain is **not re-measured this run** - the number above is
the 01:25 run's live measurement of the same construct, and it should be re-read by the next gverify
on the 5 documents named in that report. Second, the attempt is recorded as `lead`, not `kept`: the
proxy moved nothing, and `attempt.py` refuses a `kept` with `moved=0`, which is the right refusal.

**The next run's cheapest wins, in order.** (1) The spacer half - construct 1, `w:line exact` used as
a table gap - is now the only thing between `18_displacement` and a large clean gain, and its blocker
(room guard, two documents onto a second page) is a guard problem, not a measurement problem.
(2) Agent A's `stretchTw` patch, after one round trip that answers whether Google honours
`w:rpr/w:spacing` on `302_radiology_report` - if it does, 18 to 27 documents. (3) Agent B's `04`
attribution fix, which is 40 documents and an instrument change that must be re-measured like one.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
