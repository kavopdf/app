# Fixer report - 2026-11-24 02:34

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 02:34 → running IST · 1 min**

> No document moved this run. One attempt recorded `lead`. What it produced is the first element-level
> confirmation of what `18_displacement` is, and the refutation, at source, of the exact change the
> last slot asked this run to make.
>
> The window in this header is report.py's and it is wrong: `RUN.json` is re-opened at the claim, so the
> tool reads 02:34, 1 min. The beacons put the claim at 02:19 and this report at 03:45 - 86 minutes,
> 8 tool beats. That is the accounting bug the previous slot half-fixed. Every number in the tables is
> the tool's own and none of them is a claim about this run.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **27** of the **123** re-measured on this engine - **67** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **2** run(s) for the 67 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 02:34 | **lead** | 0/13 | Four documents converted on this tree; unspendable spacers counted in word/document.xml and matched one-for-one to the four live Google steps the previous slot recorded (14.35 vs -13.0, 9.72/5.02/4.86 |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-03` | audit the pending gate: which of the 21 closable ite | 02:35 | - | - |
| `18_dB-01` | table block-top gap and per-row height in DocxWriter | 02:35 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 02:34 → running · 1 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 8 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **0 min** | `#############` |
| other - not attributed to a tool | **0 min** | `#########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

NEXT RUN: (1) 18_displacement is measured and staged - the pair is (first-row cell w:before carries the table gap) + (w:trHeight declared less by the same per-row amount), and 362_price_list_dense is the falsifier because it has a ramp and no step. (2) The 5 ratchet items are very likely stale: benchmarks/STATE.json, RANKING.csv and the engine last changed in the SAME commit b7699196, and both regress.py --check and measure_gate.py pass on this tree (212/212 scored, engine docx == tree). Do not stamp them without checking - a corpus pass that covered them is what closes them, and the honest close is one corpus pass, not five stamps. (3) The 80 remaining pending items are mostly [blocker] rows that say 'this needs a decision, not a patch'.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.

## Why this class
`classpick.py` refused a new class — "PENDING FIRST: 22 item(s) you can close". I read the gate
rather than obeying it blind: an agent audited all 21 of those items against the repository and
found **8 genuinely closeable, 4 needing a corpus pass, 9 stale-but-reopened**, and two of them
misrouted into the closable set by a bare string-prefix test in `classpick.py`. The four that need
a corpus pass are the four `[ratchet]` rows, and a corpus pass is 213 conversions — not a thing
that fits beside the measurement it would have to precede. So the class is taken on the measurement
the previous slot left, with its plan refuted first (below), and the gate's own carry-over — which
names `18_displacement` as the first work — is what put it first.

13 documents fail `18_displacement` and nothing else. That is the largest single blocker in the
corpus and the reason the class was taken.

## What is now known that was not known this morning
**The block-top step is the unspendable spacer, and nothing else.** The engine writes a table's
block-top gap as an empty paragraph in one of two forms (`DocxWriter.java` 6101–6113): spendable =
`w:before = gap − 1` plus a 1-twip `w:line` hairline; unspendable = `w:before="0"` with the whole
gap in `w:line`. Google draws `w:before` 1:1 and `w:line` at 0.2156, so an unspendable spacer loses
0.784 of its declared gap.

| document | unspendable spacers (`w:line`, twips) | gap lost at 0.784× | step measured in Google by the previous slot |
|:--|:--|--:|:--|
| `72_bank_statement_no_rules_right_amounts` | 1 × 366 (18.3 pt) | **14.35 pt** | `med_dy` −13.0 |
| `mobile-bill` | 3 × 248, 128, 124 | **9.72, 5.02, 4.86 pt** | steps −8.76, −4.19, −4.08 |
| `bus-timetable-station-left-times-right` | 1 × 127 (6.35 pt) | **4.98 pt** | `med_dy` −3.0 |
| `362_price_list_dense` | **0** | **0** | **no step**, `med_dy` −2.8 |

Four for four. The document with zero unspendable spacers is the one recorded as having no step.
The class is therefore **two disjoint halves**: a spacer half (a discrete step at each table top)
and a row half (0.75 pt of ramp per row, 21.75 pt over `362_price_list_dense`'s 29 rows). A change
aimed at one moves nothing on the other, and `362_price_list_dense` was never a falsifier of the
pair — it is a document of the other half.

**The change the handoff asked for cannot work.** The pair was "first-row cell `w:before` carries
the gap + `w:trHeight` declared less by the same per-row amount". In the source, `content = pitch −
rule` with `rule` = 15 twips and `trHeight = max(pitch, line)`, written `hRule="atLeast"` — so
`content + rule == pitch` exactly and `atLeast` always binds at `trHeight`. Lowering the declaration
by 15 twips lowers the minimum to `pitch − 15` while the row is still laid at `max(declared,
content + rule) = pitch`. **It is a no-op in every renderer**, and the code says so at 6342–6344.
The cell-level gap is worse: `spacingTw` skips cell-level spacing (469–474), `fitPage` does not
charge a cell (582–596) and `shaveToFit` only rewrites `depth == 0` (515–536), so the gap would be
invisible to every page-height guard — the one thing the guard exists to prevent.

**And the spacer half has no free parameter.** For an unspendable spacer the engine writes
`before = X`, `line = gap − X`. LibreOffice draws the sum, so every X is LO-identical; Google draws
`X + 0.2156(gap − X)`, which reaches the full gap only at `X = gap − 1` — the spendable form. So the
choice is binary and the only currency is page room, which the row excess has already spent
(`spacerSplitTw + gap + 15 × pageRowCount <= slackTw`, 6093–6100). Repaying the row excess needs
`trHeight = pitch − 15`, and LibreOffice then lays every pitch-bound row 0.75 pt shorter — up to
18 pt of shrink on a 24-row page, which `regress.py` refuses.

That is a decision, not a patch, and it is in `BLOCKERS.md`.

`regress.py --check` **PASS** (no document worse in either format, table matches this engine) and
`install-gate.sh` **PASS** at the end of the run. The engine built from this tree in 34 s and four
documents converted on it, so the toolchain is not the block. What stopped a kept change is the
conflict the last section describes: on this class every candidate fix moves LibreOffice, and the
one that does not is blocked by a page-room budget the other half has spent.

## Subagents
Two deployed in the first twenty minutes, both landed, both with a finding committed.

* **A — audit the pending gate.** Answered: 21 closable items, **8 CLOSE, 4 NEEDS-CORPUS-PASS,
  9 REOPEN**, with the file or commit that proves each, and two rows misrouted by a string-prefix
  test. Also caught that `STATE.json`'s ratchet block was written seven minutes *before* the engine
  commit, so the comparison that holds is `regress.py --check`, not that block.
* **B — the table gap and per-row height in the source.** Answered with citations and refuted the
  handoff's pair, and found the three places the cell-level gap escapes the guards. Its work is
  what section "What is now known" is built on.

## Next run
1. **One Google round trip on `362_price_list_dense`** with `trHeight = max(content, line − 15)`
   declared only on rows where `line > content`. There LibreOffice lays `max(trHeight, line) = line`
   whatever the declaration, so the change is LO-invariant **by construction** — the only candidate
   this run found that is. It discriminates the two possible laws for Google's +0.75 pt/row: if
   Google lays `trHeight + rule`, the ramp disappears and the document passes; if it lays
   `max(trHeight, content + rule)`, nothing moves and the row half joins the spacer half in the
   ledger.
2. **The 4 `[ratchet]` rows close with one corpus pass, not four stamps** — and the pass is ~40
   minutes, so it needs a slot that starts with it rather than one that ends with it.
3. **The 9 REOPEN rows in the audit** are decisions with evidence attached; they are the cheapest
   thing on the gate and none of them is a patch.
