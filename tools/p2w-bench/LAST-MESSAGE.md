# Fixer report - 2026-11-24 13:12

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 13:12 → 15:03 IST · 1h 51m**

> One instrument kept. The 18_displacement patch was measured across the whole corpus for the first
> time and the gate refused it: 7 documents better, 22 worse than the last commit.

## Progress

| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; subagents: 4 deployed vs no FINDINGS file for txt -01, 18_dA-06 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **0** of the **0** re-measured on this engine - **190** of the 190 scored are still on an older engine, and **35** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 190 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (26 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:59 | **lead** | 0/None | started the 213-document pass on the uniform-pitch patch: 52/213 converted, 24/212 measured, slot ran out at 55-60 min of compute on a 1.05-core pod (cpu.max 105000/100000). Kept instead an instrument |

## The txt

| | |
|:--|:--|
| Measured | **1.3 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `conv-01` | conversion cost | 14:00 | - | - |
| `txt -01` | txt discrepancy | 14:00 | - | - |
| `18_dA-06` | where does the 11 s/doc conversion go, and the small | 14:00 | - | - |
| `18_dB-03` | why do RANKING-TXT.csv and the report disagree by 50 | 14:00 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 13:12 → 15:03 · 1h 51m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 163 |
| Longest silence | **15.3 min** — from 13:22:26, after `relay: p2w --force --budget 240 to measure real per-doc rate` |
| Silences over 2 min | 5 |
| Obstacles | 2 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **`docx open` has read 59 on every PROGRESS.md row since 21 Nov - four row-days, older than 24 h - while the f |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **6 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 34m** | `###################` |
| record - attempt, handoff, class rows | **6 min** | `#` |
| report - the report and the chain | **3 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 26 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. PENDING FIRST: 23 item(s) you can close - run pending.py and take them in its order before the class below. 18_displacement: APPLY tools/p2w-bench/FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch, build, then START the slot with the 212-document pass (p2w.py --force --budget 250, repeat) - that pass is the whole cost. It is measured: 362_price_list_dense 41/42 -> 42/42 in Google, electricity-bill and 330_cad_drawing_sheet byte-identical. Do NOT re-run the trHeight=max(content,line-15) probe - it is refuted and the guard makes it unnecessary. After the pass: regress.py --check, --stamp, commit app/+RANKING.csv, attempt.py --class 18_displacement. Then check the 9 documents named in FINDINGS/18_displacement-UNIFORM-PITCH-GUARD-GOOGLE-42of42-0450-fixer.md for a uniform pitch.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.

## What was kept, and what the pass now costs

`benchmarks/p2w.py`: a chunk's conversion share was defeated by one slow document. The stop test was
a flat 6 s checked *between* documents while one document may run for 90 s, so a 250 s chunk
converted a dozen documents and measured one (`conv_end 09:19:02`, `prerender 09:20:43`,
`measured 85 of 213`). Headroom is now twice the chunk's own median conversion cost. Measured:
**+1 → +30 documents measured per 250 s chunk**, and the pass then closed 213/213 converted and
212/212 scored inside this slot.

That settles the 06:50 finding. A full `--force` pass is **~4 s per document** here, not the 11 s
measured on a contended pod, so it does fit a 90-minute slot - the blocker was the scheduler, not
the cost. `18_displacement` is therefore no longer a slot problem: it is a 7-better/22-worse patch,
and the next run's work is what those 22 have in common. `electricity-bill` and
`68_journal_wide_table_spanning` both rose by under 0.3 share@5, which is the uniform-pitch guard
admitting a table that has no pitch to preserve.
