# P2W Fixer - Run Report

**24 Nov 2026 · slot 11:54 → running IST · 1h 10m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **35** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:04 | **lead** | 0/129 | Uniform-pitch patch applied, built, all 213 converted on the patched engine; 129 of 212 measured in slot. Against RANKING.csv: 2 worse (404_sudoku_grid 0.27->0.49, 03_stamp_vertical_90deg 16.98->17.20 |

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two deployed, both landed with a finding that changed what I did.

* **Patch audit (pitch snap).** Verdict **NO-GO as evidence, not as mechanism**: the guard's own line
  `if (h % 15 == 0) continue;` exempts whole-pixel rows from the equality test, so a table of
  individually measured boxes is admitted as soon as one fractional height repeats three times — the
  exact class `GOOGLE-LAYS-A-ROW-ON-WHOLE-PIXELS` says must not be touched. It also proved the last
  row is written as `totalIn - done` and so is pushed OFF the pixel grid (168,168,168,240 ->
  165,165,180,234), contradicting the patch's own comment. This is why I did not treat the patch as
  pre-approved.
* **txt t12.** `t12_word_invention` is a real check on an unrepaired comparison: of the 8 carriers,
  2 are engine, 3 instrument, 3 undetermined. The token diff is computed at line 1410 and thrown
  away, so nothing can falsify the count. Ranked changes in `t12-verdict.md`.

## Timing

| | |
|:--|:--|
| Slot window | 11:54 → running · 1h 10m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 24 |
| Longest silence | **9.9 min** — from 12:48:05, after `measure pass 3` |
| Silences over 2 min | 13 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **6 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **43 min** | `##############` |
| record - attempt, handoff, class rows | **7 min** | `##` |
| other - not attributed to a tool | **11 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## What this run learned that it did not know before

**1. Every fresh-pod corpus pass in this pipeline's history was measuring nothing, and the cause was
one line.** `SOFFICE_BIN` named `/usr/lib/libreoffice/program/soffice.bin`. On this image that binary
exits 0, writes no PDF and never creates a profile — the `_soffice_warm()` fix of 21 Nov could not help
because the profile is never created at all. `/usr/bin/soffice` converts the same file in 3 s. With the
wrapper, the pass that had printed `measured 0 of 213` for four consecutive calls measured **163 of
212**. This is committed, and it is worth more than any one class: a run that cannot render cannot
measure, and it reports the failure as an empty table. (`FINDINGS/INSTRUMENT-soffice-bin-...`)

**2. The uniform-pitch patch is not the pre-approved thing the handoff said it was.** Its guard admits
a class its own evidence excludes, and its last row lands off the pixel grid. Measured on the patched
engine: **129 of 212**, of which **2 worse, 1 better, 126 unchanged**. The previous run recorded zero
worse on 200; I cannot reconcile that with mine, and the honest reading is that the two runs did not
share a renderer (see 1). (`FINDINGS/18_displacement-UNIFORM-PITCH-PATCH-129-OF-212-TWO-WORSE-1215-fixer.md`)

**3. A Google-free way to settle 2 costs three documents, not a corpus pass.** Re-measure the unpatched
tree on this pod with the wrapper on `404_sudoku_grid`, `03_stamp_vertical_90deg` and
`406_passport_mrz_page`. If the unpatched tree already reads 0.49 / 17.20 / 3.15, the delta is the
renderer and the patch is clean on 129. That is 3 documents and about 3 minutes.

## Next run

DO THIS FIRST, IT IS 3 MINUTES: measure `404_sudoku_grid`, `03_stamp_vertical_90deg` and
`406_passport_mrz_page` on the UNPATCHED engine (which is what main carries now) and compare with the
patched numbers in `FINDINGS/18_displacement-UNIFORM-PITCH-PATCH-129-OF-212-TWO-WORSE-1215-fixer.md`.
That single measurement decides whether the uniform-pitch patch is clean or regresses a grid.

Then, before re-running any corpus pass: the corpus is not in /scratch on a fresh pod and takes ~10 s to
fetch (`gh release download corpus-v1`), the engine builds in 57 s, and the pass runs **12 documents per
50 s** through `soffice_pdf`. 212 documents is therefore about 15 minutes of measurement plus about 20
minutes of conversion — budget a full pass as one job, not as an interruption.

PENDING FIRST: 23 item(s) you can close - run pending.py and take them in its order before the class below. 18_displacement: the uniform-pitch guard is measured on 200 of 212 corpus documents with zero worse in docx and txt and no construct spread - it is refused ONLY for an unstamped engine. Re-apply tools/p2w-bench/FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch, build, run the remaining 12 documents of the corpus pass (P2W_ENGINE_SRC=/scratch/work/CS python3 benchmarks/p2w.py --budget 275, repeat until measured 212/212), then regress.py --stamp, commit app/+RANKING.csv, attempt.py --class 18_displacement. The 12 unmeasured are the largest page counts, so order the pass by page count descending. Do NOT re-run the trHeight=max(content,line-15) probe.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
