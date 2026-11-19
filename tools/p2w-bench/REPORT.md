
  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
# P2W Fixer - Run Report

**19 Nov 2026 · slot 18:00 → running IST · 42 min**

> No change was kept this run. The numbers below say what was tried.

## What the tables cannot show

**The class is not one mechanism, and that is this run's finding.** `content-present-partly-displaced`
is the biggest OPEN class and the brief says to take the biggest, because one mechanism fixed once
clears every document under it. Measured on four of its documents with a word-box alignment against
the rendered output, that premise is false here: `75_merged_header_cell_three_columns` welds two
header columns into one and emits every data row's numbers one row above its depot name;
`bank-statement-horizontal-rules-only` is correct to +0.03 pt at the top of the page and +5.77 pt at
y421, a constant 0.34 pt per positioned row against a source pitch of exactly 18.4 pt;
`374_org_chart` is -0.18 pt at the top and +4.48 pt in its bottom box row;
`payslip-label-left-amount-right` carries one block a constant 3.45 pt high. Three mechanisms in four
documents. The per-document numbers are in
`FINDINGS/content-present-partly-displaced-fillrule-131500-fixer.md`.

**The one attempt was a real root cause whose obvious fix is wrong.** A fill-only shading rectangle
was being used as a table cell edge, which welds `Fleet held` and `Breakdowns` into one cell and
shifts the rows by one. Skipping fill-only rules from the edge list is the obvious fix and it is
worse: the table splits across two pages, because on this page the shading band is the *only* rule
that closes those header cells. Reverted and written up so no later run spends the same forty minutes
on it. The half still worth trying is `w:vMerge`: `spanR` is computed at `PdfToWord:7950` and read by
nothing, so a table whose source merges cells vertically is written with three `w:gridSpan` and zero
`w:vMerge`.

**A measurement the whole pipeline reads had been empty for a day.** `benchmarks/CENSUS.csv` has been
the header row and nothing else since 18 Nov 17:19, through four complete measurements that each
logged `census: ok`. `census.py` writes its output *beside the ranking it describes*, and `gate.py`
passes it `/scratch/output/RANKING.csv` - so every census went to `/scratch/output`, which a fresh pod
does not have, and the repository copy was never touched. `gate.py` now publishes `CENSUS.csv` and
`CENSUS.md` into `benchmarks/` the way it already publishes `RANKING.csv`.

**Two of our own tools contradicted each other, and the report could not be committed.** report.py
writes `slot 18:00 → running IST` while the slot is open, and lastmessage.py demanded a clock at both
ends, so it refused the report report.py had just produced. It also counted its own beacon: each
regeneration saw one more beat than the last, so the two calls could never agree. Both fixed; the
end clock is checked only when there is one, and the beat count is the run's work rather than the
reader's footsteps.

**The subagent ran inline and cost this run its second angle.** It was dispatched in the background
and the platform ran it inside the turn anyway - nineteen minutes of silence - so the second agent,
on the 0.34 pt row accumulation, was never deployed. Both are recorded in `HANDOFF.json` rather than
dressed up as landed work.

**No beacon for the measuring.** A conversion, a soffice render and a compile write none, so the
longest silence below is real work, not a dead run.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 53 of 213 |
| Corpus improvement vs 15 Nov | **+32.81%** — mean 6.15 → 4.13 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **28** of 213 — the rest are still off |
| Moved but still open | **25** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 18:40 | **reverted** | 0/18 | fill-only shading rectangles were treated as table cell edges (PdfToWord:1277-1285 built an Edge from every rule, ignoring the null stroke that stampPathRules gives a non-hairline fill). Dropping them |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **166** (77.9%) |
| Failing at least one check | **47** |
| Most common failure | `t13_amount_columns` - 19 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `contA-03` | 75_merged_header_cell_three_columns: the table body  | 18:16 | 13:11 | 25 min |
| `contB-03` | 13 of the 18 documents are within 1 pt everywhere ex | 18:16 | 13:11 | 25 min |

## Timing

| | |
|:--|:--|
| Slot window | 18:00 → running · 42 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **23.9 min** — from 18:16:17, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **23 min** | `############` |
| measure or build - a conversion, screen or compile writes no beacon | **14 min** | `#######` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `salary-slip-factory-wages` | 18.09 | 0.73 | -17.36 |
| `mobile-bill` | 18.48 | 1.55 | -16.93 |

## Next run

Implement w:vMerge in DocxWriter's table emission from the spanR PdfToWord already computes (PdfToWord:7950 writes it, nothing reads it). Screen 75_merged_header_cell_three_columns plus the 17 other content-present-partly-displaced documents. Do not retry dropping fill-only rules from the Edge list - measured 27.31 -> 46.58.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
