# P2W Fixer - Run Report

**21 Nov 2026 · slot 00:57 → running IST · 54 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 4 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **19** files in 6 commit(s) from `e840302` — ...NT-PROPOSAL-clip-flag-NOT-APPLIED-0210-fixer.md, 38-faux-bold-TRIPLE-DRAW-0225-fixer.md, 39-small-caps-gap-threshold-0150-fixer.md, ATTEMPTS.json, BLOCKERS.md, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSA |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 00:57 | **reverted** | 0/5 | claimed (8th attempt). t01_word_accuracy, 5 documents, .txt half. Two bank forms now carry t06/t08/t09 only. Remaining: 38_faux_bold_italic_synthesised, 39_small_caps_letter_spacing, 411_nested_xobjec |
| 01:41 | **reverted** | 0/5 | SECOND ATTEMPT, measurement only, no engine change. Two subagents on the class. 411_nested_xobject_transforms: the handed diagnosis (matrix disagreement, line off page) is FALSE - both parsers compute |
| 01:47 | **reverted** | 0/5 | THIRD ATTEMPT, measurement only. 38_faux_bold_italic_synthesised: the page draws each of its two headings THREE times at the identical position (two fill spans + one stroke span, same font, same size, |
| 01:51 | **reverted** | 0/5 | FOURTH ATTEMPT, read-only census for the next run's engine attempt on 601_fillable_admission_form. Walked every page's /Annots of all 213 PDFs, resolved each /Widget's /AP /N stream and searched for t |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t01_A-02` | is the handed diagnosis (nested form matrix disagree | 01:41 | 20:11 | 0 min |
| `t01_B-02` | why does 39_small_caps_letter_spacing lose 8 words a | 01:41 | 20:11 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 00:57 → running · 54 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 31 |
| Longest silence | **28.3 min** — from 00:57:53, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | two of the five documents (411_nested_xobject_transforms, 39_small_caps_letter_spacing) fail t01 only because  |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **41 min** | `#################` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| report - the report and the chain | **8 min** | `###` |
| other - not attributed to a tool | **0 min** | `#` |
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
