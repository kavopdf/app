# Fixer report - 2026-11-20 04:59

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 04:59 → running IST · 19 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.44%** — mean 6.15 → 3.72 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |
| Committed | **13** files in 1 commit(s) from `6dfe946` — ...laced-rules-flush-works-displaces-055000-f1x.md, ...s-flush-by-top-WORKS-DISPLACES-055000-f1x.patch, ATTEMPTS.json, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, REPORT.md, ROUND.json, RUN-LOG.md, RU |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:11 | **partial** | 2/23 | flushShapes writes a page's shapes in TOP ORDER among its blocks (DocxWriter.pageXml) and ruleAsBorder turns a horizontal hairline the flow has reached into w:pBdr with a real w:before gap, ctx.flowY= |
| 05:17 | **reverted** | 0/23 | REVERTS attempt 10. attempt 10 was recorded 'partial 2/23' from the LibreOffice screen before the Google check existed; the Google check then decided against it. flushShapes (top-ordered shape emit in |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 04:59 → running · 19 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 14 |
| Longest silence | **12.4 min** — from 04:59:16, after `attempt.py: recording an attempt` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **18 min** | `#####################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Re-apply FINDINGS/rules-flush-by-top-WORKS-DISPLACES-055000-f1x.patch with 'git apply' - the flush-by-top change is PROVEN (18_centred: 0->2 pBdr, 2->0 drawings, both rules at the page's own ys 110.0 and 793.89, 32_stroke_lines FAIL->PASS in Google) and it is the precondition the last three runs were missing. Then fix the ONE thing it breaks: 18_displacement. It is NOT the gap (border 1 lands within 0.5 pt of its rule), NOT the below=flowBoxPt*(1-LINE_BASE) term (flowBoxPt is 0 when the rule is flushed) and NOT the kind!=0 guard (removing it changed nothing). It is the reader's position AFTER the carrier paragraph. Measure both variants on 18_centred through gverify: (a) ctx.flowY = s.topPt as written, (b) ctx.flowY left unchanged. One build, one Google round trip, and 18_displacement decides. THEN, separately: columnPage() (DocxWriter.java:2005, :2146, :2214) emits before/cells/after with plain emitBlock loops and returns before pageXml's emit loop, so no multi-column document can be reached - 315_gazette_notification measures pBdr 0 / drawings 5 / 40-42 unchanged because its two horizontal rules land in 'after' with flowY already 751.87. That is a second construct and the bigger share of the corpus.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
