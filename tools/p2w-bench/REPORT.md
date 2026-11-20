# Fixer report - 2026-11-21 02:52

```
# P2W Fixer - Run Report

**21 Nov 2026 · slot 02:52 → running IST · 35 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 03:25 | **partial** | 2/26 | THE CELL'S OWN BORDER WAS PAID TWICE. insetTw measures a cell's text x from the cell's left EDGE on the page, and the writer then draws a rule on that edge; a renderer puts cell content inside its bor |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 02:52 → running · 35 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 8 |
| Longest silence | **33.8 min** — from 02:52:05, after `(no activity given)` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 4 need a human |
| Still a wall | Today's `PROGRESS.md` row records 46 `.txt` failing and `health.py` now reads 27 from the same table, the same |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **33 min** | `#####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

t01_word_accuracy holds 5 documents and two of those five is the bar. Two of them now have a measured, named cause and a fix shape, so start there rather than re-diagnosing. (1) 601_fillable_admission_form loses exactly three tokens and two of them are ticked checkboxes drawn in widget appearance streams as 'BT /ZaDb 9 Tf (3) Tj ET' - PDFBox never processes annotation appearance streams, so the engine emits nothing, which is real content loss on a filled form. FINDINGS/601-tick-is-a-widget-appearance-2342.md has the xrefs; the engine side is a glyph walk over each widget's /AP /N, the shape formValuesOf/widgetValue already have, and the instrument side already reads that stream in _ap_stream_text - both sides must call a /ZaDb glyph a tick or neither is honest. (2) 38_faux_bold_italic_synthesised loses the SECOND draw of its title because faux bold strokes the fill and the source carries 'PROJECT REPORT - CIVIL' twice while our .txt carries it once, which is correct; the 21:46 attempt that collapsed identical spans was REJECTED, so it needs a different construct. (3) 411_nested_xobject_transforms loses 'S' and 'O' - pymupdf and PDFBox disagree about a nested form's matrix and the rotated line runs off the page to y=-16.4. The two bank forms have LEFT this class; what is left on them is t06_encoding, t08_line_order and t09_page_furniture, which is the writer and not the font. Do not rebuild a ligature matcher: FINDINGS/ligature-identity-UNRECOVERABLE-2350.md proves the identity is not in the file.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
