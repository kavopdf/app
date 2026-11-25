# P2W Fixer - Run Report

**26 Nov 2026 · slot 01:25 → running IST · 23 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **42** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 6 vs ATTEMPTS.json history 3 |
| Document-moves this run | **0** — 6 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `59_shape_anchor` - taken from the pending list (22 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `59_shape_anchor` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 01:45 | **lead** | 0/0 | Live Google round trip on the 3 solo-59 documents + 2 passing controls. Shipped instrument reproduced 41/42 and identical source/render counts. All convictions are same-box, dy +3.2 to +3.65 pt; per-r |
| 01:47 | **lead** | 0/0 | Probe 2: rebuilt 52_one_cm_margin_wide_body.docx with w:hRule atLeast->exact on all 6 rows, rendered in Google. Byte-identical render to the twip (7 baselines identical, 59 source=18 render=15 unchang |
| 01:48 | **lead** | 0/0 | Probe 3: 52 rebuilt with all 37 w:lineRule exact->atLeast, rendered in Google. Document destroyed - 2 pages instead of 1, 23_line_pitch source 17.0 render 23.0, 18_displacement source=0 render=1. w:li |

## Verdict

**Nothing was kept, and nothing was broken.** No engine change, no instrument change: the tree that
produced every number above is the tree that was committed, and `regress.py --check` and
`measure_gate.py` both pass on it.

**What the run bought is a falsification, and it was not free.** Three documents (`351_omr_answer_sheet`,
`48_form_coloured_border_coloured_values`, `52_one_cm_margin_wide_body`) have been carried since 24 Nov
as instrument artefacts — "the check is wrong, `_same_object` is dead code, fix the check and they go
clean". Six live Google renders in this slot say otherwise:

* the shipped instrument reproduced the committed verdicts **exactly** (41/42, and the `source`/`render`
  counts to the unit), so the renders and the store are the same measurement;
* every conviction is the **same-box** branch — the rectangle Google drew is the source's rectangle
  within 2 pt, and the text inside it is 3.2-3.65 pt low;
* the per-run `dy` distributions **do not overlap** between failing and passing documents (failing p90
  +2.95 to +3.27 pt against passing max +0.74), so this is not a renderer offset wearing a check's name.

Wiring `_same_object` in would have changed **zero** convictions and left three documents failing while
looking fixed. That is the trap this run was sent to check, and the answer is that the check is right.

**And both fix candidates are now measured dead, on the same document.**

| probe | change | Google's answer |
|---|---|---|
| 2 | `w:trHeight hRule` atLeast → exact, all 6 rows | **identical to the twip** — 7 baselines unchanged, still 41/42, still `source=18 render=15` |
| 3 | all 37 `w:lineRule` exact → atLeast | **document destroyed** — 2 pages, `23_line_pitch` 17.0 → 23.0, `18` source=0 render=1 |

Source row pitch is 17.00 pt six times; Google's is 18.41 · 17.25 · 16.09 · 18.41 · 18.00 on six
identically declared rows — content-driven, because Google ignores `w:line exact` as a height on 8.5 pt
cell text, and that construct cannot be traded away because the page's layout depends on it.

**Three attempts, all `lead`, no document moved.** The honest state of `59_shape_anchor` is: three
documents, a real 3.2 pt displacement, the mechanism narrowed from "the check is wrong" to "the row
pitch is not expressible through any construct this engine can emit", and one named next test —
instrument `rowHeightTw` and the cell paragraph's `w:before`/`w:line` emission on `52` alone. If no
construct lays a fixed 17.00 pt row in Google, these three belong in a written waiver with these three
probes behind them, not in a fourth run's fix queue.

**Self-check, stated rather than hidden.** `report.py` reports one disagreement: `RUN.json`'s attempt
counter reads 6 against 3 in `ATTEMPTS.json`. The ledger is right — this run made three attempts — and
the counter increments by two on each `attempt.py` call. The counter is not edited by hand here; the
ledger and this report carry the real number.

## The txt

| | |
|:--|:--|
| Measured | **28 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 01:25 → running · 23 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 21 |
| Longest silence | **19.6 min** — from 01:25:43, after `gaps.py: reading the timeline` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **19 min** | `##################` |
| record - attempt, handoff, class rows | **3 min** | `###` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

`classpick --leverage` says six checks can make a document clean: `18_displacement` 25,
`60_text_column_right_edge` 6, `47_margins` 3, `59_shape_anchor` 3, `32_stroke_lines` 2,
`17_matched_runs` 1.

**Do not take `59_shape_anchor` as a check-side fix.** This run measured it three ways and the check is
right: the three solo documents carry a real 3.2-3.9 pt downward displacement inside a box Google
reproduces, and `_same_object` would not change one conviction. Both .docx constructs that could have
explained it are closed — `hRule` atLeast/exact render identically, and `w:line` cannot be relaxed
without destroying the document. Read
`FINDINGS/59_shape_anchor-IS-RIGHT-THE-THREE-SOLO-DOCS-ARE-3PT-LOW-0150-relay.md` before touching 59,
and if no construct lays a fixed 17.00 pt row, write the waiver rather than the fourth attempt.

**Take `18_displacement` construct A** (the refused table spacer, 7 documents, `68_journal` the proof
document) or `47_margins`. Both are engine-side; both have the leverage.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
