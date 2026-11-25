# P2W Fixer - Run Report

**25 Nov 2026 · slot 04:56 → running IST · 49 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **36** of the **187** re-measured on this engine - **4** of the 191 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **22** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (20 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:34 | **lead** | 0/None | instrument: the check read its background from get_drawings(), which on a Google export yields only the page-sized sheet fill, so behind was None on every run and the check returned 0 across 392 expor |
| 05:45 | **lead** | 0/None | Separated the two box-text knobs by measurement. The pair (gapcap 20000tw + zganchor=false) REGRESSES 65_two_col_full_width_figure_caption from share@5px 1.75 to 7.75 and max 8.6pt to 31.7pt, problem |

## The txt

| | |
|:--|:--|
| Measured | **54 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `invisible-text-blind-01` | is 25_invisible_text blind after the 24 Nov sheet fi | 05:20 | 05:45 | 25 min |
| `gapcap-risk-01` | which documents become worse if the gap-cap + zero-g | 05:20 | 05:45 | 25 min |

## Timing

| | |
|:--|:--|
| Slot window | 04:56 → running · 49 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **23.9 min** — from 05:09:12, after `pending.py: reading the pending gate` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **29 min** | `#################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| other - not attributed to a tool | **6 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

See "What landed", "What was refuted" and "Next run" below - written by this run, not the pending queue.

## What landed

**`25_invisible_text` can fail again.** The check measured its background with `get_drawings()`, and on a
Google export that yields exactly one fill per page - the page-sized sheet Google paints itself. So
`behind` was `None` on every run of every page and the check returned 0 across 392 exports. It was not a
strict check that happened to pass; it was a check that could not fail, and its 43 recorded failures were
a number nobody could move.

It now reads a 0.5 pt ring of rendered pixels immediately outside each run's ink box, grown only until it
holds 12 px and never past 1.5 pt, and **abstains** unless one colour covers 90 % of that ring. On 34 real
Google exports: 35 of 37 unchanged, 2 fail - `mutual-fund-statement` (0 to 4: a navy table header arrived
as a raster, so the white `Field`/`Value` is white on white) and `eway-bill` (0 to 3). Both confirmed by
eye. Stable across tolerance 0.04-0.12, purity 0.80-0.95 and 72/100/150 dpi. `test_checks.py` 44/44,
`regress.py --check` PASS, and an independent synthetic probe behaves: white-on-white gives 1 invisible
run, black-on-white gives 0.

The radius was never the knob. On `340_bill_of_lading` the ring reads 61 % black / 39 % white at 0.5 pt
*and* at 3.5 pt, because that run sits on a barcode - growing the radius only reaches further into the
neighbour. Uniformity separates a real defect from a neighbour; distance cannot.

**Honest cost:** those two documents were counted clean before. That is the instrument telling the truth,
not a document getting worse - but the clean count on those two drops, and whoever restamps should expect it.

## What was refuted

The previous run's handoff said: apply the pair, take it to Google on two documents, and if the trade holds,
ship it. The trade does not hold, and it fails on the first document anyone looked at.

| document | HEAD | anchor off | cap only | both |
|---|---|---|---|---|
| `65_two_col_full_width_figure_caption` (passes `18_displacement` today) | 1.75 / 8.6 pt | 1.75 / 8.6 pt | **1.75 / 8.6 pt** | **7.75 / 31.7 pt** |
| `policy-2col-spanning-section-heading` | 2.36 / 14.4 pt | **48.34 / 57.1 pt** | - | - |
| `27_two_column_left_short_txtpos` | 1.62 / 7.7 pt | - | 1.62 / 7.7 pt | 1.62 / 7.7 pt |

share@5px / worst case in pt, from `benchmarks/p2w.py:measure_doc`.

Box characters say the same from the other side: `65` goes 627, 627, 624, **0** across those four builds, so
it is only emptied when *both* knobs are on. The interaction, not either knob, reflows that caption -
consistent with its 25 separate anchored boxes. And on `policy-2col` the anchor's 3,046 to 49 drop is not
text rescued from a box: it is the two-column body losing its placement, 2.36 to 48.34. Reading a falling
box-character count as a gain is what made the pair look attractive.

**So: the anchor stays on, the pair does not ship, and the cap alone is the only knob with evidence.** It
zeroes `27`'s 57 box characters - the document already proven 40/42 to **42/42 in Google** under the pair,
where the anchor contributed nothing (57 to 57) - while leaving `65` bit-identical to HEAD.

## What this run could not do

21 of the 23 documents the cap changes have no position measurement. Two were measured, both benign, and the
cap's blast radius is a third smaller than the pair's 33. That is the gap the next run closes; it is not
evidence the cap is safe, and it must not be shipped as if it were.

## Next run

1. Apply `patches/gapcap-instrument.patch`, build with `-Dp2w.gapcap=20000`, `corpus-convert.py --force`, and
   take the **cap alone** to Google on `27` (stored verdict says 42/42) plus 3 of the 21 unmeasured carriers
   that currently PASS `18_displacement`.
2. Only then ship the cap as a default and restamp. The anchor stays on.
3. `65_two_col_full_width_figure_caption` is the regression witness for any future attempt to reflow
   full-width spanning captions. Never trade it for a box-character count.
4. The `:20 gverify` cron re-measures the 4 documents still on an older engine; the two new
   `25_invisible_text` failures arrive with it.

JVM note for whoever builds next: this pod's 2 GB cgroup cannot start a default JVM - it reserves 1 GB of
compressed class space and dies. `-Xmx700m -XX:CompressedClassSpaceSize=64m -XX:MaxMetaspaceSize=256m`.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
