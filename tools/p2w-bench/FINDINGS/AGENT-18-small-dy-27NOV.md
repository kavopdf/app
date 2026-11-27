# 18_displacement, the SMALL-DY cluster: an ascent artefact AND a one-line engine defect, separated by arithmetic

**Measured 27 Nov 2026.** Repo `kavopdf/app` @ `fb81b49`, engine built from HEAD with
`tools/p2w-bench/build-engine.sh`, corpus `corpus-v1` fetched with `corpus-fetch.sh`
(214 PDFs, 212 scored). Every render below is **LibreOffice 7.4.7.2**, labelled as a proxy:
no Google render was made (see §9). Nothing in `app/` or `tools/` is left modified
(`git status` clean at `fb81b49`).

---

## 1. Answer in one paragraph

`dy` decomposes exactly into a baseline term and a font-metric term:

    dy(bbox top) = dy(origin) + (ascent_source - ascent_built)          residual 0.0000 pt

so the question has a computable answer per document, not a judgement. On the SMALL-DY
population **both branches of the question are real, and they are in different documents**.
`31_times_body_arial_headings` is **(a) an instrument artefact**: its baselines are within
**0.08 pt** of the source and the whole 2.6 pt charge is the 1.07 em → 0.80 em ascent
difference. `74_balance_sheet_indented_subitems` is **(b) an engine defect**, and it is a
single line of code: `DocxWriter.java:7013` writes a table cell's `w:before` as
`rowHeight - box` where the rest of the file writes `LINE_BASE * (rowHeight - box)`, which
puts the baseline **0.2 × `w:before`** too low — **1.70 pt predicted, 1.71 pt measured**.
Fixing that one line turns **4** of the 23 documents that fail 18_displacement and nothing
else into clean documents, measured, with 0 regressions in 13 rebuilt documents.

---

## 2. The population, from the store (not a sample)

`benchmarks/gverify/*.json`, 213 rows, engine `d28ca7516c3f9165` (210) + 2 + 1 older:

* **118 documents fail `18_displacement`.**
* Leverage, `sum(1/n_failing_checks)` over those 118 = **52.61** — this is where the
  "52.6 clean documents" figure comes from, and it reproduces exactly.
* **23 fail 18_displacement and nothing else** (the store's 25, less 2 whose `checks`
  field is a string rather than a dict).

SMALL-DY population, defined as `|med_dy| <= 4.0` and `worst_dy <= 6.5` pt — the documents
whose lines are off by a few points rather than shifted: **32 of the 118**, of which **9**
fail nothing else. Leverage of the set: 16.60.

| document | med_dy | worst_dy | failing checks |
|:--|--:|--:|--:|
| `353_admit_card` | +1.0 | 3.0 | 5 |
| `342_packing_list` | +0.5 | 3.1 | 2 |
| **`70_magazine_drop_cap_photo_caption`** | +3.0 | 3.3 | **1** |
| `brochure-3col-with-sidebar-box` | +0.1 | 3.4 | 2 |
| `payslip-label-left-amount-right` | +0.1 | 3.4 | 3 |
| **`36_embedded_subset_font`** | +1.7 | 3.5 | **1** |
| **`31_times_body_arial_headings`** | +2.6 | 3.5 | **1** |
| `42_table_coloured_header_alternating_rows` | +1.4 | 3.6 | 2 |
| `314_tender_rfp_boq` | +2.8 | 3.6 | 5 |
| **`303_discharge_summary`** | −0.2 | 4.1 | **1** |
| `08_two_overlapping_stamps` | +0.8 | 4.1 | 6 |
| **`74_balance_sheet_indented_subitems`** | +2.2 | 4.2 | **1** |
| `newspaper-2col-fullwidth-headline` | +3.5 | 4.2 | 4 |
| `405_sheet_music_lyrics` | +0.9 | 4.3 | 3 |
| `406_passport_mrz_page` | −0.4 | 4.4 | 2 |
| `363_warranty_card` | −1.3 | 4.5 | 2 |

