# Fixer report - 2026-11-22 03:14

```
# P2W Fixer - Run Report

**22 Nov 2026 · slot 03:14 → running IST · 47 min**

> The carrier is dead as a patch, and the reason the last two runs gave for it was the wrong one. It does not damage the clean document in Google, and the narrowing it was told to build does not exist. What kills it is a floating table nested in a table cell.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 03:35 | **lead** | 0/213 | Blast radius of the horizontal-only carrier patch measured for the first time on all 213: 161 documents change .docx content, not 16. 143 of them fail 32 (gain candidates), 5 pass 32 (pure risk) and 1 |
| 04:01 | **reverted** | 0/16 | corpus pass on HEAD+horizontal-only carrier: 52 better, 54 worse, regress.py REFUSED 58; regressed docs median 9 carriers vs 1 unchanged; HEAD reproduces baseline on 3 controls so the instrument is so |
| 04:08 | **lead** | 1/None | Google measurement of the carrier on two documents: 51_two_cm_margins stays 42/42 (rewritten, not worse), 17_three_column_widths_txtpos 40/42 -> 42/42. Refuted the 02:50 prescription: 32_stroke_lines |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |


## What this run adds

Two runs before this one worked `32_stroke_lines` and both stopped on a reason that does not survive
measurement.

The 02:50 run's reason: *"a document that is already right, rewritten by a patch that is supposed to
fix documents that are wrong, is the definition of the trade the gate forbids."* That is a statement
about a **change**. Non-negotiable 3 is about a **score**, and nobody had measured which one
`51_two_cm_margins` was. Measured, through Google Docs itself - patched `.docx` uploaded as a Google
Doc, exported as Google's own PDF, scored against the source:

| document | committed Google (HEAD) | patched engine, this run | |
|:--|:--|:--|:--|
| `51_two_cm_margins` | **42/42** | **42/42** | rewritten, 2 drawings -> 1 drawing + 1 carrier table, score unchanged |
| `17_three_column_widths_txtpos` | 40/42, fails `05_chars_extra` + `32_stroke_lines` | **42/42** | 0 drawings, 2 carrier tables, both failures gone |

The 02:50 run's prescription: narrow the predicate *"so it cannot fire where the rule already
renders"*, naming the five documents that pass `32_stroke_lines` while changing as the set it had to be
right about. A subagent compared their `document.xml` against the documents Google fails. `51` and `17`
differ in **four numbers only** - `cx`, `cy`, `posH`, `posV`. Every attribute is identical, from the one
fixed template in `DocxWriter.shape()`.

`51` passes `32_stroke_lines` because the check is **vacuous** on it: its 0.8 pt rule touches the page
frame at both ends, the 3 pt isolation filter discards it, and the source set is empty. Corpus-wide the
split is exact - **45 scored documents have zero isolated source rules and all 45 pass `32`; 147 have at
least one and 145 fail.** The property that separates them is on the source side, which is what the
check measures. No predicate over the engine's `Shape` fields can see it. **There is nothing to narrow.**

So the carrier is not killed by the clean document and not killed by its predicate. It is killed by the
04:00 run's measurement, which is the one that counts: **54 documents worse on the proxy, gate REFUSED,
regressed documents carrying a median of 9 carriers against 1 for unchanged ones.** A floating table
nested inside a table cell displaces the cell's flow. That is the blocker, and it is a placement
problem, not a substitution problem.

## Falsification

| test | expected | measured |
|:--|:--|:--|
| the carrier damages the one clean document it rewrites | a score below 42 | **42/42, unchanged** - falsified |
| a `{05,32}` document reaches 42/42 under the carrier | 42/42 | **42/42** |
| the five "risk" documents share a structural property with the failing ones | a discriminator exists | **none exists** - the 45 vacuous documents are the whole explanation |
| the carrier reaches every document that fails `32` | reaches all | **no** - `407_id_card_front_back` (41/42, fails `32` alone) keeps all 41 drawings and gets 0 carriers |
| the 04:00 run's regressions are the instrument's | HEAD reads the same bad numbers | **no** - HEAD reproduced the baseline to the digit; the patch is the cause |

## What the next run should build

Not a narrowed predicate - that was measured and it is empty. The predicate already declines what it
cannot reach. What is missing is a guard on **where the carrier goes**: a rule whose anchor paragraph
sits inside a `w:tc` must keep the drawing, because the carrier's own floating table then nests in a
cell. The 04:00 finding names the 54; `benchmarks/blast-carrier-2008.json` names the 161. The test is
narrow and cheap - convert those 54 and count carriers per document; the number to beat is a median of 1.

Two numbers to close first, both cheap:

1. `17`'s 40/42 is a **possibly-stale record**. `05_chars_extra` was re-instrumented on 21 Nov 23:37
   (one U+200B per `w:tab`) and the committed JSONs predate it; `17` has 23 tabs. The defensible
   reading is HEAD 41/42 failing `32` alone, and the carrier takes it to 42/42.
2. `407_id_card_front_back` is 41/42 failing `32` alone and the patched engine does not touch it - all
   41 drawings survive `isRuleShape()`. The carrier is worth what it reaches, and this is a document it
   never reaches.

## Subagents

Two, both run inside this turn (a scheduled run has no later turn for a background result).

**Drawing XML discriminator** (general-purpose, 5.5 min): built the engine, converted `51`, `17`, `315`,
`373`, `64` and the rule-heavy bank-statement and boq documents, and compared every drawing attribute
against the Google verdict. **Negative result, and it is the most valuable thing the run produced** -
no attribute separates them, and the 213-row correlation (`isolated-rules-vs-google-32.csv`) shows why.

**Carrier collateral checks** (general-purpose, 4.8 min): read all 6341 lines of `verify_google.py` and
said which of the 42 checks a correctly placed border can newly fail. Exactly one -
`46_text_crossing_rule` - plus six conditional ones (`18_displacement`, `59_shape_anchor`,
`60_text_column_right_edge`, `61_blank_not_filled`, `62/63`, `47_margins`). None fired on either document
measured here; `51` is the sharper test of the two because it passes `46` today with source 0. It also
found that 21 of 213 documents are `page_count_refused` and 64 are scored out of 47, so a corpus-wide
42/42 yardstick is not like-for-like.


## Timing

| | |
|:--|:--|
| Slot window | 03:14 → running · 47 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 13 |
| Longest silence | **23.9 min** — from 03:36:51, after `report.py: building the report` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **18 min** | `#########` |
| measure or build - a conversion, screen or compile writes no beacon | **23 min** | `############` |
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

Do not apply rule-carrier-horizontal-only-2008 as a global substitution. Narrow isRuleShape so a band that sits on a table cell/row edge or a stamp frame gets no carrier, then screen the 54 regressed documents before any corpus pass. Or Google-score 08_two_overlapping_stamps, 50_invoice_coloured_total_row and product-catalogue-code-left-price-right first: if Google is clean the 54 are an LO artefact of nested floating tables and the predicate needs no narrowing

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
