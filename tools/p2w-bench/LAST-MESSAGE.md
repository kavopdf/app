# P2W Fixer - Run Report

**26 Nov 2026 · slot 11:49 → running IST · 2 min**

> No change was kept. Three Google renders: one structural finding that redirects the class, and one lever refuted by its own falsifier.

## Progress

| Check-instances passing | **7419** of 7881 (94.1%) on 182 documents |
| Check-instances still failing | **462** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **48** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
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

## The txt

| | |
|:--|:--|
| Measured | **6 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 11:49 → running · 2 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 11 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **0 min** | `#######` |
| report - the report and the chain | **0 min** | `########` |
| other - not attributed to a tool | **0 min** | `#######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Read `FINDINGS/18-displacement-PAGEFIRST-DEAD-CODE-AND-AUTOFLOW-1200-relay.md` before touching this class. The header above says 11:49 because the slot was re-claimed at 11:48 after a rebase reset `RUN.json`; the run itself began at 11:20.

1. **The page-top lever cannot reach this class.** All **23** documents whose only failing check is `18_displacement` are **single-page** (measured with PyMuPDF over the corpus PDFs). `TOPGAP_ROW` and the page-break `w:before` drop both act only on pages after the first, so on these they are byte-inert - verified: `document.xml` of a flag-on and a flag-off build of `electricity-bill` is identical. Do not re-run that lever on these 23.
2. **`autoflow` removes a real constant and is still not a keeper.** On `electricity-bill` the default `exact` construct puts every run 7.18 pt high (median -7.18, 113/125 runs out, a tight -10.4 to -0.1 band - re-rendered in this run, so the stored row reproduces on this tree). `autoflow` moves that median to **+0.08** with 26/125 out. On `72_bank_statement` the same switch moves the median from **+1.1 to +3.51** and the worst from **4.8 to 8.44**. Opposite signs, neither document clean.
3. **The one lever the evidence points at next:** declare an exact box `L' = 12L/K` with `K = 2.74663` (the Google-proven charge, `FINDINGS/w-line-exact-GOOGLE-CHARGE-075617-f0cc.md`) and put `-(L'-L)/20` into `w:before`. `before + line` is preserved, so Word and LibreOffice see the same advance, while Google's charge for `L'` lands on the intended pitch. This is the correction `autoflow` approximates, without changing the construct LibreOffice honours.
4. Measure it on `electricity-bill` **and** `72_bank_statement` first - they are now a positive and a negative control for this class, with numbers on file.

**`spacing()`'s `pageFirst` was dead code in every build.** Both flow call sites passed `ctx.newPage` after clearing it, so the first-line compensation never ran - which is why `autoflow` had never been a fair experiment. Patch saved at `patches/PATCH-pagefirst-autoflow-1200-relay.patch`; inert at the default `exact` by construction.

## Subagents

Two, at the start. One mapped the engine's spacing construct - `spacing()` :149, the `ctx.newPage` state (:819, cleared at :3800 and :4722), the table spacer emitter :6055-6185 - and returned the line numbers and patch shapes this run used. The second returned the same content and was not needed.
