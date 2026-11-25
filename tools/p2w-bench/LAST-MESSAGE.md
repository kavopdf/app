
# P2W Fixer - Run Report

**25 Nov 2026 · slot 20:02 → running IST · 39 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **42** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (16 still open), not a new class |
| Findings vs landing | **71** finding(s) on this class and **0** documents moved - writing is cheaper than landing, and nothing else says so |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 20:36 | **lead** | 0/10 | `18_displacement` rank 1 - the census's top mechanism - falsified in Google on the worst document in the class. |

## The measurement, and what it killed

`FINDINGS/18-displacement-B-GROUP-CENSUS-25NOV-relay.md` ranks "Google lays a table row's pitch on whole
0.75 pt pixels while the engine declares twips" first, worth 54.8 clean documents. I tested it on
`320_balance_sheet_statutory`, the group-B document with the largest recorded ramp.

**The change.** `DocxWriter.table()` writes rows `<w:trHeight w:val="H" w:hRule="atLeast"/>` at the
page's own pitch. I rounded the row's border box (`H` + the drawn rule) up to a whole multiple of 15
twips and declared `H = snapped - rule`. Ceiling only, behind one constant.

**The declaration moved, verified from the .docx and not from the tool.** `w:trHeight` went 280 -> 292
twips on 16 rows, 260 -> 262 on 5; with the rule charged that is a 300-twip box, **15.00 pt**, which is
exactly the pitch the census recorded Google laying on this document.

**Google did not move.**

| `320_balance_sheet_statutory` | passed | `18_displacement` | `med_dy` | `worst_dy` |
|:--|--:|:--|--:|--:|
| before | 41/42 | FAIL | **+8.2** | **19.4** |
| after (box on the 0.75 pt grid) | 41/42 | FAIL | **+8.2** | **18.7** |

Both sides are Google's own layout of the same .docx: upload -> copy as a Google Doc -> export PDF ->
`verify_google.py`. 73 runs matched on both. `med_dy` is unchanged to the tenth of a point; `worst_dy`
moves by one snap on one row.

**Why it failed, and what is left.** `hRule="atLeast"` is a floor. Google lays
`max(trHeight, cell content + rule)`, and the cell content already exceeds the declaration, so raising
it is absorbed. The pitch Google uses comes from the cell's own lines - the census's **rank 2**, which
it could not separate from rank 1 on ten points. That is now the only live candidate, and the
discriminating probe is in the finding: a cell whose declared `w:line` is already a whole multiple of
15 twips. If Google still drifts, `w:lineRule` is not honoured on import and the lever is not a number.

This satisfies the census's own stated falsifier for rank 1, which said a document whose row box is
already on the grid and which still ramps would mean the pitch is not the lever. That document now
exists. The patch is reverted, not left in the tree: it moves nothing in Google and adds up to 0.7 pt a
row in LibreOffice, which is regression risk for no gain.

## Next run

Do not re-derive the row snap. Read
`FINDINGS/18-displacement-ROW-SNAP-FALSIFIED-25NOV-fixer.md`, then probe `w:lineRule="exact"` on a
single cell before touching the class again. `18_displacement` is still worth 54.8 documents and is
still the class to take - but rank 1 is spent.

## Subagents

One, on the engine code: it produced the patch specification and corrected the site (group B goes
through `table()`, not `columnPage()`), which is why the experiment was one compile and one conversion
rather than an hour of guessing.

## Honest limits

The corpus was mid-build when the slot ended (169 of 213 converted on the old engine, then 213 to go
again on the patched one), so `regress.py --check` was never run on the patched tree - it was not needed,
because the patch is reverted and the tree carries no engine change. Nothing is committed to `app/`.

## The txt

| | |
|:--|:--|
| Measured | **45 min ago** |
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
| Slot window | 20:02 → running · 39 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 15 |
| Longest silence | **14.6 min** — from 20:02:51, after `pod-prep: warm pod, installing hook` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **30 min** | `#################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **5 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. classpick --leverage picks the class; six checks can make a document clean (18_displacement 25, 60_text_column_right_edge 6, 47_margins 3, 59_shape_anchor 3, 32_stroke_lines 2, 17_matched_runs 1) and they are weighted 3x over the 34 that cannot. Read pending.py first, then take the class it gives.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
