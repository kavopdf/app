# Fixer report - 2026-11-28 05:54

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 05:54 → running IST · 10 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - kept change: 2 code commit(s) in this window, first: findings: 18_displacement is a 0.6pt line box, a vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; subagents: 2 deployed vs no FINDINGS filename carries 63_tB-02 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (62 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## Why nothing moved, in this run's own words

> No engine change was made, and that is the decision, not an overrun.
>
> Two agents were deployed in the first twenty minutes and both landed a committed finding. Between them
> they closed the question this run was set up to answer, and the answer was "do not make the change".
>
> Agent A (18_displacement) proposed: the row's top edge is invented from a pitch while the cell's
> baseline is written from a box, so text lands (1 - LINE_BASE) x before low; fix it by writing
> w:before = 0 and w:line = the row's pitch. Its evidence was LibreOffice, +3.70 pt on
> 35_four_typefaces_one_page.
>
> I read the .docx the engine actually writes for that document and for 71_invoice_space_aligned_no_rules,
> and the pair is already self-consistent: before = 368 tw, w:line = 12 tw, and the renderer puts the
> baseline back at before + 0.8 x box = 18.88 pt, which is the position the engine chose. The anomaly is
> not `before` at all - it is that `w:line` is 12 twips, a 0.60 pt exact line box under a 12 pt font. The
> baseline is 96% `before` and 4% box, so a renderer that floors a sub-glyph exact line box moves the text
> by a constant and never by a ramp. That is exactly the constant +0.62..+4.72 pt agent B measured, with no
> drift, on a table at the top of a page and a table 210 pt down it.
>
> Agent B settled the other half in the same hour: ROW_RUNG_UNDER_TW is a deliberate Google compensation,
> not a bug. Two later attempts to revert it are on record and 6865f403 measured that rung = 0 drops both
> cross-checked documents from 47/47 to 46/47 in Google. So the row rung stays.
>
> Landing agent A's fix would move every cell's baseline in GOOGLE by 18.40 pt on one document and 17.40 pt
> on the other - in the renderer the score is taken in, on rows Google currently reads at med_dy 0.1, 47/47.
> That is not a fix, it is the same LibreOffice-looking trade the rung history records twice. The gate
> would be right to refuse it and I would have spent the slot producing a commit that had to be reverted.
>
> So the attempt is recorded as `lead`, and the next attempt is named: the candidate is `w:line`, not
> `w:before` - give the cell the font's natural line box and move the identical difference into `before` so
> the baseline is preserved by construction, and neither term is sub-glyph. That predicts a zero move in
> Google if and only if Google is already preserving the baseline today, and it is falsifiable in one
> document.
>
> What this run leaves behind: three committed findings (two agents, one mine), one attempt recorded as a
> lead with its next step named, and a class that will not be re-tried along a dead axis.
>
> The gap I could not close in the slot, stated plainly: there is no Google export of
> 35_four_typefaces_one_page anywhere in the repo, so the Google side of every number above is the recorded
> verdict (med_dy 0.1, 47/47), not a measurement I took. The next run should take one before it trusts the
> w:line hypothesis.

### The run before this one said

> **Something did move: two documents, measured through Google.** This section is here because the tool
> asks for the reasoning, not because the run was empty.
>
> **The choice, and its reason.** `classpick.py --leverage` prices `18_displacement` at 46.6 clean
> documents and `60_text_column_right_edge` at 23.63. I took `60` and not `18`, and the reason was not that
> `60` looked easier: `60`'s population was exact: 62 documents, one mechanism, one file, and a census of all 62 could be
> measured inside the slot. `18`'s 108 failing documents split across at least three sub-constructs - a
> rigid offset (12), a per-run tail (6) and the page-break drop (18 multi-page) - so no single mechanism was
> established for it and an attempt would have been a guess at which one. **Before the attempt I asked which
> documents become CLEAN if this works: two.** Both did.
>
> **And a correction to my own reasoning.** I first wrote that `18`'s 46.6 was untrustworthy because it
> disagreed with the store's 108 failing / 18 alone. It does not disagree: 46.6 is `sum(1/len(failed))` over
> the 108 and reproduces exactly, and the same is true of `60`'s 23.63. **`--leverage` is a ranking, never a
> yield** - the document count behind 46.6 is 18 solo plus 28 solo-plus-one, and behind 23.63 it was 2. I
> recorded the wrong reason and am correcting it rather than leaving it to mislead the next run.
>
> **What the attempt was.** `60` reads the bbox of a MuPDF "line" object as a column's right edge. Google's
> PDF export puts a whole table row in one such object, so the check read the right-hand cell's edge as the
> left-hand column's overrun. The engine writes no right edge at all (`w:pgMar w:right="0"` on 62 of 62), so
> this was never an engine defect. The fix splits a line at its cell gutters. Threshold measured, not tuned:
> the 0.5-2 pt band is empty over 5,843 gaps.
>
> **Proved wrong first.** The before column is an independent script that reimplements the shipped
> predicate and the split side by side, not the file I edited. It FAILs all three probe documents on the
> shipped predicate and passes them on the split; the patched `gverify` then scores the same export PDFs
> 47/47 on two of them. Census of all 62: 0 pass->fail, because a split can only shrink a box.
>
> **The second attempt was a refutation, and that is the run's other product.** The corpus's `18_displacement`
> spacer model (`shift = 0.961*gap - 0.58`) was taken on an engine two revisions old. Re-taken here it is
> `0.2288`, and the page-break leg is binary (a flat -59.03 pt at every gap value), so the proposed inverse
> correction is worth **zero documents**. That is a run not spent later. The lead it leaves is different and
> better: the displacement accumulates up the page (`dy = -8.44 - 0.027*y`), which is `w:lineRule="exact"`
> clipping one line at a time, and the engine already has a mode switch for it that was measured at the same
> magnitude and **never taken to a verdict**.
>
> **What stopped this run was not the clock.** The pipeline rotated to `measure` while I was writing up and
> `--claim-fixer` now refuses. The kept change was committed, measured and pushed before that happened
> (`620dc85e`, `30121a9a`).

Accounts share 16% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **37 min ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-01` | root cause of cell displacement; landed c8056b8 | 06:04 | - | - |
| `63_tB-02` | ROW_RUNG_UNDER_TW bug or compensation; landed 0b15dc | 06:04 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 05:54 → running · 10 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 14 |
| Longest silence | **6.0 min** — from 05:57:09, after `relay: verifying gate health` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **6 min** | `################` |
| record - attempt, handoff, class rows | **0 min** | `##` |
| report - the report and the chain | **0 min** | `##` |
| other - not attributed to a tool | **0 min** | `##` |

The unattributed row is 3 distinct beat(s) that matched no phase. They said:

- `relay: both agents landed, implementing cell-top fix`
- `relay: verifying gate health`
- `relay: writing the report`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
