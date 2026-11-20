# P2W Fixer - Run Report

**20 Nov 2026 · slot 15:55 → 17:12 IST · 1h 17m**

> **22_invoice_four_columns_txtpos** improved — 1.00 → 0.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **5** — 3 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t13_amount_columns` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 16:14 | **reverted** | 0/26 | a claim-time placeholder, corrected in place at 17:06 by the kept row below - the class was claimed before the diagnosis existed |
| 17:06 | **kept** | 5/6 | TxtWriter: hoist the table amount end column from per-Table to one set per page column of the cell's right edge, pooled over every table in the document and marked in paraEndSnap so paragraph and tabl |
| 17:08 | **reverted** | 0/1 | itr-computation-with-slab-table is not a padding fault. Its failing source amount column (7 rows, end column 130) arrives as 1 row at 130 and 6 at 132, because 61,000.00 is in a different Table whose |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **182** (85.4%) |
| Failing at least one check | **31** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 12 documents |

## What landed

TxtWriter.java only, and scope.py proves it cannot reach a .docx byte. The table path measured its amount end column inside the call, from that one Table; the paragraph path measured the same thing per page; neither saw the other. Two tables covering one source column therefore disagreed - on 22_invoice_four_columns_txtpos block 7 ended every figure at column 102 and block 8 at 103, same right edge 539.276 pt, 4 of 16 rows one column away from the other 12.

The change pools every numeric table cell in the document by the page column of its right edge, merging keys one column apart the way the paragraph path already merged end columns, and marks those targets in paraEndSnap so both paths agree on a page that uses both. Two structural properties rather than measured ones: the key is the page column of the right edge, so cells of different lengths in one page column are one column by construction; and the target is a maximum over a set that includes the cell's own left edge plus length, so a numeric cell can only move right. Nothing moves left, so nothing that passes today can lose its column.

| document | before | after |
|:--|:--|:--|
| `22_invoice_four_columns_txtpos` | t13 | clean |
| `29_dot_leaders_txtpos` | t13 | clean |
| `balance-sheet-two-columns-of-figures` | t13 | clean |
| `74_balance_sheet_indented_subitems` | t02, t13 | t02 |
| `gst-invoice-multipage-item-table` | t09, t13 | t09 |

The whole corpus was re-converted and re-scored with the new engine, 213 of 213. The baseline table was deliberately left untouched, so the gate compared fresh scores against a table this run never wrote and still found no document worse.

## The one it did not fix

itr-computation-with-slab-table keeps t13. Its failing source amount column has 7 rows at end column 130 and arrives as 1 row at 130 and 6 at 132. The odd row is 61,000.00, in a different Table whose cell right edge is 535.58 pt against the other's 549.92 pt - 3.4 columns on this document's 4.1616 pt ruler. The source's own figures all end within one column of each other, so one table's cell right edge is 14 pt left of where the page draws them. That is table geometry in PdfToWord, which owns the .docx too, and it needs a .docx measurement. Padding cannot reach it, and a wider merge window would be inventing a column the page did not draw.

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t13_A-02` | every offending t13 line, per document: source column x, leading spaces, emitting path | 15:58 | 16:15 | 17 min |
| `t13_B-02` | the reach of a per-page end column over the whole .txt corpus, before and after | 16:00 | 16:24 | 24 min |

The first produced the line-by-line map the fix was built from and proved the emitting path by replaying the writer byte for byte. The second confirmed the structure in the source but ran out of its budget before the before/after pass, and said so rather than estimating - its measured throughput is why the corpus pass here was run in chunks of sixty and not attempted as one call.

## Timing

| | |
|:--|:--|
| Slot window | 15:55 → 17:12 · 1h 17m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 31 |
| Longest silence | **51.9 min** — from 16:14:08, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 13m** | `#####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **3 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

The class rotation goes to the .docx half next. If a run takes t13\_amount\_columns again, start at the itr cell geometry recorded in FINDINGS/t13-page-end-column-KEPT-172000.md and first measure which of the two cellRight values is the wrong one. Do not retry the padding path - that file carries both the numbers and the reason.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