(bold = fails 18_displacement and nothing else)

**The store is stale in one specific way.** These `med_dy`/`worst_dy` values are the
**bbox-top** metric: `31_times` reads 2.6 here and 2.70 is the bbox-top figure measured in
§4. The check at HEAD (`verify_google.py:5923`, `ds` built from `roy`) already reads the
**baseline origin**. So the 118 and the 52.61 are a bbox-top count; §7 measures what
moving to origins actually buys.

---

## 3. The two documents, and the exact XML the engine wrote

Both converted with `ConvertOne <in.pdf> <outDir>` from `tools/engine-verify`, then unzipped.

### 3a. `31_times_body_arial_headings` — 1 page, 29 matched runs, **zero tables**

Every paragraph in `word/document.xml` is the same shape (24 paragraphs, 20 distinct
`w:spacing` values):

```xml
<w:p><w:pPr>
  <w:pStyle w:val="Heading3"/>
  <w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
             w:before="1230" w:after="0" w:line="13" w:lineRule="exact"/>
  <w:ind w:left="1120" w:right="0" w:firstLine="0"/>
</w:pPr>
<w:r><w:rPr>
  <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:b/>
  <w:sz w:val="24"/><w:szCs w:val="24"/>
</w:rPr><w:t xml:space="preserve">THE UNITED COFFEE ESTATES COMPANY LIMITED</w:t></w:r></w:p>
```

Census of the whole part:

| attribute | value |
|:--|:--|
| `w:spacing` `w:before` | 209, 227, 267, 269, 319, 329, 347, 525, 568, 687, 823, 867, 971, 1230, 1288, 3506 twips |
| `w:spacing` `w:after` | **`0` on all 24 paragraphs** |
| `w:spacing` `w:line` | 13 (×20), 11 (×3), 12 (×1) twips = **0.65 / 0.55 / 0.60 pt** |
| `w:spacing` `w:lineRule` | **`exact`, all 24** |
| `w:sz` / `w:szCs` | 16, 20, 21, 22, 24 half-points (8, 10, 10.5, 11, 12 pt); both attrs always present |
| empty paragraphs | **0** |
| `w:tbl` / `w:tblCellMar` | **0 / 0** |
| `w:snapToGrid` | `0` on every paragraph |

So: **no `w:after`, no spacer paragraph, no table, no cell margin.** The line's whole
vertical position is carried by `w:before`, and the line box is a hairline of
`w:line = 13` twips (`hairlinePt()`, `DocxWriter.java:4119`: `min(0.069 * size, 0.6485)`
pt = `min(1.38 * size, 12.97)` twips).

### 3b. `74_balance_sheet_indented_subitems` — 1 page, 54 matched runs, 2 tables

```xml
<w:tr><w:trPr><w:trHeight w:val="340" w:hRule="atLeast"/><w:cantSplit/></w:trPr>
  <w:tc><w:tcPr><w:tcW w:w="6567" w:type="dxa"/></w:tcPr>
    <w:p><w:pPr><w:pStyle w:val="TableText"/><w:snapToGrid w:val="0"/>
      <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
                 w:before="170" w:after="0" w:line="170" w:lineRule="exact"/>
      <w:ind w:left="348"/></w:pPr>
      <w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"
                           w:cs="Times New Roman"/>
        <w:sz w:val="17"/><w:szCs w:val="17"/></w:rPr>
        <w:t xml:space="preserve">(a)  Share capital</w:t></w:r></w:p></w:tc>
```

