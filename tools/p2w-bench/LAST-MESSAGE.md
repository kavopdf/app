# P2W Fixer - Run Report

**26 Nov 2026 · slot 21:10 → running IST · 1h 17m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8479** of 8969 (94.5%) on 207 documents |
| Check-instances still failing | **490** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **55** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; .txt age: measured 10.9 h ago vs nothing re-measures it on a schedule; subagents: 1 deployed vs no FINDINGS filename carries 18_dA-02 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **47** of the **205** re-measured on this engine - **0** of the 205 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (52 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:11 | **lead** | 0/208 | aa496ebe re-measured across 208 of 212: newsletter 0.20->86.30, 600 54.30->62.46, but itr-computation 42.33->9.10 - a 33pt regression, so the engine stays unstamped and the gate stays closed |

## Why nothing moved, in this run's own words

> Because the gate was shut, and the gate was the work.
>
> Commit aa496ebe landed at 10:20 UTC today - the pgMar page-top patch, 141 lines of DocxWriter.java -
> after the docx table had been stamped at 02:54. Nothing re-measured it. So `measure_gate.py` said
> NOT READY ("RANKING.csv was measured on docx engine a4de7df8 and the tree is 7e0de1ab") and
> `regress.py` refused every .docx change as unmeasured. A fixer in that state can measure nothing it
> lands, so it can land nothing.
>
> I re-measured instead. 213 of 213 documents converted (0 failed), then 208 of 212 scored on the live
> tree. The answer is not the one the commit claimed: the patch is real and it is large -
> newsletter-3col-header-footer 0.20 -> 86.30, 600_reviewed_invoice_with_annotations 54.30 -> 62.46 -
> but itr-computation-with-slab-table falls 42.33 -> 9.10. A 33-point regression. Two documents bought
> with one is not a pass, so the engine stays unstamped, RANKING.csv stays untouched, and the gate
> stays closed - correctly, and now for a measured reason instead of an unmeasured one.
>
> The cache is the asset. 208 documents are scored against 7e0de1ab, so whoever takes this next needs
> 4 documents and not 212: `324_loan_amortisation_schedule.docx` was refused twice by soffice (91 s, no
> render) and is recorded in PRE/.soffice-fail; the other three were mid-retry when the slot ended.
> The next move is a bisect of aa496ebe on itr-computation-with-slab-table alone - the section
> w:pgMar w:top is written per section, and a slab table that spans pages is the shape most likely to
> have its page-top term counted twice. If the two cannot be separated, revert to 9f0a8207 and carry
> the newsletter gain as an unlanded lead.
>
> One more thing the run found and did not chase: the two-agents-per-run rule was met with one agent,
> because a delegated agent in an unattended run is not background - it blocks the turn, and this one
> took 23 of the 90 minutes. It came back with a usable mechanism (Google snaps w:trHeight to a 0.75 pt
> rung and adds one rung on a ruled table, so a ruled table's error is one-signed and cumulative - a
> ramp, not an offset), and with the measurement method that produced it: rewrite only the trHeight
> values in the .docx and render in LibreOffice, and you get Google's layout of that file to under 1 pt.
> That method is worth more than the patch, and it belongs in the toolbox before the next run.

### The run before this one said

> The class was `t09_page_furniture`, and the reason was a pending item, not a preference: two documents fail it and nothing else in the `.txt` population, a patch for it was already sitting in `FINDINGS/` unlanded, and `pending.py` says pending items come before any new class. The tool's own suggestion (`t12_word_invention`) was refused because 37 pending items stand in front of a new class.
>
> The patch is wrong, and it is wrong in a way a synthetic test could not catch. It recovers the `.txt` band as the first and last three non-empty lines **of each U+000C-delimited segment**, and its comment says a unit test on a three-page synthetic file caught a form-feed bug in that split. The real writer emits **no form feeds at all**: `segs=1`. So the band becomes the first and last three lines of the whole document, it holds none of the 29 owed occurrences, and the document would read **0 of 29** where it reads 125 of 29 today — the patch makes the document worse. A test built from what the writer is supposed to emit is not a test of what it emits.
>
> Its second half does not finish it either. Drop one-character keys and the population is `Date` alone: owed 3 (one per date box, pages 0-2), present 6 (three in the band, three in a body column header). Only a band-scoped `present` removes that surplus, and the first paragraph is why the patch's band cannot work. A correct version needs both halves **plus a real aligner** — each `.txt` line mapped to the drawn line it came from so it can inherit that line's `y`. That is a larger change, it is an instrument change, and it needs the whole 213-document `.txt` table re-measured before and after. The slot did not have that in it, so it is not landed. That is the next run's first job.
>
> I also took the previous run's "the `.txt` loses 21 values" claim and could not reproduce it as a loss. The per-key counts do reproduce — drawn `Y` 48 `D` 40 `M` 52 against `.txt` 41/33/45 — but the two sides are different populations: the PDF draws `DDMMYYYY` as one letter-spaced `Tj` and `_src_pages` inherits PyMuPDF's per-glyph line model, while the `.txt` count is over 5684 lines of which 274 are single characters, mostly letter-spaced words exploded one character per line. And `t01_word_accuracy` and `t04_structure` **pass** on this document, which they would not if 21 real glyphs had gone. The refusal that rested on that claim does not stand; the check's asymmetry does.
>
> The second measurement is the one worth carrying forward. The store was re-measured under this run by the gverify cron — 142 records on this engine at 20:40, 205 at 21:05 — so the census was re-stamped on the refreshed store rather than reported at its stale size. **42 documents are one check from clean and 25 of them fail only `18_displacement`.** Fourteen of those 25 have a worst run of 3.3-6.8 pt, and the tail clause fires only at `2 x _tol` (6.3 pt on a 9 pt run, 7.0 on a 10 pt), so those fourteen cannot be failing on the tail at all: they fail the **count** clause, `n_out > max(2, ceil(5% of runs))`, where three or four runs a point or two out is enough. The last two runs measured the spacer-spend arm, which moves `med_dy` and the tail. This says the population that is left is mostly the count, which is a different construct and has not been measured.
>
> `60_text_column_right_edge` was the other candidate and is now closed as a source of clean documents: all six of its one-away documents are the DejaVu set, and `335_msds_safety_data_sheet`, new to the list, is DejaVu too (measured from its own PDF). Google has no DejaVu and drops an embedded face, so no `.docx` construct can reach them.
>
> One instrument fault found and written down, not fixed: `runclock.py`'s `elapsed` is reset by `attempt.py`, so the 75-minute checkpoint can never fire after a run records its first attempt. Measured back to back in this run (claimed 14:29 → 22 min; after one `attempt.py`, claimed 15:05 → 0 min), and `round.py --heartbeat` does not do it. It is one line in `attempt.py`, which is the ledger — a wrong edit there silently mis-credits every future attempt — so it is a finding, not a patch.
>
> The gate was run and it refused for the reason it always refuses on a fresh pod: `regress.py --check` reports `corpus: could not be built (1)` and then timed out past 250 s building it, because 126 of 213 documents are still unconverted on this tree. `pod-prep.sh` fetched the corpus (213 PDFs), the JDK, the libs and compiled the engine, and converted 53 of the 179 documents it found outstanding; `measure_gate.py` still reports `RANKING.csv` measured on `a4de7df896875a39` against a tree of `7e0de1abdeb221ae`, NOT READY. The pre-commit hook is not installed for the same reason (`install-gate.sh` runs that same build before it writes the hook), so this run's commits went in unguarded. They add FINDINGS documentation and ledger rows only — no engine code and no instrument code — so no document can have moved.
>
> One agent was deployed in the first ten minutes on the t09 question — writer defect or instrument asymmetry — with the document, the census method and the success test named in its brief. Its census is committed as `FINDINGS/t09_page_furniture-SINGLE-CHAR-CENSUS-agent-26NOV.md`: 274 single-character `.txt` lines, 264 of them artifacts of cut letter-spaced runs, and a band-restricted `present` of 29 against 29 owed. Its verdict (instrument, not writer) agrees with the asymmetry in the first paragraph above; its proposed implementation is the one paragraph 3 says needs a real aligner and a full `.txt` re-measure. report.py's own `Subagents` row reads "None deployed this run" because the agent ledger it reads was not written — the FINDINGS file is the record.
>
> ## For the next run
>
> 1. `18_displacement`'s remaining population is the **count clause on 14 documents within 7 pt**, not the tail. Measure the per-run `dy` list on `70_magazine_drop_cap_photo_caption` (worst 3.3, 24 runs) and `31_times_body_arial_headings` (worst 3.5, 29 runs) — a 24-run page forgives 2 and a 29-run page forgives 2, so three runs out fails it. That is the smallest number of runs standing between 14 documents and clean.
> 2. `t09`: build the aligner, then `restamp_txt.py --force` over all 213, then land. Do not land the `FINDINGS/t09-FIX-*.patch`; it reads 0 of 29.
> 3. `runclock.py`'s reset: one line in `attempt.py`, and it needs a run that starts with it.
> 4. `pod-prep.sh` finishes the corpus in three more slices of ~280 s each (53 per slice). Nothing later inherits it, so a run that wants a guarded commit should spend the 14 minutes first, not last.

Accounts share 14% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **11.1 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-02` | find the single construct behind the displaced runs  | 22:14 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 21:10 → running · 1h 17m |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 137 |
| Longest silence | **23.3 min** — from 21:11:11, after `pending.py: reading the pending gate` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **1 min** | `#` |
| build - compiling the engine | **6 min** | `##` |
| fix - diagnose and change the engine | **6 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **43 min** | `############` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **13 min** | `####` |
| other - not attributed to a tool | **3 min** | `#` |

The unattributed row is 2 distinct beat(s) that matched no phase. They said:

- `re-measuring docx corpus on engine 7e0de1ab (unblocks the gate)`
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

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. measure the last 4 documents, then bisect aa496ebe on itr-computation-with-slab-table

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
