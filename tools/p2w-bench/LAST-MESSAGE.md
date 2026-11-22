# P2W Fixer - Run Report

**23 Nov 2026 · relay slot 01:14 → running IST**

> **The guarded spacer split is worth one clean document and costs one check. Reverted.** The 23:10
> run read 4 of 16 at 42/42; this build reproduces one of those four. The guard itself works: both
> documents that cost that run a page are held at 46/47 and one page.

## What Google said, one round trip per document

Engine `1779a130` + the patch. Before is the committed Google table at `462353f9`, which is
byte-identical to `1779a130` in `engine/`.

| document | before | after | verdict |
|:--|:--|:--|:--|
| 29_dot_leaders_txtpos | 41/42 | 42/42 | won |
| 41_coloured_headings_white_bg | 41/42 | 41/42 | unchanged (the 23:10 run read 42/42) |
| 73_marksheet_subject_marks_grade | 41/42 | 41/42 | unchanged (the 23:10 run read 42/42) |
| 72_bank_statement_no_rules_right_amounts | 41/42 | 41/42 | unchanged (the 23:10 run read 42/42) |
| 22_invoice_four_columns_txtpos | 41/42 | 41/42 | unchanged |
| 16_right_aligned_amounts_txtpos | 41/42 | 40/42 | worse, new 23_line_pitch |
| mobile-bill | 46/47 | 46/47 | guard held |
| insurance-policy-schedule | 46/47 | 46/47 | guard held |

The guard is the carrier, not the spacer's size: the wins are tables whose cell borders are all nil
(rules are floating shapes), the losses are ruled tables. Outside that gate the paragraph is
byte-identical to before, so nothing else in the corpus moved at all.

The 4 wins do not reproduce on this build. Three of the four read 41/42 here, same engine, same
patch, same conversion path. The one loss is the dither moving 16_right's row declarations, not the
spacer. Evidence, and what would re-open it, in
`FINDINGS/18_displacement-GUARDED-SPACER-SPLIT-1-WIN-1-COST-0219-relay.md`.

# P2W Fixer - Run Report

**23 Nov 2026 · slot 01:14 → running IST · 16 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| Slot window | 01:14 → running · 16 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 18 |
| Longest silence | **9.0 min** — from 01:14:31, after `report.py: building the report` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **7 min** | `##########` |
| measure or build - a conversion, screen or compile writes no beacon | **9 min** | `############` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

APPLY patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch and ratchet it corpus-wide - measured clean on two-tables-stacked-with-no-gap (42/42 PASS, n_out 0) and it moves EVERY ruled table, so the gate refuses it unratcheted. The row grid is 0.75 pt, NOT whole points: nine identical rows per page read 18.00/18.75/19.50, and the law laid=0.75*(round(h/0.75)+1) reproduces the 13-declaration sweep exactly when its readings are rounded. Then close the small-spacer over-charge the patch exposes: mobile-bill's 128/124 tw spacers are now charged in full where Google previously charged ~0, leaving that page +2..+5 pt low. Evidence: FINDINGS/18_displacement-ROW-GRID-AND-SPACER-1518-relay.md

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

