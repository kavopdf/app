
# P2W Fixer - Run Report

**20 Nov 2026 · slot 05:51 → running IST · 30 min**

> No change was kept — and this run found out why four runs could not keep one. The rule class
> is not blocked by the engine any more. It is blocked by the gate: the fix Google needs is
> always a small LibreOffice regression, and the brief forbids landing one.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.44%** — mean 6.15 → 3.72 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |
| Committed | **14** files in 1 commit(s) from `17bc575` — ...-displaced-rules-are-flow-neutral-065000-f1x.md, ATTEMPTS.json, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, REPORT.md, ROUND.json, RUN-HISTORY.json, RUN-LOG.md, RUN.json, TIMELINE.jsonl, TRACE.md,  |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:53 | **reverted** | 0/23 | attempt 12: rules flush-by-top re-applied + ctx.flowY residual test (flowY left at s.topPt vs carrier-bottom) on 18_centred |
| 06:20 | **reverted** | 0/23 | attempt 13: rule as the FOLLOWING paragraph's w:top border, found by a pre-pass, no reordering, no extra paragraph - flow-neutral, measures exactly baseline on 8/8 documents (18_centred 0.00, bank-sta |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 05:51 → running · 30 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **27.2 min** — from 05:53:11, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | The fixer run that claimed the slot at 05:17:58 IST (23:47:58 UTC) beat until 05:18:43 IST, committed `6dfe946 |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **27 min** | `####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FINDINGS/content-present-partly-displaced-rules-are-flow-neutral-065000-f1x.md BEFORE TOUCHING THE RULE CLASS. Two handoff claims are now measured FALSE: (1) the flush-by-top precondition is a regression, not a precondition - with the border path OFF it takes bank-statement 0.10 -> 17.07 and gst-invoice 0.38 -> 15.13, because every shape moved into the flow charges ~9.6 pt; (2) the residual on 18_displacement was never the gap or the flowY bookkeeping - a carrier paragraph costs 9.6 pt in LibreOffice whatever it contains (measured four ways), which is the whole of 0.00 -> 77.01. A flow-neutral construct exists and is in FINDINGS/rules-top-border-FLOW-NEUTRAL-065000-f1x.patch: a pre-pass hands each rule to the paragraph that follows it as a w:top border, the gap becomes w:before and the rule-to-text distance becomes w:space, nothing is reordered and no paragraph is added. It measures EXACTLY baseline on all 8 documents tried (18_centred 0.00, 411 0.00, 62 0.00, bank-statement 0.10, gst-invoice 0.38, mobile-bill 1.55, 315 1.91, 64 3.46) - and places pBdr=0, because its own safety guards decline every rule it could reach. Where a border IS placed, 18_centred goes 0.00 -> 0.53. THAT is the wall and it is not an engine bug: regress.py scores share@5 on a LibreOffice render, LibreOffice draws the floating drawing exactly, and a border can never be pixel-identical - so a fix Google needs is always a small LibreOffice regression, and the brief forbids landing one. DO NOT start another rule-class attempt until a human answers: gate this class in Google (32_stroke_lines / 05_chars_extra on the Google result), declare the class out of scope, or authorise a stated tolerance. Spend the next slot on a class the gate can see.
## The two claims this run measured and found false

**The flush-by-top change is not a precondition. It is the regression.** The handoff called it
PROVEN on the strength of one document with two rules. With the border path switched off, so only
the reordering is active, it takes `bank-statement-horizontal-rules-only` from **0.10 to 17.07** and
`gst-invoice-horizontal-rules-only` from **0.38 to 15.13** in LibreOffice. Every shape moved into the
flow becomes a paragraph, and a paragraph in this document costs the flow **9.6 pt**.

