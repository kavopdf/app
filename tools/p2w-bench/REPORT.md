# Fixer report - 2026-11-20 21:57

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 21:57 → 22:43 IST · 46 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **18** files in 3 commit(s) from `b87c499` — ATTEMPTS.json, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, HISTORY-TXT.jsonl, LAST-MESSAGE.md, REPORT.md, ROTATION.json, ROUND.json, RUN-HISTORY.json, RUN-LOG.md, RUN.json, STATE-TXT.json, TIMELINE.jsonl, TRACE.md, ff |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:39 | **reverted** | 2/7 | U+FFFD is the /ToUnicode CMap's own destination value (<0124> <FFFD> etc. in REAQAG+Effra-Regular), not a missing or malformed CMap; PdfToWord.processTextPosition trusts it because isJunk() accepts U+ |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t01_ToUnicode CMap destination-01` | Is the U+FFFD the CMap's own answer or a parse failu | 22:39 | 17:09 | 0 min |
| `t01_adversarial patch review-01` | How can this Identity-H recovery write wrong text in | 22:43 | 17:13 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 21:57 → 22:43 · 46 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **23.3 min** — from 21:57:13, after `pending.py: reading the pending gate` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **42 min** | `####################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **3 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Do not apply the FFFD patch first. Render page 1 of 041122-Account_Opening_Form at 150 DPI and look at the 127 glyph sites - ligature or not decides whether the patch is right. Read FINDINGS/fffd-cmap-destination-PATCH-REVIEW-2325.md. If ligature, the fix is CIDToGIDMap plus the descendant cmap; if not, apply FINDINGS/fffd-cmap-destination-2300-fixer.patch and budget the whole slot for p2w.py --budget 250 to completion, then restamp_txt.py --run/--apply, classrow.py --write, regress.py --check.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
