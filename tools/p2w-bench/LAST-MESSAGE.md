# P2W Fixer - Run Report

**21 Nov 2026 · slot 21:53 → running IST · 45 min**

> **041122-Account_Opening_Form** improved — 4.00 → 3.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **9** — 1 attempt(s), 1 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t08_line_order` |

## What the change was, and how it was falsified

`t08_line_order` built its ground truth from `_src_pages` in PyMuPDF content-stream order — the order
the page *painted* its glyph runs — and scored the `.txt` against that. Its own ABOUT string said so:
"lines arrive in the order the page drew them". A page that paints a chart axis bottom-up, or a heading
before the line above it, therefore read as broken with a `.txt` in correct reading order.

The change is four lines inside the t08 block only: sort each page's upright lines by
`(round(y,1), x)` before extending `src_seq`, page-major. `_src_pages` is untouched, so t09 and t13
(whose amount list is deliberately in draw order) cannot move.

Falsified both ways on `46_chart_coloured_labels_body_text`, whose axis is painted bottom-up:

| case | before | after |
|:--|:--|:--|
| the engine's real `.txt`, correct reading order | FAIL 37/43 | PASS 43/43 |
| two lines of the SAME column deliberately transposed | PASS | FAIL 42/43 |
| `39_small_caps_letter_spacing` — source paints y=65.11 before y=52.64 | PASS | FAIL |

The middle row is the one that counts: after the change the check still fires on a genuinely inverted
`.txt`. It is not quiet and it is not comparing sorted-with-sorted. The last row is the only document
that gains a failing check, and the source proves it is a real inversion the check now catches; that
document already failed t01 and t12, so nothing that was clean became dirty.

The whole flat-document sort a sub-agent proposed is rejected on its own numbers: it interleaves pages
(a correct two-page synthetic fails 7/10, and `041122` reads 351/461, worse than before).

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:38 | **kept** | 9/10 | t08 ground truth was PyMuPDF paint order, not reading order: sort each page's upright lines by (round(y,1),x) in the t08 block only. All 213 .txt rescored with the same engine: clean 190->197, t08 fai |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two, both run inside the slot and both with a real problem rather than a grep.

* **t08 verifier question** (general-purpose, 6 min): built five synthetic pages whose paint order and
  reading order disagree, and mutated real `.txt` files, to answer whether t08 measures line order or
  drawing order. Answer: drawing order, and the ground truth was the wrong one. It also killed its own
  proposed fix (the flat sort interleaves pages; `_src_pages` is shared with t09/t13) and handed back
  the per-page sort that was landed here. I re-ran both falsifications myself before committing.
* **32_stroke_lines reach census** (Explore, 23 min, partial): counted all 837 rules in every document that fails it, with the check's own imported predicate — the counts agree with the repo's earlier
  census — and split them by placement. **Not one of the 256 vertical rules sits on a cell boundary or
  inside a table region**, and `DocxWriter.java:6420` emits `w:bottom` only, inside an existing table.
  The handoff's "tcBorders can carry the 102 vertical rules" does not survive the census. It did not
  write its markdown deliverable before its window closed; the numbers are in its summary and in
  `FINDINGS/t08_line_order-DRAWING-ORDER-CONFIRMED-2153.md`'s sibling note in HANDOFF.

## Timing

| | |
|:--|:--|
| Slot window | 21:53 → running · 45 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 9 |
| Longest silence | **24.3 min** — from 21:53:34, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **13 min** | `#######` |
| measure or build - a conversion, screen or compile writes no beacon | **30 min** | `###############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

The t08 question is closed: the check was reading paint order and it now reads reading order. Two
documents still fail it, and only one is an engine bug — `39_small_caps_letter_spacing`, where
TxtWriter emits a doubled heading in paint order rather than reading order (the source paints y=65.11
before y=52.64). That is a small, measurable TxtWriter fix worth one slot. The other,
`305_vaccination_certificate`, is a seal-ring paragraph with no `y` to order by and should be
documented as an abstention, not fixed.

The bigger item is the one the census bought: **32_stroke_lines is not one build away, and the class
should stop being priced as if it were.** 668 of its 837 rules are free-standing ink with no table to
attach to, and 256 of them are vertical, which `tcBorders` cannot emit at all. The reachable
sub-population is the 14 documents whose rules sit exactly on cell edges of a table the engine already
emits — `16_right_aligned_amounts_txtpos` is the cheapest test there (13 of its 17 rules, on a table we
already write). Take that, or take the 16 remaining `.txt` failures, but do not re-price 32_stroke as
36.3 clean documents.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