**The residual on `18_displacement` was never the gap or the flowY bookkeeping. It was the carrier
paragraph.** Measured by editing the emitted XML and re-rendering, one variant at a time, on
`18_centred`: carrier as written +10.60; carrier with the `w:pBdr` made inert +10.40; carrier with no
run at all +10.60; carrier with `w:line="20"` +11.60; **no carrier at all +1.00**. An empty `<w:p>`
with `w:line="1"` and `w:sz="2"` costs 9.6 pt. That is the whole of `0.00 → 77.01`, and it means the
pBdr-carrier construct can never be flow-neutral in any renderer.

## What is now built and measured

A flow-neutral construct, saved as `FINDINGS/rules-top-border-FLOW-NEUTRAL-065000-f1x.patch` (231
lines, applies to `4e61dfd`): a pre-pass hands each rule to the paragraph that follows it as a
`w:top` border, the gap down to the rule becomes the paragraph's `w:before`, and the rule-to-text
distance becomes the border's `w:space`. Nothing is reordered, no paragraph is added, and a rule that
cannot be placed keeps the drawing it always had. It measures **exactly the baseline on all eight
documents it was tried on** — `18_centred` 0.00, `411` 0.00, `62` 0.00, bank-statement 0.10,
gst-invoice 0.38, `mobile-bill` 1.55, `315` 1.91, `64` 3.46.

It places **zero** borders on those eight. That is not a bug: the guards that keep it from moving ink
are the same guards that decline the rules it could reach — the rule's edges must agree with the
paragraph's indents within 1.5 pt, the border's `w:space` cannot exceed 31 pt, and the flow must have
reached the rule. A no-op is not a fix, so it is reverted, and the patch is kept so the next run
starts from a working skeleton.

## The wall, which is the actual finding

Where a border *is* placed — correct y, correct weight, text within 2 pt — `18_centred` goes
**0.00 → 0.53**. `regress.py` scores `share@5` on a **LibreOffice** render; LibreOffice draws the
floating `<w:drawing>` exactly where the PDF drew it; a `w:pBdr` can never be pixel-identical to it.
So every document whose rules are already right in LibreOffice must get worse the moment its rules
become borders, however well they are placed — and those are exactly the documents the gate checks.
The 145 documents that fail `32_stroke_lines` are the ones **Google** drops, and Google is not what
the gate measures.

That is not an engine defect and no further attempt will clear it. It needs a human decision, and
`HANDOFF.md` now says so in as many words: gate this class in Google, declare it out of scope, or
authorise a stated tolerance. Four runs have now spent themselves here.

## Why the slot was claimed from a dead run

`round.py --phase` said `fix`, and `--claim-fixer` refused with "last activity 0 min ago". The run
before this one (04:59) wrote its report and never released: `RUN.json` still had `ended_ts: null`
and the timeline had no event after 05:18:43. The "0 min" was my own `--phase` call refreshing
`TIMELINE.jsonl` — `claim()` takes the newest of the slot, its beat and that file's mtime. With the
dead claim cleared, the claim archived the previous run's record into `RUN-HISTORY.json` as
`killed - never released the slot`, which is what it was.

## What the tables cannot show

The honest summary is that this run bought no documents and closed a question. Three runs in a row
rebuilt the same flush-by-top precondition because the handoff said it was proven; it was proven on a
document with two rules, and it costs 15 to 17 `share@5` points on a document with a rule per row.
That is now a number in a finding file instead of a sentence in a handoff.

The construct is the part worth keeping. When someone decides how this class is to be judged, the
patch applies and the mechanism is measured: a border that spends a gap the paragraph was already
spending costs the flow nothing, and the eight-document table above is the proof that it can be added
without moving a point of ink.


## Why no subagents were deployed

Two background agents were the plan and neither was deployed: the run's whole budget went into
measuring one construct seven ways, and a background agent started at that point would have
outlived the turn — and a run that stays `running` on the platform blocks every later run, which is
what cost three hours on 19 Nov. The slot is released with `--force` for that reason, not because
there was nothing to ask. The two questions worth handing over are in `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

