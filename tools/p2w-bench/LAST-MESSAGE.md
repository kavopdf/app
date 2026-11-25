# P2W Fixer - Run Report

**25 Nov 2026 · slot 12:13 → running IST · 1h 09m**

> **415_inline_images** fixed — 89.04 → 0.00. Corpus ratchet clean across 213 documents.

## The one line

The stall two runs blamed on soffice was a **missing scipy in a tool that never calls `main()`**:
every rendered measurement was running on a transform **48x slower** than the one it should use.
Fixed at the point of need. The class that three 280 s calls could not measure now measures **23 of
23 in 82 s**.

## What was found

Two runs, and this run's first sub-agent, put the `screen.py` stall in the renderer. A stack dump at
the stall put it somewhere else:

```
  p2w.py:162 _dt1d  <-  p2w.py:177 edt  <-  p2w.py:541 position  <-  p2w.py:881 measure_doc
```

`user 2m23s`, `sys 1.3s`, no soffice in the stack. `edt()` had taken its pure-Python
Felzenszwalb-Huttenlocher fallback because **scipy was not on the pod**. One real corpus page
(`mobile-bill`, 1754x1241 px at 150 DPI):

| path | time |
|---|---|
| scipy | **1.38 s** |
| exact-fallback | **66.07 s** |

All ten unrendered documents converted in **4.9-6.8 s each**. No document wedges the renderer.

**Why the guard did not fire.** `p2w.py` checks, installs and verifies scipy - at the top of
`main()`. `screen.py` imports p2w as a module and calls `docx()`/`run()` directly, so the guard never
ran. `_ensure_scipy()` now sits at the top of `edt()`, beside the only thing that needs it.

## Before and after, on the real class

`screen.py --class "content-present-partly-displaced"`

| | before | after |
|---|---|---|
| calls | 3 x 280 s | 1 x 82 s |
| measured | 12 prerendered, **0 measured** | **23 of 23** |
| verdict | none, killed each time | `SCREEN FAIL - nothing improved` |

`SCREEN FAIL` is correct: the engine is unpatched, so nothing should improve. The point is that the
instrument answers. The exactness gate still passes, including `C diag(3,4)->5`.

## The class I picked, and why

Not a class - the instrument. Before every attempt the brief asks which documents become CLEAN if it
works; the honest answer was **none yet, and none ever**, because no rendered attempt could complete.
`regress.py --check` and `measure_gate.py` both passed before I started: the gates were healthy and
the pipeline still looked dead, which is the case the brief says to check first. It was the screen
instrument, one layer below where it looked.

## Kept

1. `benchmarks/p2w.py` - `_ensure_scipy()` called from `edt()`.
2. `benchmarks/p2w.py` - a soffice user profile per process. **Not the cause, kept anyway**: a shared
   profile took a 1-page document from 13.9 s to 56.7 s behind a hog, a SIGKILLed parent leaves 3
   soffice processes holding it, and a wedged survivor took a 23-document prerender to **0 of 23 in
   90 s with no error**. Real, and not what stalled the 11:24 run.
3. `FINDINGS/SCIPY-GUARD-BYPASSED-BY-SCREEN-25NOV.md`.

## Not done, and said plainly

- **No document was fixed.** The engine is untouched. The next run has a working instrument.
- **The 11:24 lead (row-pitch dither) is still unjudged.** It is now measurable - the four documents
  it named can be screened in one call - but the slot ran out before it.
- **A 900-page document exceeds 300 s** to convert; the per-document retry names and skips it rather
  than blocking the class.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 6 vs ATTEMPTS.json history 3 |
| Document-moves this run | **0** — 6 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` - taken from the pending list (19 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `content-present-partly-displaced` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:21 | **lead** | 0/0 | Instrument, not engine: edt() ran the 48x-slower pure-Python fallback in every tool that imports p2w instead of running main() - screen.py is one. Guard moved beside the requirement. This class: 3x280 |
| 13:22 | **error** | 0/0 | Hypothesis refuted: a single document wedges the renderer. Probed all 10 unrendered documents individually with a 45 s cap each and a fresh soffice profile: 4.9, 5.1, 5.4, 5.8, 5.8, 5.8, 5.9, 5.9, 6.0 |
| 13:22 | **kept** | 0/0 | Kept, and not the cause of the stall: soffice launched with no -env:UserInstallation, so every launch shared one profile and a soffice orphaned by a killed call held it. Measured: 1-page doc 56.7 s be |

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*One deployed in the first ten minutes: a general-purpose agent root-caused the renderer stall.
It got the mechanism wrong (soffice profile, not EDT) and the defect it found is real and was kept -
but its measurements are what pointed at the renderer, where a stack dump then found the actual cause.*

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 6 vs ATTEMPTS.json history 3 |
| Document-moves this run | **0** — 6 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` - taken from the pending list (19 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `content-present-partly-displaced` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 13:21 | **lead** | 0/0 | Instrument, not engine: edt() ran the 48x-slower pure-Python fallback in every tool that imports p2w instead of running main() - screen.py is one. Guard moved beside the requirement. This class: 3x280 |
| 13:22 | **error** | 0/0 | Hypothesis refuted: a single document wedges the renderer. Probed all 10 unrendered documents individually with a 45 s cap each and a fresh soffice profile: 4.9, 5.1, 5.4, 5.8, 5.8, 5.8, 5.9, 5.9, 6.0 |
| 13:22 | **kept** | 0/0 | Kept, and not the cause of the stall: soffice launched with no -env:UserInstallation, so every launch shared one profile and a soffice orphaned by a killed call held it. Measured: 1-page doc 56.7 s be |

## The txt

| | |
|:--|:--|
| Measured | **1.2 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*One deployed in the first ten minutes: a general-purpose agent root-caused the renderer stall.
It got the mechanism wrong (soffice profile, not EDT) and the defect it found is real and was kept -
but its measurements are what pointed at the renderer, where a stack dump then found the actual cause.*

## Timing

| | |
|:--|:--|
| Slot window | 12:13 → running · 1h 09m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 32 |
| Longest silence | **24.3 min** — from 12:23:19, after `gaps.py: reading the timeline` |
| Silences over 2 min | 10 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **6 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **36 min** | `###########` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **6 min** | `##` |
| other - not attributed to a tool | **19 min** | `######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. Fix or bypass the screen.py soffice prerender hang FIRST - it blocks every rendered attempt. Then judge the dither by share@5 on mobile-bill, electricity-bill, salary-slip-corporate, very-long-single-column-table before a corpus pass.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
