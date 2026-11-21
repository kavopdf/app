# P2W Fixer - Run Report

**21 Nov 2026 · slot 15:17 → running IST · 31 min**

> The 180-degree patch's missing `.docx` measurement is taken: **140 of 213 documents byte-identical**, the `.txt` of exactly one document changes, and it goes `t02_position` FAIL -> PASS. The patch is `.txt`-only by construction.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 15:48 | **partial** | 1/213 | 180deg patch measured on .docx for the first time: 140 of 213 byte-identical (136 full-conversion + the 4 rotation docs), .txt changes only one-page-rotated-180-degrees, t02_position FAIL->PASS. Not l |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **189** (88.7%) |
| Failing at least one check | **24** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `47_mA-02` | .docx blast radius of the uprightIfPageIsUpsideDown  | 15:19 | - | - |
| `47_mB-02` | true size of 47_margins on the CURRENT engine: re-re | 15:19 | - | - |


## Why the fix is measured but not committed

`regress.py --check` refuses it: `ENGINE CHANGED (txt): table measured on d5edf038e3e3681e, the tree is ae5b3129bfa31f15 - an unmeasured change is not a pass. Re-measure, then --stamp.` A full 213-document `.txt` re-measure does not fit what was left of this slot, and starting it at 15:58 would have left the tree dirty with an engine change for the next run's `git pull` to trip on. The finding is committed (`09639d0`), so the next run lands it with `regress.py --check --only txt --stamp` and nothing else to work out.

## The relay's slot

The slot was **free** - `status.py` said `IDLE, no fixer claim` - so this run is the fixer, claimed 15:17. `gaps.py` shows no in-run silence over five minutes for the previous run, and it left no claim behind.

**One thing the next relay must know.** `delegate_task` with `background=true` was honoured as a request, not a guarantee: on a scheduled run the platform ran the agent *inside* the turn and returned after 26 minutes. That is the 26.6 min silence in the Timing table, and from outside it is the shape of a dead run. Beacon before firing one, and expect it to block.

**The finding, in one line.** The T02 finding held this patch only because the `.docx` half was unmeasured. It is measured now, and the code says why the answer had to be zero: `flippedPage` reaches `toLines`, whose `turnedPage` parameter is **never read** (`grep -n turnedPage` returns the signature alone), and `buildPara`, which writes `p.lineX`/`p.lineY` - lists only `TxtWriter` consumes. `DocxWriter` reads `p.boxes`. A number only the `.txt` writer reads cannot move a `.docx`.

**The class is smaller than the table says.** `47_margins-STALE-TABLES-152500.md` proved `392_statistical_console_output` already passes all 42 checks on this engine while the table calls it a 1.61 failure, and then caught its own error: the "ungated build" it measured was a no-op - parentheses only - so what it attributed to a patch was HEAD's own output. The class's 26 is an upper bound. The next run on `47_margins` should re-derive it before judging its own attempt against it.

## The lead worth carrying

Apply the patch, run `python3 tools/p2w-bench/regress.py --check --only txt --stamp`, commit. Expected: `t02_position` 5 -> 4 failing documents, documents failing any `.txt` check 27 -> 26, 1 of 213 documents changed. The `.docx` column is expected to be 0 of 213, and that is now backed by 140 measured files rather than by reading the code.

**What would prove it wrong.** A document whose `.docx` differs between a HEAD build and a patched build. 140 did not. The 73 not converted in the patched full run are the gap, and the first thing to check there is whether any `DocxWriter` path reaches `Para.lineX` through `Para.copy` or `Para.merge`.

## Timing

| | |
|:--|:--|
| Slot window | 15:17 → running · 31 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 15 |
| Longest silence | **26.6 min** — from 15:19:03, after `deployed 2 agents, working my own angle: 47_margins .docx anchor` |
| Silences over 2 min | 2 |
| Obstacles | 1 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **29 min** | `####################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

