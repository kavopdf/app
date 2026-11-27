# Fixer report - 2026-11-27 16:06

```
# P2W Fixer - Run Report

**27 Nov 2026 · slot 16:06 → 16:46 IST · 39 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8681** of 9273 (93.6%) on 212 documents |
| Check-instances still failing | **592** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **43** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; kept change: 6 code commit(s) in this window, first: slot: release the fixer claim after the 27 Nov 1 vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **212** re-measured on this engine - **0** of the 212 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **1** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (54 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 16:43 | **lead** | 0/None | table-with-no-header-row: the charge is a per-row PITCH RAMP (source 18.4pt, render 17.9pt, 0.44pt/row, 0.7->12.0pt over 27 rows), not the constant offset med_dy reports; and worst_dy 101.4 is the che |

## Why nothing moved, in this run's own words

> # Why nothing moved
>
> Because the class I took is not blocked on an engine change. It is blocked on a **renderer that has no
> cache**, and this run spent its slot proving that rather than assuming it.
>
> ## 1. The measurement that decided the run
>
> I did not take `18_displacement` because the tool printed it. I took it because it is the largest single
> blocker in the store and the reason is checkable in one query:
>
>     40 documents fail exactly ONE check
>     30 of those 40 fail ONLY 18_displacement
>     18_displacement fails on 119 of 211 scored documents
>     60_text_column_right_edge, the next largest, fails on 63
>
> So the class is worth up to 30 clean documents from one construct, and `classpick --leverage` puts its
> worth at 54.6. The rotation said `18_displacement` too. That is a reason; it is not the tool's print.
>
> ## 2. What the two agents settled, before I touched the engine
>
> **Agent A — the small-dy cluster of 15 documents (each fails only this check).**
> It converted all 15, rendered them through LibreOffice, and scored them with `verify_google.py` itself,
> twice: at HEAD, and with `dy` taken from the baseline origin instead of the bbox top.
>
> - The baseline-in-line site is **arithmetically excluded**. Its whole lever is `LINE_BASE × hairlinePt(size)`,
>   and `hairlinePt` caps the box at 0.6485 pt, so the entire term is ≤ **0.52 pt**. The observed charge is
>   1.6–3.0 pt and **sign-mixed (8 positive, 7 negative)**. A lever that cannot change sign cannot explain a
>   population that does. That is why the `BASELINE_EM` swap moved `31_times` 1.04 pt where it predicted 2.76.
> - 11 of the 15 **pass under LibreOffice**. Their `.docx` already puts every line where the page put it as far
>   as any renderer honouring Word's spacing model is concerned; the residual is Google's layout of the same
>   construct.
> - 4 of the 15 are wrong in **both** renderers (`table-with-no-header-row` −5.0 pt, `worst_dy` 101.4;
>   `two-tables-stacked-with-no-gap` −2.5 / 5.6; `71_invoice_space_aligned_no_rules` +1.5 / 8.7;
>   `balance-sheet-two-columns-of-figures` +0.0 / 3.5). Those are genuine engine faults and they are the
>   table-row class, not the baseline class.
>
> **Agent B — the previous run's txt lead.** Closed, with a fixture rather than an argument: the form-feed bug
> was real, is already fixed at `verify_txt.py:944` (commit `0d45ff6`), is **not** a writer bug, and clears
> **0** documents under A/B on the same files. The premise was stale: the `.txt` half has read **205 clean /
> 8 failing** since 26 Nov, not the 186/27 the hand-off quotes.
>
> ## 3. The one attempt I made, and what it found
>
> `table-with-no-header-row` is the document where the engine is wrong in both renderers, so it is the one
> that can be validated **without** Google. I converted it, rendered it, scored it: `41/42`, `18_displacement`
> the only failure, `med_dy -4.9`, `worst_dy 101.4`, 215 runs — the same run count as the recorded Google row.
>
> Then I extracted both pages' row grids. Both have 32 rows. **Source pitch 18.4 pt, render pitch 17.9 pt, on
> 26 consecutive gaps.** The charge is a **linear ramp of 0.44 pt per row, 0.7 → 12.0 pt over 27 rows** — not
> a constant offset. `med_dy` is just the value at the middle of the ramp and has no independent meaning.
>
> And `worst_dy 101.4` is not a displacement at all. The largest pair is `'Diesel'`, source row 130.4 → render
> 29.1, and the same source row's other cells pair to 100.7 and 118.6 — **one source row claimed by three
> render rows 5.5 rows apart**. That is the greedy assignment claiming the nearest *unused* occurrence of a
> normalised string on a header-less table of short numeric cells. It changes no verdict here (the page fails
> on the count clause anyway), but prior work in this class fitted corrections to `worst_dy` by document. If
> `worst_dy` can carry a 5.5-row pairing error, those fits were fitting noise.
>
> ## 4. Why that is a lead and not a kept change
>
> The ramp is confirmed in **one renderer on one document**. To fix it I would have to change how the row's
> laid pitch is written, then prove it on the corpus. That needs two things this slot did not have:
>
> 1. **A corpus rebuild.** `corpus-convert.py` keys every document on the engine source hash; one line under
>    `app/src/main/java` invalidates all 213 keys and `regress.py --check` refuses to stamp until they are
>    rebuilt — ~27 min, and a rebuild I cannot finish is a corpus with no stamp, worse than the one I had.
> 2. **A Google render.** The only renderer that sees this cluster is Google, and there is **no cached Google
>    export on the pod** — `/scratch/work/p2w/gverify/gd` is empty, and `/scratch/work` does not survive a run.
>    Every measurement of this class costs a Drive round trip, which is why 57 attempts have steered by
>    `med_dy` alone.
>
> I chose to land the measurement rather than a patch I could not verify. The pod was warm this run (corpus,
> JDK and engine all present), so the 32 minutes the last run spent building it went into the agents and the
> probe instead — and that is what produced the two findings and the closed lead.
>
> ## 5. What the next run should do first
>
> 1. **Read `med_dy` as a ramp for any table document.** The store carries no per-row data, so the ramp is
>    invisible in it. That gap is the highest-value instrument change available to this class.
> 2. **Do not fit a correction to `worst_dy` alone.** Guard first: a pair whose `|dy|` exceeds 2× the page's own
>    row pitch is more likely a mis-pair than a displacement.
> 3. **The 4 Group-1 documents are the only ones in this cluster that can be validated without Google.** Start
>    there; a fix that moves them is measurable in the slot.

### The run before this one said

> # Why nothing moved
>
> Because the class I took is not blocked on an engine change. It is blocked on a **renderer that has no
> cache**, and this run spent its slot proving that rather than assuming it.
>
> ## 1. The measurement that decided the run
>
> I did not take `18_displacement` because the tool printed it. I took it because it is the largest single
> blocker in the store and the reason is checkable in one query:
>
> 40 documents fail exactly ONE check
> 30 of those 40 fail ONLY 18_displacement
> 18_displacement fails on 119 of 211 scored documents
> 60_text_column_right_edge, the next largest, fails on 63
>
> So the class is worth up to 30 clean documents from one construct, and `classpick --leverage` puts its
> worth at 54.6. The rotation said `18_displacement` too. That is a reason; it is not the tool's print.
>
> ## 2. What the two agents settled, before I touched the engine
>
> **Agent A — the small-dy cluster of 15 documents (each fails only this check).**
> It converted all 15, rendered them through LibreOffice, and scored them with `verify_google.py` itself,
> twice: at HEAD, and with `dy` taken from the baseline origin instead of the bbox top.
>
> - The baseline-in-line site is **arithmetically excluded**. Its whole lever is `LINE_BASE × hairlinePt(size)`,
> and `hairlinePt` caps the box at 0.6485 pt, so the entire term is ≤ **0.52 pt**. The observed charge is
> 1.6–3.0 pt and **sign-mixed (8 positive, 7 negative)**. A lever that cannot change sign cannot explain a
> population that does. That is why the `BASELINE_EM` swap moved `31_times` 1.04 pt where it predicted 2.76.
> - 11 of the 15 **pass under LibreOffice**. Their `.docx` already puts every line where the page put it as far
> as any renderer honouring Word's spacing model is concerned; the residual is Google's layout of the same
> construct.
> - 4 of the 15 are wrong in **both** renderers (`table-with-no-header-row` −5.0 pt, `worst_dy` 101.4;
> `two-tables-stacked-with-no-gap` −2.5 / 5.6; `71_invoice_space_aligned_no_rules` +1.5 / 8.7;
> `balance-sheet-two-columns-of-figures` +0.0 / 3.5). Those are genuine engine faults and they are the
> table-row class, not the baseline class.
>
> **Agent B — the previous run's txt lead.** Closed, with a fixture rather than an argument: the form-feed bug
> was real, is already fixed at `verify_txt.py:944` (commit `0d45ff6`), is **not** a writer bug, and clears
> **0** documents under A/B on the same files. The premise was stale: the `.txt` half has read **205 clean /
> 8 failing** since 26 Nov, not the 186/27 the hand-off quotes.
>
> ## 3. The one attempt I made, and what it found
>
> `table-with-no-header-row` is the document where the engine is wrong in both renderers, so it is the one
> that can be validated **without** Google. I converted it, rendered it, scored it: `41/42`, `18_displacement`
> the only failure, `med_dy -4.9`, `worst_dy 101.4`, 215 runs — the same run count as the recorded Google row.
>
> Then I extracted both pages' row grids. Both have 32 rows. **Source pitch 18.4 pt, render pitch 17.9 pt, on
> 26 consecutive gaps.** The charge is a **linear ramp of 0.44 pt per row, 0.7 → 12.0 pt over 27 rows** — not
> a constant offset. `med_dy` is just the value at the middle of the ramp and has no independent meaning.
>
> And `worst_dy 101.4` is not a displacement at all. The largest pair is `'Diesel'`, source row 130.4 → render
> 29.1, and the same source row's other cells pair to 100.7 and 118.6 — **one source row claimed by three
> render rows 5.5 rows apart**. That is the greedy assignment claiming the nearest *unused* occurrence of a
> normalised string on a header-less table of short numeric cells. It changes no verdict here (the page fails
> on the count clause anyway), but prior work in this class fitted corrections to `worst_dy` by document. If
> `worst_dy` can carry a 5.5-row pairing error, those fits were fitting noise.
>
> ## 4. Why that is a lead and not a kept change
>
> The ramp is confirmed in **one renderer on one document**. To fix it I would have to change how the row's
> laid pitch is written, then prove it on the corpus. That needs two things this slot did not have:
>
> 1. **A corpus rebuild.** `corpus-convert.py` keys every document on the engine source hash; one line under
> `app/src/main/java` invalidates all 213 keys and `regress.py --check` refuses to stamp until they are
> rebuilt — ~27 min, and a rebuild I cannot finish is a corpus with no stamp, worse than the one I had.
> 2. **A Google render.** The only renderer that sees this cluster is Google, and there is **no cached Google
> export on the pod** — `/scratch/work/p2w/gverify/gd` is empty, and `/scratch/work` does not survive a run.
> Every measurement of this class costs a Drive round trip, which is why 57 attempts have steered by
> `med_dy` alone.
>
> I chose to land the measurement rather than a patch I could not verify. The pod was warm this run (corpus,
> JDK and engine all present), so the 32 minutes the last run spent building it went into the agents and the
> probe instead — and that is what produced the two findings and the closed lead.
>
> ## 5. What the next run should do first
>
> 1. **Read `med_dy` as a ramp for any table document.** The store carries no per-row data, so the ramp is
> invisible in it. That gap is the highest-value instrument change available to this class.
> 2. **Do not fit a correction to `worst_dy` alone.** Guard first: a pair whose `|dy|` exceeds 2× the page's own
> row pitch is more likely a mis-pair than a displacement.
> 3. **The 4 Group-1 documents are the only ones in this cluster that can be validated without Google.** Start
> there; a fix that moves them is measurable in the slot.
>
>
>
>
>
>
> # Why nothing moved
>
> Because the slot was spent building the pod, and then on an instrument that stops the next run
> spending its slot the same way.
>
> ## 1. The 32 minutes before any document can be touched
>
> A fixer run starts on an empty pod. `/scratch/work` is gone, so the corpus cache, the JDK and the
> compiled engine are gone with it. Measured this run, 2 cores:
>
> corpus-fetch.sh                 16 s    213 PDFs
> jdk-fetch.sh                    23 s
> libs + aar + stubs + engine     50 s    out/ConvertAll.class
> corpus conversion, 213 docs    ~27 min  6 slices: 103 -> 133 -> 161 -> 187 -> 208 -> 213
>
> That is 32 of the 90 minutes, and a run that goes quiet for 45 minutes during it is reaped, so it has
> to be sliced into calls that each finish inside 300 s. Six calls of bookkeeping before the first
> document exists to look at.
>
> ## 2. Why the remaining 58 minutes could not hold an engine change
>
> `corpus-convert.py` keys every document on the engine source hash. One line changed under
> `app/src/main/java` invalidates all 213 keys, and `regress.py --check` refuses to run until the corpus
> is rebuilt and stamped - the hook will not let the commit land before then.
>
> 32 min setup  +  27 min rebuild  =  59 min
>
> leaving 31 minutes for the change, its Google verification, and the report. That arithmetic is the
> whole reason runs land one attempt: by the time the engine is measurable there is room for one look,
> and the first look usually refutes the hypothesis.
>
> I did not start a rebuild I could not finish. A commit that cannot pass the gate is not a change, and
> half a rebuilt corpus is a corpus with no stamp, which is worse than the one I started with.
>
> ## 3. What was done instead, and why it is worth the slot
>
> `corpus-slice.py` had no way to name a document. `--budget 0 -j 1` converts exactly one document - but
> it converts `todo[0]`, the first *pending* document alphabetically, so the filesystem chose the
> document, not the person fixing it. `--only <stem>` now names it: **4.5 s for one document** against
> 27 minutes for the corpus.
>
> That is not a document. It is the thing that makes the *next* run's first attempt cost 4.5 s instead
> of 27 minutes, which is the difference between the one attempt every run gets and the four to six the
> charter asks for.
>
> ## 4. What I could not prove
>
> The post-conversion stamp guard in `--only` is the only new behaviour and it is the only thing I did
> not run: the corpus was fully converted and stamped before the patch landed, so no unconverted document
> existed to name, and manufacturing one meant either invalidating a real key (deleting a file) or
> adding a probe PDF to a corpus of 213. It is written down in
> `FINDINGS/cold-pod-tax-and-only-flag-27NOV-relay.md` as not exercised, with the two branches that were.
>
> ## 5. The self-check's two disagreements, in plain words
>
> * *A code commit with no kept record in ATTEMPTS.json.* `attempt.py` refuses a class that is not in
> `benchmarks/DEFECT-CLASSES.md`, and `instrument` is not one - it said so: "that is not there writes
> against nothing and leaves the real class at zero." Recording a tooling change under a document
> defect class would corrupt that class's count, so it is recorded here and in the commit message
> instead. The next run should read this before assuming the class is parked.
> * *RUN.json says 14:28, TIMELINE.jsonl says 13:54.* The window was reset by this run's claim; the
> 13:54 row is the slot's previous occupant.
>
> Accounts share 20% of their significant words - a different account (the cut is 50%).

Accounts share 72% of their significant words - **the same blocker, named twice** (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **3.3 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dsmall-dy cluster of 15-01` | which code site places a run's baseline, and is the  | 16:45 | - | - |
| `txtform-feed lead-01` | is _txt_lines dropping page separators, and how many | 16:45 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 16:06 → 16:46 · 39 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 39 |
| Longest silence | **24.4 min** — from 16:11:08, after `pending.py: reading the pending gate` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `###` |
| fix - diagnose and change the engine | **24 min** | `##############` |
| record - attempt, handoff, class rows | **5 min** | `###` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **4 min** | `##` |

The unattributed row is 4 distinct beat(s) that matched no phase. They said:

- `gate check: regress --check running`
- `18_displacement -> lead`
- `fixer released (forced)`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
