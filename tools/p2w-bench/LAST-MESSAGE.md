# P2W Fixer - Run Report

**24 Nov 2026 · slot 07:12 → running IST · 9 min**

> **`25_invisible_text` was a check that read the paper.** A Google PDF export opens with a page-sized
> white rectangle and rasterises our bands into images, so white type on an orange band counted as
> invisible text. 48 documents failed it and LibreOffice passed all 48. Fixed and measured live in
> Google: **all 5 documents that failed nothing else are now 42/42**, corpus **29 -> 34** clean.

## Progress

| | |
|:--|:--|
| Document-moves this run | **5** — 3 attempt(s), 2 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **34** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **34** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 07:11 | **kept** | 2/5 | check read the page-white sheet instead of the band behind the run; 2 of the 5 single-check documents re-measured 42/42 in Google, at-risk document unchanged at 40/42 |
| 07:12 | **kept** | 5/5 | all five single-check documents re-measured 42/42 in Google on this engine after the check fix |
| 07:21 | **reverted** | 0/2 | A2's row declared one rule short is NOT LO-invariant: mobile-bill 104/112 lines moved up to -10.5 pt, electricity-bill 117/125 up to -10.0 pt; ruleTwHere is 10 tw not 15, and LibreOffice lays the decl |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 07:12 → running · 9 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **4.1 min** — from 07:13:44, after `report.py: building the report` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `######` |
| record - attempt, handoff, class rows | **1 min** | `###` |
| report - the report and the chain | **5 min** | `#############` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

NEXT RUN: (1) THE PREVIOUS PAIR IS REFUTED - do not spend a slot on it. content+rule==pitch and hRule=atLeast make a trHeight-only change a no-op, and a cell-level gap escapes fitPage/shaveToFit (FINDINGS/18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md). (2) The class is two disjoint halves: a spacer half (the step at each table top = 0.784 x the declared w:line of an unspendable spacer, confirmed on 4 of 4 documents) and a row half (+0.75 pt per row, 21.75 pt over 362_price_list_dense's 29 rows). (3) FIRST MOVE: one Google round trip on 362_price_list_dense with trHeight = max(content, line-15) on rows where line > content only - LO-invariant by construction, and it tells you whether Google lays trHeight+rule or max(trHeight, content+rule). (4) The 4 ratchet rows need one corpus pass (~40 min) - start the slot with it, do not end with it. (5) The 9 REOPEN rows in PENDING-AUDIT.md are decisions with evidence attached.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## Next run

**(1) THE CHECK WAS THE DEFECT, ON 5 OF THE 48.** The five documents that failed nothing but
`25_invisible_text` are 42/42 in Google. The other 43 still fail it and whether they are the same false
positive is **not measured** — the stamp case was proven by eye (band present, white on orange), the
rest were not looked at. One export each is the whole test.

**(2) AGENT A2'S LAW STANDS, ITS FIX DOES NOT — AND THAT IS THE USEFUL PART.** The law, fitted to every
committed Google number: `laid = 0.75 * round((max(trHeight, content) + rule) / 0.75)`, so `w:trHeight`
is a quantised **floor**. `362_price_list_dense` draws no rules (`rule = 0`), so it does **not** ramp
+0.75 pt/row and its foot drifts *negative* — the measured `med_dy` -2.8. **The carry-over's
"29 x 0.75 = 21.75 pt of pure ramp" is ruled-table arithmetic on an unruled table.** 362 cannot test the
row half; a ruled document can.

A2's one-line fix — declare the row one rule short at `DocxWriter:6468` — was **built and refuted in
this slot**: `mobile-bill` moved 104/112 lines up to -10.5 pt and `electricity-bill` 117/125 lines to
-10.0 pt in LibreOffice. The rule is 10 twips, not the 15 assumed, and LibreOffice lays the
**declaration** where it exceeds the content, so `max(P-r, P) = P` was wrong. Engine reverted,
`regress.py --check` PASS. This is the same wall `…WHOLE-PIXELS-0052` hit, reached from the arithmetic
instead of from a corpus sweep.

**(3) WHAT IS LEFT ON THE ROW HALF IS THE CELL'S CONTENT, NOT THE DECLARATION** (`:6403`, `:6786-6803`).
The row is as tall as the cell asks it to be, and that is the only place a change can move both
renderers together. Do not spend the next slot on `trHeight` again.

**(4) `18_displacement` is still 101 documents and still the class**; 14 documents fail nothing else —
the largest single-check group left. `60_text_column_right_edge` (5) is next.

**(5) The gates are clean.** `regress.py --check` PASS before and after every attempt,
`measure_gate.py` READY, `google_safe` could not check (no `.docx` output directory in this pod). The
kept change touches no emitted byte, only how a PDF is read.
