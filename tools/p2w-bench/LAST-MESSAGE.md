# P2W Fixer - Run Report

**22 Nov 2026 · slot 09:51 → running IST · 15 min**

> No change was kept this run — and the lead the last run left is now **half settled and half
> refuted**, measured in Google rather than reasoned about. The spacer construct still works. The
> row-height construct the last run told me to build cannot work as described, and the row excess it
> was meant to remove is in a different place than anyone thought.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 10:06 | **lead** | 0/3 | Three constructs built together and measured in Google on three documents: the table spacer as w:before + hairline w:line=1, the 2880→4320 twip cap, and a hairline cell box for sizeless single-line cells. `68_journal` **42/42 clean**; `mobile-bill` and `insurance-policy-schedule` **38/42, two pages** — a regression on HEAD's 41/42. Reverted. |

## The class, and why it was this one

`classpick.py` said `18_displacement`, "holds an open LEAD and nothing outranks it". That is the
reason and I took it: 38.7 clean documents, the largest single check in the corpus, 16 documents
failing it and nothing else, and a construct measured in Google last slot. No override.

## The row excess is not 0.70 pt/row, and it is not the cell box

The 10:05 instruction was explicit: land the spacer **and** scale the row height by 0.9634
(18.40/19.10), "measured, NOT the 0.9785 in the 08:20 finding". I built the spacer and refused the
scale, on two independent reads of the emitter. Then I measured the pitch off the Google export of
`mobile-bill`, from the rule positions on page 1:

| | source | Google, this build |
|:--|--:|--:|
| median row pitch | **18.40 pt** (24 of 26 gaps exactly 18.4) | **19.00 pt** |
| pitch histogram | 18.4 ×24 | 19.0 ×16, 20.0 ×5, 18.0 ×3 |

The engine writes these rows 360/360/380 twips repeating — 18.0/18.0/19.0, the `floor(18.4k)`
quantisation. Google lays the 380 rows at 19.0, as it should, and grows the 360 rows to 19.0 and
**20.0**. Two things follow:

- **The 0.9634 scale is inert.** Under `hRule="atLeast"` the written `w:val` is a floor and the row
  is laid out at `max(val, content)`. Every row Google grows is a row whose floor is *below* its
  content, so scaling the floor down changes nothing; it would only shrink the two rows in the corpus
  whose floor genuinely binds (`370_offer_letter` 620 tw, `table-with-rotated-header` 1480 tw). I
  have recorded this as a withdrawal of the instruction in `LAST-MESSAGE.md`, with the arithmetic.
- **The cell box is 14 % of it, not the cause.** The hypothesis I built the third edit on was that
  Google prices the cell's `w:line` as a multiple of the face's line height —
  `(w:line/240) × 1.164 × size` — which reproduces 19.1003 pt on an 18.40 pt pitch exactly. But these
  cells were **already** hairline boxes before the edit: `w:before="194" w:line="10" exact` is 9.70 pt
  of before and a 0.53 pt box, a charge of **10.23 pt** against an 18.40 pt floor. A cell charging
  10.23 pt cannot grow an 18.40 pt row. Rewriting the pair moved the rendered pitch **0.10 pt**
  (19.10 → 19.00), not 0.70.

The growth concentrates where the evidence points: rows holding a cell with **two paragraphs**.
`mobile-bill` rows 5–12 carry 6 `<w:p>` on a 3-column table and render at 20.0; the single-line rows
render at 18.0–19.0. Two paragraphs at ~9.7 pt is ~19.4 pt of content against an 18.0 pt floor, which
is 2.0 pt of growth on exactly those rows. Those are the rows my cell guard deliberately skipped
(`rowParts == 1`), because there the box *is* the line advance and a hairline would collapse the two
lines onto each other. **The next build has to reach the multi-paragraph path.**

## Why it was reverted

`mobile-bill` and `insurance-policy-schedule` were 41/42 at HEAD and came back **38/42 with two
pages** — `01_page_count`, `18_displacement`, `32_stroke_lines`, `55_orientation_mix`. A change that
makes a document worse is not a fix. The spacer construct is correct and still takes `68_journal` to
**42/42**; it cannot land until the row excess on those two pages is removed, because before this
change Google was *under*-spending the spacer by ~19.5 pt and that slack was absorbing the row
overflow.

The engine is back at HEAD. Nothing in the corpus, the tables, the branches or the Drive was touched.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-04` | every place the engine emits trHeight/hRule, and whether 0.9634 belongs on w:val | 09:56 | 09:59 | 2 min |
| `18_dB-03` | given the real `DocxWriter.java`, which emitted number Google ignores when it grows a row | 10:00 | 10:05 | 5 min |

Both landed and both changed the plan. Agent A was given the wrong sandbox (it found a different
checkout and could not see the engine), but its OOXML reading was still correct and it was the first
to say `atLeast` makes `w:val` a floor. Agent B had the real file and produced the
`(w:line/240) × 1.164 × size` mechanism that reproduces 19.1003 pt — **the measurement then refuted
it**, because the cells were already hairline. That is the most useful kind of wrong: it is a
falsified hypothesis with its arithmetic on the record, and the next run does not have to build it.

## Timing

| | |
|:--|:--|
| Slot window | 09:51 → running · 15 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **6.4 min** — from 09:55:15, after `building engine (~2 min)` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **4 min** | `######` |
| measure or build - a conversion, screen or compile writes no beacon | **6 min** | `#########` |
| record - attempt, handoff, class rows | **3 min** | `#####` |
| report - the report and the chain | **0 min** | `#` |

**The instrument is wrong and this row is why.** Wall clock for this slot was 49 minutes, not 15. The
beat counter stops at the last heartbeat, and the two steps that took the most time — converting 16
documents through 16 JVMs, and nine Drive calls to render three documents in Google — write no beacon,
so they are invisible to it. The 3 min in "record" is likewise the tool's own floor. The row is
reproduced verbatim because `lastmessage.py` checks it against `report.py`, and that check is right to
exist; what is wrong is the number it checks. A fixer that renders in Google will always under-report
here until `gverify.py` and the `ConvertOne` loop write a beat per document.

## What this run leaves behind

A finding, `FINDINGS/18_displacement-cellbox-REFUTES-ROWSCALE-1035-f1x.md`, that withdraws the
0.9634 instruction with the arithmetic and the pitch histogram that refute it, refutes the cell-box
mechanism with the emitted pairs and a 0.10 pt movement where 0.70 was predicted, and names where the
excess actually lives — the multi-paragraph cell path, 2.0 pt per wrapped row.

Three probe Google Docs created and deleted; `KavoPDF-Verify` is empty.

**Next run:** do not build the 0.9634 scale, and do not build the hairline cell box for single-line
cells — both are measured inert. Build against `rowParts > 1`: either raise the row floor to the true
368 twips so floor and content agree instead of the floor being quantised 8 twips low, or take the
`w:before` off the continuation paragraphs inside a wrapped cell. Prove it on `mobile-bill` and
`insurance-policy-schedule` first — they are the only two documents blocking a construct already
measured to take 6 documents clean.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv, or measured this run off the corpus PDF and the Google export. Never remembered, never estimated.*
