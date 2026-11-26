# P2W Fixer - Run Report


**26 Nov 2026 · slot 11:50 → 12:00 IST · 9 min**

> One document went clean in Google on an unlanded construct (`72_bank_statement`, 41/42 -> 42/42). Nothing was committed to the engine: the corpus has not been measured on the new defaults, and rule 3 forbids landing it blind. The 90-minute slot began at 11:20; the clock below restarted when the claim was re-taken at 11:50 after a rebase reset `RUN.json`.

## Progress

| Check-instances passing | **7419** of 7881 (94.1%) on 182 documents |
| Check-instances still failing | **462** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **48** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - subagents: 2 deployed vs no FINDINGS file for 5K6VD2QX509EHTJ0, 4XPVKR9J4N9V4R2C |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **41** of the **181** re-measured on this engine - **26** of the 207 scored are still on an older engine, and **1** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 26 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **6** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (47 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 11:48 | **lead** | 0/23 | pageFirst dead-code fix + -Dp2w.lineRule=autoflow measured in one Google export (electricity-bill): page-0 median dy -7.2 -> +0.08 pt, worst 10.4 -> 6.56 pt, still fails 26/125 runs; all 23 solo-faili |
| 11:49 | **reverted** | 0/23 | autoflow falsifier: electricity-bill median dy -7.2 -> +0.08 but 72_bank_statement +1.1 -> +3.51 and worst 4.8 -> 8.44 (52/80 runs out of tolerance); opposite signs, neither clean - autoflow is not a |
| 11:50 | **lead** | 0/23 | control render in this run: the default exact build of electricity-bill in Google gives page-0 median dy -7.18 (min -10.43, max -0.10, 113/125 runs out), reproducing the stored -7.2 on the current tre |
| 11:53 | **lead** | 1/23 | autoflow + -Dp2w.autoEm=1.2207 (the substitute face's real ratio, from the w-line-exact finding): 72_bank_statement_no_rules_right_amounts 41/42 -> 42/42 PASS in Google (median dy +3.51 -> +0.21, 2/80 |

## The txt

| | |
|:--|:--|
| Measured | **17 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run
## Next run

Read `FINDINGS/18-displacement-PAGEFIRST-DEAD-CODE-AND-AUTOFLOW-1200-relay.md` first. The header clock says 11:49 because the slot was re-claimed at 11:48 after a rebase reset `RUN.json`; the run began at 11:20.

**The lever, measured in Google, three constructs on two controls:**

| document | exact (default) | autoflow, 1.15 em | autoflow, `-Dp2w.autoEm=1.2207` |
|:--|--:|--:|--:|
| `72_bank_statement_no_rules_right_amounts` | 41/42, med +1.1 | 41/42, med +3.51, 52/80 runs out | **42/42 PASS**, med +0.21, 2/80 out |
| `electricity-bill` | 46/47, med -7.18, 113/125 out | 46/47, med +0.08, 26/125 out | 46/47, med -1.47, 41/125 out |

1. **Land it properly, first thing:** build the corpus with `-Dp2w.lineRule=autoflow -Dp2w.autoEm=1.2207`, run `regress.py --check`, and if nothing gets worse in the LibreOffice proxy make those the defaults, then let the `:20 gverify` cron re-measure. The construct is measured; only the corpus pass is missing.
2. **Then the table, not the line.** Under that construct the 41 runs still failing on `electricity-bill` are 37 table-cell runs at 7.20 pt explained to +-0.11 pt by `dy(row i) = dy(caption) - 2.96 + i*0.652` - a table-entry offset of -3.0 pt (identical at both tables) and a +0.652 pt/row pitch inflation (19.07 pt rendered against 18.4 pt source). The 4 page-furniture runs (header +5.4, footer -3.37) are a second construct, and the check counts bad PAGES, so both must go before the document turns green.
3. **Do not re-run the page-top lever on this class.** All **23** documents whose only failing check is `18_displacement` are **single-page** (PyMuPDF over the corpus PDFs), so `TOPGAP_ROW` and the page-break `w:before` drop are byte-inert on every one of them.
4. **The `L' = 12L/K` exact-box transform is arithmetically impossible** - keeping the advance constant needs `before' = before - 3.3695 L`, negative for every line in the corpus. `auto` is the only construct that escapes Google's exact-line charge.
5. `spacing()`'s `pageFirst` was dead code in every build; the patch is at `patches/PATCH-pagefirst-autoflow-1200-relay.patch` and is inert at the default `exact`.

## Subagents

Two. The first mapped the engine's spacing construct - `spacing()` :149, the `ctx.newPage` state (:819, cleared at :3800 and :4722), the table spacer emitter :6055-6185 - and returned the line numbers and patch shapes this run used. The second classified the 41 residual runs on the positive control: 10 distinct lines, 37 of them table cells at 7.20 pt, a two-parameter table defect (entry -3.0 pt, pitch +0.652 pt/row) plus 4 page-furniture runs. Both landed in FINDINGS.

## Subagents

Two. The first mapped the engine's spacing construct - `spacing()` :149, the `ctx.newPage` state (:819, cleared at :3800 and :4722), the table spacer emitter :6055-6185 - and returned the line numbers and patch shapes this run used. The second classified the 41 residual runs on the positive control: 10 distinct lines, 37 of them table cells at 7.20 pt, a two-parameter table defect (entry -3.0 pt, pitch +0.652 pt/row) plus 4 page-furniture runs. Both landed in FINDINGS.

## Timing

| | |
|:--|:--|
| Slot window | 11:50 → 12:00 · 9 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 18 |
| Longest silence | **4.1 min** — from 11:54:15, after `lastmessage.py: running report.py for the numbers` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **1 min** | `###` |
| report - the report and the chain | **7 min** | `#################` |
| other - not attributed to a tool | **1 min** | `##` |