| attribute | table 1 (rows 1-4) | table 2 (rows 1-6) |
|:--|:--|:--|
| `w:trHeight` | `340` `hRule="atLeast"` | `340` `hRule="atLeast"` |
| cell `w:spacing` `w:before` | **170** twips (8.5 pt) | **328** twips (16.4 pt) |
| cell `w:spacing` `w:line` | **170** twips (8.5 pt) | **12** twips (0.6 pt) |
| `w:lineRule` | `exact` | `exact` |
| `w:after` | 0 | 0 |
| `w:sz` / `w:szCs` | 17 / 17 (8.5 pt) | 17 / 17 |
| `w:tblCellMar` | top/left/bottom/right **all 0** | all 0 |
| page `w:pgMar` | top/right/bottom/left **all 0** | — |

`w:before + w:line` = 340 twips on both tables = exactly the declared row height. That is
the signature: **the cell's whole row pitch has been split into a gap (`w:before`) and a
box (`w:line`).**

For contrast, `303_discharge_summary` (the same-face control, DejaVuSans on both sides)
carries `w:before` 158-459 twips with `w:line` 10-13 hairline, 1 empty paragraph, 2
`w:tblCellMar`, and one `w:line="1"` zero-height paragraph — and it renders clean.

---

## 4. The arithmetic: PDF text layer vs what the .docx asks for

Source side: `page.get_text("dict")` → per-span `origin` (baseline) and `bbox`. Built side:
the same extraction on the LibreOffice render, paired by (page, normalised text, nearest x)
— 29 pairs on `31_times`, 54 on `74_balance`.

### 4a. The decomposition identity (this is the number that decides (a) vs (b))

| document | pairs | dy(origin) med / max | dy(bbox top) med / max | Δascent med | identity residual |
|:--|--:|:--|:--|--:|--:|
| `31_times_body_arial_headings` | 29 | **+0.08 / 0.95** | **+2.70 / 3.25** | +2.65 | **0.0000 pt** |
| `303_discharge_summary` | 45 | +0.33 / 1.00 | +0.01 / 0.66 | −0.32 | **0.0000 pt** |
| `74_balance_sheet_indented_subitems` | 54 | **+1.71 / 3.31** | +2.66 / 4.26 | +0.95 | **0.0000 pt** |

`dy(bbox top) = dy(origin) + (ascent_source − ascent_built)` holds to the last decimal on
all 128 pairs. Per size, on `31_times`:

| size | source face | built face | ascent_src | ascent_built | Δasc | dy(origin) | dy(bbox) |
|--:|:--|:--|--:|--:|--:|--:|--:|
| 8.0 | Helvetica | LiberationSans | 8.52 | 6.40 | +2.12 | +0.01 | +2.13 |
| 9.0 | Times-Roman | LiberationSerif | 9.47 | 7.20 | +2.27 | +0.11 | +2.38 |
| 10.0 | Times-Bold | LiberationSerif-Bold | 10.53 | 8.00 | +2.53 | +0.11 | +2.64 |
| 10.5 | Times-Roman | LiberationSerif | 11.05 | 8.40 | +2.65 | +0.08 | +2.74 |
| 11.0 | Times-Bold | LiberationSerif-Bold | 11.48 | 8.80 | +2.68 | +0.01 | +2.69 |
| 12.0 | Helvetica-Bold | LiberationSans-Bold | 12.84 | 9.60 | +3.24 | +0.01 | +3.25 |

Source ascent is 1.07 em (Helvetica/Times, the two faces PDF producers embed for
standard-14); the built face reports 0.80 em. **0.27 em at 10.5 pt = 2.84 pt, and that is
the 2.6 pt the check charges `31_times`.** The engine's baselines are within 0.08 pt.

### 4b. The table-cell arithmetic on `74_balance`

The engine's own model of a line is `baseline = box_top + LINE_BASE * box` with
`LINE_BASE = 0.8` (`DocxWriter.java:220`). Inside a row, `box_top = row_top + w:before`, so

    baseline_written = row_top + before + 0.8 * box

The page drew its cell text at the foot of the row: `baseline_page = row_top + 0.8 * rowPitch`.
With `rowPitch = w:trHeight = 340` twips = 17.0 pt:

