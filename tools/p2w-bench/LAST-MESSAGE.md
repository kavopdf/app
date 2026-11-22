
# P2W Fixer - Run Report

**23 Nov 2026 · slot 23:10 → running IST · 1h 29m**

> **The spacer split is worth 4 clean documents and costs 2. Reverted.** `18_displacement` is the largest single check in the corpus (38.7 clean documents by `classpick.py --leverage`) and 16 documents sit at 41/42 failing it and nothing else.

## What the 16 said

LibreOffice: `share5` identical to two decimals on every one of the 16. The `.docx` changed (that
document's table-top spacer went from `before="0" line="247"` to `before="227" line="20"`), so this is
exactly the asymmetry the split was built for: a construct LibreOffice does not measure and Google
does.

Google, one round trip each:

| document | before | after the patch |
|:--|:--|:--|
| `73_marksheet_subject_marks_grade` | 41/42 | **42/42 PASS** |
| `41_coloured_headings_white_bg` | 41/42 | **42/42 PASS** |
| `29_dot_leaders_txtpos` | 41/42 | **42/42 PASS** |
| `72_bank_statement_no_rules_right_amounts` | 41/42 | **42/42 PASS** |
| `22_invoice_four_columns_txtpos` | 41/42 | 41/42 — 21/71 runs out, med -2.76 pt |
| `16_right_aligned_amounts_txtpos` | 41/42 | 41/42 — 20/64 runs out, med -2.45 pt |

The whole corpus was then rebuilt with the patched engine (213/213 converted, 212 scored) and
`regress.py --check` passed: no document worse in `.docx` or `.txt`, google-safe clean. I committed
it.

## Then I tried to prove it wrong, and it was

A run that landed while I was measuring (23:54 slot) wrote that this patch's blocker is **scope, not
row height**, and that it costs two exactly-full pages. I Google-verified both of them at the same
engine, and then again with the patch removed — same hour, same corpus, one edit between them:

| document | patch | no patch |
|:--|:--|:--|
| `mobile-bill` | 43/47, **2 pages**, content lost | 46/47, 1 page |
| `insurance-policy-schedule` | 43/47, **2 pages**, content lost | 46/47, 1 page |

Not engine drift, not a stale baseline. Both pages are exactly full, so spending the gap at its true
value removes the ~19.5 pt of slack that was absorbing Google's row excess. The patch is reverted in
full — engine, `RANKING.csv`, engine stamp — and `regress.py --check` passes on the tree as it now
stands.


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
| 00:11 | **lead** | 0/3 | Row-height dither refuted (trHeight stored not laid); census of the 11 non-ruled docs = 3 faults; spacer needs a scope guard, handed to next run |
| 00:39 | **reverted** | 0/16 | spacer split lands 4 of 16 in Google (73_marksheet, 41_coloured, 29_dot_leaders, 72_bank_statement 42/42) but breaks mobile-bill and insurance-policy-schedule 46/47 one page -> 43/47 two pages in a co |
| 23:33 | **lead** | 0/None | Measured where Google's row-pitch charge lives: LibreOffice lays w:trHeight exactly and never charges the rule; Google charges the row's own rule and rounds to a whole point. A paragraph border is not |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two, both before my own attempt:

| Agent | What it answered |
|:--|:--|
| Explore - 18_displacement instrument | `18_displacement`'s `dy` is box-top against the **Google** export; `RANKING.csv`'s `*_pt` is nearest-ink against the **LibreOffice** render. Five independent differences - renderer, box vs ink, run-paired vs all pixels, signed vs unsigned, per-page vs worst-page - so the "max_pt 1.44-2.40 yet fails" comparison was never a comparison. It also showed branch `not ds` did not fire on any of the six, refuting SETTLED.md's own reading. |
| Explore - dead-ends dossier | 17 prior attempts at `18_displacement` and their verdicts, `60_text_column_right_edge`'s zero recorded attempts, and which hypotheses are refuted with the evidence line quoted. Its ranked recommendation - land the split and score all 16 - is what this run executed. |

## Timing

| | |
|:--|:--|
| Slot window | 23:10 → running · 1h 29m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **67.1 min** — from 23:32:40, after `relay: 4 of 16 solo-18 docs now 42/42 in Google; full-corpus measure f` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 07m** | `#################` |
| measure or build - a conversion, screen or compile writes no beacon | **15 min** | `####` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **6 min** | `##` |
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
