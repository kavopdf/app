# P2W Fixer - Run Report

**25 Nov 2026 · slot 18:03 → running IST · 1h 03m**

> The gate was the work this run: a cold pod made every commit cost 4m40s and time out, so the corpus
> was built, the gate now passes in 32 s, and two read-only investigations root-caused the three
> largest open classes. **No engine byte changed, so no document moved.** That is stated as a failure
> to move documents, not dressed up as progress.

## Progress

| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (16 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **202** (94.8%) |
| Failing at least one check | **11** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t02_position` - 4 documents |

## Subagents

Two deployed in the first ten minutes, both `background=true`, both read-only, neither touched a repo file.

| agent | question | what it returned | duration |
|:--|:--|:--|--:|
| Explore 18_displacement root cause | Which construct produces 18, and is the proven lever reachable? | The three constructs with file/method/line at HEAD; the check's exact tolerance `clamp(0.35*size, 1.5, 4.5)` pt with `TAIL_FACTOR = 2.0`; **and the correction that kills the lever: all 25 solo-18 documents are single-page, so a section top margin cannot reach one of them** | 7 min |
| Explore 60 and 59 root cause | What emits the column-edge and shape-anchor failures? | 60-P built and measured in LibreOffice (column edge -42.09 to +0.38 pt, 42/42 on five documents) with its Google assumption named and untested; **59's `_box_moved` lacks a position term - every one of the 332 real boxes flips True to False when it is added**; counts corrected to 64 fail 60 and 52 fail 59 at HEAD | 25 min |

## Timing

| | |
|:--|:--|
| Slot window | 18:03 → running · 1h 03m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **33.1 min** — from 18:04:11, after `pending.py: reading the pending gate` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **49 min** | `#################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **3 min** | `#` |
| other - not attributed to a tool | **9 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 15 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. FIRST ATTEMPT: add the drawnByAppearance(apDrawn, ...) guard to the annotationRuns loop in PdfToWord.pageText() (~line 956) - its sibling loop at line 947 already has it. Measured on one document: 600_reviewed_invoice_with_annotations goes 20 tokens/83 chars -> 7 tokens/30 chars, paragraphs 14 -> 13. Needs the 213-document docx ratchet before it lands. SECOND: the (Authorised signatory) duplication on 041122-Account_Opening_Form and Account_Opening_Form_Fillable_filled is a table-row/paragraph overlap, a different construct, and clearing it closes the last 2 txt documents that are not the annotation one. THIRD: _ensure_scipy() should refuse rather than warn, and p2w.py:1112 must not swallow the scipy.ndimage import - see FINDINGS/SCREEN-HANG-IS-SCIPY-NOT-SOFFICE-25NOV.md.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## What this run did, and why nothing moved

**The obstacle that ate the slot, and the fix.** `install-gate.sh` timed out at 300 s on the first call.
`pod-prep.sh` explains why: the gate's `regress.py --check` builds the 213-document corpus itself in
240 s slices, so on a cold pod the commit exceeds the call limit and reads from outside as "REFUSED.
This commit would land a regression" on a tree nobody touched. Four `corpus-slice.py` calls fixed it -
148 to 95 to 60 to 1 to go, **213 converted, stamp written for engine `981ff1fa35e2cf67`** - and the gate
then passed in **32 s**. Both gates now pass on a clean tree: `regress.py --check` "no document worse
than baseline" in both formats, `measure_gate.py` "READY - every document measured".

**The finding that decided the attempt.** `18_displacement` is worth 54.8 clean documents and its only
Google-proven lever is `w:pgMar w:top` carrying the page-top gap (`bank-statement-5-pages` 37/42 to
40/42). Re-verified at HEAD: **all 25 documents that fail 18 alone are single-page.** A section margin
needs a second page top to place itself on. The lever is proven and it cannot reach a single document it
was chosen for. Predicted value if landed: about fifteen documents improved by one to three checks and
**zero new clean documents**. That is a ratchet, not a fix, and it was not landed under a slot with no
time left to re-measure the corpus after an engine edit.

**What did land:** one committed FINDINGS file, `18-60-59-THREE-CLASSES-ROOT-CAUSED-AND-THE-LEVER-THAT-
CANNOT-REACH-1900-fixer.md` - the three constructs with HEAD line numbers, the refutation table for the
four dead levers, the 59 position-term tripwire, 60-P's measured local result and its untested Google
assumption, and the corrected counts. Commit `d7e71192`, through the gate.

## Next run

Warm pod, 32 s gate, corpus stamped. Take these in this order:

1. **59-C first - check side, no engine rebuild.** `_box_moved` (`verify_google.py:2318-2596`) compares
   extent and never position; adding the position term flips every one of the 332 real boxes True to
   False and takes `59` from **2/45 to 44/45** on the recorded population. Worth 15.1 clean documents
   and the cheapest large move on the board. It is an instrument change: commit it with the fingerprint
   moving and the corpus re-measured in the same slot.
2. **Falsify 60-P in one Google round trip** on `302`: does Google honour `w:jc="distribute"` on a
   one-line paragraph, or normalise it to `both`? Everything in the patch rests on that and no run has
   asked Google. The local result is real: -42.09 to +0.38 pt, 42/42 on five documents.
3. **The sectPr margin patch last**, as a scheduled ratchet, never as a fix - see the FINDINGS file.

Do **not** retry: spending the refused spacer in `w:before` (refuted, `68_journal` 41 to 40/42), the
`w:trHeight` dither (0 of 13 moved), the 1x1 `trHeight` row (5 to 6 pages, 33/42), or 59-S (shape
populations identical, 9/9 and 6/6, boxes to 0.07 pt).
