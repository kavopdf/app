# P2W Fixer - Run Report

**21 Nov 2026 · slot 19:58 → running IST · 16 min**

> No change was kept. The rule carrier now DRAWS in Google for the first time - and it draws only
> one rule per document, because two floating tables stack under the first. That is the finding;
> the engine is back at HEAD.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 20:15 | **lead** | 0/210 | FLOATING-TABLE CARRIER BUILT AND MEASURED THROUGH GOOGLE, not landed. DocxWriter.ruleCarrier() turns a hairline shape into a one-cell w:tblpPr table with a w:tcBorders bottom edge. Measured on 73_mark |

## The one thing that changed in the render

`73_marksheet_subject_marks_grade` fails exactly `05_chars_extra, 18_displacement, 32_stroke_lines`
in Google and passes 42/42 in LibreOffice on the same engine. It carries two rules. Before this run
Google drew **0 of them**; with the carrier built this run it drew **2 of 2, at the requested weight
and colour** - and still read 39/42, because only the first floating table in a document is placed
at its `w:tblpY`. Rule 1 asked for 83.6 pt and landed at 83.5. Rule 2 asked for 793.6 and landed at
84.5, stacked one rule-thickness under rule 1. `w:tblOverlap w:val="overlap"` changed the bytes and
not the render; an inline carrier lost x entirely (both rules to x = 0).

Two other things are settled and cost nothing to keep:

* **A rule on this corpus is a FILL, not a stroke.** Both of that document's rules leave the writer
  as a filled 483 × 0.9 pt rectangle with `a:ln noFill` and `lineRgb = -1`. A carrier gated on "has a
  stroke colour" would have skipped every rule on the class's own document - which is probably why
  the earlier `w:pBdr` and cell-border attempts kept finding nothing to carry.
* **A table costs no character.** A four-case probe - a paragraph, a normal table with text, a
  normal table with an empty cell, a floating table with an empty cell - rendered through Google with
  **0** `U+200B`. So the two `U+200B` on `73_marksheet` are not the table: they sit at the two points
  where the carrier band overlaps running text. A carrier in white space may cost nothing at all.
  That is a hypothesis with one probe behind it, not a measurement.

## Why the class was taken

`classpick.py` suggested `32_stroke_lines` because it holds an open lead. The lead was worth taking
on arithmetic, not on the suggestion: `--leverage` prices the class at 36.3 clean documents, and a
census of the committed Google results (delegated, below) puts **35 documents** at clean if the
carrier clears `32` plus `05` and `18` - 15 that fail exactly those three, 15 that fail exactly
`32+05`, 2 that fail `32` alone, and 3 that fail only a subset of `05`/`18`. 41 of the 213, from
6. The construct was measured end to end through the renderer that matters before anything was
built into the engine, which is the part the last two runs did not have.

## Subagents

One agent, on the census above. It read all 426 committed verification files, reported the failing
set of every document, and - the useful part - flagged which Google/LibreOffice pairs were measured
on **different engine stamps** (13 of 35) and so are not controlled comparisons, and which carry no
stamp at all (8). Those 21 documents are the ones whose "it is clean in LibreOffice" claim has not
actually been established.

## What the next run should do

One floating table **per page**, holding that page's rules as rows: `tblpY` = the first rule's y and
each row's exact height = the gap to the next rule. Rows inside one table do stack, so that places
every rule at its own y with one band - and one wrap region, which is the `05_chars_extra` question
too. Before building it, one probe settles the ZWSP: draw a rule through a paragraph and a rule in
white space in the same document and count `U+200B` in the export.

Do not retry: the per-rule floating table (stacks, measured), the inline table (loses x, measured),
`tblOverlap` (no effect, measured).

## The txt

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **190** (89.2%) |
| Failing at least one check | **23** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Timing

## Timing

| | |
|:--|:--|
| Slot window | 19:58 → running · 16 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 13 |
| Longest silence | **9.6 min** — from 20:04:52, after `engine patched: hairline rule -> floating tblpPr carrier (ruleCarrier(` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **15 min** | `####################` |
| record - attempt, handoff, class rows | **1 min** | `##` |
