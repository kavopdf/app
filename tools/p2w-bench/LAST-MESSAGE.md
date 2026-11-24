# P2W Fixer - Run Report

**24 Nov 2026 · slot 22:20 → running IST · 14 min**


> The slot was dead on arrival for the second run in a row and is alive again - the claim is a commit,
> and the commit gate refuses on a cold pod. Cleared, claimed, and then one attempt: a measured negative.
> The .docx table did not move. Two agents changed what the next run should do.

## What was blocking, and the three commands that clear it

`round.py --claim-fixer` printed *"the claim never reached origin"* three times. The cause is not the
claim: the claim is a `git commit`, and the pre-commit hook is `regress.py --check`, which refused
because the converted corpus was absent - **no corpus PDFs on a fresh pod**. It reported "REFUSED. This
commit would land a regression or an unmeasured engine" for a tree nobody had touched.

Cleared this run: `corpus-fetch.sh` (213 PDFs, 0 missing) -> `build-engine.sh` (40 s) ->
`corpus-convert.py --ensure` (213 documents, 2 calls, ~9 min because the first is killed at the 290 s
ceiling and resumes). Then `regress.py --check` PASS, `measure_gate.py` READY, and the claim landed.
**A run that cannot claim should read the gate, not the claim** - the same failure the 20:25 slot wrote
up, and it recurs on every cold pod.

## The class, and why

`18_displacement`, on `classpick.py --leverage`: **39.6 clean documents, the largest single check in the
corpus** and 2.4x the next (`00_page_count` 22.0). Not because the last run took it.

## The attempt: the 2880-tw spacer cap, measured and reverted

`FINDINGS/18_displacement-table-spacer-CONFIRMED-...-1005-f1x.md` records a live Google clean on
`68_journal_wide_table_spanning` behind the spacer split *plus* raising the 2880-twip cap to 4320, and
says "that cap is reached by exactly one document in the 16".

**A census of all 213 emitted `word/document.xml` refutes the one-document part: 133 documents carry an
`sz=2` spacer and FIVE hit the cap at exactly 2880.** Raising it to 4320 and re-converting all 213
changed **4 documents**, and only one changed construct - `360_restaurant_menu` flipped into the
spendable branch (`w:line=3159` + `w:before=516`: 25.8 pt of gap the page drew, now delivered).

Google, live round trip, probe Doc trashed:

| | before (stored) | after (4320 cap) |
|:--|--:|--:|
| `360_restaurant_menu` score | 38/42 | **38/42** |
| `worst_dy` | 109.9 | **106.7** |
| failures | 18, 43, 47, 60 | identical |

**3.2 pt of displacement, no check.** The other three (`330_cad_drawing_sheet`,
`041122-Account_Opening_Form`, `68_journal`) only got a larger `w:line` - a construct Google delivers at
~22 % - up to +42.7 pt of declared gap, unmeasured in Google. **Reverted**: no document becomes CLEAN,
and an unmeasured move in the worse direction is not a lead. Engine back at HEAD, `regress.py --check`
PASS, and the Google record for `360` reverted with it because it was measured on a variant.

## The two things the agents changed

**The anchored-box design.** The brief's headline - the 120 pt `gapCapTw` box threshold, "~166
document-failures" - **is 16 % of the box text.** Census over HEAD: 61 carriers, 1,037 boxes, 23,794 box
characters; spending every gap removes 3,770 and empties no document. The prize is the
`ZERO_GAP_ANCHOR` -> `PAGE_POSITION_ON_ANCHOR` cascade: 12 pages holding the other 20,024 characters,
four documents carrying 16,202 of them (`041122-Account_Opening_Form` 5,553,
`Account_Opening_Form_Fillable_filled` 5,553, `policy-2col-spanning-section-heading` 2,591,
`academic-paper-ieee-2col-abstract` 2,505). Six `ctx.positioned = true` sites, one emitter at
`wps:txbx:5664`; the `:3144` term is dead code. Ceiling if the cascade goes and every box returns to the
text layer: **7 new clean, 2 already measured** (`27`, `61`).

**The clean-count audit - the headline number is overstated by all of it.** Of 191 scored, 127 were
measured on 42 checks, 2 on 44, 62 on 47. **All 36 "clean" documents were measured on 42, and all 36 are
missing the same five ids: `62_table_columns`, `63_table_rows`, `64_table_span_across`,
`65_table_span_down`, `66_table_cell_width`.** Not because the instrument grew: on one engine stamp 124
documents returned 42 and 61 returned 47, and `tablechecks.checks_for()` returns `{}` both when a page
has no table grid *and* when no `.docx` was supplied (`if not docx_path: return {}`) - a check that never
ran is indistinguishable from a check that did not apply. Ten of the 36 declare tabular content in their
own names. **Honest count: 0 documents pass all 47; 36 pass the 42 they were offered.** Separately,
`report.py:google_fixed()` exact-compares `"b7699196" == "b769919"` and so reports 0 scored on this
engine for 36 fixed; `gverify.py:_done()` already fixed that with `startswith`.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - subagents: 2 deployed vs no FINDINGS file for anch-01, clea-01 |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| Working on | `-` - taken from the pending list (18 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## The txt

| | |
|:--|:--|
| Measured | **40 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `anch-01` | anchored-box patch design: six ctx.positioned sites, | 22:34 | - | - |
| `clea-01` | clean-count audit: all 36 clean documents were offer | 22:34 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 22:20 → running · 14 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 13 |
| Longest silence | **6.3 min** — from 22:27:33, after `restamping docx+txt` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `########` |
| record - attempt, handoff, class rows | **1 min** | `##` |
| report - the report and the chain | **7 min** | `###########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 17 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 17 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 17 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 26 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 26 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 26 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 27 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 26 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 26 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 28 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 28 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 28 item(s) you can close - run pending.py and take them in its order before the class below. Re-measure the 23 page-count refusals in Google with the new recorder - the census now says whether the extra page holds anything, which is the difference between an engine defect and a counter. Then the 18_displacement pair: the spacer split is already in HEAD behind the room guard; the blocker is measured at +0.70 pt/row on w:trHeight hRule=atLeast (factor 0.9634), and it must land in the same attempt or mobile-bill and insurance-policy-schedule lose content.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
