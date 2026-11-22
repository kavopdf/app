**22 Nov 2026 · relay slot 13:56 → running IST**

> One document was made clean this run, and no document was made worse. `two-tables-stacked-with-no-gap`
> went **41/42 → 42/42 PASS** in Google, `n_out` 55 → **0**. The cause was not the pitch everyone has
> been chasing for three runs: it was a **table spacer Google never saw**.

## Progress

| | |
|:--|:--|
| Document-moves this run | **1** — 2 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## The class, and why this one

`classpick.py --leverage` still prices `18_displacement` at **38.7 clean documents**, the largest step
in the table, and the census says 16 documents fail it and nothing else. The 13:18 slot left a measured
lead here, so this slot took the same class with a different question: not "what pitch does Google lay"
but "is the pitch the thing that is wrong".

## What this slot measured

**1. The declared→laid row map is a grid, and it is now exact.** A purpose-built probe - nine identical
rows per page, so the pitch reads to ±0.06 pt instead of the ±0.5 pt a rule-position read gives:

    17.00 → 18.00   17.40 → 18.00   17.80 → 18.75   18.20 → 18.75   18.60 → 19.50

`laid = 0.75 * (round(declared / 0.75) + 1)` - snapped to 0.75 pt, then one whole quantum added.
`hRule` and border weight do not enter it. It reproduces all three engine builds the 13:18 slot left,
which that run read as "the charge grows with the declaration": it does not. It is one quantum seen
through a 0.5 pt measurement.

**2. Diffusing the pitch onto that grid, alone, made two documents worse.** two-tables dy median
-4.66 → -9.43; mobile-bill -6.73 → -12.73. The reason is exact and worth more than the fix: at HEAD the
table's header lands at **dy -10.18** and the pitch error is **+0.7 pt/row** over 13 rows, so the two
**cancel** by the foot of the table. A pitch fix removes the compensation and leaves the step naked.

**3. The -10.18 pt step is the table spacer, and it was a no-op in Google.** The paragraph before a
table carried its height in `w:line=247` with `w:sz=2` and no run; Google charges `w:line` as
`(w:line/240) × lineHeight(face,size)`, so a 1 pt face was charged ~1.2 pt for a 12.35 pt gap. Moved to
`w:before` with a hairline `w:line=1` (the construct `calibrate.py` measured as honoured exactly).

**4. Together:**

| document | before | after |
|:--|:--|:--|
| `two-tables-stacked-with-no-gap` | 41/42, n_out 55, med -4.66, span 10.31 | **42/42 PASS**, n_out **0**, med +0.05, rms 0.64 |
| `mobile-bill` | 41/42, n_out 100, med -6.73, rms 2.05 | 41/42, n_out **39**, med +2.35, rms 0.54 |

## Why it is a patch and not a commit

It moves **every ruled table in the corpus**, so `commit-gate.sh` refuses it unratcheted - correctly,
and there is no override. It is in
`patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch`, and applying it plus one corpus
pass is the next run's first move. Every number above is a live round trip on this sandbox.

`mobile-bill` is **+2 to +5 pt low** with the patch, and the residual is the same construct
over-correcting: its two small spacers (128 and 124 tw) were charged ~0 before and are now charged in
full. That is the next lead in the class and it is one build away.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:42 | **kept** | 1/16 | table spacer moved from w:line to w:before (a no-op in Google, tables started ~10pt high) + row pitch diffused onto the measured 0.75 pt grid; two-tables 41/42 -> 42/42 PASS, n_out 55 -> 0 |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two Explore agents, both landed inside the turn (a scheduled run has no one to answer later):

* **A - the instrument.** `18_displacement` compares per **text run**, tolerance `clamp(0.35·size, 1.5,
  4.5)` pt, per **page**, and never cumulatively; a page fails at >max(2, 5%) runs out of band. It
  also established that `benchmarks/gverify/*.json` stores **no dy at all**, which is why every dy
  number in this repo comes from a live round trip and not from the table.
* **B - the engine.** `w:trHeight` at `DocxWriter:6318`, `atLeast`, no quantisation and no 360 floor;
  `rowEdge` from the cell rectangles at `Pdf2Word:7957`; **no `w:tcMar` top/bottom and no cell
  spacing** - which is why the +0.75 pt charge is a renderer constant and not our padding.

## Timing

| | |
|:--|:--|
| Slot window | 13:56 → running · 49 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **22.3 min** — from 14:23:17, after `report.py: building the report` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **22 min** | `##########` |
| measure or build - a conversion, screen or compile writes no beacon | **20 min** | `#########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **2 min** | `#` |
| other - not attributed to a tool | **2 min** | `#` |

## Next run

APPLY `patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch` and ratchet it corpus-wide -
it is measured clean on `two-tables-stacked-with-no-gap` (42/42, n_out 0) and it moves every ruled
table, so the gate refuses it unratcheted. Then close the small-spacer over-charge it exposes:
`mobile-bill`'s 128/124 tw spacers (6.4/6.2 pt) are now charged in full where Google previously charged
~0, leaving that page +2..+5 pt low - gate the spacer to gaps the page really drew (the 2 pt floor at
`DocxWriter:5852` is too low) or subtract the hairline advance. Evidence:
`FINDINGS/18_displacement-ROW-GRID-AND-SPACER-1518-relay.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md,
TIMELINE.jsonl, benchmarks/RANKING.csv - or measured this run by a live Google round trip. Never
remembered, never estimated.*
