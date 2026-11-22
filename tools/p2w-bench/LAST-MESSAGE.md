**22 Nov 2026 · relay slot 13:18 → running IST**

> No document was made clean this run, and none was made worse. The product is a law: the map from a
> declared row height to the height Google actually lays, measured on a real ruled row in three live
> round trips. It kills the `+0.75 pt` constant the pipeline has been subtracting since 11:14, and it
> kills the `w:hRule="exact"` half of the construct before anyone builds it.

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

## The class, and why this one

`classpick.py --leverage` prices `18_displacement` at **38.7 clean documents**, nearly double
`32_stroke_lines` at 23.3. The census this slot took over `benchmarks/gverify/*.json` says why: of the
documents that fail exactly one check, **16 of them fail `18_displacement` and nothing else**. No other
check is one edit from 16 documents. That is the reason, and it is a measurement, not a preference.

Probe: `two-tables-stacked-with-no-gap` — one of those 16, one page, 13 ruled rows, source rule pitch
**18.40 pt** on every row. Same source PDF, three builds, three Google round trips.

| build | declared / `hRule` | pitch Google laid | score |
|:--|:--|:--|:--|
| HEAD, no patch | 360, 380 tw (18.0 / 19.0 pt), `atLeast` | 19.1 pt mean | 41/42 — `18_displacement` only |
| declared = source pitch, `exact` | 368 tw (18.40 pt), `exact` | 19.5 pt mean | 40/42 — `18_displacement` **and** `23_line_pitch` |
| declared = pitch **less the rule**, `exact` | 348 tw (17.40 pt), `exact` | 18.0 pt mean | 41/42 — `18_displacement` only |

## What this slot settled

**1. `w:hRule="exact"` at the page's own pitch is a regression.** 368 tw declared, 19.5 pt laid — 1.1
pt taller than declared and 0.4 pt taller than the `atLeast` build it replaced. `23_line_pitch` goes
from passing to failing. Retire that half of the construct.

**2. The declared-to-laid map is not affine, so 18.40 pt is unreachable.** 17.40 → 18.0 (+0.60),
18.00 → 19.0 (+1.00), 18.40 → 19.5 (+1.10). Laid pitches are always multiples of 0.5 and laid rule
positions sit on the half-point grid. The charge grows with the declaration; it is not the constant
`+0.75 pt` three runs have been subtracting.

**3. Declaring net of the rule is the closest reachable point and costs nothing.** 19.1 → 18.0 against
a source of 18.4, score unchanged, no document worse — which is exactly why it is a lead, not a fix.

**4. The next test is one round trip and it is bracketed.** The ladder is 18.0, 18.5, 19.0, 19.5.
**18.5** is 0.1 pt a row from the source, reachable between the 17.40 and 18.00 declarations measured
here, and lands `18_displacement` on a document that is one check from clean. Build that first.

The patch is `tools/p2w-bench/patches/18-row-pitch-net-of-rule-and-subpoint-grid.patch`; the evidence is
`FINDINGS/18_displacement-ROW-PITCH-LAW-135800-relay.md`. It is a patch, not a commit, because it moves
every ruled table in the corpus and the ratchet does not fit a slot.

## What was tried
 why this one

`classpick.py --leverage` prices `18_displacement` at **38.7 clean documents**, nearly double
`32_stroke_lines` at 23.3. The census this slot took over `benchmarks/gverify/*.json` says why: of the
documents that fail exactly one check, **16 of them fail `18_displacement` and nothing else**. No other
check is one edit from 16 documents. That is the reason, and it is a measurement, not a preference.

Probe: `two-tables-stacked-with-no-gap` — one of those 16, one page, 13 ruled rows, source rule pitch
**18.40 pt** on every row. Same source PDF, three builds, three Google round trips.

| build | declared / `hRule` | pitch Google laid | score |
|:--|:--|:--|:--|
| HEAD, no patch | 360, 380 tw (18.0 / 19.0 pt), `atLeast` | 19.1 pt mean | 41/42 — `18_displacement` only |
| declared = source pitch, `exact` | 368 tw (18.40 pt), `exact` | 19.5 pt mean | 40/42 — `18_displacement` **and** `23_line_pitch` |
| declared = pitch **less the rule**, `exact` | 348 tw (17.40 pt), `exact` | 18.0 pt mean | 41/42 — `18_displacement` only |

## What this slot settled

**1. `w:hRule="exact"` at the page's own pitch is a regression.** 368 tw declared, 19.5 pt laid — 1.1
pt taller than declared and 0.4 pt taller than the `atLeast` build it replaced. `23_line_pitch` goes
from passing to failing. Retire that half of the construct.

**2. The declared-to-laid map is not affine, so 18.40 pt is unreachable.** 17.40 → 18.0 (+0.60),
18.00 → 19.0 (+1.00), 18.40 → 19.5 (+1.10). Laid pitches are always multiples of 0.5 and laid rule
positions sit on the half-point grid. The charge grows with the declaration; it is not the constant
`+0.75 pt` three runs have been subtracting.

**3. Declaring net of the rule is the closest reachable point and costs nothing.** 19.1 → 18.0 against
a source of 18.4, score unchanged, no document worse — which is exactly why it is a lead, not a fix.

**4. The next test is one round trip and it is bracketed.** The ladder is 18.0, 18.5, 19.0, 19.5.
**18.5** is 0.1 pt a row from the source, reachable between the 17.40 and 18.00 declarations measured
here, and lands `18_displacement` on a document that is one check from clean. Build that first.

The patch is `tools/p2w-bench/patches/18-row-pitch-net-of-rule-and-subpoint-grid.patch`; the evidence is
`FINDINGS/18_displacement-ROW-PITCH-LAW-135800-relay.md`. It is a patch, not a commit, because it moves
every ruled table in the corpus and the ratchet does not fit a slot.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:29 | **lead** | 0/1 | Declared-to-laid row-pitch law measured on a real-shaped ruled row in Google, 3 round trips: declared 360/380 atLeast lays 19.1 pt, declared 368 (the source 18.40) with hRule=exact lays 19.5 and REGRE |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None recorded by the pipeline this run* — but one Explore agent was deployed and it
landed. It answered the vertical-position code path in full: `w:trHeight` at
`DocxWriter.java:6316` with the pitch taken from `rowEdge` at `:6132`, `pointKey` at
`PdfToWord.java:7700`, `w:pgMar` hardcoded to zero at `DocxWriter.java:2305`, and **no
`w:tblHeader` and no `w:headerReference` anywhere in the engine** — which is the mechanism
behind the 48–68 pt UNIFORM PAGE SHIFT the dy finding records on continuation pages, and a
separate, unbuilt construct. It ran inside the turn rather than in the background, so the
pipeline counted zero.

## Timing

| | |
|:--|:--|
| Slot window | 13:18 → running · 13 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 10 |
| Longest silence | **4.7 min** — from 13:18:54, after `gaps.py: reading the timeline` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `########` |
| fix - diagnose and change the engine | **4 min** | `########` |
| record - attempt, handoff, class rows | **0 min** | `##` |
| report - the report and the chain | **1 min** | `##` |
| other - not attributed to a tool | **1 min** | `##` |

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
