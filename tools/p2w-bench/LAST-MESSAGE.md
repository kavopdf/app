**22 Nov 2026 · slot 16:12 → 16:29 IST · 16 min**

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
fix that works takes the corpus from 23 clean to 39, on the 192 of 213 documents that both renderers scored. I recomputed
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
| Slot window | 16:12 → 16:29 · 16 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 17 |
| Longest silence | **8.3 min** — from 16:12:54, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `#############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **2 min** | `####` |
| other - not attributed to a tool | **3 min** | `####` |
