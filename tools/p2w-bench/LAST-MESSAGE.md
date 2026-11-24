# P2W Fixer - Run Report

**24 Nov 2026 · slot 13:12 → 14:07 IST · 55 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - subagents: 4 deployed vs no FINDINGS file for conv-01, txt -01 |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| Working on | `18_displacement` - taken from the pending list (26 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:59 | **lead** | 0/None | started the 213-document pass on the uniform-pitch patch: 52/213 converted, 24/212 measured, slot ran out at 55-60 min of compute on a 1.05-core pod (cpu.max 105000/100000). Kept instead an instrument |

## The txt

| | |
|:--|:--|
| Measured | **55 min ago** |
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
| Slot window | 13:12 → 14:07 · 55 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 155 |
| Longest silence | **15.3 min** — from 13:22:26, after `relay: p2w --force --budget 240 to measure real per-doc rate` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **6 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **39 min** | `################` |
| record - attempt, handoff, class rows | **6 min** | `###` |
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

PENDING FIRST: 23 item(s) you can close - run pending.py and take them in its order before the class below. 18_displacement: APPLY tools/p2w-bench/FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch, build, then START the slot with the 212-document pass (p2w.py --force --budget 250, repeat) - that pass is the whole cost. It is measured: 362_price_list_dense 41/42 -> 42/42 in Google, electricity-bill and 330_cad_drawing_sheet byte-identical. Do NOT re-run the trHeight=max(content,line-15) probe - it is refuted and the guard makes it unnecessary. After the pass: regress.py --check, --stamp, commit app/+RANKING.csv, attempt.py --class 18_displacement. Then check the 9 documents named in FINDINGS/18_displacement-UNIFORM-PITCH-GUARD-GOOGLE-42of42-0450-fixer.md for a uniform pitch.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

---

## What was kept

`benchmarks/p2w.py` — `CONVERT_SHARE=0.55`: conversion and measurement no longer share one
deadline. Committed `1b515f0b`, pushed.

**Before and after, same engine, same corpus, one `--budget 250` chunk:** measured **0** of 212
before, **24** of 212 after. Three consecutive chunks before the change each logged
`measured 0 of 212`, because `docx(end)` spent the whole window converting and `run(end)` then
entered with the deadline gone. That is why eight chunks in the last run reached `docx 213/213` and
only `36/212` measured: the measurement phase was only ever entered on a chunk that had already run
out of time. `rank()` already writes `RANKING.partial.csv` on a partial run, so a chunk that
measures is safe.

## What was measured and refuted

| Change | Speedup | Output | Verdict |
|:--|--:|:--|:--|
| parallel conversion, 2 workers, 10 documents | 1.10x (65.8 s to 59.8 s) | `.txt` identical 10 of 10 | reverted |
| parallel measurement, 2 workers, 7 documents | 1.02x (21.5 s to 21.2 s) | `median_pt` and `share5` identical | reverted |

`/sys/fs/cgroup/cpu.max` is `105000 100000` — 1.05 cores. `nproc` reports 2, which is the host's
cores, not the quota. Nothing in this pod parallelises; do not spend another slot on either.

## The cost of the pass, first hand

| phase | per document | whole corpus |
|:--|--:|--:|
| bare JVM start | 0.255 s | - |
| one conversion, cold | 3.0-4.4 s | - |
| conversion, sustained | 11 s | about 39 min |
| measurement, render prerendered | 2.4-4.4 s | - |
| measurement, one 7-page bank form | 81.4 s | - |
| measurement | | about 15-20 min |

A single-document `ConvertOne` on a warm cache reads 3x fast. The last run's 38-minute conversion
was right; the one-document timing was not.

## The stale txt table

`tools/p2w-bench/RANKING-TXT.csv` is a stale duplicate of `tools/p2w-bench/txt/RANKING-TXT.csv` and
says 149 clean / 64 failing, 50 documents apart. `txt_gate.py` and `step_txt.py` read only the
`txt/` copy, so the 199 / 14 above is the truth. `report.py` silently falls back to the stale copy.
Written up in `FINDINGS/two-RANKING-TXT-tables-ONE-STALE-2400-fixer.md`.

## Subagents

Both deployed and recorded. The conversion-cost agent landed the cache design and the fact that
`rank()` already writes `RANKING.partial.csv` on a partial run. The txt agent found the mechanism
but was briefed on the stale table and got the direction wrong; corrected against `git log`.

## Next run

1. Claim, read, deploy the two agents — and nothing else.
2. Apply `FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch`, `build-engine.sh`.
3. Six to seven back-to-back `p2w.py --force --budget 250` chunks, about 30 min, no gaps.
4. `regress.py --check`, `--stamp`, commit `app/` and `RANKING.csv`, `attempt.py`.

55-60 min of compute on a 1.05-core pod. A 90-minute slot fits it with about 15 min for the claim
and this report, and no room for a third thing — which is what killed this run.
