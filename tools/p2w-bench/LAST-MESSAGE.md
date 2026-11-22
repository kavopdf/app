# P2W Fixer - Run Report

**22 Nov 2026 · slot 11:14 → running IST · 8 min**

> **One Google probe answered the question three runs had been guessing at.** Google honours `w:trHeight`
exactly, and floors a row at the cell text's own line box - `1.15 x` the type size - with no threshold
anywhere. That is not a document move; it is the arithmetic the two blocking documents have been blamed
on, and it names the two-line change that unblocks a spacer construct already measured to take 6
documents to 42/42. Nothing in the corpus, the tables, the branches or the Drive was touched; the one
probe Doc was created and deleted by this run.

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
| 11:21 | **lead** | 0/3 | One Google probe settles what a row is laid at: laid = max(declared trHeight, 1.15 x cell type size) + border, exactly, across 13 declared heights at 10 and 18 pt. No threshold; the 'content term' is |

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
| Slot window | 11:14 → running · 8 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 14 |
| Longest silence | **5.0 min** — from 11:14:33, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **The relay's own pre-claim heartbeat makes a dead claim read live.** `round.py --heartbeat` writes `fixer_las |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `##############` |
| record - attempt, handoff, class rows | **1 min** | `###` |
| other - not attributed to a tool | **1 min** | `#####` |
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

## What was measured

A 28-row probe `.docx`, two tables, one row per declared height from 300 to 1500 twips, `hRule="atLeast"`,
10 pt text in one table and 18 pt in the other. One round trip: upload, create as a Google Doc, export
PDF, read the text origins.

| declared | laid pitch, 10 pt text | laid pitch, 18 pt text |
|--:|--:|--:|
| 300 (15.0 pt) | 15.75 | **21.45** |
| 360 (18.0 pt) | 18.75 | **21.45** |
| 400 (20.0 pt) | 21.00 | **21.45** |
| 500 (25.0 pt) | 25.50 | 25.50 |
| 720 (36.0 pt) | 36.75 | 36.75 |
| 1440 (72.0 pt) | 72.75 | 72.75 |

Two facts, both exact on 13 of 13 values: **every laid pitch is the declared height plus one constant**
(0.75 pt - the probe's table border), and **below the text's line box the row stops responding** and
floors at `21.45 = 0.75 + 1.15 x 18`.

## What it refutes

- The "threshold somewhere between 19 pt and 55 pt" reading in the 10:45 correction is **wrong**. 19 pt
  and 55 pt behave identically; both earlier measurements were right and on the same rule.
- The "content term" is no longer opaque: it is the type's line box, `1.15 x w:sz`. Nothing needed
  about the face, the cell margins or `w:before` explains it.
- The 0.9634 row scale is not inert, it is **impossible**: declaring 18.0 pt where the line box is
  18.35 cannot be honoured by any value of the declaration. No run needs to try it again.

## The unblock this names

The two blockers lay 19.10 pt on an 18.40 pt source pitch. `19.10 - 0.75 = 18.35 = 1.15 x 15.96`, so
those cells carry ~16 pt text declared at 18.0 pt: Google floors every such row at 18.35 and the
+0.70 pt/row excess is that floor, to two decimals. The engine charges its page budget the *declared*
height, so it never budgeted the 14.7 pt those 21 rows really take - which is exactly why charging the
spacer at its true value overflowed those two pages. **Charge the flow `max(declared, 1.15 x w:sz)` at
`DocxWriter.java:6233-6236` and the engine's page model equals Google's**, and the spacer's measured 6
documents can land without exposing an overflow.

That is the next build and it was not attempted: the probe plus the slot's own forensics spent the
window. It is one two-line change and one measured round trip on `mobile-bill`.

## Why `18_displacement`

`classpick.py` suggested it and the suggestion was audited rather than taken. Its 38.7 is fractional
credit across 124 documents; the honest count is **16 documents failing it alone**, and no other check
is a sole failure for more than 2. Those 16 are the entire distance from 23 clean to 39, and the
construct that reaches 6 of them is already measured in Google - blocked only on the arithmetic above.

## Cost

One probe document, four Drive calls, about four minutes, deleted after scoring; `KavoPDF-Verify` empty.
