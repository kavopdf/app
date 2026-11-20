# Fixer report - 2026-11-20 12:52

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 12:52 → running IST · 43 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7** of 192 measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:34 | **partial** | 3/13 | The spaces a page wrote as indent were emitted as run text, so the indent was n x whichever face's space advance rendered it: 392's 20-space row landed at 64.2 instead of 107.5 pt under a substituted |
| 13:34 | **reverted** | 0/13 | Pin the centred line's own extent [b.x, b.right] and drop w:jc, so a centred line stops delegating its left edge to the renderer's text width. Under the substitution proxy it fixes the check on 317_rt |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **179** (84.0%) |
| Failing at least one check | **34** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 12 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `47_mA-01-01` | what 47_margins actually compares, and where the pag | 13:36 | 08:06 | 0 min |
| `47_mB-01-01` | the space-led indent construct on 47_margins | 13:36 | 08:06 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 12:52 → running · 43 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 20 |
| Longest silence | **40.9 min** — from 12:53:03, after `pending.py: reading the pending gate` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **40 min** | `#####################` |
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

47_margins: extend the strip-and-pin indent construct from flowFromBox to the table-cell emitter (40_devanagari_shaping_font, 77_arabic_rtl_document, 78_mixed_english_devanagari_line), then a corpus pass in its own call. Read FINDINGS/47_margins-MECHANISM-133500-f2.md first - the class definition is already measured and the two failed constructs are already ruled out.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
