# P2W Fixer - Run Report


**23 Nov 2026 · relay slot 01:14 → running IST**

> **The spacer split alone takes five documents to 42/42 in Google with nothing worse. The dither
> was eating the wins.** Measured twice in this slot, Google, one round trip per document. The
> engine change is not committed: the whole-corpus LibreOffice measurement it needs did not fit.

## What Google said

Engine `1779a130`. Before = the committed Google table at `462353f9`, byte-identical to `1779a130`
in `engine/` (an empty `git diff --stat`), so it is a legitimate before for this engine.

| document | committed | split + dither | split only |
|:--|:--|:--|:--|
| 29_dot_leaders_txtpos | 41/42 | 42/42 | 42/42 |
| 41_coloured_headings_white_bg | 41/42 | 41/42 | 42/42 |
| 73_marksheet_subject_marks_grade | 41/42 | 41/42 | 42/42 |
| 22_invoice_four_columns_txtpos | 41/42 | 41/42 | 42/42 |
| 16_right_aligned_amounts_txtpos | 41/42 | 40/42 (new 23_line_pitch) | 42/42 |
| 72_bank_statement_no_rules_right_amounts | 41/42 | 41/42 | 41/42 |
| mobile-bill | 46/47 | 46/47 | 46/47 |
| insurance-policy-schedule | 46/47 | 46/47 | 46/47 |

The guard is the carrier, not the gap's size: the wins are tables whose cell borders are all nil
(rules are floating shapes), the two documents that lost a page to the unguarded split are ruled
tables on exactly-full pages. Outside the gate the spacer paragraph is byte-identical to before.

Split only: five documents to 42/42, none worse, neither full-page document touched. Split plus the
row-pitch dither: one win, one document worse - the dither was not carrying the wins, it was eating
them.

Why this is a lead and not a commit: the engine change needs a whole-corpus LibreOffice measurement
(`regress.py --check`) before it may land, and the slot ran out. The patch is one command:
`git apply tools/p2w-bench/patches/18-displacement-SPACER-BEFORE-GUARDED-NO-DITHER.patch`, build,
`p2w.py --force`, `regress.py --check`, then Google the remaining eleven of the sixteen and a sample
of documents that are clean today. Evidence:
`FINDINGS/18_displacement-GUARDED-SPACER-SPLIT-1-WIN-1-COST-0219-relay.md`.

**23 Nov 2026 · slot 01:14 → 01:34 IST · 19 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 01:30 | **reverted** | 0/None | guarded spacer split (non-ruled carrier, gap<=20pt) reproduces 1 of the 4 wins the 23:10 run reported (29_dot_leaders 42/42) and costs 16_right_aligned_amounts 41/42 -> 40/42 via a new 23_line_pitch; |
| 01:33 | **lead** | 0/None | spacer split ALONE (guard: non-ruled carrier, gap<=20pt; dither disabled) takes 5 of 8 measured documents to 42/42 in Google with no document worse: 29_dot_leaders, 41_coloured, 73_marksheet, 22_invoi |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dcarrier guard-01` | why the spacer split breaks two documents and what a | 01:31 | 20:01 | 0 min |
| `18_dsolo-18 census-01` | per-document spacer/border/row census of the 16 that | 01:31 | 20:01 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 01:14 → 01:34 · 19 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 28 |
| Longest silence | **9.0 min** — from 01:14:31, after `report.py: building the report` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **9 min** | `###########` |
| measure or build - a conversion, screen or compile writes no beacon | **9 min** | `##########` |
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

APPLY tools/p2w-bench/patches/18-displacement-SPACER-BEFORE-GUARDED-NO-DITHER.patch (spacer split, guard = non-ruled carrier and gap<=20pt, dither DISABLED - the dither is what ate 16_right), build, convert and measure the whole corpus, regress.py --check, then Google-verify the remaining eleven of the sixteen plus a sample of today's Google-clean documents that carry a non-ruled table. Measured this slot: 5 of 8 to 42/42, none worse, mobile-bill and insurance held at 46/47. Evidence: FINDINGS/18_displacement-GUARDED-SPACER-SPLIT-1-WIN-1-COST-0219-relay.md

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

