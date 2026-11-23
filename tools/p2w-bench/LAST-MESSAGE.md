# P2W Fixer - Run Report

**23 Nov 2026 · slot 13:20 → running IST · 42 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **0** of the **2** re-measured on this engine - **188** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 188 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:02 | **reverted** | 0/None | partial spend of the table-gap spacer: Google 68_journal 41/42 -> 40/42, adds 59_shape_anchor, fixes nothing; flow-invariant so LibreOffice could not have caught it |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `A118_displacement-01` | writer-construct | 13:21 | 13:31 | 10 min |
| `B160_text_column_right_edge-01` | right-edge+shape_anchor | 13:21 | 13:34 | 13 min |

Both landed and both are committed as findings. A found the table-gap spacer and named the 7 documents it reaches; its 7-document LibreOffice before/after was identical, which is what made the change look safe. B found that `60_text_column_right_edge` and `59_shape_anchor` are two constructs, not one, and put the width formula at `DocxWriter.java:2793` (`max(4,advance)*1.12 + size*1.5`) as the excess. Neither was measured in Google by the agent; this run measured A's in Google and it regressed.

## Timing

| | |
|:--|:--|
| Slot window | 13:20 → running · 42 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **14.4 min** — from 13:21:17, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **7 min** | `####` |
| measure or build - a conversion, screen or compile writes no beacon | **23 min** | `############` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **11 min** | `######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

**18_displacement is REFUTED as a partial-spend problem, and the refutation is a Google measurement with a control.** `68_journal_wide_table_spanning` — the largest gap in the corpus, 144 pt — scored **41/42** on the unmodified engine and **40/42** with the partial spend: `18_displacement` unchanged at `source=0 render=1`, plus a new `59_shape_anchor`. The change preserved `before + line` to the twip on all 51 documents it touched (0 paragraph-count changes, 0 sum changes), so **LibreOffice could not have caught this** — it is the exact case the charter's "Google is the truth" rule exists for. Reverted; patch kept at `FINDINGS/18_displacement-PARTIAL-SPEND-REGRESSES-GOOGLE-1428-relay.patch`.

**The open question is now sharp and worth a whole slot:** `w:before` is NOT honoured at its declared value on this spacer. 144 pt of `w:before` would have closed a 144 pt gap; it closed none. Until someone explains what Google does with a `w:before` above some threshold, every mass-shift between `w:before` and `w:line` is a guess. Cheapest next probe: the same 4-call Google round trip on `insurance-policy-schedule` (46/47, fails only `18_displacement`) with the patch applied — it is a 14.4 pt gap, not 144, so it tests the threshold rather than the extreme.

**Two levers carried forward, both unmeasured in Google:** `60_text_column_right_edge` (16.9 clean, `DocxWriter.java:2793`) and `00_page_count` (23.0 clean, the empty-paragraph merge, mechanism from the 05:30 run).

> The five other documents the spacer reaches were **not** run — the slot ran out. They each fail exactly `18_displacement` and nothing else, so any one is a clean probe.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
