# P2W Fixer - Run Report

**20 Nov 2026 · slot 20:01 → 20:46 IST · 45 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What the two attempts measured

47\_margins was the class the rotation handed over, and 360\_restaurant\_menu is the one document in it
with a real column-position error: its body column renders 12 pt left of where the page drew it, source
52 against render 40, which the check reads as 9 unregistered runs with a worst displacement of 11.9 pt.
Neither attempt kept a change, and both are now fully explained.

The first found the mechanism, and it is not the one the previous run was hunting. The menu body is a
table, not a flow block - only the masthead and footer flow. The writer computes a 240 twip indent from
the cell's ink x of 52 pt against a column edge at 40 pt, and then DocxWriter.java:6366 sells that indent
to buy one line: if (textOverflows) insetTw = Math.max(0, spanTw - needTw). Menu names run 60 to 92 pt in
a 71.85 pt column, so five of them gave the whole indent back and were set at x=40, and the page's anchor
read 40 against the source's 52. Removing the sale pins the anchor at 52, takes unregistered runs from 9
to 0, flips the check to PASS and the document from 37 to 38 of 42 - and is still not keepable, because
the sale was buying those lines: 13 names now wrap at the right x and the pixel score goes 34.43 to
41.04. A variant that keeps the sale only where it buys the line measures worse on both, 47.78.

The second took a different hook. The widening loop in the cell emitter could only take room from cells
that are EMPTY; the cell beside a menu name holds leader dots, so the loop declined and the writer fell
through to selling its indent. A narrow helper - dots, bullets, ellipsis and spaces only - plus a fit
guard lets the cell widen over the leaders and appends them, so no character is lost and no column index
moves. It fires, and it is the best single-document pixel move this class has had: x pinned at 52 with no
wrap, 34.43 to 26.25. And it is still a regression, because pinning the name displaces the leader: the
dots' xink moves 112 pt to 144 pt, so 47\_margins goes 9 to 14, 13\_text\_colours newly fails on the dots'
grey, 43\_within\_10pt\_x newly fails, and the document reads 36 of 42.

The reason both lose is the thing worth the run. The page's own ink does not fit its own column: the name
is drawn at x=52 and runs to 144 pt while its column ends at 111.85, and the dots are drawn from 112 pt,
inside the name's column. Three positions, one column budget - pin the name and the dots move, keep the
dots and the name must wrap or give up its indent. There is no third option that keeps the page's grid,
because the page did not lay this out on that grid. Both measurements are written into
FINDINGS/47\_margins-INDENT-SALE-AND-LEADER-MERGE-2030.md with their numbers.


## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 20:28 | **reverted** | 0/14 | claimed. 47_margins (.docx, 14 in LO / 26 in Google). MECHANISM FOUND for the one document with a real 12 pt column error: 360_restaurant_menu's menu body is a TABLE, not a flow block (writer=table tw |
| 20:44 | **reverted** | 0/14 | SECOND ATTEMPT, different construct: WIDEN THE CELL OVER ITS LEADER-DOT COLUMN instead of selling its indent. DocxWriter tableBody's widening loop could only take room from EMPTY neighbours; a menu/in |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **182** (85.4%) |
| Failing at least one check | **31** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 12 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `47maanchor trace-01` | which writer construct puts 360_restaurant_menu's bo | 20:07 | 20:32 | 25 min |
| `47maclass census-01` | which clause of 47_margins each document fails, grou | 20:33 | 20:37 | 4 min |

## Timing

| | |
|:--|:--|
| Slot window | 20:01 → 20:46 · 45 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **26.4 min** — from 20:02:06, after `archive.py: housekeeping` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **42 min** | `#####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
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

The class's remaining untried direction is its .txt half - every attempt on it so far was .docx. Do not
rebuild the indent sale or the leader merge; both are measured above with their numbers. If the rotation
keeps 47\_margins, re-measure the class against a fresh render before believing either table:
392\_statistical\_console\_output already reads 0.06 with 42 of 42 passing on this engine while
RANKING.csv says 1.61.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

