**22 Nov 2026 · fixer slot 17:00 → running IST**

> **`report.py`'s "Next run" was pointing the next run at a patch that makes a document twice as wrong
> in LibreOffice.** The 15:18 relay measured `SPACER-BEFORE + ROW-PITCH-DITHER` at **42/42 PASS in
> Google** on `two-tables-stacked-with-no-gap` and never measured it in the proxy. I applied it and
> measured: **share1 21.85 → 43.33, share5 0.77 → 30.01**. The dither rewrites `w:trHeight` on every
> ruled row of every table, and LibreOffice lays `w:trHeight` as a real height. That is not a proxy
> artefact to waive - nothing establishes the proxy is wrong there. Do not ratchet that patch.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:34 | **lead** | 0/8 | spacer->w:before built and screened in LibreOffice: mobile-bill 1.55 -> 1.74 (+0.19, WORSE), 16_right_aligned 0.00 -> 0.00. Corrects the 08:56 finding's claim that LO is blind to this construct; the c |
| 19:10 | **lead** | None/None | spacer gap SPLIT (w:before=G-20, w:line=20) is LO-identical on mobile-bill 43.87/1.55 and removes 8.7 of the 11.3 pt Google table-top step on two-tables-stacked (80.1->88.8 vs source 91.4); still 46/4 |
| 19:17 | **lead** | None/None | the ready relay patch (SPACER-BEFORE + ROW-PITCH-DITHER) regresses LibreOffice on two-tables-stacked-with-no-gap: share1 21.85 -> 43.33, share5 0.77 -> 30.01, measured with benchmarks/p2w.py measure_d |

## The class, and why this one

`18_displacement` is the only class where a single construct can turn documents CLEAN: **16 of the 21
one-check-away documents fail it and nothing else** (the other 5 split 2 `60_text_column_right_edge`,
2 `32_stroke_lines`, 1 `47_margins`). I re-derived that from `benchmarks/gverify/*.json` rather than
reading the table, because the table's `05_chars_extra` column is wrong - see below.

## Three things measured, and what each changes

**1. The spacer gap can be split instead of moved, and LibreOffice cannot tell.** `w:before = G-20`,
`w:line = 20` keeps the paragraph's height at `G` in any renderer that honours both attributes, while
Google - which charges `w:line` at ~0.22 of the written twips and `w:before` at 1.0 - receives the gap.
Measured: `mobile-bill` **43.87 / 1.55 → 43.87 / 1.55** (bit-identical, against the 1.55 → 1.74 the
08:56 attempt produced), and `two-tables-stacked-with-no-gap`'s table-top step **11.3 pt → 2.6 pt**
(80.1 → 88.8 pt against a source of 91.4). It still reads 46/47 because the per-row drift is a second
term. Patch and numbers in `FINDINGS/18_displacement-SPACER-SPLIT-1900-f1x.md`.

**2. Google Docs ignores `w:spacing` character spacing - and that is the engine's whole justification
model.** A five-paragraph controlled probe: spacing 20 tw and spacing 60 tw lay within **0.5 pt** of
each other; `w:jc=distribute` is a no-op; `w:jc=both` does not stretch a one-line paragraph. 22 of 213
documents carry the construct, and `60_text_column_right_edge` fails on exactly two documents
(`313_power_of_attorney`, `321_auditors_report`) that are justified prose: source widest line 538.6 pt,
render 480.1 pt, **identical text and identical line breaks**. Engine commit `4147d540` was validated
in the proxy only. `FINDINGS/GOOGLE-IGNORES-CHARACTER-SPACING-1915-f1x.md`.

**3. `05_chars_extra`'s 109 recorded failures are stale.** The check now strips U+200B (one per
`<w:tab/>`); the rows were written before that. Re-measured through Google:
`01_stamp_rotated_15deg_upright` **34/42 with 05 failing → 36/42 with 05 passing**. Two other
documents reproduced their recorded verdict exactly, so this is the check and not the engine. It makes
no document clean on its own - **no document fails 05 and nothing else** - but `classpick.py
--leverage` prices 05 at 21.2 clean documents off a table that is wrong for 109 rows.

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
| Slot window | 17:00 → running · 2h 18m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 26 |
| Longest silence | **29.8 min** — from 18:38:54, after `18_displacement: building LO-neutral spacer split (before=G-20tw, line` |
| Silences over 2 min | 9 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **30 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **1h 29m** | `##############` |
| record - attempt, handoff, class rows | **5 min** | `#` |
| report - the report and the chain | **4 min** | `#` |
| other - not attributed to a tool | **7 min** | `#` |
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

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
