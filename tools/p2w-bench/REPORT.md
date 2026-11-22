# Fixer report - 2026-11-23 04:56

```
# P2W Fixer - Run Report

**23 Nov 2026 · slot 04:56 → running IST · 0 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **28**, out of the 190 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `-` |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 04:56 → running · 0 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 6 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

18_displacement: the spacer HAIRLINE is now 1 tw (was 20) and the guard's room test is keyed to a fixed 20 so no document changes side of the guard. FINDINGS/18_displacement-HAIRLINE-WAS-078PT-ONE-CLEAN-0402-fixer.md. 22_invoice_four_columns 41/42 -> 42/42 in Google (base and patched measured in the same hour); 16_right_aligned stays 41/42. Corpus 212/212 re-measured, 0 worse, share@5px changed on 0 of 213 (0.05 pt against a 5 px tolerance); txt 213 scored, 213 unchanged. NEXT LEVERS, in order of evidence: (1) the CELL LINE BOX is the remaining constant - declared 7.60+9.50=17.10 pt, Google lays 7.60+8.193=15.793, a -1.307 pt per row term identical on 22 and 16 (FINDINGS/18_displacement-RESIDUAL-2.5PT-ARITHMETIC-0355-fixer.md has the arithmetic); fixing it means inflating the cell's declared w:line, which moves text INSIDE the row in LibreOffice because trHeight 380 atLeast absorbs the height and not the position - measure both renderers. (2) 72_bank_statement is refused by the guard 58 tw short (18 rows -> 270 tw row term, gap 346 tw, room 558 tw): measure Google's real per-row excess on a ruled table and replace the inherited 15 tw/row, worth +1. (3) do NOT key the guard's room test to spacerHairTw - at hair=1 that flips 22_invoice's second spacer to refused and moves that table 7.65 pt. Any Google reading at the 41/42-42/42 margin must be taken twice.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
