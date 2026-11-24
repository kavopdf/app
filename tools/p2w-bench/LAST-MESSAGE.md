# P2W Fixer - Run Report

**25 Nov 2026 · slot 01:24 → running IST · 36 min**

> One change was kept: the commit gate now runs on a cold pod. One lead, and the reason the
> thirty-one runs before this one could not land a measured engine change at all.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1 |
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
| Working on | `18_displacement` - taken from the pending list (16 still open), not a new class |
| Findings vs landing | **67** finding(s) on this class and **0** documents moved - writing is cheaper than landing, and nothing else says so |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 02:00 | **lead** | 0/None | row-pitch dither alone: ditherOn true, trHeight moves onto the 0.75pt grid (mobile-bill 360/380 -> 345/360/375); page result unmeasured because p2w.py --force measured stale docx (mtime 19:57 vs patch |

## What was kept - the gate, which is why nothing had been landing

The commit gate could not run on a fresh pod, so **no measured engine change could ever be
committed**. It refused four times in a row, each with a different message, because three
prerequisites are each documented in their own script and nothing called them in order:

| # | refusal | what was missing |
|:--|:--|:--|
| 1 | `corpus: could not be built (1) - no corpus PDFs found` | 208 of the 213 PDFs are release assets, not repository content |
| 2 | `no java on PATH and no JAVA_HOME` | the engine is Java; a fresh pod has no JDK |
| 3 | `ClassNotFoundException: ConvertAll` | nothing in the repo compiled `tools/engine-verify/out` |

`tools/p2w-bench/pod-prep.sh` is the missing caller: corpus-fetch, jdk-fetch, the four maven
jars, the AAR unzip, the stubs, then the engine with `ConvertAll` and `ConvertOne` - idempotent at
every step. `tools/install-gate.sh` now runs it before it writes the hook.

    before : REFUSED. This commit would land a regression or an unmeasured engine.
    after  : PASS - nothing got worse in both formats, and the table matches this engine.

Corpus fetched: **213 PDFs, 212 scored, 0 missing.** Corpus converted: **213 of 213 .docx**.
Every commit this run passed the gate.

## The class, and why this one

`classpick.py --leverage` puts **18_displacement at 39.6 CLEAN documents** - the largest single
lever, ahead of `00_page_count` at 22.0 and `60_text_column_right_edge` at 19.8 - and it is the
one class where a measured half-fix was already in the tree: the spacer split is in HEAD behind
the room guard, and only the row-pitch half was missing. Pending was not taken first, and that is
the deviation: 16 items are open, but they are long-standing blockers and ratchets, and none is
worth 39.6 documents.

## What the attempt did

Applied `patches/18-displacement-row-pitch-dither-ONLY.patch` - the dither alone, because the
patch's spacer hunk would delete HEAD's room guard (`DocxWriter.java:6092-6111`). It applies clean
and compiles. **The dither is not a no-op.** Instrumented the switch at `DocxWriter.java:6386`:

    mobile-bill                      rows=5/8/11  exactRows=true recut=false squeeze=1.0
    table-with-no-header-row         rows=26      exactRows=true recut=false squeeze=1.0
    two-tables-stacked-with-no-gap   rows=13      exactRows=true recut=false squeeze=1.0
    362_price_list_dense             rows=29      exactRows=true recut=false squeeze=1.0

The gate is open on all four and the `.docx` moves onto Google's 0.75 pt grid - `w:trHeight` on
`mobile-bill`:

| build | row heights |
|:--|:--|
| HEAD | 24 rows: **360 x15, 380 x9** (18.0 / 19.0 pt; 380 is off the grid) |
| + dither | 24 rows: **345 x15, 360 x6, 375 x3** (every value a multiple of 15 twips) |

## What could not be measured, and why that is the finding

`p2w.py --force --budget 240` printed `docx 0/213 -- converting 213` and compared 165 documents as
**0 worse, 0 better, 165 identical**. That null is false. `/scratch/work/p2w/out/mobile-bill.docx`
is stamped **19:57**; the patch landed **19:59** and the `--force` pass ran **20:06**. The same
document converted by hand at 20:29 with the dither on has 345/360/375 - the file the measurement
scored has 360/380. The pass converted a subset until its budget ran out, then measured the whole
corpus, scoring the not-yet-rebuilt files as measurements of the new engine. `docx 213/213` counts
files that *exist*, not files that were *rebuilt*.

**Every fixer run that changes the engine and measures through `p2w.py --force` can read the
previous build.** Same shape as the two instrument defects already in this directory, and it is why
a run reports "no change" instead of a number. It is worth more than 39.6 documents.

Engine reverted to HEAD; nothing unmeasured was committed.
`FINDINGS/18-displacement-DITHER-FIRES-BUT-P2W-FORCE-MEASURED-STALE-DOCX-2520-fixer.md`.

## Subagents

Two, both deployed in the first ten minutes and both used.

| agent | what it produced |
|:--|:--|
| `18_displacement patch audit` | verified every hunk against HEAD, found hunk 1 of both patches would delete the room guard, produced the dither-only patch that was applied. Also reported that `+0.70 pt/row` and `0.9634` appear in none of the supplied files - treat that factor as unsourced. |
| `Cold-pod gate prep` | produced `pod-prep.sh` and the `install-gate.sh` insertion - the six steps that unblocked the gate. |

## Next run

1. **Reproduce the stale reuse first.** `--force` on two documents, compare mtime and the
   `trHeight` list before and after, then fix the skip condition. No engine change is measurable
   until this is done.
2. Re-run this dither through a measurement known to be fresh. Falsifier, unmeasured: Google
   should take `table-with-no-header-row` 46/47 to 47/47 and `mobile-bill` 46/47 to 47/47, with
   `362_price_list_dense` and `two-tables-stacked-with-no-gap` unchanged, and `mobile-bill` and
   `insurance-policy-schedule` must not lose a page.
3. `pod-prep.sh` prints `java JAVA_TOOL_OPTIONS:` in its closing line - it parses the wrong field
   of `java -version`. Cosmetic, not fixed.

## Gates

    regress.py --check   PASS - nothing got worse in both formats, and the table matches this engine
    measure_gate.py      READY - every document measured (docx 212/212 scored)

## The txt

| | |
|:--|:--|
| Measured | **1.0 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 01:24 → running · 36 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 14 |
| Longest silence | **5.3 min** — from 01:54:39, after `measuring the corpus after the dither (chunk 5 retry)` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **0 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **10 min** | `########` |
| other - not attributed to a tool | **19 min** | `##############` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |


---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
