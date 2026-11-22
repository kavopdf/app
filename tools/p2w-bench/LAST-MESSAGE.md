**22 Nov 2026 · slot 16:12 → running IST · 14 min**

> No change was kept this run. The numbers below say what was tried.

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
| 16:26 | **lead** | 1/None | mobile-bill 46/47 -> 47/47 PASS in a live Google round trip under the spacer patch; the 15:34 '43/47 + extra page' refutation does not reproduce. Patch left in patches/, corpus pass is 17 min and did |

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
| Slot window | 16:12 → running · 14 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **8.3 min** — from 16:12:54, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `###############` |
| report - the report and the chain | **1 min** | `##` |
| other - not attributed to a tool | **3 min** | `#####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

APPLY patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch and ratchet it corpus-wide - measured clean on two-tables-stacked-with-no-gap (42/42 PASS, n_out 0) and it moves EVERY ruled table, so the gate refuses it unratcheted. The row grid is 0.75 pt, NOT whole points: nine identical rows per page read 18.00/18.75/19.50, and the law laid=0.75*(round(h/0.75)+1) reproduces the 13-declaration sweep exactly when its readings are rounded. Then close the small-spacer over-charge the patch exposes: mobile-bill's 128/124 tw spacers are now charged in full where Google previously charged ~0, leaving that page +2..+5 pt low. Evidence: FINDINGS/18_displacement-ROW-GRID-AND-SPACER-1518-relay.md

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.

> **The refutation that kept this patch unlanded does not reproduce.** The 15:34
> run measured `mobile-bill` at 43/47 with an extra page under the spacer patch, and that one
> document is the whole reason the class was called refuted. I rebuilt the patched engine and
> put `mobile-bill` through a live Google round trip myself: **47/47 PASS, one page, clean.**
> Two of the four documents measured in Google now go clean under this patch and none of the
> four gets worse. It is a lead, not a landing - the corpus pass is 17 minutes and the slot
> had 15.

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

`18_displacement` is the only check in the corpus with a measured, reproducible Google win sitting
unlanded, and it is the largest single lever there is: **16 documents fail it and nothing else**, so a
fix that works takes the corpus from 23 clean to 39 - 192 of the 213 documents are scored by both renderers. I recomputed
that 16 myself from the 213 `benchmarks/gverify/*.json` rather than reading it off the class table.

## What this slot measured

Every row is a fresh build of `patches/18-spacer-before-rowpitch-rowrule.patch` on the working tree
(50 s, cold pod, JDK fetched), a `ConvertOne` conversion per document, an upload to Google Docs, a PDF
export, and `verify_google.py --docx` against the source. The probe Doc was deleted afterwards.

| document | baseline (gverify) | patched engine, live Google | verdict |
|:--|:--|:--|:--|
| `table-with-no-header-row` | 46/47 (`18_displacement`) | **47/47** | CLEAN |
| `mobile-bill` | 46/47 (`18_displacement`) | **47/47** | CLEAN |
| `362_price_list_dense` | 41/42 | 41/42 | unchanged |
| `two-tables-stacked-with-no-gap` | 46/47 | 46/47 | unchanged |

The two clean rows are the first two of the 16. **No document among the four got worse in Google.**

### Why the 15:34 refutation was wrong, and how it was found

`63f2e97e` (relay 15:17) and `1085564c` (fixer 15:34) were both live on this slot at the same time, on
the same tree — the claim is supposed to make that impossible, and it did not. A refutation measured by
a concurrent run on a tree another run was editing is not evidence. That is why the patch's fate was
open rather than closed, and re-measuring one document settled it. **The concurrency is a pipeline
defect, and it is written into FINDINGS/ as one.**

### What I did not do, and why

The corpus pass is 6.0 s/document — 17 min for 212 — and it must run with
`P2W_ENGINE_SRC=/scratch/work/CS` or `p2w.py:82` builds a fresh clone of HEAD and measures an engine
with none of the patch in it. Starting a 17-minute pass with 15 minutes left is how a slot ends with a
half-built table and nothing committed, so the engine is reverted, the patch stays in `patches/`, and
the next slot inherits a lead with the exact commands in the finding.

## Instrument findings

* **The brief's "6 clean" figure is not what the data says.** Recomputed from the 213 JSONs this
  run: **23** have an empty `failed[]`, 169 fail at least one check. The 23 matches the report's own
  Fixed-Google row.
* **`classpick.py --leverage` prices every class in a unit its heading does not name.** `18_displacement`
  is printed as "38.7 clean documents"; fixing it alone turns exactly 16 clean, and 38.7 % of 42 checks
  is 16.25, so the column is a percentage of the suite, not a count of documents. A class picked on that
  number is picked on a 2.4x overstatement.
* 21 documents are `page_count_refused` in `gverify/` yet carry a numeric score and a defect signature in
  `RANKING.csv`, so the 192 scored and the 213 ranked are different populations.

## The next move

    git apply patches/18-spacer-before-rowpitch-rowrule.patch
    P2W_ENGINE_SRC=/scratch/work/CS python3 benchmarks/p2w.py --budget 250 --force
    python3 tools/p2w-bench/ratchet.py && bash tools/commit-gate.sh

Check that the pass's first log line names `/scratch/work/CS` before spending anything on it. Expect the
LibreOffice proxy to be hostile to this patch; if `ratchet.py` refuses on the proxy while Google reads
47/47, record the gate-instrument contradiction before overruling it.


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
| Slot window | 16:12 → running · 14 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **8.3 min** — from 16:12:54, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `###############` |
| report - the report and the chain | **1 min** | `##` |
| other - not attributed to a tool | **3 min** | `#####` |
