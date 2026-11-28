# P2W Fixer - Run Report

**28 Nov 2026 · slot 04:58 → running IST · 8 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - kept change: 1 code commit(s) in this window, first: chore: claim bookkeeping vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; run window: RUN.json says this run began at 04:58 vs TIMELINE.jsonl records the claim at 04:00, so the window was reset and the duration is short |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (62 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> For four slots (26, 27 and 28 Nov) every fixer run ended "nothing kept", and each wrote it up as a
> slot that ran out of time. It was not time. `.git/hooks/pre-commit` runs `regress.py --check`, that
> command compared all 213 documents against the 15 Nov baseline, `main` itself carries 84 documents
> worse than that floor, and so the hook refused an engine fix, a tools file, a findings file and the
> run's own report alike. Nothing could be paid down, because paying down required committing.
>
> `regress.py` now compares per commit, which is what the rule was always for:
>
> | at HEAD | the rule now |
> |:--|:--|
> | document at or above its 15 Nov baseline | keeps that absolute floor, any movement up refused, exactly as before |
> | document already worse than baseline (the debt) | may improve freely, may not get worse than its last measurement - the ratchet, unchanged |
> | document missing from the table | still refused |
>
> The debt stays on the books and is printed on every check. It cannot grow and it cannot deepen. The
> Google veto and the .txt comparison are untouched. Falsified in `tools/p2w-bench/gate_debt_test.py`,
> 6 of 6: a clean document moved up is refused, a debt document moved up is refused, a debt document
> improving passes. Written up in
> `FINDINGS/GATE-FREEZES-THE-DEBT-INSTEAD-OF-REFUSING-THE-TREE-28NOV-relay.md`.
>
> Two other things had to be true for the gate to pass at all, and both were checked rather than assumed:
> the converted corpus was completed from 181 to 214 `.docx` (`corpus-slice.py`, stamp written), and the
> `google-safe` mark was re-based from 213 to 214 documents because the corpus gained
> `Prakashan_Print_Fidelity_Handbook`. Every construct's document count rose by exactly one across that
> re-base, so no existing document gained a construct.
>
>
> | agent | question | answer |
> |:--|:--|:--|
> | A | of the 84, how many pass every applicable Google check? | ten - `mobile-bill`, `electricity-bill`, `insurance-policy-schedule`, `73_marksheet_subject_marks_grade`, `33_sans_nondefault_body`, `36_embedded_subset_font`, `16_right_aligned_amounts_txtpos`, `41_coloured_headings_white_bg`, `29_dot_leaders_txtpos`, `362_price_list_dense`. The other 74 fail at least one, and `18_displacement` is in 59 of the 84 |
> | B | is `ROW_RUNG_UNDER_TW` Google-proved or pure LibreOffice cost? | Google-proved. `FINDINGS/THE-RUNG-IS-GOOGLE-PROVED...` (commit `6865f403`) measured rung=0 at 46 of 47 on both `mobile-bill` and `electricity-bill`, failing `18_displacement` |
>
> That second answer overturns the instruction the last report left for this run. The last message said
> the first job was to land the rung "in its per-row form" to release 27 of the 84. The rung is right in
> the renderer the user opens, and reverting it would have spent two documents' 47 of 47 to buy back a
> LibreOffice number. **Do not revert it.** The 84 are a proxy charge against a Google-proved construct,
> which is the shape the gate is supposed to be able to tell apart and currently cannot.
>
>
> 1. Do not re-baseline and do not revert the rung. Both were proposed; one ratifies, the other spends.
> 2. The gate passes now, so a measured change can land. `18_displacement` is in 59 of the 84 and is
> worth 46.6 clean documents, the largest lever in the corpus by a factor of two.
> 3. The ten Google-clean documents in the debt are the case for a second gate refinement: a document
> that passes every applicable check in the committed `gverify` results, measured on this engine,
> cannot be a LibreOffice regression under non-negotiable 1. That is 84 down to 74 with evidence. It
> was not done this run because it changes a rule for the second time in one slot.
>
>
> A commit that passes the new gate and makes a document worse than its last measurement, or a document
> that joins the debt through a commit the old rule would have caught. `gate_debt_test.py` cases 1 and 2
> are those two, and both are refusals today.

## The txt

| | |
|:--|:--|
| Measured | **2.4 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 04:58 → running · 8 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 16 |
| Longest silence | **3.7 min** — from 05:03:38, after `corpus-slice: 48 of 53 converted` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **4 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
