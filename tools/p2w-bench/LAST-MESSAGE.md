# P2W Fixer - Run Report

**22 Nov 2026 · slot 03:14 → running IST · 47 min**

> The lead the handoff carried for four slots is dead, and this run is what killed it. The carrier
> patch is a real Google win and it cannot land: it takes 54 documents the wrong way on the proxy.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

"Regressions: none" is true of the tree, and only because the change was reverted. The pass measured
54 documents worse. None of them shipped.

## What this run did

The slot was free when I arrived. The run before me claimed at 02:09, beat once, announced "16 Google
exports downloaded; scoring the 42 checks" and went silent for 69 minutes; its Google measurement
survived it and was already committed. What I inherited was the handoff's instruction to apply
`rule-carrier-horizontal-only-2008.patch` and spend the slot on the 213-document pass.

I did that. Applied the patch, built the engine, converted 213 documents and scored 212, then ran the
gate.

    docx: 58 REGRESSION(S) ... REFUSED. This commit would land a regression or an unmeasured engine.

## The instrument was tested before the verdict was written

The prediction, written first: if the regressions are the patch's, HEAD's engine reproduces the
committed baseline on the same documents in this sandbox; if they are the instrument's, HEAD reads the
same bad numbers.

HEAD reproduced the baseline on all three regressed documents I control-tested, to the digit. The
patched engine moved the same three by 8 to 98 share@5 points. The patch is the cause. The evidence,
the three control numbers and what would prove this wrong are in
`FINDINGS/32_stroke_lines-CARRIER-54-REGRESSIONS-0400-f1x.md`.

The same control caught a second, older lie: `415_inline_images` scores 0.00 on a fresh HEAD render
against 89.04 in `RANKING-BASELINE.csv`. My own first reading of this pass said "52 better, 0 worse"
because `benchmarks/RANKING.csv` is copied by hand from `/scratch/output/RANKING.csv` and had not been
replaced — I was comparing an older engine's table and calling it this run's. `regress.py --check`
passes that, because the stamp moves and the table does not.

## The cause, which is the part worth keeping

Counting the floating carriers each document actually received in the patched `.docx`: regressed
documents carry a median of 9, unchanged ones 1, and 14 of the 16 target documents — the ones that stay
clean — carry 2 to 3. The horizontal guard removed the verticals; what is left still contains the
horizontal table separators, and a floating table nested inside a table cell displaces the cell's flow.
A document with 21 carriers is not a page with 21 rules.

The narrowing is one predicate, not a cap: a band that sits on a table cell or row edge, or on a stamp
frame, gets no carrier. The test that decides between that and "the proxy is over-weighting a construct
Google honours" is in the handoff: Google-score the three regressed documents I control-tested. That is
the measurement this slot did not have time for, and it is the whole question.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

Measured on this engine rather than assumed: `restamp_txt.py --run` scored all 213 in 34 s and came
back with 0 newly clean, 0 newly failing, 213 unchanged, and `RANKING-TXT-BASELINE.csv` byte-identical.
The carrier does not touch the .txt anywhere in the corpus, not only on the 16 the last run checked.

## Subagents

*None deployed this run, and that is a decision, not an oversight.* A scheduled run has no later turn
for a background result to arrive in, so a subagent runs inside the slot — the 01:53 run measured one
at seven minutes of a forty-five minute window. This slot had a pass to run and a falsification to
finish; the falsification was done directly, in two bash calls and a control test, in about four
minutes.

## Timing

| | |
|:--|:--|
| Slot window | 03:14 → running · 47 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 13 |
| Longest silence | **23.9 min** — from 03:36:51, after `report.py: building the report` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

The longest silence is the rebase: another run claimed the slot at 03:59 and pushed bookkeeping commits
while I was mid-pass, and the merge of `ROUND.json` and `ATTEMPTS.json` took that long to resolve
without discarding either run's record.

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **18 min** | `#########` |
| measure or build - a conversion, screen or compile writes no beacon | **23 min** | `############` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |

The pass is the slot. Four conversion slices and four measurement slices, each under the five-minute
call limit, and there is no way to stamp an engine without it.

## One thing that is not mine to fix

Another run claimed the slot at 03:59 while I was mid-pass. I did not release the claim at the end:
releasing a slot I do not hold would hand a live run's work to whoever fires next. Two runs overlapping
one slot is the relay's own failure mode, and the heartbeat that keeps a claim alive is written by any
caller, not only the owner — the same defect `BLOCKERS.md` already records for 21 Nov.

## Next run

Do not apply `rule-carrier-horizontal-only-2008` as a global substitution. Either Google-score
`08_two_overlapping_stamps`, `50_invoice_coloured_total_row` and
`product-catalogue-code-left-price-right` — if Google is clean, the 54 are an artefact of nested
floating tables and the predicate needs no narrowing — or narrow `isRuleShape` so a band on a table cell
edge or a stamp frame gets no carrier, and screen the 54 before spending a corpus pass.
