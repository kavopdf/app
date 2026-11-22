# Fixer report - 2026-11-22 23:54

```
# P2W Fixer - Run Report

**23 Nov 2026 · slot 23:54 → running IST · 17 min**

> No document was made clean this run and none was made worse. The slot was handed a plan — land the
> table spacer **and** a row-height correction together — and spent itself proving the second half of
> that plan wrong before building it. **Google stores `w:trHeight` and does not lay it.** A dither on the
> declaration is inert in the renderer it was designed for and takes 0.75 pt off every row in the one
> that refuses it. What the spacer needs is a **scope**, not a row fix: one condition, not a rewrite of
> every table in the corpus.

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

## Why this class

`classpick.py --leverage` prices `18_displacement` at **38.7 clean documents**, nearly double
`32_stroke_lines` (23.3), and 16 documents fail it and nothing else. It carries the only lead in the
repository with a **proven document count**: the spacer construct is measured to take six documents to
42/42 in Google, and a seventh (`68_journal_wide_table_spanning`) at 10:35 once its 2880→4320 twip cap
was raised. No other class has a measured fix of that size sitting unlanded.

## What was measured

**The eleven non-ruled documents, counted for the first time.** Of the 16 that fail this check and
nothing else, 5 are ruled tables; the other 11 had never been looked at. They are **three** faults, not
one — 6 are the table gap spacer (the same term as the lead, and the same six documents), 2 are cell
line-box growth, 3 are a placement offset present in *both* renderers. The discriminator between the 11
and the ruled 5 is **who owns the rules**, not how many: all 11 emit `tblBorders` all-`nil` with rules
as floating `<w:drawing>`; the ruled 5 carry `insideH w:val="single"`. A rule-count filter is wrong on
two of the eleven.

**The row-height instruction, refuted before it cost a build.** A subagent fitted a 0.75 pt quantum law
to eleven published points (0.07 pt residual) and proposed a dither on `w:trHeight` to land the mean at
18.40. Two findings the repository already holds kill it: Google normalises `hRule="exact"` back to
`atLeast` on import and **stores the declaration while laying 18.0/19.0/20.0 on rows written 380**
(`18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` §1, §3), and the combined spacer+row build was
already run at 09:51–10:35 (`18_displacement-cellbox-REFUTES-ROWSCALE-1035-f1x.md`). The 0.75 quantum is
real, but it quantises the **cell's line box**, not the declaration — the law fits and the instrument is
wrong.

## The lead this run hands forward

The spacer as `w:before` is worth **seven** clean documents. It costs exactly the two whose page is
**already full** (`mobile-bill`, `insurance-policy-schedule`), because spending the spacer at its true
value removes the ~19.5 pt of slack that was absorbing Google's row excess. On a page with slack nothing
overflows.

So spend the spacer **only where the flow budget still has slack after the table** — `(page height −
table bottom) > 0.75 pt × rows` — and emit today's `w:line` everywhere else. `mobile-bill` and
`insurance-policy-schedule` then come out **byte-identical to HEAD**, so `regress.py --check` has nothing
to refuse and no construct two renderers disagree about is needed. One condition at the `spacerTw > 0`
branch, ~`DocxWriter.java:5870`.

The gate is unchanged: 124 documents carry a spacer and **13 of them are clean today** (largest:
`041122-Account_Opening_Form`, 22 spacers, max 166.00 pt). Render those 13 plus the 16, before and after.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two, deployed before my own attempt, on real problems and not greps.

| id | question | outcome |
|:--|:--|:--|
| census-01 | what do the 11 non-ruled `18_displacement` documents actually hold, and is it one construct | **landed** — three groups, not one; the discriminator is who owns the rules. `FINDINGS/18_displacement-ELEVEN-NON-RULED-IS-THREE-FAULTS-CENSUS-2354-fixer.md` |
| rowlaw-01 | why does Google lay 19.10 where the engine declares 18.0/19.0, and what declaration lands 18.40 | **landed, then refuted by this run** — a 0.75 pt quantum law fitted to 0.07 pt, whose recommended dither is inert because `trHeight` is not the height. Kept so the next slot does not fit the same curve. `FINDINGS/18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md` |

## Timing

| | |
|:--|:--|
| Slot window | 23:54 → running · 18 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **9.4 min** — from 23:54:49, after `reading state: handoff, leverage, pending` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **16 min** | `#####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

DO NOT apply patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch - measured LO-regressive by 21.5 points on two-tables-stacked-with-no-gap (FINDINGS/18_displacement-RELAY-PATCH-REGRESSES-LIBREOFFICE-1930-f1x.md). Start from FINDINGS/18_displacement-RULES-AS-PBDR-PITCH-FIXED-PLACEMENT-BROKEN-2330-fixer.md: the Google row-pitch charge is the row's OWN RULE and a paragraph border is not charged (Google mean 18.25-18.33 vs 19.08 with cell borders, source 18.40; LibreOffice identical to 0.05 pt). The bottom-border build fixes the pitch and breaks text placement (median dy -4.66 -> -10.70, n_out 55 -> 69). Next round trip: pBdr TOP per row AND nil the table's own top side (the C build drew 18 rules vs 15 because the table top was still drawn), then re-run the A/B on two-tables-stacked-with-no-gap. Census first: only five of the sixteen documents that fail 18_displacement and nothing else are ruled tables with a sub-point pitch - the other eleven are a different term.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
