# Fixer report - 2026-11-26 20:35

```
# P2W Fixer - Run Report

**26 Nov 2026 · slot 20:35 → 20:46 IST · 11 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8479** of 8969 (94.5%) on 207 documents |
| Check-instances still failing | **490** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **55** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - kept change: 2 code commit(s) in this window, first: p2w: one-away census re-stamped on the refreshed vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; .txt age: measured 9.5 h ago vs nothing re-measures it on a schedule; subagents: 1 deployed vs no FINDINGS filename carries t09_A-01 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **47** of the **205** re-measured on this engine - **0** of the 205 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (51 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 20:35 | **lead** | 0/None | the band arm the FINDINGS patch uses reads 0 of 29 (the .txt has no form feeds: segs=1), and dropping one-char keys alone leaves Date 6 vs 3; a correct fix needs an aligner plus a full 213-doc .txt re |

## Why nothing moved, in this run's own words

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

## The txt

| | |
|:--|:--|
| Measured | **9.5 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t09_A-01` | is the 125 single-char present a TxtWriter line-asse | 20:47 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 20:35 → 20:46 · 11 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 14 |
| Longest silence | **7.9 min** — from 20:35:59, after `writing findings + report` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **7 min** | `#################` |
| report - the report and the chain | **1 min** | `###` |
| other - not attributed to a tool | **1 min** | `###` |

The unattributed row is 5 distinct beat(s) that matched no phase. They said:

- `t09_page_furniture -> lead`
- `writing findings + report`
- `clock test`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
