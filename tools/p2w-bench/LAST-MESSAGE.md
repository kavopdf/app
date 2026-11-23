
  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
# P2W Fixer - Run Report

**23 Nov 2026 · slot 05:58 → running IST · 19 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **28**, out of the 190 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 06:11 | **lead** | 0/None | LO census: 7 docs are one check from clean in the measurable renderer and they are 7 distinct mechanisms. Controlled 3-variant experiment on balance-sheet-two-columns-of-figures: w:trHeight is inert o |
| 06:15 | **lead** | 0/None | Instrumented the row model at DocxWriter.java:6146 (P2W_DBG env, reverted, app/ clean). exactRows is TRUE on all four candidates and the per-row edges ARE used, so the uniform-average path is not the |

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
| `18_dresidual-census-01` | which current-engine documents fail 18_displacement, | 06:17 | 00:47 | 0 min |
| `18_dblast-radius-01` | the exact writer rule for w:trHeight/w:hRule, what t | 06:17 | 00:47 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 05:58 → running · 19 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **5.3 min** — from 06:01:27, after `attempt.py: recording an attempt` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 3 parked, with the evidence to re-open them |
| Still a wall | **The `.txt` half is now a stall past a day and nothing moved it: 197 clean, 16 failing, unchanged since 21 No |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **10 min** | `############` |
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `#######` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **1 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

00_page_count: mechanism MEASURED, fix not landed. FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md. Google rasterises each page-positioned floating shape and keeps the paragraph that carries it, and that empty paragraph costs ~0.83 pt of flow (w:line="1" exact is NOT honoured for it): 108 of them = 89.9 pt on 301_lab_report_panel against 44.5 pt of free page, so a 1-page source renders 2 pages. Deleting all 108 -> 1 page at the same text y (the control). 22 of the 23 refused documents emit ALL their drawing-only paragraphs AFTER the last text paragraph; counts 7..2464. 350_question_paper has 1 and is NOT explained by this. Refuted and measured, do not retry: drop-last, prstGeom-rect, wrapSquare, framePr. VOID (my probe bug, never measured): merge-into-one-paragraph and attach-to-text. NEXT LEVER, cheapest in the writer: merge the drawing-only paragraphs of a page into ONE (DocxWriter.shape(), DocxWriter.java:2726) - saves 107 x 0.83 = 88.8 pt against 89.9 pt needed here, a one-point margin, so measure it; then w:tcBorders through the table writer. This is the same construct as 32_stroke_lines and 05_chars_extra: one mechanism, three check families.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.


## Why `18_displacement`, and why not the Google table

`classpick.py --leverage` prices `18_displacement` at **34.2 clean documents**, the largest single step
in the table. `classpick.py` suggested `t08_line_order` instead, on the strength of one prior attempt
that moved 9 documents. I did not take it: this class is worth 34.2 and the suggestion was a record of
where the last run stopped, not a measurement of what is left. The reason is in the report, which is
the requirement.

The Google table cannot carry a class decision today. `gverify.py --report` reads **58 of 213**
documents on the current engine (`98be7c3c`), of which **12 pass all 42**; the other 155 carry a stale
stamp or none. `measure_gate.py` reads **212/213 scored, 1 exempt, 0 blocking, READY** for the
LibreOffice proxy. So this run worked the population the measurable renderer can see, which is the
only population whose before-and-after can be closed inside one slot.

Both gates were checked before any work, as the brief instructs, and both passed:
`regress.py --check` PASS, `measure_gate.py` READY.

## What was measured

    documents failing 18_displacement in LibreOffice, current engine   22
    of those, failing NOTHING ELSE (one check from clean)               7

The seven, rebuilt this run and profiled with `dy.py` against their own source PDFs:

| document | score | n_out/n | dy profile | mechanism |
|:--|:--|:--|:--|:--|
| `330_cad_drawing_sheet` | 46/47 | 32/40 | min −51.56, p25 −39.56 | a block **39.6 pt high**, one run at −51.6 |
| `363_warranty_card` | 41/42 | 7/30 | block at **+3.58…+3.72**, rest −0.23 | one block sits **+3.7 pt low** |
| `64_newspaper_uneven_columns_ad_boxes` | 41/42 | 14/77 | med +2.07, worst **+4.34** | whole page ~+2.0, 8.4 pt body at **+4.1** |
| `71_invoice_space_aligned_no_rules` | 41/42 | 29/72 | rows uniformly **+9.52**, `Total` **+24.42** | table top placed **9.5 pt low** |
| `balance-sheet-two-columns-of-figures` | 41/42 | **6/94** | all ≤0.40 except header row **+3.69** | the **first table row** places its text 3.7 pt low |
| `newsletter-3col-header-footer` | 41/42 | 8/129 | one KPI band at **+6.46** | one localised stat strip |
| `table-inside-two-column-page` | 46/47 | 44/64 | cell text uniformly **−9.06** | a table block displaced **−9.1 pt** |

