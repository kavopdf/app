**22 Nov 2026 · fixer slot 13:56 → running IST**

> No document was made clean this run, and none was made worse. One measurement kills the lead the class
> has been carrying since 13:18: **the row-pitch ladder is whole points, so the "build 18.5 next"
> instruction cannot be followed — 18.5 does not exist.**

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

## The measurement

One build, one live Google round trip, **thirteen row declarations in a single document**
(`two-tables-stacked-with-no-gap`, declared 344 → 392 twips in 4-twip steps):

| declared (pt) | 17.2 | 17.4 | 17.6 | 17.8 | 18.0 | 18.2 | 18.4 | 18.6 | 18.8 | 19.2 | 19.4 | 19.6 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| **laid (pt)** | **18** | **18** | **18** | **19** | **19** | **19** | **19** | **19** | **20** | **20** | **20** | **20** |

**Not one laid pitch is a half point.** The 13:18 relay measured three points, called the ladder
18.0/18.5/19.0/19.5, and left "build 18.5 first" as the next instruction. Three points cannot tell a
0.5 pt ladder from a 1 pt one, and the ladder is 18 / 19 / 20.

Two consequences, both arithmetic:

- **`laid = round(declared_pt + 0.875)`**, where 0.875 is the row's own `w:sz="7"` rule charged on top of
  the declaration. Eleven of the twelve rows fit it exactly.
- **A source pitch of 18.40 pt cannot be declared to.** It rounds to 19 on every row, +0.6 a row, and the
  foot of a 13-row table lands 9.8 pt below where the page drew it. That is the whole of the check.

## What was built, and what it did

The quantisation cannot be removed, but it can be **spread**: declare one row a point short and the next
a point long, carrying the rounding error forward. Measured on a second live round trip:

| | HEAD | error-diffused |
|:--|:--|:--|
| foot of the table (source 316.7) | 326.5 (**+9.8**) | 317.5 (**+0.8**) |
| `23_line_pitch` | passes | passes, render now reads the source's own **18.4** |
| `verify_google` | 46/47 | **46/47 — the same single failure** |

92 % of the drift removed, and the document still does not clear `18_displacement`: one run is more than
twice its own tolerance out, on the single row the diffusion hands a 20 pt target to (it lays 21.0). That
is the next attempt, and it is written in HANDOFF so the next run starts at the build.

## What else this run found

- **`benchmarks/CENSUS.csv` is header-only — zero data rows.** The brief says to read it before forming a
  theory; it cannot be read. Not fixed here.
- **16 documents fail exactly one check and it is `18_displacement`** (12 at 41/42, 4 at 46/47) — the
  class's target list, written to `FINDINGS/18_displacement-SOLO-DOCS-16-142500-agentB.md`.
- **The engine's row floor is already `1.25 × size`, not absent** — so the 11:30 relay's "charge the
  budget `max(declared, 1.15 × size)`" two-line change is a no-op wherever a cell size is measured. Code
  map in `FINDINGS/18_displacement-ROWHEIGHT-CODE-MAP-142000-agentA.md`.

The engine is reverted; the change is `patches/18-row-pitch-error-diffused.patch`, because it moves every
ruled table in the corpus and a ratchet does not fit a slot. Three probe Docs and three staged `.docx`
were deleted after scoring; Drive root left empty.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Timing

| | |
|:--|:--|
| Slot window | 13:56 → running · 26 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 20 |
| Longest silence | **6.7 min** — from 13:57:47, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **20 min** | `#################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **2 min** | `##` |
| other - not attributed to a tool | **2 min** | `##` |

## One negative worth having

The engine's row floor is `1.25 × size` and Google's measured floor is `1.15 × size`, so lowering it looks
like the obvious second half of this fix. It was built: **the declarations did not move one twip.** The
row that lays 21.0 when the diffusion targets 20 is bound by its cell's paragraph spacing or a wrapped
line, not by the type floor. Written into the finding so nobody spends a round trip on it.