| table | `w:before` | `w:line` | baseline written | baseline the page drew | error | measured dy |
|:--|--:|--:|--:|--:|--:|--:|
| 1 | 170 (8.5 pt) | 170 (8.5 pt) | 8.50 + 0.8×8.50 = **15.30 pt** | 0.8×17.0 = **13.60 pt** | **+1.70 pt** | **+1.71 pt** |
| 2 | 328 (16.4 pt) | 12 (0.6 pt) | 16.40 + 0.8×0.60 = **16.88 pt** | 0.8×17.0 = **13.60 pt** | **+3.28 pt** | **+3.31 pt** |

The error collapses to one expression:

    error = (1 - LINE_BASE) * w:before = 0.2 * w:before

Predicted 1.700 / 3.280 pt against measured 1.710 / 3.310 pt — residual 0.03 pt, which is
the renderer's 0.05 pt quantisation. The law was then tested blind on every matched run of
five documents, with `w:before` read out of the built `.docx` and no knowledge of the dy:

| document | runs matching `|dy − 0.2·before| < 0.45 pt` |
|:--|:--|
| `bus-timetable-station-left-times-right` | **165 of 168** (pred 3.17 vs meas 3.19) |
| `74_balance_sheet_indented_subitems` | **30 of 39** (pred 1.70/3.28 vs meas 1.71/3.31) |
| `71_invoice_space_aligned_no_rules` | 1 of 65 (a different, larger construct) |
| `mobile-bill`, `insurance-policy-schedule` | 0 of 106, 0 of 101 (dy ≤ 1.5 pt, opposite sign) |

So the construct is identified exactly where it fires and does not pretend to explain
documents it does not touch.

---

## 5. The engine code sites

All in `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`.

| what | where |
|:--|:--|
| **the line's baseline model** — `LINE_BASE = 0.8f`, "the baseline sits 0.8 of the box below its top" | **`:220`** |
| **the hairline box** `w:line = min(0.069·size, 0.6485) pt = min(1.38·size, 12.97) twips` | **`:4119` `hairlinePt()`** |
| **the box solver** `box = (pitch − (1−LINE_BASE)·prevBox)/LINE_BASE`, clamped to `[size, 1.15·size]` | **`:4134` `flowLinePt()`** |
| **the one place every `w:spacing` is emitted** (before / after=0 / line / lineRule) | **`:155` `spacing()`** |
| absolute flow placement + re-sync (`place()` / `resync()`, "the position is now ABSOLUTE") | `:4171`-`:4230` |
| **flow line writer**: `before = target − box_top − LINE_BASE·box` | `:4483`-`:4520` |
| cell/row writer: row height, `w:trHeight`, `cellLineHere` | `:2284`, `:2300`, `:6494` |
| **the correct cell form**: `cellBeforeTw = round(LINE_BASE * (rowLineTw − cellBoxTw))` | **`:6933`** |
| **THE DEFECT**: the "raise a slightly-short cell" branch writes `cellBeforeTw = rowHeightTw − cellBoxTw` | **`:7013`** |

`:7013` sits inside the branch `if (vspan <= 1 && !cell.isEmpty() && … && deficitTw > 0 &&
deficitTw * 4 <= rowHeightTw)`, whose own docstring explains it is for a cell "within a
quarter of its row [that] is the same row measured slightly short, and the page's own text
has to fill it". It fills the row, but it charges `LINE_BASE` to the box only, so the
baseline lands `(1 − LINE_BASE) × (rowHeight − box)` below the row's foot.

The file already knows this: the fallback twelve lines below at `:6929-6933` carries the
comment *"Writing `before = rowLineTw − box` instead moved every cell 0.2 × row pitch lower
and 18_median_dy went 64 → 100 documents."* That is the same arithmetic, and `:7013` is
that construct, reinstated in the branch that fills the deficit.

---

## 6. Verdict, with the number that proves it