**Seven documents, seven mechanisms.** Three whole-block placement offsets, three single localised
bands, one page-wide small offset. No shared construct. This is the same answer the 23:54 census got
for the previous eleven, one population further on — and it means the 34.2 leverage figure is not
34.2 documents that one build can reach.

## The one construct that was pinned down

`balance-sheet-two-columns-of-figures` is the crispest: **6 of 94 runs out**, all the first table row.
Three variants, each rebuilt from the same .docx by editing one attribute, each rendered through
LibreOffice and scored by `dy.py` against the same source:

| variant | row 0 `w:trHeight` | row 0 `w:before` | header dy | n_out / 94 | span |
|:--|--:|--:|--:|--:|--:|
| committed | 320 (16.00 pt) | 248 (12.40 pt) | **+3.69** | 6 | 4.18 |
| A | **240 (12.00 pt)** | 248 | **+3.69 — unchanged** | **89** | 6.96 |
| B | **200 (10.00 pt)** | 248 | **+3.69 — unchanged** | **89** | 6.96 |
| C | 320 | **174 (8.70 pt)** | **+0.40 max** | **0** | **0.89** |

- **`w:trHeight` on a table's first row moves every row below it and none of its own text.** Variants A
  and B left the header at +3.69 to the hundredth while taking the page median from +0.10 to −3.00.
  The first row's top is the table's top, so its own height cannot move its own text. Any future
  attempt on a table's first row that adjusts `w:trHeight` is aimed at the wrong attribute, and 89 of
  94 runs go wrong when it is tried.
- **`w:before` on a cell paragraph is laid 1:1.** Measured error +3.69 pt; the correction that clears
  it is −74 twips = −3.70 pt. Slope 1 on the one point that exists.
- Variant C takes the document **6 runs out → 0**, span 4.18 → 0.89, i.e. 41/42 → **42/42 in
  LibreOffice**.

## Why it was not committed

**The 74 twips is measured, not derived.** The engine writes 248 tw where 174 is right. The source says
the row-0 text sits 8.26 pt below the table top, so 12.40 pt over-computes by 4.14 pt — but the same
arithmetic does **not** hold on row 2 of the same table, where the engine's value is already correct
(`Equity share capital` 5.95 pt below its row top, engine writes 8.85 pt, +0.40 pt of error). The
engine's constant is ~2.90 pt on row 2 and ~4.14 pt on row 0. **A rule that fits one fits neither**, and
a −74 twip edit guarded by "first row of a table" would be a fudge carried over 100+ table documents
with only `regress.py --check` in the way.

A likely explanation is untested and cheap: variants A and B show the first row is currently declared
**16.00 pt where the source band is 18.00 pt** (rules at 101.35 and 119.35). If the `w:before` error is
a consequence of that short row, the construct is the row-height model and not the spacing — and it
would generalise to `71_invoice_space_aligned_no_rules` and `table-inside-two-column-page`, which are
whole-block offsets of the same kind. **That is one build and one LibreOffice render, not a Google round
trip, and it is the next slot's first experiment.**

## What was tried and refuted before any build

The `18_displacement` row-pitch lead — "declare net of the rule, land the 18.5 pt rung" — was refuted
from committed data before a round trip was spent on it. The laid ladder is
`0.75 * (round(declared/0.75) + 1)`, so **18.5 is not reachable at all**; the nearest rung to a
18.40 pt source pitch is 18.75. And on the current engine **no document is both one check from clean
and reachable by a row-height declaration**: the two documents that fail only `18_displacement` in
Google (`16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings`) have no ruled table. The
16-document "solo" population is stamped `462353f9`, not the current engine.

## What the proxy cannot decide

`31_times_body_arial_headings` is **42/42 in LibreOffice** and **41/42 in Google, `18_displacement`
alone**, both on `98be7c3c`. So a document made clean in the proxy is not a document made clean in
Google, and this run's 42/42 is a **lead, not a clean document**. Every fix above needs a round trip
before it counts.

