# Fixer report - 2026-11-28 15:08

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 15:08 → running IST · 40 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (64 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 15:47 | **lead** | None/None | Google loop proven end-to-end (42/47 reproduced on bank-statement-5-pages, same 5 failures, engine a05b20eb); ROW_RUNG_UNDER_TW 10->25 refuted as inert on 320_balance_sheet_statutory - all 21 rows emi |

## Why nothing moved, in this run's own words

> **Two things were measured and neither moved a document, and that is the honest shape of this slot.**
>
> The first is a blocker, and unblocking it was worth more than a document. `BLOCKERS.md` says, at 12:15
> today, that a locally built `.docx` cannot reach Google because the upload call needs an `s3key`, and
> concludes that only a public probe branch works. That is wrong: the platform `upload` tool mints an
> `s3key` for any file that is **already in a saved location**, and the reason four runs concluded otherwise
> is that a file under `/scratch/work` is refused *before* any Drive call, and the refusal arrives as the
> Drive tool's 403 "file key does not belong to this project or session" — which reads like a permission
> problem and is a path rule. `bank-statement-5-pages` was put through the three calls end to end today and
> `gverify.py --collect` scored it **42/47**, failing exactly the same five checks as the row already stored
> for it (`18_displacement, 25_invisible_text, 27_text_off_page, 44_header_footer, 59_shape_anchor`, engine
> `a05b20eb05fe0fc8`, `med_dy -54.1`). The path reproduces the stored number, so it measures the same thing.
> That is the reason any future slot can build an engine change and measure it in Google inside the slot.
>
> The second was an attempt on `18_displacement`, the biggest class (108 documents) and the one that decides
> whether 19 documents become CLEAN, since 19 of them fail that check **alone**. `320_balance_sheet_statutory`
> fails only `18_displacement` at `worst_dy 16.2` over 21 `w:trHeight` rows, and 21 x 0.75 pt = 15.75 pt — the
> quantum law's number to within a rounding. The hypothesis was that the engine's existing
> `ROW_RUNG_UNDER_TW = 10` twips (0.5 pt) under-declaration is short of the 0.75 pt rung and the residual
> accumulates; 25 twips should remove it.
>
> **The hypothesis is refuted, and the refutation is the result.** The engine was rebuilt with the constant at
> 25 and the corpus reconverted, and the emitted heights are identical: all 21 rows write `280` twips at both
> settings. The subtraction is guarded by `if (pitchBinds && footRoom && ...)` and one of those predicates is
> false for every row of a dense balance sheet — so the declaration is the raw pitch, uncompensated, and the
> rung is charged on top of it. The constant cannot reach this document at all. **The lever is `footRoom`,
> which asks whether the row's own text leaves 5 pt of room below it — a question a dense table always answers
> "no", which is why the compensation that exists to stop this drift is switched off exactly where the drift
> accumulates.**
>
> The change was reverted, the engine left byte-identical to HEAD, and `regress.py --check` passes. What the
> next run should do first is the experiment this one could not finish: drop the `footRoom` guard (or lower
> its threshold) and measure `320` in Google with the loop above — one document, one number, 19 documents at
> stake. The measurement apparatus now exists for it; when this slot began, it did not.

## The txt

| | |
|:--|:--|
| Measured | **2.0 h ago** |
| Scored | **214** of 214 |
| Clean - every applicable check passes | **209** (97.7%) |
| Failing at least one check | **5** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

One, run inside the turn rather than in the background: *can a locally built `.docx` reach Google without an s3key?* It answered **no for a local path, yes for the platform `upload` tool**, which is the answer the loop above is built on, and its finding is folded into
`FINDINGS/GOOGLE-LOOP-PROVEN-TODAY-AND-RUNG-CONSTANT-INERT-28NOV-fixer.md`.

## Timing

| | |
|:--|:--|
| Slot window | 15:08 → running · 40 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 23 |
| Longest silence | **9.9 min** — from 15:32:15, after `reconverting corpus back to HEAD engine for the gate` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `##` |
| fix - diagnose and change the engine | **5 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **24 min** | `##############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| other - not attributed to a tool | **4 min** | `###` |

The unattributed row is 3 distinct beat(s) that matched no phase. They said:

- `proving google loop on bank-statement-5-pages`
- `attempt: row rung under 10->25 twips on 320`
- `18_displacement -> lead`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