**(a) for `31_times_body_arial_headings` — instrument artefact, 2.65 of 2.70 pt.**
`dy(origin)` median **+0.08 pt**, max **0.95 pt**: the engine's baselines coincide with the
page's to a tenth of a point. `dy(bbox top)` is **+2.70 pt**, and the ascent difference
between the source's Helvetica (1.07 em) and the built Liberation Sans (0.80 em) is
**+2.65 pt** at the median size. **2.65 / 2.70 = 98 % of the charge is font metrics, not
placement.** No engine change can clear this; the check can, and at HEAD it already does.

**(b) for `74_balance_sheet_indented_subitems` — engine defect, 1.71 pt.**
`dy(origin)` is **+1.71 pt** on 12 of 54 runs and **+3.31 pt** on 15 more, and those are
exactly the runs in table cells whose row pitch is split into `w:before` + `w:line`. The
predicted offset `0.2 × w:before` is **1.700 pt** and **3.280 pt**; measured **1.71** and
**3.31**. `dy(origin)` is **+0.01 pt** on every run in a hairline paragraph of the same
document — the same page, the same engine, the same faces. **The engine places flow lines
exactly and table-cell lines 0.2·`w:before` too low.**

**Neither verdict covers the cluster.** Of the 23 documents that fail 18 and nothing else,
under the LibreOffice proxy at HEAD: 8 pass, 15 fail, and **flipping the metric from bbox
top to origin changes exactly 1 verdict** (`68_journal_wide_table_spanning`: PASS on bbox →
FAIL on origin). The ascent artefact is real and worth 2.1-3.2 pt of *charge*, but the
cluster is not made of it.

---

## 7. The proposed change, and what it was measured to be worth

**One line, `DocxWriter.java:7013`:**

```java
-  cellBeforeTw = rowHeightTw - cellBoxTw;
+  cellBeforeTw = Math.max(0, Math.round(LINE_BASE * (rowHeightTw - cellBoxTw)));
```

which makes the branch land the baseline on the row's foot (`LINE_BASE × rowHeight`),
identical in form to the fallback at `:6933` that already does it correctly.

Measured, engine rebuilt at HEAD + this patch, all 13 documents re-converted and
re-rendered, check 18 read on origins:

| document | HEAD | patched | verdict |
|:--|:--|:--|:--|
| `74_balance_sheet_indented_subitems` | med +1.71 worst 3.31 | med **+0.01** worst **0.01** | **FAIL → PASS** |
| `72_bank_statement_no_rules_right_amounts` | +1.71 / 4.31 | **+0.01 / 0.81** | **FAIL → PASS** |
| `bus-timetable-station-left-times-right` | +3.19 / 3.19 | **−0.01 / 0.49** | **FAIL → PASS** |
| `36_embedded_subset_font` | +0.75 / 4.66 | **+0.05 / 0.76** | **FAIL → PASS** |
| `71_invoice_space_aligned_no_rules` | +3.31 / 14.01 | +1.51 / 8.71 | FAIL → FAIL (improved) |
| `price-list-2col-dense-right-aligned` | +4.42 / 135.62 | +1.22 / 132.42 | FAIL → FAIL (improved) |
| `303_discharge_summary` | +0.33 / 1.00 | +0.33 / 1.00 | unchanged PASS |
| `31_times_body_arial_headings` | +0.08 / 0.95 | +0.08 / 0.95 | unchanged PASS |
| `320_balance_sheet_statutory` | +0.35 / 0.75 | +0.35 / 0.75 | unchanged PASS |
| `325_demat_holdings_statement` | +0.40 / 1.00 | +0.40 / 1.00 | unchanged PASS |
| `402_calendar_month_grid` | −0.50 / 1.98 | −0.50 / 1.98 | unchanged PASS |
| `report-2col-table-spanning-both-columns` | −0.51 / 2.54 | −0.51 / 2.54 | unchanged PASS |
| `electricity-bill` | −2.61 / 8.51 | −2.61 / 8.51 | unchanged FAIL |

