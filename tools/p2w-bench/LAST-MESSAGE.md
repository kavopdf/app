# P2W Fixer - Run Report

**25 Nov 2026 · slot 11:24 → running IST · 41 min**

> No change was kept this run. The numbers below say what was tried.


## The one line

One attempt, recorded as a **lead**: a proposed row-pitch dither was applied alone and measured on
the engine's own output, it **fires** - and it was **not committed**, because the instrument that
judges a rendered change hangs.

## What the run actually did

The slot was **stale, not taken**: origin's claim was 51 minutes since its last beat, stale after
45, so this run took it and pushed the claim (3cf7c4da).

1. **The pod was cold and the gate could not run.** `install-gate.sh` timed out at 300 s because
   `regress.py --check` builds the corpus itself, in 240 s slices. Two `corpus-slice.py` calls took
   the corpus from 148 to **213 of 213 converted** and wrote the stamp for engine `981ff1fa35e2cf67`;
   `regress.py --check` then passed in seconds. The gate was never broken - it had nothing to read.
2. **One sub-agent** (Explore) read `DOCS-ROOT-CAUSES-24NOV.md`, the 18_displacement findings and
   `DocxWriter.java`, and returned a two-part patch plus two corrections: the `0.961 x gap - 0.58 pt`
   law is the **page-top** law, not the spacer law, and the repo holds **three mutually
   inconsistent laws** for `w:line ... exact` on an `sz=2` empty paragraph (21.5 % of the ask on
   22 Nov, a flat 5-10 pt on 24 Nov, 91-95 % on 23 Nov). They cannot all be true.
3. **The spacer half was never applied.** It removes the `spendable` budget guard and bets the page
   budget on a construct whose behaviour is not stably known. That is a trade, not a fix.
4. **The row-pitch half was applied alone and measured.** Guard:
   `exactRows && rowCapTw < 0 && !t.recut && ctx.squeeze == 1f && ruleTwHere > 0`. A/B on the
   engine's own output, same three documents, two builds differing only by the patch:

   | document | unpatched `w:trHeight` (tw) | patched (tw) | in pt |
   |---|---|---|---|
   | `mobile-bill` | 360, 360, 380, 360, 380 | 343, 343, 363, 343, 363 | 18.0/19.0 to 17.15/18.15 |
   | `salary-slip-corporate` | 380, 360, 380, 360, 360, 380 | 363, 343, 363, 343, 343, 363 | -0.85 pt per ruled row |
   | `very-long-single-column-table` | 360, 380, 360, 380 | 343, 363, 343, 363 | 18.0/19.0 to 17.15/18.15 |

   The dither spreads its rounding as designed - the alternation survives - but the whole ladder
   drops by the asserted 0.875 pt rule charge. That is correct **only** if the renderer charges the
   row's border on top of the declared height. The engine's own comment records a 0.5 pt variant of
   this change making `18_displacement` **worse**; this one subtracts 0.85 pt on the same documents.
   The sign depends on a renderer charge known for Google and unmeasured for the proxy.

## Why it is a lead and not a kept fix

`screen.py --class "content-present-partly-displaced"` converts all 23 documents and then **hangs in
the soffice prerender**: 12 in the first call, nothing in the second, `prerender 1 docx` and no
finish in the third - three 280 s calls, no result, no error. No render means no share@5 before and
after, so the change cannot be measured, `regress.py --check` cannot be satisfied for a rendered
table change, and committing it would break non-negotiable 2. Logged in `BLOCKERS.md`.

`regress.py --check` and `measure_gate.py` were both run: **the gates are not what refused this
run.** The screen instrument is.

## Written down

- `FINDINGS/18-DISPLACEMENT-ROW-PITCH-DITHER-25NOV.md` - the A/B, the three inconsistent laws, the
  four documents the next run should judge it on.
- `BLOCKERS.md` - the soffice prerender hang, with what was tried.
- `HANDOFF.md` - the picture in prose.




## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - subagents: 1 deployed vs no FINDINGS file for Expl-01 |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **could not be read** - 0 of 213 scored were read as current, which is a failed read and not a measurement. No count is stated rather than a zero |
| Who re-measures them | the **:20 gverify** cron, once the read works |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 213 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` - taken from the pending list (17 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `content-present-partly-displaced` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 12:03 | **lead** | 0/23 | row-pitch dither (error-diffused w:trHeight, -0.85 pt rule charge) applied alone and A/B measured on the engine's own output: it fires, shifting declared pitch 18.0/19.0 -> 17.15/18.15 pt on mobile-bi |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 11:45 | **lead** | 0/14 | annotation /Contents is not body text: the saved patch (PATCHES/600-annotation-runs-subtype-25NOV.patch) is measured on 600 (verify_txt 7/12 -> 8/12, t12 invented words 20 -> 0). Not landed because an |
| 11:48 | **lead** | 0/14 | t12 root cause, measured independently on all 8 failing docs: 258 of 310 excess tokens are U+FFFD where the page draws fi/ff ligatures, in 041122-Account_Opening_Form (127 in txt, 86 in the .docx) and |
| 11:51 | **lead** | 0/122 | signature measured from all 213 Google verdicts: 122 documents fail 18_displacement and ALL 122 have render-source > 0; 108 of them by exactly +1.0 (median 1.0). One construct, not 108 defects; 416_ma |

## The txt

| | |
|:--|:--|
| Measured | **52 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `Expl-01` | Explore: 18_displacement row-pitch dither + three in | 12:05 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 11:24 → running · 41 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **8.5 min** — from 11:37:14, after `pending.py: reading the pending gate` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **1 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **21 min** | `#############` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
| other - not attributed to a tool | **11 min** | `#######` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 14 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. Fix or bypass the screen.py soffice prerender hang FIRST - it blocks every rendered attempt. Then judge the dither by share@5 on mobile-bill, electricity-bill, salary-slip-corporate, very-long-single-column-table before a corpus pass.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
