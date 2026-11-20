# P2W Fixer - Run Report

**20 Nov 2026 · slot 08:52 → 09:24 IST · 32 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |
| Committed | **15** files in 3 commit(s) from `61c8fee` — ...ed-rule-guard-was-not-the-blocker-100700-f1x.md, ATTEMPTS.json, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, INCIDENTS.md, LAST-MESSAGE.md, REPORT.md, ROUND.json, RUN-HISTORY.json, RUN-LOG.md, RUN.json, TIMELINE.jso |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:22 | **reverted** | 0/23 | relaxed the rule-border guard twice and wrote the paragraph indents from the rule so a border lands exactly on it: 3 of 39 rules on bank-statement-horizontal-rules-only now become w:pBdr, but 36 never |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `contA-08` | is the rule-as-drawing construct still in the engine | 08:58 | 09:05 | 7 min |
| `contB-08` | how much of 18_displacement the rule construct can e | 08:58 | 09:05 | 7 min |

## Timing

| | |
|:--|:--|
| Slot window | 08:52 → 09:24 · 32 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 27 |
| Longest silence | **7.6 min** — from 09:06:08, after `screen pass 2 of the displacement class` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 2 need a human |
| Still a wall | **This watchdog run has no `cron` tool**, so a paused or zombie cron cannot be moved by automation - a person  |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **9 min** | `#######` |
| measure or build - a conversion, screen or compile writes no beacon | **12 min** | `#########` |
| record - attempt, handoff, class rows | **3 min** | `##` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **5 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

the rule class is a TABLE-PATH job, not a guard job: 36 of 39 rules on bank-statement-horizontal-rules-only belong to table rows and never reach flowFromBox, so give the rule to the row or cell (w:tcBorders top) instead of loosening the guard again. Verify per document by counting w:pBdr in word/document.xml before screening - a count of 0 means the change is not being exercised

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
