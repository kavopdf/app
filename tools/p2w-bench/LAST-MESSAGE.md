# Fixer report - 2026-11-24 04:52

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 04:52 → running IST · 58 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **29** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **29** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:50 | **lead** | 0/None | Google lays a table row out on whole CSS pixels and truncates the fraction: a 168-twip row (11.2 px) renders at 11 px, 0.15 pt a row, 4.35 pt over 29 rows. Carrying the remainder across rows took 362_ |

## What the run did

`18_displacement` was the class. The charter's handover said to test whether Google lays a row at
`trHeight + rule` or `max(trHeight, content + rule)`. **Neither.** The question was wrong, and one
Google round trip on `362_price_list_dense` answered a different one.

**Google lays a table row out on whole CSS pixels and truncates the fraction.** The source's row pitch
is 8.40 pt; the document declares `w:trHeight 168`; 168 twips is 8.40 pt is 11.2 px, and Google
rendered 8.25 pt - exactly 11 px - on 27 of 27 rows. 0.15 pt a row, 4.35 pt over 29 rows, and the page
fails on a median 2.8 pt.

Three probes, each a hand edit of `w:trHeight` only, uploaded and exported through Google:

| declared | px | pitch Google rendered | check |
|---|---|---|---|
| 168 tw (8.40 pt) | 11.2 | **8.25 pt** (11 px) | 41/42 FAIL |
| 180 tw (9.00 pt) | 12.0 | **9.00 pt** (12 px) | 41/42 FAIL |
| 165/180 diffused | 11.2 avg | 8.25 and 9.00 mixed | **42/42 PASS** |

Snapping every row to a whole pixel is not the fix - it overshoots 0.6 pt a row and fails the same
check from the other side. **Carrying the remainder** is: snap the cumulative height, write each row as
the difference. Built into the engine, `ConvertOne` on that document alone, through Google again:

| | before | after |
|:--|--:|--:|
| `362_price_list_dense` | 41/42, `med_dy` -2.8, `worst_dy` 5.4 | **42/42**, `med_dy` -0.9, `worst_dy` 2.6 |

**That is a document going CLEAN in the renderer the user opens**, measured on the built engine and not
only on a probe. Nine other documents are one `18_displacement` from clean.

## Why it is not committed

Full corpus pass on the patched engine, 212 of 212 measured, against the committed table:

| | |
|:--|--:|
| documents worse | **17** |
| documents better | 5 |
| unchanged | 190 |
| worst | `electricity-bill` 1.33 -> **2.33** |
| over the gate's tolerance | `330_cad_drawing_sheet` 4.91 -> **5.22** |

LibreOffice does not quantise to pixels, so on that renderer the redistribution is pure loss: rows move
by up to half a pixel and nothing is gained, because the drift it corrects only exists in Google.
`regress.py --check` and `gate.py` both refuse, correctly. **The engine was reverted; nothing landed.**

Two narrower guards were tried and neither is the answer: `ruleTwHere == 0` still cost 17 documents
(`electricity-bill`'s rows draw no rule either), and adding `!exactRows` excluded the target document
itself, which is an `exactRows` table. The right discriminator is whether the table's row heights are
**uniform**, which needs a pre-pass over the rows that did not fit this slot.

`FINDINGS/18_displacement-GOOGLE-LAYS-A-ROW-ON-WHOLE-PIXELS-0052-fixer.md` carries the probes, the
patch, the cost table and the pre-pass the next run needs.

The txt corpus was re-scored on the patched engine before the revert: 213 scored, 0 newly clean, 0
newly failing, 213 unchanged. The change cannot reach a `.txt`, and that was measured rather than
argued.

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
| Slot window | 04:52 → running · 58 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **5.9 min** — from 05:08:37, after `corpus pass 3 + starting the Google round trip on 362` |
| Silences over 2 min | 13 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **13 min** | `#####` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **41 min** | `################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

NEXT RUN: (1) **THE MECHANISM IS SETTLED - do not re-derive it.** Google truncates a table row to whole
CSS pixels (1 px = 15 twips = 0.75 pt); 168 twips renders at 165, and the loss is per row and
accumulates. Three probes and a built engine agree. (2) The fix is the cumulative pixel snap, and it
works: `362_price_list_dense` 41/42 -> 42/42 in Google. (3) It is blocked on ONE thing - the LibreOffice
cost on 17 documents - and the discriminator is a **pre-pass that computes every row's `rowHeightTw`
before the first row is written, applying the snap only when they are all equal**. A uniform pitch is a
line grid whose total must be preserved; individually measured boxes are already where the page drew
them. (4) Measure `electricity-bill` and `330_cad_drawing_sheet` FIRST - they are the two documents that
carry the cost, and each is one convert and one score. (5) There is a second decision in the finding:
`18_displacement`'s tolerance is 1.5-4.5 pt, which is 2-6 px, so **no construct in the .docx can remove
a quantisation floor** on a long table. Either the check tolerates a pixel of accumulated quantisation
per page, or every long table with a fractional pitch is permanently unfixable. (6) The five ratchet
rows still need a corpus pass; the pass in this run measured 212 of 212 on the patched engine and its
numbers are in this report, not in the tables, because the engine was reverted.