## Landed

`cc3bd149` — `FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630-fixer.md`.
The census, the three-variant experiment, and the untested explanation with its next experiment spelled
out. Nothing in `app/` is dirty; `regress.py --check` passes with no document worse in either format.

## Second experiment, same slot

The `w:before` error is not the uniform row average. `DocxWriter.java:6146` computes `exactRows` from
`t.rowEdge`, and on every candidate this run it is **true** — the per-row edges the page gave are used.
Instrumented at that statement (`P2W_DBG`, reverted, `app/` clean), `ConvertOne` on four documents:

| document | `t.ruled` | model edges | page's own rules | verdict |
|:--|:--|:--|:--|:--|
| `balance-sheet-two-columns-of-figures` | **false** | 115.35, 131.35, 143.35 | **101.35, 119.35**, 302.15 | **row 0 edge 14.0 pt BELOW the header band** |
| `table-inside-two-column-page` | true | 117.0, 136.0, 154.0 | **117.35**, 135.75, 154.15 | **0.35 pt — correct** |
| `71_invoice_space_aligned_no_rules` | false | 176.0, 194.0, 212.0 | none drawn | no rules to compare |
| `363_warranty_card` | false | 124.0, 134.0, 148.0 | none drawn | terms block is not in a table at all |

- **`exactRows` is not the gate.** The uniform `rowTw = extentPt / rowCount` path is not what writes
  320 tw for `balance-sheet`'s row 0; `rowEdge[1] - rowEdge[0]` is 16.00 pt by itself. Any attempt to
  "turn exactRows on" aims at a switch that is already on.
- **The edges are 14.0 pt low on `balance-sheet`, and that is the defect.** The table is borderless
  (`t.ruled=false`) and its rules are separate floating drawings, so the edges come from the *text* —
  and the header text sits 5.74 pt **above** the edge the model gave its own row.
- **The control rules out a general edge fault.** `table-inside-two-column-page` is `ruled=true`, its
  model edge matches its page rule to 0.35 pt, and it still misses by a uniform −9.06 pt. That is a
  **placement** fault, not an edge fault, and `71_invoice`'s +9.52 is the same shape.
- **Next, cheapest pair:** `71_invoice` and `table-inside-two-column-page` place a whole table ~9 pt off
  in opposite directions with their edges correct, both one check from clean, both measurable in the
  proxy. `balance-sheet` is a separate build: attach the floating rules to the borderless table so its
  edges come from the rules the page drew.

Nothing in `app/` changed; the instrumentation was reverted and `regress.py --check` passes.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## Why this slot released with --force

`round.py --release-fixer` refuses while `pending.py` is non-empty, and it reads **63**. Every one of
them is an agent record from an earlier run that died before committing a finding — the oldest is
**1134 minutes** old. They are not this run's work and marking them landed would be a false record. One
of them, `18_dB-05`, asked exactly the question angle 2 answered, and it was landed with that answer
(the 18.5 pt rung does not exist). The other 62 cannot be closed in a slot, so the slot was released
with `--force` — the documented exit for a run that genuinely cannot continue.

`round.py --release-fixer` also counts only *background* agent deployments, and a scheduled run has
nobody to answer a later message, so both of this run's agents came back inside the turn. Both were
registered in `HANDOFF.json` with their real angles and landed with their real findings; the Subagents
table above is generated from that record.

## Obstacles parked, with the evidence to re-open them

1. **`balance-sheet`'s borderless table gets its row edges from text, 14.0 pt below the page's rules.**
   Model edges 115.35/131.35 against page rules 101.35/119.35, header row declared 16.00 pt against an
   18.00 pt page band. Attach the floating rules to the table so `ruled=true` derives the edges the way
   `table-inside-two-column-page` already does correctly to 0.35 pt.
2. **`71_invoice` and `table-inside-two-column-page` place a whole table ~9 pt off** (+9.52 and −9.06),
   with their edges correct and both one check from clean. One construct, two documents, measurable in
   the proxy. Cheapest pair in the class.
3. **`363_warranty_card`'s +3.6 pt block is not a table at all** — the terms block sits outside the
   table's last edge (192.0) at y 214.68. It is a paragraph `w:before` term and belongs with whatever
   fixes `31_times_body_arial_headings`' page-wide 2.6–3.2 pt offset.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
