# 18_displacement: 25 near-clean documents are two constructs, not one

**Measured 27 Nov 2026.** The population, the split, and the two engine constants responsible.

## The population, from the store (not a sample)

`benchmarks/gverify/*.json`, rows with `engine == d28ca7516c3f9165` (212 documents, 42 clean,
592 failing check-instances):

| failing checks on the document | documents |
|---|---|
| 0 | 42 |
| 1 | 40 |
| 2 | 37 |
| 3 | 23 |
| 4 | 24 |
| 5-9 | 45 |
| 23 | 1 |

Of the 40 documents that fail exactly one check, the single failure is:

| check | documents |
|---|---|
| **18_displacement** | **25** |
| 60_text_column_right_edge | 6 |
| 59_shape_anchor | 3 |
| 47_margins | 3 |
| 32_stroke_lines | 2 |
| 17_matched_runs | 1 |

25 is the largest single-check population in the corpus by a factor of four over the next
(6). It is also the dominant component of the 2-check documents: `18_displacement +
60_text_column_right_edge` is 12 more. So a fix here is worth 25 documents outright, 42 -> 67
clean, and it is a term in most of the rest.

## It is vertical only

On all 25, `detail.med_dx` is within 0.8 pt of zero. The failure is entirely in `detail.med_dy`.
That rules out column width, indentation and horizontal justification as causes, and it is why
60_text_column_right_edge appears beside it as a separate, independent check.

## The split: 12 constant offsets, 13 accumulated drifts

The discriminator is the stored Google-side `23_line_pitch` pair (source pitch vs Google-render
pitch, paired by text), which gives the per-line advance error delta. If delta is about 0 the
advance is right and a failure can only be a rigid shift; if delta is 0.5-1.0 pt the error
compounds once per row. Checked against row counts: 320 predicts 21 rows x 1.0 = 21.0 against
`worst_dy` 19.4; 303 predicts 5 x 0.8 = 4.0 against 4.1; 402 predicts 6 x 0.9 = 5.4 against 6.5.

| class | documents | construct |
|---|---|---|
| constant offset | 12 (8 plain, 4 block-scale) | A: baseline placed at `LINE_BASE` of the line box |
| accumulated drift | 13 | B: table row rendered taller than its declared `w:trHeight` |
| block-scale offset | 4 of the 12 | C: block placed against a measured edge |

### A - the baseline sits too high inside the line box

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:220` `private static final float
LINE_BASE = 0.8f;`. The engine places the baseline at 0.8 of the line box and records the
position from that assumption (`place()`, and `resync()`). Google puts the baseline at
approximately 0.31 em. The shortfall is about 0.26 em, constant per line, so it is a rigid
shift that grows with font size and never with line count.

Test of the fit on the stored numbers: `|med_dy| / 0.26 / size` is 0.95 on
31_times_body_arial_headings (10.5 pt -> 2.73 predicted, 2.6 measured), 0.97 on
74_balance_sheet_indented_subitems, 1.03 on price-list-2col-dense-right-aligned.

### B - a table row renders taller than its declared height

`DocxWriter.java:54` `ROW_RUNG_UNDER_TW = 10` and the row loop that declares `w:trHeight`
(line 6601). The declared height equals the source row pitch exactly (14.0 -> 14.0 on 320,
15.0 -> 15.0 on 303 and 325), yet Google renders the row 0.5-1.0 pt taller, so every row below
it is displaced by the sum. The growth correlates with the row's own slack
(`trHeight` minus cell content): r = 0.38 over 23 documents, 320 slack 4.15 -> +1.0 pt,
electricity-bill slack 7.10 -> +0.8 pt.

### C - block placement

`flowFromBox()`'s `afterTablePt` / `edgeGap` branch: one large rigid shift of a whole table
block, not a per-line effect. 68_journal_wide_table_spanning has `med_dy` -114.3 and
`worst_dy` 115.0 - med equals worst, which is the signature of a block move.

## What this file does NOT claim

The per-run Google dy for these documents was **not** measured in this run. The classification
rests on the stored Google `med_dy`/`worst_dy`, the stored Google-side `23_line_pitch` pair, the
declared `w:trHeight` in the built `.docx`, and the engine source. A LibreOffice render is not
evidence here: on 320_balance_sheet_statutory LibreOffice gives `med_dy` 0.05 / `worst_dy` 0.45
where Google gives 8.2 / 19.4, while on 31_times the two agree (2.70/3.25 vs 2.6/3.5). That is
the charter's point about the proxy, measured again.

Signs are also mixed: electricity-bill drifts +0.8 pt per row yet has `med_dy` -8.5, so a
document can carry a drift term and an offset term of opposite sign. The table classifies the
carrier, not the net sign.

## The one-document experiment

`31_times_body_arial_headings`: zero tables, 29 runs, flow only, `med_dy` 2.6 against
0.26 x 10.5 = 2.73 - construct A in isolation.

1. Import its `.docx` to Drive as a Google Doc and export the PDF.
2. Fit `dy = c + slope * y` per run. Expect slope about 0 (rigid) and c about +2.6.
3. Rebuild with `LINE_BASE` 0.8 -> 0.31 and re-measure the same document. `med_dy` should go
   2.6 -> about 0 and 18 should flip to pass, with `23_line_pitch` staying inside 1.0 pt as the
   guard - `LINE_BASE` also drives the advance, so the guard is what stops this becoming a
   line-pitch regression.

The drift twin is `320_balance_sheet_statutory`: declare `w:trHeight` 14.0 -> 13.0 (its
delta = 1.0) and `worst_dy` should fall from 19.4 toward 0.

## Provenance

Classification table: `18displacement-25-classification.csv` (25 rows, columns document,
med_dy, worst_dy, src_pitch_pt, google_pitch_pt, pitch_delta_pt, declared_rows, trHeight_pt,
class, construct). Produced this run from the store and the engine source; the two engine
constants named above were re-checked in `DocxWriter.java` at lines 54 and 220.
