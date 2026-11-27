# P2W Fixer - Run Report

**27 Nov 2026 · slot 18:00 → running IST · 56 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **84** of 84 (100.0%) on 2 documents |
| Check-instances still failing | **0** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **45** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; kept change: 1 code commit(s) in this window, first: finding 27NOV: the cell-before shortfall reaches vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; .txt scored: RANKING-TXT says 214 vs corpus says 213 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **2** of the **2** re-measured on this engine - **210** of the 212 scored are still on an older engine, and **42** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 210 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **1** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (55 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 18:56 | **lead** | 0/None | cell-before shortfall: patch reaches the XML (w:before 170->136 tw on 74_balance_sheet, 317->254 on bus-timetable) but screen.py on 10 docs shows share5/median_pt/p90_pt bit-identical - share5's 5px t |

## Why nothing moved, in this run's own words

> Nothing was kept because the change cannot be certified by the instrument this repo gates on, and
> that is a measurement, not a shrug.
>
> The engine change is real and it reaches the output. The "raise a slightly-short cell" branch in
> DocxWriter.java wrote `before = rowHeight - cellBox` while the branch eleven lines above it writes
> `before = LINE_BASE * (rowHeight - cellBox)` and the file's own comment states the law
> `before + LINE_BASE*box = LINE_BASE*rowLine`. Rebuilt both ways from the same PDF, the emitted XML
> moves by exactly the arithmetic the branch predicts: `w:before` 170 -> 136 twips (-1.70 pt) on
> 74_balance_sheet_indented_subitems, 317 -> 254 twips (-3.15 pt) on bus-timetable.
>
> Then the repository's own instrument was asked, and it is blind. screen.py on 10 documents - the
> four the sub-agent named plus six controls chosen for the raise branch's scope - returned share5,
> median_pt and p90_pt IDENTICAL on 10 of 10. Not a small improvement: bit-identical. The reason is
> structural. The largest move available here is 6.6 px at 150 DPI and share5 counts ink more than
> 5 px from where the page drew it; a 1.70 pt move is 3.5 px, inside the threshold by construction.
> And median_pt did not move either, which means LibreOffice is not laying the cell line out from
> w:before at all.
>
> So regress.py --check can neither certify nor refute this construct. It would have said "no
> document worse" - true, and worth nothing. Committing on that is the 23 Nov mistake, so the patch
> is in PATCHES/18-small-dy-cellbefore.patch and the run stops at the one measurement that settles
> it: a Google render of 74_balance_sheet_indented_subitems at HEAD and at the patch, reading
> 18_displacement's dy off the export. That needs four Drive calls per document and a slot that
> budgets for it; this one spent its middle on the corpus conversion and had ~20 minutes left.
>
> The other two results are negative and cheap, which is what a slot is for. flowFromBox is not the
> second anchor site: its zero-gap branch is the wrong predicate and the guard there is worth one
> document of 214, so it was not landed. And the txt half's "a document got worse" is not a
> regression at all - one document was ADDED (Prakashan_Print_Fidelity_Handbook), none removed, no
> failed_ids changed: 205/213 -> 205/214 and 8 -> 9 failing with no document moving. The txt ratchet
> cannot tell a new document from a worse one, and a run that believes it will hunt a regression that
> does not exist.

## The txt

| | |
|:--|:--|
| Measured | **4 min ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **205** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

Two, deployed in the first ten minutes, both back inside the slot.

| agent | question | verdict |
|:--|:--|:--|
| 18 small-dy | which code site places a table cell's baseline, and is the small dy an ascent artefact or a displacement | **engine defect**, one branch, `DocxWriter.java` ~:7013. The identity `dy(bbox) = dy(origin) + (ascent_src - ascent_built)` holds to 0.0000 pt over 128 pairs; 31_times is the artefact side, 74_balance_sheet is the engine side. Committed as `FINDINGS/AGENT-18-small-dy-27NOV.md`. Its "+4 documents flip on LibreOffice" did not survive my own re-measurement. |
| flowFromBox | is `flowFromBox` a second anchor site, and does the foot-band guard transfer | **no, do not land.** Anchor points at :4512 and :4549 (guarded) and :4627 (unguarded), but the guard is the wrong predicate at :4627. Over all 214 PDFs / 573 pages: 1,042 anchor boxes, flowFromBox owns 25 (2.4%) on 18 documents; guarding its zero-gap branch changes 1 document of 214. Also corrected the brief's premise: there is no guard at the PAGE_POSITION_ON_ANCHOR emit site at all. Committed as `FINDINGS/AGENT-flowFromBox-anchor-site-27NOV.md`. |

## Timing

| | |
|:--|:--|
| Slot window | 18:00 → running · 56 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 33 |
| Longest silence | **37.4 min** — from 18:00:58, after `pending.py: reading the pending gate` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **1 min** | `#` |
| fix - diagnose and change the engine | **3 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **45 min** | `##################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| other - not attributed to a tool | **5 min** | `##` |

The unattributed row is 3 distinct beat(s) that matched no phase. They said:

- `both agents back; verifying the 18_displacement cell-before claim`
- `screening 10 docs: 4 predicted flips + 6 controls`
- `18_displacement -> lead`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
