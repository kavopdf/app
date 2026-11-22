# P2W Fixer - Run Report

**22 Nov 2026 · slot 22:58 → running IST · 36 min**

> No document was made clean this run and none was made worse. The class was not the question: **where
> Google's row-pitch charge lives** was, and it is now measured in both renderers. It is the row's own
> rule, and a paragraph border is not charged. The construct that follows from it fixes the pitch and
> breaks the text's placement, so it is a lead with a patch, not a keep.

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

## Why this class

`classpick.py --leverage` prices `18_displacement` at **38.7 clean documents**, nearly double
`32_stroke_lines` (23.3), and the census says **16** documents fail it and nothing else. The class was at
attempt 23, every one of them `lead`. That is the arithmetic reason to be here, and it is also the reason
to distrust the last 23 framings: all of them assumed the term to fix was the **declaration**
(`w:trHeight`, the ladder, the dither). It is not.

A source-only census this run, which nobody had done: of the sixteen documents that fail this check and
nothing else, only **five** are ruled tables with a sub-point row pitch — `mobile-bill`,
`insurance-policy-schedule`, `table-with-no-header-row`, `bus-timetable-station-left-times-right`,
`two-tables-stacked-with-no-gap`. The other eleven carry four horizontal rules or fewer on their page and
are a different term entirely. So the row-pitch construct's whole population is a quarter of the class,
and anyone spending a slot on it should know that before they start.

## The measurement: where the charge lives

Four synthetic tables of thirteen rows, one source pitch of 18.40 pt, each in its own document, one live
Google round trip each, LibreOffice measured on the same file.

| variant | LO laid | **Google laid** | mean |
|:--|:--|:--|--:|
| control: cell borders, `w:trHeight` 18/19 | 18/19 | 19,20,18,20,19,18,20,19,19,19,19,19,19 | **19.08** |
| control repeated in a second document | 18/19 | the same thirteen values | **19.08** |
| declare net of the rule | 17.5/18.5 | 18,20,18,19,18,18,20,18,19,18,18,20,18 | 18.62 |
| declare a constant 17.9 | 17.9 | 18.7 | 18.7 |
| line-driven, no `w:trHeight` | 18/19 | 19,21,19,21,20,… | 19.9 |
| cell borders at a quarter point | 18/19 | **no rules drawn at all** | — |
| **paragraph borders instead of cell borders** | 18/19 | 18,19,18,19,18,18,18,18,19,18,18,19 | **18.33** |
| **same, cell margins zero** | 18/19 | 18,18,18,19,18,18,19,18,19,18,18,18 | **18.25** |

Settled: **LibreOffice lays `w:trHeight` exactly and never charges the rule** — every variant above came
back to the declaration within 0.05 pt, which is why every "declare it a rule short" construct regresses
the proxy. **Google charges the row's own rule on top of the declaration and rounds to a whole point**:
+0.83 pt a row, +9.1 pt at the foot of thirteen rows, which is the whole of this check on a ruled table.
**A paragraph border is not charged** — the same rule, the same declaration, drawn inside the cells.
Refuted: thin cell borders, which Google drops entirely, losing the grid.

## The engine, A/B, on a real document

`two-tables-stacked-with-no-gap`, one tree, two builds, one live round trip each, LibreOffice on both.
The patch is 51 lines behind `-Dp2w.pbdr=true` and **inert by default** — `document.xml` byte-identical
with the flag off, verified.

| | LO rule positions | Google mean pitch | first rule (source 86.52) | Google dy | n_out |
|:--|:--|--:|--:|:--|--:|
| A — cell borders (HEAD) | 18.4/18.3/18.5 | **19.23** | 77.5 (−9.0) | −2.34 + 0.01414 y, med −4.66 | 55/72 |
| B — paragraph borders | identical to A, to 0.05 pt | **18.50** | **87.5 (+1.0)** | −11.90 − 0.00663 y, med −10.70 | **69/72** |

Both builds score **41/42, `18_displacement` the only failure**.

**The pitch half works and the placement half breaks.** B removes 0.73 pt a row of drift and puts the
table's top rule within a point of the page's where A was nine points high — and then the cell text does
not travel with the rules: median dy −4.66 → −10.70 and n_out 55 → 69. The rule moved from the row's box
edge to the paragraph's bottom edge, so the row grows below its text, and the engine places cell text at
`LINE_BASE` of the row pitch — an offset tuned to a box whose bottom edge was the rule. **Not kept**: worse
on the check it was built for, and the charter is that no document gets worse.

## What the next run does first

`FINDINGS/18_displacement-RULES-AS-PBDR-PITCH-FIXED-PLACEMENT-BROKEN-2330-fixer.md` carries the whole
measurement and both patches. The bracketed next round trip: emit the rule as **`w:pBdr` top**, not
bottom, so the row grows above the text, **and nil the table's own top side at the same time** — a
top-border build (C) was already converted and measured in LibreOffice and drew 18 rules where A drew 15,
at 58.05, 93.75, 105.45, 115.35, 132.75, because the table's own top rule was still drawn. That second
half is the only thing standing between C and a clean A/B.

Also corrected in `HANDOFF.md`: report.py's "Next run" was still telling every run to **apply the relay's
spacer-plus-dither patch**, which the 19:00 slot measured as regressive in LibreOffice by 21.5 points.
That instruction is now withdrawn in the handoff, with the finding that refutes it named.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

One, deployed before my own attempt: the row that lays 21.0 pt when the diffusion targets 20.0. It found
the cause in the model, not the declaration — `snapEdges` with `SNAP_TOL` of three points merges the two
stacked tables' rules at 252.12 and 254.12 into one edge at 253.12, so the second table's first row is
given a 20.0 pt band where the page drew 18.4. That is a second term on the same document and it is
recorded in the finding.

## Timing

| | |
|:--|:--|
| Slot window | 22:58 → running · 36 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 13 |
| Longest silence | **16.0 min** — from 23:17:45, after `attempt.py: recording an attempt` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **16 min** | `##########` |
| measure or build - a conversion, screen or compile writes no beacon | **14 min** | `#########` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **4 min** | `###` |

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl,
benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. The renderer measurements are this run's own
round trips, recorded in FINDINGS/.*
