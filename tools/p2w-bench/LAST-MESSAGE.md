# Fixer report - 2026-11-22 10:20

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 10:20 → running IST · 26 min**

> No change was kept this run, and the run is not empty. Three constructs the last slots were
> steering towards were built and measured in Google and did not move a document; the audit that
> the brief asks for then found **three of this run's own five claims overstated**, and they are
> corrected in `FINDINGS/18_displacement-CORRECTION-1045-relay.md`. The engine is at HEAD;
> nothing in the corpus, the tables, the branches or the Drive was touched.
>
> What survives, narrowed: **on mobile-bill's 18 pt rows, `w:hRule="exact"`, `w:before` and the
> hairline `w:line` all produced a Google PDF identical rule for rule.** That is a fact about
> those rows. It is not a law, and the repository already holds two findings where an `exact` row
> of 72 pt and 55.8 pt *was* honoured — so the difference is row height, and the 09:51 reading
> ("Google lays the row at max(trHeight, content)") is the one this run failed to disprove.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| 10:37 | **lead** | 0/3 | Four constructs built and measured in Google; none moved a document, and the audit afterwards found three of this run's own five claims overstated (corrected in FINDINGS/18_displacement-CORRECTION-1045-relay.md). The one construct that reproduces the page's sawtooth - box at the row's height - needs |

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
| Slot window | 10:20 → 10:47 · 27 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 19 |
| Longest silence | **7.6 min** — from 10:39:18, after `report.py: building the report` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **3 min** | `###` |
| report - the report and the chain | **9 min** | `########` |
| other - not attributed to a tool | **13 min** | `###########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

DO NOT build the 0.9634 row scale or the hairline cell box for single-line cells - both measured inert. Build against rowParts>1: raise the row floor to the true 368 twips (the floor is quantised 8 twips low at 360) OR take w:before off the continuation paragraphs inside a wrapped cell. Google grows 360-twip rows to 19.0/20.0; source pitch is 18.40; mobile-bill rows 5-12 hold 6 w:p on 3 columns and render at 20.0 = 2.0 pt of growth. Prove on mobile-bill and insurance-policy-schedule FIRST - they are the only two documents blocking a spacer construct already measured to take 6 documents clean (68_journal 42/42 this run). Then land the spacer (w:before + hairline w:line=1 at 5868-5875, cap 2880->4320 at 5852,5866) with it.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.

## What this run measured, in Google

Four builds, four Google round-trips, and one synthetic probe. Each line is what a PDF or a read-back
showed, with the overstatements already removed.

| what was tried | what Google did |
|:--|:--|
| `w:hRule="exact"` on mobile-bill's 360/380-twip rows | exported PDF **identical** to `atLeast`, all 24 rows. Not inert in general - see below |
| `w:before` cut from 190-210 to 163-188 twips | exported PDF **identical** again |
| a probe sweeping `w:before` 5.0 to 17.0 pt on one 18 pt floor | all thirteen rows laid 19.0. **Not sensitive to the question**: every value tested fits under 19.0, so this says nothing either way |
| the hairline `w:line` (0.069 em) | Google's own `.docx` export returns it with a **changed value and `lineRule="auto"`**. The "14.4 pt substitute" this run first read out of that is **withdrawn** - under `auto` the attribute is 240ths of a line, not points |
| `w:trHeight` | Google **stores** 360/380 and exports them back unchanged, then lays 18.0/19.0/20.0 - on these rows |

**The one measurement that points anywhere.** A probe cell written `w:before="0"` with `w:line` equal
to the row's own height, floors 360/360/380, eleven rows, laid **18.00, 18.00, 18.75** - the page's
sawtooth, reproduced. One document, one font size, one column width, not repeated. It is a lead.

It still cannot land: a box the height of the row puts the baseline at `LINE_BASE` = 0.8 of the row
and this corpus draws at 0.5, and `before + 0.8 * box = 184` with `before + box = 360` has no
solution - it needs a box of 880 twips, taller than the row. **The row height and the baseline cannot
both come from one paragraph's `spacing`.** Built with `w:vAlign="center"` to lift the line, it cost
LibreOffice 47/47 to 45/47 on mobile-bill and 47/47 to 46/47 on insurance-policy-schedule, and was
reverted **unmeasured in Google** - so whether that pair fixes the class in Google is unknown and
must not be assumed.

## The corrections, because they matter more than the negatives

- `google_safe.py` carries **seven** `IGNORED` constructs, not one. No entry matches `w:line` or
  `lineRule`, which is the real and much smaller gap.
- `hRule="exact"` is **not** inert in general: `FINDINGS/32_stroke_lines-CELL-BORDER-HONOURED-1830-f1x.md:119,124-127`
  measures a 1440-twip `exact` row at 72.00 pt in Google, and
  `FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md:25,36-37` measures a 1103-twip one
  honoured. The engine's other row emitter already writes `exact` unconditionally at
  `DocxWriter.java:2161` and that document passes.
- The probe above cannot see `w:before`'s charge, and the "14.4 pt substitute" story contradicted it
  outright. Both withdrawn.

## The probe loop, so the next slot does not pay for it again

One document is four calls and about ninety seconds: `upload` to `GOOGLEDRIVE_CREATE_FILE`, then
`GOOGLEDRIVE_CREATE_FILE` with the Google Doc mime type into `KavoPDF-Verify`, then
`GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` to PDF, then `verify_google.py`. Two traps that cost time:
`upload` refuses a path under `/scratch/work` (copy to `/scratch/output` first), and
`GOOGLEDRIVE_FIND_FOLDER` returns 170 KB of JSON to tell you a folder id you then paste forever.
The loop reproduced the committed mobile-bill result, 46/47 with `18_displacement` alone, before it
was used to judge anything. That control is why the negatives are worth believing and the
overstatements were findable.

## Next run

**Do not build the 0.9634 row scale, the hairline cell box for single-line cells, `hRule="exact"` on
short rows, or a cut to `w:before`.** All four are measured not to move these documents, and the
09:51 handoff still recommends the first two.

The live question is the one the 09:51 run asked and this run could not close: **what makes Google lay
a row at `max(trHeight, content)`, and what is the content term at 18 pt?** The committed evidence
says a 72 pt and a 55.8 pt `exact` row are honoured and an 18 pt one is not, so the answer is a
threshold or a content height near 18-19 pt - and a probe that sweeps the floor from 300 to 1500 twips
on one cell is the cheapest way to find it. **That probe was not run.** It is the first thing to do,
and it is one Google round-trip.

If a construct is found, the second half is unchanged: the row height and the baseline cannot both
come from one `spacing`, so the lift has to come from a construct that is not a height. `w:tcMar` is
untried and unemitted anywhere in the engine - the audit confirms zero hits - and it is the cheapest
candidate.

Prove on `mobile-bill` and `insurance-policy-schedule` first: both fail only this check in Google and
both are 47/47 in LibreOffice, so either one going 47/47 is the whole signal, and a LibreOffice
regression is visible immediately. `68_journal` cannot be the first test - it already fails
`59_shape_anchor` there.

---

*The four negatives are from exported PDFs and from Google's own `.docx` export of the same
documents. The finding is `FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md`; the
corrections that narrow it are `FINDINGS/18_displacement-CORRECTION-1045-relay.md` and should be read
first. Five probe Google Docs were created and deleted; `KavoPDF-Verify` is empty.*

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.