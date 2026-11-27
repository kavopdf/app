# Fixer report - 2026-11-28 03:24

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 03:24 → 03:28 IST · 3 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - kept change: 1 code commit(s) in this window, first: fixer 28nov 03:24: the 84 regressions are one co vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (64 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 03:24 | **lead** | 0/None | Bisected the 84-regression cluster to one constant: ROW_RUNG_UNDER_TW=10 (8fb4f503). -Dp2w.rung=0 restores 6 of 6 probed table documents (table-with-no-header-row 47.48->0.61, electricity-bill 36.78-> |

## Why nothing moved, in this run's own words

> The gate's regressions are not five constructs. They are one constant, and this run bisected them to it.
>
> The last three reports said the 84 LibreOffice regressions were several unrelated constructs and that no
> single patch would move them. That was never measured; it was inferred from the class table. So I stopped
> inferring and bisected the engine the way you bisect any regression: build the tree at each commit, score
> one document, watch the number. `table-with-no-header-row` sits at the baseline score for four commits in a
> row and jumps to its full tree score at exactly one of them. That commit is the table work of 27 November.
>
> It went in as two rules at once, so the second question was which half did it. Both were made switchable
> and measured separately, and only one of them moves anything: the rule that declares a pitch-bound table row
> ten twips under its own pitch. Turning that rule off returns every table document I probed to its baseline
> score, and five of the six come out better than the baseline rather than level with it, because the other
> engine work since 15 November is real and the rung was hiding it. The gap rule from the same commit is inert
> on both documents I tested it on.
>
> So the answer to "what makes these documents worse" is now a named constant with a named commit, and the
> probe that shows it costs fifteen seconds a document instead of a corpus pass. That is the thing this run
> was worth.
>
> What I did not do is decide which renderer is right, and I want to be plain about why that matters. The rung
> was landed on Google evidence: its own commit message says it took two documents to a clean sheet in Google
> Docs. Every measurement against it since has been LibreOffice. Under the rule this project is built on -
> Google is the truth and LibreOffice is a proxy - a change that is right in Google and wrong in the proxy is
> not a regression at all, and a tenth of the "regressed" documents pass every Google check while their proxy
> score rises. That is consistent with the gate refusing on an artifact of the proxy. It is also exactly the
> kind of comfortable story that turns out to be wrong, so it stays a hypothesis: the Google side of this
> constant is unmeasured, and it is two documents wide.
>
> The next run should measure it before it builds anything, because the answer decides two different jobs. If
> the two documents stay clean with the rung off, the constant is pure cost and should go, and the gate
> unblocks by itself. If either one loses its clean sheet, the rung is right and the gate is charging a
> Google-proved construct to a renderer nobody opens - and then the gate is the defect, with a measurement in
> FINDINGS/ to argue from rather than an opinion.
>
> Nothing was kept and no engine line was committed: a change that requires a full corpus re-measurement does
> not fit the slot that found it, and a change measured only in the proxy would be the exact mistake this file
> is warning about. The switches I built were reverted; the tree's engine is byte-identical to HEAD.

### The run before this one said

>
>
> Nothing was kept because the commit gate refuses every engine change, and this run measured what it
> refuses on rather than working around it.
>
> `regress.py --check` returns:
>
> docx: 84 REGRESSION(S)
> REFUSED. This commit would land a regression or an unmeasured engine.
>
> The 00:58 report calls the gate "unblocked". That is true of one of the tool's two refusals. It cleared
> the fingerprint refusal — the table now names the engine it was measured on — and the regression refusal,
> which is a different message from the same tool, was never cleared and is live now. No engine change can
> land until it is.
>
> The run's real work was to test the lead the last two reports discarded. Both judged `ROW_RUNG_UNDER_TW = 0`
> by comparing it against `benchmarks/RANKING.csv`, which is the rung=10 tree's own output; that comparison
> can only ever report that rung=0 is worse than rung=10, which is not the gate's question. Against
> `RANKING-BASELINE.csv`, the 15 Nov state the gate actually compares to, rung=0 is a net improvement:
> 57 documents worse than baseline instead of 84, 64 better instead of 47, and exactly one document newly
> worse (`marksheet-subject-left-marks-right`, 4.55 → 5.21, where rung=10 gives 2.15). The rung=0 table's
> stamp was re-derived by hashing the tree with only that constant changed, so the table is a measurement of
> the tree and not of some other state.
>
> That still does not unblock the gate — 57 is a refusal — but it changes what the next run should build:
> the remaining 57 are five constructs, not one constant, and the largest coherent one is stamps, ten
> documents whose names all carry `stamp`. A per-row rung would keep the one document the constant earns
> and release the 28 it costs.
>
> The run did not get to a build. The pod was warm but 18 documents short of a converted corpus, and
> diagnosing the stamp cluster properly is more than the slot allowed after the gate measurement. It stopped
> at the measurement and recorded it, rather than starting a patch it could not prove.
>
>
>
>
> **The gate was the work, and it is now honest.** For the last several runs `regress.py --check`
> refused every commit with one line:
>
> ```
> ENGINE CHANGED (docx): table measured on d28ca7516c3f9165, the tree is a05b20eb05fe0fc8
> An unmeasured change is not a pass. Re-measure, then --stamp.
> ```
>
> That was true and nobody had acted on it: `benchmarks/RANKING.csv` described an engine two
> commits behind the tree, so no fixer could land anything, and no fixer could see it either.
> `measure_gate.py` said NOT READY for the same reason.
>
> This run re-measured the corpus on the tree the repository actually has: `p2w.py --budget 250`
> called repeatedly, resumable, 213/213 scored (1 exempt, `416_many_tiny_pages`). The table is
> committed and the engine is stamped. `regress.py --check` now reads the tree instead of refusing
> to look at it.
>
> **What that cost, stated plainly.** The table it replaced was 82 documents optimistic. On the tree:
>
> | document | table said (d28ca751) | measured on the tree (a05b20eb) |
> |:--|--:|--:|
> | `table-with-no-header-row` | 0.61 | **47.48** |
> | `boq-tender-bill-of-quantities` | 0.62 | **41.95** |
> | `electricity-bill` | 1.33 | **36.78** |
> | `very-long-single-column-table` | 2.38 | **41.14** |
> | `balance-sheet-and-profit-loss` | 0.21 | **36.69** |
>
> Mean 3.71 → 7.68, documents at zero 76 → 49, 73 of 212 worse than the 15 Nov baseline. The
> regression is real, it is in the tree, and it was invisible because the only table anyone read
> was measured on code that no longer exists.
>
> **The lead this points at, and why it is a lead and not a fix.** The previous run reported
> `ROW_RUNG_UNDER_TW = 0` taking `table-with-no-header-row` 47.48 → 0.61 in LibreOffice. Those two
> numbers are the tree's measurement (47.48, measured here) and the *old table's* value (0.61,
> measured on d28ca751). So either the rung is exactly the difference between the two engines, or
> that run read a stale table as its own after-column. Both readings make the rung
> (`DocxWriter.java:54`, introduced in `8fb4f503`) the prime suspect for the largest regression in
> the corpus, and neither is proved. The A/B on the current engine is the next run's first
> attempt: convert with `ROW_RUNG_UNDER_TW = 0`, score, and compare against this committed table,
> not against a remembered one.
>
> I did not run that A/B because the re-measure consumed the slot: 213 documents at 5.9 s/document
> is 21 minutes of measurement after a cold-pod install, and it is the prerequisite for *any*
> change being landable. Recorded as `18_displacement` attempt 119, outcome `lead`.
>
> Accounts share 17% of their significant words - a different account (the cut is 50%).

Accounts share 21% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **46 min ago** |
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
| Slot window | 03:24 → 03:28 · 3 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 11 |
| Longest silence | **2.0 min** — from 03:25:50, after `pending.py: reading the pending gate` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **2 min** | `#################` |
| report - the report and the chain | **0 min** | `#####` |
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
