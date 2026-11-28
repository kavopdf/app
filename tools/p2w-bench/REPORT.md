# Fixer report - 2026-11-28 15:47

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 15:47 → running IST · 39 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - attempts: RUN.json counter 3 vs ATTEMPTS.json history 2; kept change: 1 code commit(s) in this window, first: fixer 28 Nov 15:08: google loop proven end-to-en vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; run window: RUN.json says this run began at 15:47 vs TIMELINE.jsonl records the claim at 15:08, so the window was reset and the duration is short |
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| 16:27 | **lead** | None/None | footRoom is the false predicate, measured: pitchBinds true on all 21 rows of 320_balance_sheet_statutory, footRoom false on all 21 (clearance 4.25/3.75 pt vs a 5.0 pt threshold). FOOT_ROOM_MIN_TW 100- |

## Why nothing moved, in this run's own words

> **Three things were measured. The first unblocks every future slot, the third moved the drift 3x closer to
> zero, and none of them turned a document CLEAN — which is the standard, so the honest count is 0 kept.**
>
> **1. The Google loop works today, and the blocker that said it did not is wrong.** `BLOCKERS.md` recorded at
> 12:15 today that a locally built `.docx` cannot reach Google because the upload call needs an `s3key`, and
> concluded only a public probe branch works. The `s3key` is minted by the platform `upload` tool — which is
> not importable and not named `GOOGLEDRIVE_*`, which is why runs looking only at the Drive tools conclude it
> does not exist. It refuses a file under `/scratch/work` **before** any Drive call, and the refusal arrives as
> the Drive tool's 403 "file key does not belong to this project or session" — read as a permission problem by
> three earlier runs, and it is a path rule. `bank-statement-5-pages` was put through the three calls end to end
> and scored **42/47**, failing exactly the five checks already stored for it, with `med_dy -54.1` on the same
> engine. The path reproduces the stored number, so it measures the same thing.
>
> **2. `ROW_RUNG_UNDER_TW` is inert, and that refutation saved the slot from a wrong change.** 21 rows x 0.75 pt
> = 15.75 pt matched `320`'s `worst_dy` 16.2 too well to ignore, so the constant went 10 -> 25 twips. The emitted
> heights were identical at both settings — all 21 rows write 280 twips — because the subtraction is guarded by
> `pitchBinds && footRoom` and one of them is false on every row. The constant cannot reach the document.
>
> **3. `footRoom` is the lever, and it is measured in Google both ways.** Instrumenting the row loop rather than
> reading it: `pitchBinds` is true on all 21 rows, `footRoom` is false on all 21, and the guard misses by 0.75 pt
> on one table and 1.25 pt on the other — it demands 5.0 pt of clearance below the lowest baseline and the rows
> have 4.25 and 3.75. At `FOOT_ROOM_MIN_TW = 75` the rows emit 270/250 twips instead of 280/260 and the rung
> finally runs: **`worst_dy` 16.2 -> 5.2 pt, `med_dy` 7.2 -> 0.4 pt**, still 46/47 because `18_displacement`
> keeps failing.
>
> **Why that is a lead and not a kept change.** `regress.py --check` refuses an unmeasured engine, and landing
> it means a corpus-wide Google re-measure and `--stamp` — 206 documents x 3 Drive calls, which is not a slot.
> So the change was reverted, the corpus rebuilt for HEAD, the gate re-run and passing, and `320` re-measured at
> HEAD so the stored row still describes the engine in the tree. What the next run inherits is a construct that
> is 11 pt closer with a named residual: T2's five rows are ladder-inert at 260 -> 250, because both land on
> 13.50 pt, and they need 240 twips to move. Apply both in one change, measure `320` first — three minutes with
> the loop above — and 19 documents that fail `18_displacement` alone are in reach.

### The run before this one said

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

Accounts share 44% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **2.7 h ago** |
| Scored | **214** of 214 |
| Clean - every applicable check passes | **209** (97.7%) |
| Failing at least one check | **5** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 15:47 → running · 39 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 32 |
| Longest silence | **15.8 min** — from 15:48:37, after `lastmessage.py: running report.py for the numbers` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **4 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **33 min** | `###################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| other - not attributed to a tool | **0 min** | `#` |

The unattributed row is 4 distinct beat(s) that matched no phase. They said:

- `18_displacement -> lead`
- `google-measuring 320 with foot-room engine`
- `re-measuring 320 at HEAD to restore the stored row`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
