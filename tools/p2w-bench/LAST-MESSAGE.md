# Fixer report - 2026-11-22 10:20

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 10:20 → running IST · 18 min**

> No change was kept this run, and the run is not empty: four constructs the last three slots
> were steering towards are now **refuted by measurement in Google**, and the one construct that
> does make Google lay the floor is built, measured and blocked on a second question with its
> arithmetic on the record. The engine is at HEAD; nothing in the corpus, the tables, the
> branches or the Drive was touched.
>
> The short version: **Google does not lay a table row at its `w:trHeight`.** It stores the
> number, exports it back unchanged, and lays something else. Every fix aimed at the row is
> aimed at the wrong object, which is why three slots in a row reverted.

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
| 10:37 | **lead** | 0/3 | Four constructs measured in Google and refuted (hRule=exact inert, w:before inert, trHeight stored but not laid, hairline w:line replaced by Google); the working construct (box at the row's height) la |

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
| Slot window | 10:20 → running · 18 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 14 |
| Longest silence | **3.7 min** — from 10:33:51, after `relay: scoring the Google-box cap in Google` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **3 min** | `#####` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **13 min** | `################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## What this run measured, in Google

Four constructs built and measured on the real renderer. Each one is a negative with a PDF or a
read-back behind it, so none of them has to be tried again.

| construct | what it was supposed to do | what Google did |
|:--|:--|:--|
| `w:hRule="exact"` where the floor binds | pin the row at the floor | **inert** - the exported PDF is identical to `atLeast`, rule for rule, on all 24 rows |
| `w:before` cut from 190-210 to 163-188 twips | keep content under the floor | **inert** - the exported PDF is identical again; a probe over before 5.0 to 17.0 pt on one floor laid every row the same |
| the floor itself | be the row's height | Google **stores** `w:trHeight="360"` and exports it back unchanged, then lays 18.0/19.0/20.0 and lays a row written 380 at 18.0 |
| the hairline `w:line` | be the cell's line box | **replaced** - written `w:line="10" lineRule="exact"`, read back from Google as `w:line="14.4" lineRule="auto"` |

The last one is the important one. `w:line` at 0.069 em is the box this engine writes into **every
single-line table cell in the corpus**, and it is a construct Google ignores. `google_safe.py` lists
only `w:position`. That list has a gap.

## The construct that works, and what blocks it

A probe table through Drive, cell written `w:before="0"` and `w:line` equal to the row's own height:
floors 360/360/380 laid **18.00, 18.00, 18.75** - the page's own sawtooth, reproduced, eleven rows
running. That is the floor binding at last.

It cannot be landed as it stands, and the reason is arithmetic rather than a bug. A box the height of
the row puts the baseline at `LINE_BASE` = 0.8 of the row; mobile-bill draws its cell text at 0.5 of
it. `before + 0.8 * box = 184` twips with `before + box = 360` has no solution - it needs a box of
880 twips, taller than the row. **The row height and the baseline cannot both come from one
paragraph's `spacing`.**

Built anyway with `w:vAlign="center"` to lift the line, and it cost LibreOffice: mobile-bill 47/47 to
45/47, insurance-policy-schedule 47/47 to 46/47. Reverted unmeasured in Google, so **whether that
pair fixes the class in Google is not known and must not be assumed.**

## The probe loop, so the next slot does not pay for it again

One document is four calls and about ninety seconds: `upload` to `GOOGLEDRIVE_CREATE_FILE`, then
`GOOGLEDRIVE_CREATE_FILE` with the Google Doc mime type into `KavoPDF-Verify`, then
`GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` to PDF, then `verify_google.py`. Two things that cost time:
`upload` refuses a path under `/scratch/work` (copy to `/scratch/output` first), and
`GOOGLEDRIVE_FIND_FOLDER` returns 170 KB of JSON to tell you a folder id you then paste forever.

The loop reproduced the committed mobile-bill result, 46/47 with `18_displacement` alone, before it
was used to judge anything. That control is why the four negatives above are worth believing.

## Next run

**Do not build the 0.9634 row scale, the hairline cell box for single-line cells, `hRule="exact"`, or
a cut to `w:before`.** All four are measured inert in Google; the 09:51 handoff still recommends the
first two and is wrong.

The open question is narrow: **a construct that sets the row's height without also setting the
baseline.** `w:tcMar` top margin on the cell is the cheapest untried candidate - a margin, not a
height, so it should lift the text inside a box at the pitch. One probe answers it, and the probe is
the table in `FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md`.

Prove on `mobile-bill` and `insurance-policy-schedule` first: both fail only this check, in Google and
in LibreOffice, so either one going 47/47 is the whole signal. Then `68_journal`, which also fails
`59_shape_anchor` and cannot be the first test.

---

*The four negatives are from the exported PDFs and from Google's own `.docx` export of the same
documents. The finding, with every rule position and every read-back, is
`FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md`. Five probe Google Docs were created
and deleted; `KavoPDF-Verify` is empty.*

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.