**Predicted clean-document count: +4** — `74_balance_sheet_indented_subitems`,
`72_bank_statement_no_rules_right_amounts`, `bus-timetable-station-left-times-right`,
`36_embedded_subset_font`, every one of which fails 18_displacement and nothing else, so
each is a whole document. **0 regressions in 13 rebuilt documents**, and the seven controls
read bit-identical med/worst.

That is the honest size of it: **+4, not +25 and not +52.6.** Two more documents improve
substantially without clearing (`71_invoice` med +3.31 → +1.51, `price-list` +4.42 →
+1.22) and are the next construct, not this one.

The ceiling is unknown: 95 of the 118 failing documents were not re-converted, so the count
of *other* documents whose cell deficit branch fires is **not measured**. On the evidence of
§4b the branch's blast radius is proportional to the filled deficit — 32 twips on
`362_price_list_dense` (0.32 pt, harmless), 170 twips on `74_balance` (1.70 pt, a fail) — so
documents with near-full rows are the ones to expect.

---

## 8. What would prove me wrong

1. **A Google render of `74_balance_sheet_indented_subitems` at HEAD showing `dy(origin)`
   ≈ 0.** Then `w:before` at the top of a cell is honoured differently by Google than by
   LibreOffice, the +1.71 pt is a proxy artefact, and the patch is a proxy fix. This is the
   single most important falsifier and it needs a Google render.
2. **A Google render of `31_times_body_arial_headings` at HEAD showing `worst_dy` > 7.35 pt
   (2 × its 3.675 pt tolerance) on origins.** Then the ascent term is not the whole charge
   and there is a residual engine displacement in pure flow as well. (The repo's
   `18dA-03` finding already reports Google `dy(origin)` +0.07 / 0.96 on this document,
   which agrees with my +0.08 / 0.95 — that is corroboration, not my measurement.)
3. **The patch regressing any document.** Measured: 0 of 13. If it regresses
   `362_price_list_dense`, `16_right_aligned_amounts_txtpos` or `402_calendar_month_grid` —
   the three documents the branch was written for — the branch is load-bearing in a way
   this sample did not see.
4. **`23_line_pitch` moving.** `LINE_BASE` also drives the advance, so the guard is that
   line pitch stays inside 1.0 pt. Not checked here.
5. **If more than 4 of the remaining 95 failing documents were 18-only and this construct
   fixed them**, my population statement in §1 ("the cluster is not made of it") is too
   strong.

---

## 9. What could NOT be determined without a Google render

* Every Google-rendered number in this file. All renders are LibreOffice 7.4.7.2. The repo
  has measured that the two disagree badly on table-heavy documents (`320_balance_sheet_statutory`:
  LibreOffice med 0.05 / worst 0.45 against Google 8.2 / 19.4), so the 8-pass/15-fail split
  in §6 is a proxy split, not a Google verdict.
* The Google value of the 118 and the 52.61 leverage after the origin change. The store
  predates it; the proxy says the change moves 1 verdict of 23, but Google is where the
  stored numbers came from and only Google can restate them.
* Whether `w:before` on a cell's first paragraph is honoured identically by Word, Google
  Docs and LibreOffice. The whole of §6(b) rests on all three placing the first baseline at
  `before + LINE_BASE·box`; measured in LibreOffice only.

## 10. Not done, and why

* No full-corpus re-measure (`regress.py --check`, `gate.py --budget 250`): the corpus
  conversion is 213 × 10.8 s plus a LibreOffice render each, well past the per-build limit.
  13 documents were rebuilt, chosen as the 4 predicted fixes plus 9 controls.
* No `23_line_pitch` guard check on the patched build (§8.4).
* The engine tree is reverted; nothing in `app/` or `tools/` is modified (`git status`
  clean at `fb81b49`). The patch above is a diff in this file, not a working-tree change.
