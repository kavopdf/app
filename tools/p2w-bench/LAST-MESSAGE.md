# P2W Fixer - Run Report

**21 Nov 2026 · slot 02:52 → running IST · 44 min**

> No engine change was kept this run: the mechanism is proved in Google, the patch is written, and the gate refuses an unmeasured engine. What landed is the patch and the proof, not a tree change.
>
> The class was not my choice. classpick.py ranked the capability table by documents and printed 47_margins, 26 documents in Google, so that is what this run worked. Ten attempts sat on it already; the last two concluded that 360_restaurant_menu cannot be won by any writer construct that keeps the page's own grid, and this run did not rebuild either of those.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
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
| 03:36 | **partial** | 2/26 | SECOND RECORD, same construct, now measured in GOOGLE. The patched build was uploaded to Drive, converted to a Google Doc and exported as PDF: 404_sudoku_grid goes 43/47 FAIL -> 44/47, with 47_margins |

### The mechanism, and the proof

A table cell's text x is measured from the cell's left edge on the page, and the writer then draws a rule of its own on that edge. A renderer lays cell content inside its border, so the text lands at edge plus border width plus the indent the page already asked for. The border the writer added is paid a second time, in full, on every cell of every ruled table.

Proved by editing only the emitted XML on 404_sudoku_grid: its nine columns carry a 2 pt left and insideV rule, all 30 of its unregistered runs sat exactly 2.1 pt right of the page, and setting those two sides to nil moved all 30 to within 0.1 pt.

### Google decides, and Google agrees

The .docx was uploaded to Drive, converted to a Google Doc and exported as PDF, and the text layer read with PyMuPDF. Page 1 grid digit x in points: source 115.91 / 159.91 / 291.91; Google on the HEAD build 117.00 / 161.25 / 294.00; Google on the patched build 115.50 / 159.75 / 292.50. So Google lays cell content inside the cell's border exactly as LibreOffice does, and the border was paid twice in the renderer the user opens.

The same document through the same 42 checks in Google: **43/47 FAIL with 47_margins at 18 unregistered runs and a 2.1 pt median, to 44/47 with 47_margins PASS**. No check newly fails; the three that still fail are 18_displacement, 23_line_pitch and 59_shape_anchor, none of which this change touches.

### Same-engine pair, nine documents, LibreOffice proxy

A HEAD build and a patched build of the same tree, both through soffice, both scored by the 42 checks.

| document | before | after | 47_margins |
|:--|--:|--:|:--|
| `404_sudoku_grid` | 46/47 | **47/47** | 30 unregistered at 2.1 pt -> 0 at 0.1 pt, PASS |
| `76_devanagari_table` | 45/47 | **46/47** | 6 at 0.6 pt -> 2 at 0.1 pt, PASS |
| `07_stamp_over_table` | 37/42 | 37/42 | unchanged |
| `21_form_labels_x60_values_x300_txtpos` | 40/42 | 40/42 | unchanged |
| `365_recipe_card` | 41/42 | 41/42 | unchanged |
| `39_small_caps_letter_spacing` | 40/42 | 40/42 | unchanged |
| `78_mixed_english_devanagari_line` | 40/42 | 40/42 | unchanged |
| `brochure-3col-with-sidebar-box` | 41/42 | 41/42 | unchanged |
| `product-catalogue-code-left-price-right` | 41/42 | 41/42 | unchanged |

Two moved, seven did not, none got worse. The patch is in `patches/47-margins-cell-border-inset.patch`; the method, both measurements and the landing sequence are in `FINDINGS/47_margins-CELL-BORDER-PAID-TWICE-034500-f1x.md`.

### What the next run must not repeat

The committed gverify-lo rows are stale for this class. `76_devanagari_table` reads 39/47 there and scores 45/47 on a pristine HEAD build; `78_mixed_english_devanagari_line` reads 36/42 with 47_margins passing and scores 40/42 with it failing. Both sides of an attempt have to be built and measured in the same run.

The remaining 47_margins failures are a different defect. On the seven documents this patch does not move, the check's median error is already 0.1 pt and only the per-page tail of unregistered runs remains.

### Why it did not land

`regress.py --check` refuses any tree whose engine fingerprint differs from the table's: an unmeasured engine is not a pass. Landing needs a full corpus pass, and that needs the patch pushed first, because p2w.py builds from origin main and not from a working tree. That is a longer run than this slot. So the patch was committed as a patch and the engine left untouched, which is why the gate passes on this tree.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

Two agents, both before the run's own attempt and neither waited on.

1. Explore - a reach census over the 26 documents. No per-document JSON carries 47_margins detail, so it measured the class rather than quoting a table, and it is what named the table-cell cluster as the only construct clearing the class's quarter bar.
2. general-purpose - asked to measure Google's cell-border inset. It confirmed the mechanism in LibreOffice at two border weights (2 pt on 404, 0.5 pt on 76) and could not reach Google: a sub-agent has no upload tool, so a local .docx cannot be staged into Drive. That blocker is why the Google measurement was taken by the run itself, and the loop is written down in the finding. It also left an empty Netlify project, p2w-gverify-tmp, that needs deleting by hand.

## Timing

| | |
|:--|:--|
| Slot window | 02:52 → running · 44 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **33.8 min** — from 02:52:05, after `(no activity given)` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 4 need a human |
| Still a wall | Today's `PROGRESS.md` row records 46 `.txt` failing and `health.py` now reads 27 from the same table, the same |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **42 min** | `#####################` |
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
