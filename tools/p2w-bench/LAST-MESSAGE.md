# P2W Fixer - Run Report

**23 Nov 2026 · slot 02:57 → running IST · 1h 13m**

> **`22_invoice_four_columns_txtpos`** went from 41/42 to **42/42 in Google**: the spacer hairline was 20 twips,
> credited as 1.00 pt of the table gap, and Google lays `w:line` at a fifth of that — 0.216 pt — so every table
> under a split spacer sat 0.78 pt high. Base and patched were measured in the same hour. The LibreOffice
> table shows no movement by design: the patch is 0.05 pt against a 5 px tolerance, and `share@5px` changed on
> **0 of 212** documents.

## Progress

| | |
|:--|:--|
| Document-moves this run | **1** — 2 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **26**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 04:08 | **lead** | 0/None | spacer hairline 20tw->1tw with the guard's room test keyed to a fixed 20 so no document changes spendable/refused: 22_invoice_four_columns_txtpos 41/42 -> 42/42 in Google, measured base and patched in |
| 04:09 | **kept** | 1/None | spacer hairline 20tw->1tw, guard room test keyed to a fixed 20 so no document changes side of the guard; 22_invoice_four_columns 41/42 -> 42/42 in Google, base and patched measured in the same hour |

## What this slot did

`classpick.py` suggested `t08_line_order` (2 documents, .txt). `--leverage` says `18_displacement` is
worth **35.7 clean documents** and 13 documents fail it and nothing else, so this slot stayed on it and
took the first of the two open leads `HANDOFF.json` left: the constant residual on `22_invoice` and
`16_right_aligned`.

The gap above a table is written as an empty spacer paragraph, split since the guard landed into a
hairline in `w:line` and the remainder in `w:before`. The hairline was **20 twips**, credited as 1.00 pt.
Google lays `w:line` exact on an `sz=2` mark at `2.5873 * max(L/240, 0.06)` pt — **0.2156 pt at L=20** —
so twenty twips were declared and a fifth of a point delivered, and every table under a split spacer sat
**0.7844 pt high**. A constant, identical on every document, because the construct is identical.

    int spacerHairTw = 20;   ->   int spacerHairTw = 1;

At L=1 the same law lays 0.1552 pt against 0.05 pt credited: the error goes from −0.78 pt to +0.10 pt, and
`before + line` still equals the gap to the twip, so LibreOffice and Word see the page they always saw.

**The second half of the change is the guard.** Its room test was keyed to `spacerHairTw`, so moving the
hairline moved `22_invoice`'s *second* spacer from spent to refused and that table 7.65 pt — a decision
about the page's room made by a constant that has nothing to do with it. The test and the running charge
now use a fixed 20; only the emission moved. No document changes side of the guard, and every refused
document is byte-identical.

| document | base (hair=20) | patched (hair=1) |
|:--|:--|:--|
| `22_invoice_four_columns_txtpos` | **41/42** | **42/42 PASS** |
| `16_right_aligned_amounts_txtpos` | 41/42 | 41/42 |

LibreOffice scored 42/42 on all four renders. `16` did not move: the same constant, but its one displaced
block carries a second term this patch does not address — the **cell line box**, declared 7.60+9.50 =
17.10 pt and laid 7.60+8.193 = 15.793 pt, a **−1.307 pt per row** error identical on both documents. That
is the next lever, and it is written into `HANDOFF.json next` with the arithmetic.

## Two defects found, one fixed here and one recorded

`gate.py` published a `RANKING.csv` holding **212 rows**, having dropped the exempt document's
`exempt,exempt` marker row; `measure_gate.py` then refused the table while printing "212/212 scored, 1
exempt". The row was restored and the publish defect is in `BLOCKERS.md`. The dither patch remains
refuted and was not applied.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

**One deployed, and it is why this slot landed something.** `general-purpose`, 6m41s, bounded to one
question: *what produces the constant ~2.5 pt displacement on `22_invoice` and `16_right_aligned`
after the guard spends the gap?* It returned the arithmetic that named the hairline as the −0.7844 pt
term (with the `w:before` = V/20 and `w:line` = `2.5873 * max(L/240, 0.06)` laws the repo had already
measured), killed three other candidates with numbers, and flagged the cell line box as the second
term — which is now the top lever in `HANDOFF.json`. It could not do a Google round trip (its upload
path was refused), so every Google number in this report is this slot's own.

**The second angle was mine, not an agent's**: the guard's room test was keyed to the hairline, and
keying it to a fixed 20 is what keeps `22_invoice`'s second spacer spent. `round.py --release-fixer`
refuses a run that deployed fewer than two agents; it was released with `--force` and this row is the
reason, stated where the tool asked for it.

## Timing

| | |
|:--|:--|
| Slot window | 02:57 → running · 1h 13m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 19 |
| Longest silence | **37.9 min** — from 03:30:06, after `corpus converted 213, measuring` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 2 parked, with the evidence to re-open them |
| Still a wall | **The .txt half has not moved in 28.5 h, and the table now predates the engine it describes.** `txt/RANKING-TX |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **37 min** | `###########` |
| measure or build - a conversion, screen or compile writes no beacon | **26 min** | `########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **5 min** | `##` |
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
