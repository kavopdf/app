# Fixer report - 2026-11-20 09:58

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 09:58 → running IST · 44 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 3 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7** of 192 measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `18_displacement` |
| Committed | **12** files in 4 commit(s) from `e5f2e9a` — ...18_displacement-engine-topoffset-101951-cda8.md, ...placement-page-top-before-DROPPED-105000-f1x.md, 18_displacement-dy-shape-101323-4fa7.md, ATTEMPTS.json, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, ROUND.json, R |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 10:36 | **reverted** | 0/107 | table-spacer gap moved from w:line(exact) into w:before: MEASURED IN GOOGLE, reverted. Mechanism was named by two agents and looked right - the spacer paragraph writes the whole gap as w:line on a 1 p |
| 10:38 | **reverted** | 0/107 | ROOT CAUSE PROVEN, no engine change landed. Controlled probe through Google: w:before on the first paragraph after a w:br w:type=page is DROPPED ENTIRELY by Google Docs (55.15 pt asked, rendered 0.33 |
| 10:41 | **reverted** | 0/107 | Third probe, hand-edited docx (no engine change): replaced the four page-top w:before gaps in bank-statement-5-pages with 1x1 trHeight-exact table rows and zeroed the before. THE DISPLACEMENT ITSELF I |

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
| `18_dA-01` | Quantify the dy signature: across the Google renders | 09:59 | 05:12 | 43 min |
| `18_dB-01` | Find the engine code path that decides each line's v | 09:59 | 05:12 | 43 min |

## Timing

| | |
|:--|:--|
| Slot window | 09:58 → running · 44 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 26 |
| Longest silence | **27.0 min** — from 09:59:51, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **8 min** | `####` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **34 min** | `#################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

18_displacement: the page-top gap is PROVEN to be the cause (Google drops w:before there; a trHeight-exact 1x1 table row is honoured to 0.97 pt). Applying it by hand to bank-statement-5-pages fixes the displacement itself (dy median -53.8 -> +0.8) but the document goes 6 pages -> 10 with a blank after each, because (a) the break paragraph already emits a blank page 1 in Google and (b) the 55 pt gap is not charged to the page fill budget. So it is NOT a construct swap: make the gap real AND charge it to the page capacity, and fix the blank page. Engine work, needs a full corpus ratchet. See FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md, second section.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
