# 18D — the census of the 19 that fail `18_displacement` and nothing else, and the measured gap law put against them

**28 Nov 2026 · read-only investigation · repo `kavopdf/app` @ `eb4512f8` (`git log -1`, 2026-11-28 03:44:34 +0000)
· engine compiled and the 19 `.docx` built on this pod · no engine file edited, nothing committed, nothing
pushed, nothing deleted.**

`DocxWriter.java` sha256 `eac6dbed620c5a4684aac6a0181ccccfce79aa25470c2d8c19408d0c130e02d3`, `git status app/`
empty. Every number below was produced by a script that read a file on this pod; the scripts and their CSVs
are named in §7.

---

## 0. The answer in one paragraph

**No. The measured Google gap law (`shift = 0.961 × gap − 0.58 pt`) does not explain these 19, and it is not
even the right population.** It is a law about *continuation pages* — the `w:before` Google drops on the first
paragraph after a page break. All 19 are **single-page** and the emitted `word/document.xml` of all 19 contains
**zero** page breaks (§2), so the law's population is empty here. Forced onto the only gap these documents do
carry — the exact-line height of an empty spacer — it lands **1 of 19 inside 1 pt** (and that one,
`35_four_typefaces_one_page`, is inside by 0.06 pt of coincidence: its shape is wrong, §3.3). Residuals run
**−0.06 to +12.39 pt, mean +4.85, sd 3.18**, and the law is one-signed while the measured `med_dy` is
two-signed (the law predicts negative on 15, the store measures negative on 8).

The reason is measurable and it is the surprise in this census: **the law is already compensated, and the
compensation has been spent on every gap these 19 have.** Of the 21 empty spacer paragraphs in the 19 with a
gap over 1 pt, **20 carry `w:before` equal to `0.70 × (gap − 0.05)` to within 0.03 pt** — that is
`SPACER_SPEND_FRAC` (`DocxWriter.java:58`) having already run at `:6171`. The 21st is not a gap at all: it is
the 4 pt post-table carrier (`POST_TABLE_TW`, `:7399`). So the question is not "which code path misses them"
— the path is taken and the spend is in the bytes — it is that the compensation's **own residue**
(`0.784 × 0.30 × G`) is at most **4.11 pt on one document** and below 1.5 pt — the check's own tolerance floor —
on 16 of the 19 (§5).

**The one change and its count: carry 100 % of every gap in `w:before` (`SPACER_SPEND_FRAC` 0.70 → 1.00) — the
rule being "no vertical advance may be declared in `w:line`, because Google draws 21.6 % of it". Predicted
CLEAN: 0 of 19.** The arithmetic, the corroborating full-spend measurement already in the repo, and the four
things that would prove this wrong are in §5.

---

## 1. The 19, by name, from the store the pipeline already has

Store: `benchmarks/gverify/*.json` (214 files, 213 scored). Read with `failed == ["18_displacement"]` and
`status != "page_count_refused"`, exactly the predicate `classpick.py --leverage` uses (`classpick.py:704-712`).
It returns **19**, and `classpick.py --leverage` prints the same number on the same store:

```
     19  18_displacement
```

`tools/p2w-bench/RESULTS.jsonl` is **not** this store — it is an older engine (`2a68de6`) with the pre-rename
check names (`18_median_dy`, `19_worst_dy`, `20_within_10pt`), so it cannot answer this question and was not
used. `benchmarks/RANKING.csv` is a pixel score with no per-check verdicts and was not used either.

| # | document | stored Google `med_dy` | `worst_dy` | runs matched | engine stamp | measured at |
|--:|:--|--:|--:|--:|:--|:--|
| 1 | `10_stamp_as_image` | −1.8 | 3.1 | 52 | `a05b20eb05fe0fc8` | 2026-11-27 12:15:15 |
| 2 | `303_discharge_summary` | +0.9 | 3.1 | 45 | `a05b20eb05fe0fc8` | 2026-11-27 12:26:55 |
| 3 | `306_clinical_protocol_synopsis` | −0.4 | 6.6 | 75 | `a05b20eb05fe0fc8` | 2026-11-27 12:27:06 |
| 4 | `30_mixed_font_sizes_one_baseline_txtpos` | +2.3 | 4.2 | 38 | `a05b20eb05fe0fc8` | 2026-11-27 12:27:09 |
| 5 | `320_balance_sheet_statutory` | +7.2 | 16.2 | 73 | `a05b20eb05fe0fc8` | 2026-11-27 12:29:18 |
| 6 | `341_shipping_manifest` | +2.4 | 21.4 | 304 | `a05b20eb05fe0fc8` | 2026-11-28 00:00:25 |
| 7 | `35_four_typefaces_one_page` | −2.8 | 3.3 | 52 | `a05b20eb05fe0fc8` | 2026-11-27 12:48:11 |
| 8 | `403_crossword_puzzle` | −7.7 | 10.6 | 27 | `a05b20eb05fe0fc8` | 2026-11-27 13:37:52 |
| 9 | `70_magazine_drop_cap_photo_caption` | +2.9 | 3.1 | 24 | `a05b20eb05fe0fc8` | 2026-11-27 14:44:22 |
| 10 | `71_invoice_space_aligned_no_rules` | +2.9 | 26.3 | 72 | `a05b20eb05fe0fc8` | 2026-11-27 14:44:22 |
| 11 | `72_bank_statement_no_rules_right_amounts` | −1.0 | 3.5 | 80 | `a05b20eb05fe0fc8` | 2026-11-27 14:44:33 |
| 12 | `74_balance_sheet_indented_subitems` | +1.5 | 4.6 | 54 | `a05b20eb05fe0fc8` | 2026-11-27 14:44:34 |
| 13 | `balance-sheet-two-columns-of-figures` | −0.5 | 4.0 | 94 | `a05b20eb05fe0fc8` | 2026-11-27 14:45:11 |
| 14 | `bus-timetable-station-left-times-right` | +4.2 | 5.9 | 177 | `a05b20eb05fe0fc8` | 2026-11-27 14:45:42 |
| 15 | `eway-bill` | −2.7 | 4.7 | 129 | `a05b20eb05fe0fc8` | 2026-11-27 14:45:54 |
| 16 | `price-list-2col-dense-right-aligned` | +5.8 | 8.8 | 253 | `a05b20eb05fe0fc8` | 2026-11-27 14:47:12 |
| 17 | `table-inside-two-column-page` | +8.0 | 69.2 | 64 | `a05b20eb05fe0fc8` | 2026-11-27 14:47:46 |
| 18 | `table-with-no-header-row` | +0.7 | 4.0 | 215 | `a05b20eb05fe0fc8` | 2026-11-27 14:48:01 |
| 19 | `two-tables-stacked-with-no-gap` | −1.2 | 2.9 | 72 | `a05b20eb05fe0fc8` | 2026-11-27 14:48:10 |

**One discrepancy, stated rather than smoothed.** `FINDINGS/18prize-01-…-CENSUS-28NOV-agent.md` (04:12 the same
day) reports **18** solo documents. Its list is this list **minus `341_shipping_manifest`**, which is the one
row in the store whose verdict was rewritten at **2026-11-28 00:00:25** — after the other eighteen. The store at
HEAD and `classpick.py --leverage` both say **19**; the census's 18 is a snapshot one row behind. The task's
number is the store's number, and this file censuses all 19.

**What the store does *not* keep, and therefore what cannot be measured.** `gverify.py:494-499` stores
`displacement` as the check's `detail` dict only — `med_dy`, `worst_dy`, `med_dx`, `bad_pages`,
`runs_matched`. **There is no per-line `dy` in the store for any of the 19.** `verify_google.py:5863-5930`
computes `ds = [(g.roy − r.roy, r.size) …]` per page and reduces it to `n_out` / `worst_here` in-process; the
reduction is never persisted. So the per-line column the brief asks for is **not measured**, for all 19, and
every `dy` used below is the stored document-level median — the one number the store actually holds. One
document of the 19 *does* have a per-row Google measurement in the repo, quoted in §3.3 from a committed
finding; the other eighteen do not.

---

## 2. The gaps, read out of `word/document.xml` of the shipped `.docx`

The `.docx` for all 19 was **not** on disk, so it was built: `bash tools/p2w-bench/jdk-fetch.sh` (JDK 17 at
`/scratch/work/.p2w-jdk/jdk`), `pod-prep.sh` steps 3-6 by hand (the whole-corpus step exceeds a 300 s call),
then `ConvertOne` per document. All 19 converted, all **single-page**:

```
306_clinical_protocol_synopsis   pages=1  paragraphs=3
341_shipping_manifest            pages=1  paragraphs=3
price-list-2col-dense-right-aligned pages=1 paragraphs=5
…
```

Conversion is deterministic: re-converting `eway-bill` into a clean directory gives a `word/document.xml`
byte-identical to the first (`sha256` equal, 126,210 bytes).

`/scratch/work/gaps.py` walks `word/document.xml` in document order and dumps every vertical gap to
`/scratch/work/gapcsv/paragraphs.csv` (1,920 rows: one row per paragraph, body and cell) and
`/scratch/work/gapcsv/documents.csv` (one row per document). It records, per paragraph: `w:before`,
`w:after`, `w:line`, `w:lineRule`, whether it carries `w:br w:type="page"`, its `w:sz`, its `pStyle`, its
text length; and per table row the `w:trHeight` `w:val` and `hRule`. The per-document summary:

| document | paragraphs | empty spacers | cell paragraphs | tables | **page breaks** | Σ spacer gap (pt) | largest spacer line (pt) | Σ `w:before` on text paragraphs (pt) |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| `10_stamp_as_image` | 51 | 2 | 35 | 1 | **0** | 11.60 | 3.50 | 660.15 |
| `303_discharge_summary` | 43 | 3 | 20 | 1 | **0** | 11.45 | 3.45 | 636.60 |
| `306_clinical_protocol_synopsis` | 101 | 4 | 94 | 2 | **0** | 30.85 | 5.70 | 42.00 |
| `30_mixed_font_sizes_one_baseline_txtpos` | 30 | 1 | 12 | 1 | **0** | 11.80 | 3.55 | 675.60 |
| `320_balance_sheet_statutory` | 88 | 2 | 79 | 2 | **0** | 19.75 | 3.60 | 469.45 |
| `341_shipping_manifest` | 305 | 1 | 300 | 1 | **0** | 18.90 | 5.70 | 229.40 |
| `35_four_typefaces_one_page` | 51 | 1 | 35 | 1 | **0** | 11.45 | 3.45 | 652.30 |
| `403_crossword_puzzle` | 28 | 1 | 14 | 1 | **0** | 58.15 | 17.50 | 648.95 |
| `70_magazine_drop_cap_photo_caption` | 24 | 1 | 0 | 0 | **0** | 0.05 | 0.05 | 791.90 |
| `71_invoice_space_aligned_no_rules` | 68 | 0 | 56 | 2 | **0** | 0.00 | 0.00 | 555.35 |
| `72_bank_statement_no_rules_right_amounts` | 99 | 1 | 90 | 1 | **0** | 18.30 | 5.50 | 475.95 |
| `74_balance_sheet_indented_subitems` | 48 | 2 | 30 | 2 | **0** | 6.55 | 1.00 | 619.95 |
| `balance-sheet-two-columns-of-figures` | 107 | 2 | 96 | 2 | **0** | 12.65 | 3.80 | 594.15 |
| `bus-timetable-station-left-times-right` | 173 | 1 | 165 | 1 | **0** | 6.35 | 1.95 | 256.70 |
| `eway-bill` | 129 | 3 | 119 | 3 | **0** | 30.95 | 5.60 | 395.15 |
| `price-list-2col-dense-right-aligned` | 250 | 0 | 245 | 1 | **0** | 0.00 | 0.00 | 141.35 |
| `table-inside-two-column-page` | 40 | 1 | 34 | 1 | **0** | 0.05 | 0.05 | 358.65 |
| `table-with-no-header-row` | 214 | 1 | 208 | 1 | **0** | 12.35 | 3.75 | 323.90 |
| `two-tables-stacked-with-no-gap` | 71 | 1 | 65 | 1 | **0** | 12.35 | 3.75 | 560.90 |

Four facts fall out of that table, and they decide the whole question:

1. **Zero page breaks in all 19.** The `w:before`-after-a-page-break leg of the law — the leg that produced
   `0.961 × gap − 0.58` over 332 continuation pages — **cannot fire on a single one of them**. `bad_pages` is
   `[0]` in the store for all 19, which agrees.
2. **Every document is one page**, so there is no page-top gap and no page scale.
3. **`w:lineRule="exact"` on 1,920 of 1,920 paragraphs** — the construct `SETTLED.md:497` records for 213/213.
4. **The gaps are tiny.** The largest exact-line spacer gap anywhere in the 19 is `403_crossword_puzzle`'s
   **17.50 pt**; 13 of 19 have Σ spacer gap under 4 pt and 4 have none (G ≤ 0.05 pt). The large vertical distances in
   these documents (e.g. 403's 314 pt before its closing paragraph, 70's 225 pt) are carried in **`w:before` of
   a text paragraph**, which Google honours 1:1 and which therefore needs no compensation.

---

## 3. Measured `dy` against the law's prediction, per document

**The prediction.** The law as the corpus states it (`FIXER-BRIEF.md:195`, fitted in
`DOCS-ROOT-CAUSES-24NOV.md:609`) is `shift = 0.961 × gap − 0.58 pt`, one-signed and cumulative, so
`dy_predicted = −(0.961 × G − 0.58)` where `G` is the gap Google does not draw. On these documents the only
candidate `G` is the exact-line height asked of an empty spacer (the construct the brief names: "Google
delivers only 5–10 pt of an exact line height asked of an empty spacer"), so `G` is the sum of `w:line` over
the document's empty body paragraphs, in points. That is the most favourable reading of the law for these
documents; the alternative reading (the whole `before + line` of the spacer) is worse, because `w:before` is
honoured 1:1 and must not be counted as lost.

| # | document | stored Google `med_dy` | `worst_dy` | runs | tol (pt) | exact-line spacer gap G (pt) | spacers w/ gap>1 pt | of which compensated | law `dy = −(0.961·G − 0.58)` | **residual** (measured − predicted) |
|--:|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | `10_stamp_as_image` | -1.8 | 3.1 | 52 | 2.97 | 3.55 | 1 | 1 | -2.83 | **+1.03** |
| 2 | `303_discharge_summary` | +0.9 | 3.1 | 45 | 2.80 | 3.55 | 1 | 1 | -2.83 | **+3.73** |
| 3 | `306_clinical_protocol_synopsis` | -0.4 | 6.6 | 75 | 2.62 | 12.15 | 3 | 2 | -11.10 | **+10.70** |
| 4 | `30_mixed_font_sizes_one_baseline_txtpos` | +2.3 | 4.2 | 38 | 3.15 | 3.55 | 1 | 1 | -2.83 | **+5.13** |
| 5 | `320_balance_sheet_statutory` | +7.2 | 16.2 | 73 | 2.62 | 6.00 | 2 | 2 | -5.19 | **+12.39** |
| 6 | `341_shipping_manifest` | +2.4 | 21.4 | 304 | 2.17 | 5.70 | 1 | 1 | -4.90 | **+7.30** |
| 7 | `35_four_typefaces_one_page` | -2.8 | 3.3 | 52 | 3.15 | 3.45 | 1 | 1 | -2.74 | **-0.06** |
| 8 | `403_crossword_puzzle` | -7.7 | 10.6 | 27 | 2.45 | 17.50 | 1 | 1 | -16.24 | **+8.54** |
| 9 | `70_magazine_drop_cap_photo_caption` | +2.9 | 3.1 | 24 | 3.22 | 0.05 | 0 | 0 | +0.53 | **+2.37** |
| 10 | `71_invoice_space_aligned_no_rules` | +2.9 | 26.3 | 72 | 3.15 | 0.00 | 0 | 0 | +0.58 | **+2.32** |
| 11 | `72_bank_statement_no_rules_right_amounts` | -1.0 | 3.5 | 80 | 3.01 | 5.50 | 1 | 1 | -4.71 | **+3.71** |
| 12 | `74_balance_sheet_indented_subitems` | +1.5 | 4.6 | 54 | 3.04 | 2.00 | 2 | 2 | -1.34 | **+2.84** |
| 13 | `balance-sheet-two-columns-of-figures` | -0.5 | 4.0 | 94 | 2.73 | 3.85 | 1 | 1 | -3.12 | **+2.62** |
| 14 | `bus-timetable-station-left-times-right` | +4.2 | 5.9 | 177 | 3.01 | 1.95 | 1 | 1 | -1.29 | **+5.49** |
| 15 | `eway-bill` | -2.7 | 4.7 | 129 | 2.45 | 9.40 | 3 | 3 | -8.45 | **+5.75** |
| 16 | `price-list-2col-dense-right-aligned` | +5.8 | 8.8 | 253 | 2.73 | 0.00 | 0 | 0 | +0.58 | **+5.22** |
| 17 | `table-inside-two-column-page` | +8.0 | 69.2 | 64 | 3.11 | 0.05 | 0 | 0 | +0.53 | **+7.47** |
| 18 | `table-with-no-header-row` | +0.7 | 4.0 | 215 | 2.59 | 3.75 | 1 | 1 | -3.02 | **+3.72** |
| 19 | `two-tables-stacked-with-no-gap` | -1.2 | 2.9 | 72 | 2.59 | 3.75 | 1 | 1 | -3.02 | **+1.82** |

(`tol` is the check's own `clamp(0.35 × size, 1.5, 4.5)` at the document's median matched run size,
`verify_google.py:5863-5864`; the size is read off the emitted `w:sz`.)

### 3.1 How many it explains, to within 1 pt: **one of nineteen**

| statement | count |
|:--|--:|
| residual within ±1 pt | **1 of 19** (`35_four_typefaces_one_page`, −0.06) |
| residual within ±2 pt | 3 of 19 |
| residual mean / sd / min / max | **+4.85 / 3.18 / −0.06 / +12.39** |
| law predicts negative (built text high) | 15 of 19 |
| store measures negative | **8 of 19** |
| sign agreement | 12 of 19 |
| document's `med_dy` already inside its own tolerance | **12 of 19** |
| `worst_dy` past 2 × tolerance (the tail clause) | **7 of 19** |

### 3.2 What the residual looks like on the eighteen it does not explain

* **It is one-signed positive and systematic: +4.85 pt on average.** The law is a *one-signed high* predictor;
  the built page sits **lower** than the law says, on every document but one. A law of the form
  `−k·G + c` with `k ≈ 0.961` and `c = 0.58` has the wrong intercept for this population: fitting the same
  two-parameter form to the 19 gives `dy = +3.68 − 0.575·G` (r = −0.676, R² = 0.46), i.e. **slope 0.575, not
  0.961, and intercept +3.68, not −0.58**. Even the best two-parameter fit of the law's own shape leaves an
  rms residual of **2.71 pt** against tolerances of 2.17–3.22 pt.
* **The error is not in the median at all on most of them.** 12 of 19 already have `|med_dy|` inside their own
  tolerance; the failure is in the **count clause / tail clause**, exactly as
  `FINDINGS/18DISPLACEMENT-COUNT-0125-27NOV.md` measured on the then-14: a handful of runs 3–7 pt out while the
  median is under 1 pt. 7 of 19 have `worst_dy` past twice their tolerance (`table-inside-two-column-page`
  69.2 pt, `71_invoice` 26.3, `341_shipping_manifest` 21.4, `320_balance_sheet` 16.2, `403_crossword` 10.6,
  `price-list-2col-dense` 8.8, `306_clinical_protocol` 6.6). A single translation — which is what the law is —
  cannot close a spread: the gap between `worst_dy` and `|med_dy|` runs from 0.5 pt to **61.2 pt**.
* **The three documents where the lever actually exists are the three the law is worst on.** Only 3 of 19 have
  an exact-line spacer gap over 6 pt: `403_crossword_puzzle` (17.50), `306_clinical_protocol_synopsis` (12.15),
  `eway-bill` (9.40). The law's residuals there are **+8.54, +10.70, +5.75** — the worst three, not the best.

### 3.3 The one document that "fits" fits on level and fails on shape

`35_four_typefaces_one_page` is the only residual inside 1 pt, and the repository already holds a **per-row
Google measurement** for it (`/scratch/input/18d-WLINE-GOOGLE-MEASURED.md` §5, from
`benchmarks/gverify/35_four_typefaces_one_page.json` and the 28 Nov 08:24 export):

| row | source | Google | dy |
|:--|--:|--:|--:|
| header | 139.18 | 137.22 | −1.96 |
| BCO-401 | 158.18 | 155.97 | −2.21 |
| BCO-402 | 177.18 | 174.72 | −2.46 |
| BCO-403 | 196.18 | 193.47 | −2.71 |
| BCO-404 | 215.18 | 212.22 | −2.96 |
| BCO-405 | 234.18 | 230.97 | −3.21 |
| BCO-406 | 253.18 | 250.47 | −3.71 |
| laid row pitch | 19.00 | **18.75** | **−0.25 / row** |

The spacer law predicts a **constant** `dy` for every run below the gap. Measured, `dy` **ramps** −1.96 →
−3.71, a straight −0.25 pt per row. The law's level (−2.74) happens to fall inside that ramp; its **shape** is
refuted by the same seven numbers. This is the one document in the 19 whose per-row data exists, and it says
the displacement is per-row accumulation, not one gap.

---

## 4. What compensation the engine already has, exactly where, on which path — and why it is not the answer

### 4.1 What exists (grep of `app/src/main/java`, `DocxWriter.java` unless stated)

| what | where | what it does | on which code path |
|:--|:--|:--|:--|
| **`SPACER_SPEND_FRAC = 0.70f`** | **`DocxWriter.java:58`**, spent at **`:6171`** (`int spendTw = Math.round(SPACER_SPEND_FRAC * wantTw);`) | moves 70 % of a table spacer's gap out of `w:line` (Google draws **21.6 %**) into `w:before` (1:1) | **only** the `if (spacerTw > 0)` block of `table(StringBuilder, PdfToWord.Table, Ctx)` (`:6011`), i.e. the spacer paragraph the engine emits **before a `<w:tbl>`** whose top rule the page drew below the flow |
| the 21.6 % law, written down | `:57` (constant's docstring), `:6170`, `:6174-6176` ("Google lays an exact line box at `2.5873 * max(L/240, 0.06)` pt … a gap carried by `w:line` alone is a gap the reader never draws … high by **0.784 × G**") | the constant's justification | comment only |
| `spacerHairTw = 1` | `:6155` | the twip left in `w:line` after the spend | same block |
| **`HAIRLINE_EM = 0.069f`** | **`:113`** (box emitted at `:4130` `hairlinePt()`), documented at `:80-112` | writes `w:line = 1.38 × size` so that Google's *floor* charge `0.069 × size` equals Word's `w:line/20` | **every flow line** — this is the engine's per-line gap compensation, and it is why the law's slope is 0.961 rather than 1 |
| **`ROW_RUNG_UNDER_TW = 10`** | **`:54`**, used at **`:6601`** (`rowHeightTw -= ROW_RUNG_UNDER_TW`) | declares a pitch-bound row 0.5 pt under the 0.75 pt rung Google snaps to | the table row loop |
| `FOOT_ROOM_MIN_TW = 100` | `:56`, used `:6598-6601` | gate for the above | same |
| `LINE_BASE = 0.8f` | **`:220`** | baseline at 0.8 of the line box — the model, not a compensation | every placement |
| `gapCapTw(ctx)` | `:405`, caps `GAP_CAP_TW = 2400` (`:267`) / `GAP_CAP_SPEND_TW = 20000` (`:289`) | beyond the cap the flow is anchored into a drawing box instead of being given a gap | page-top / inter-block gaps |
| `POST_TABLE_TW = 80` / `POST_TABLE_TW_STACKED = 1` | `:7399` / `:7408`, emitted `:7186-7192` | the 4 pt carrier paragraph after a table — **no spend applied** | after every table |
| `breakPage()` | `:686-701` | the page-break carrier, `w:line="1"` — **no spend applied**, and none needed | page breaks |

**There is no `0.961` and no `1.04` anywhere in `app/src/main/java`.** `grep -rn "0\.961\|1\.04\|0\.784\|0\.7712\|0\.2288\|21\.6" app/src/main/java/`
returns only the three `21.6 %` comment lines (`:57`, `:6170`, `:6175`) and the unrelated `1.049 Courier New`
calibration figure at `:87`. The measured law is **not** encoded in the engine as a constant; what is encoded
is its *consequence* — "move the gap into the property that is honoured" — and only for one paragraph kind.

### 4.2 Why it does not reach these 19 — and the answer is not any of the three the brief suggests

The brief offers three candidate explanations: the code path is not taken, a different paragraph kind, or a
page-break-following paragraph. Measured against the emitted bytes, **the third is structurally impossible and
the first is false**:

* **Page-break-following paragraph: impossible.** All 19 emit **zero** `w:br w:type="page"` (§2). Nothing in
  the 19 follows a page break, so the leg of the law that produces the `0.961` fit cannot apply to any of them.
* **Code path not taken: false.** Of the **21** empty spacer paragraphs with a gap over 1 pt across the 19,
  **20 have `w:before` = `0.70 × (gap − 0.05 pt)` to within 0.03 pt** — i.e. `:6171` ran and its output is in
  the file. Examples, measured: `403_crossword_puzzle` p12 `w:before="813"` (40.65 pt) against a gap of 58.15
  pt (0.70 × 58.10 = 40.67); `72_bank_statement` p5 `w:before="256"` (12.80) against 18.30 (0.70 × 18.25 =
  12.78); `35_four_typefaces` p4 `w:before="160"` (8.00) against 11.45 (0.70 × 11.40 = 7.98);
  `bus-timetable` p4 `w:before="88"` (4.40) against 6.35 (0.70 × 6.30 = 4.41).
* **Different paragraph kind: this is the true part, but it is not a gap.** The one spacer with a gap over 1 pt
  that carries **no** spend is `306_clinical_protocol_synopsis` p99 (`w:before="0"`, `w:line="80"` = 4.00 pt),
  and it is the **post-table carrier** (`POST_TABLE_TW = 80`, `:7399`) — a separator paragraph, not a gap.
  Seven further empty paragraphs across the 19 are the 1-twip end-of-body carriers (`w:line="1"`, gap 0.05 pt).

**So the compensation does not miss these 19. It has already been spent on them, and what is left is its own
residue.** With `s = 0.70` spent and `h = G − s` left in `w:line`, Google draws `s + 0.216·h`, so the shortfall
is `0.784·h = 0.784 × 0.30 × G = **0.235·G**`. On these documents that is:

| | value |
|:--|--:|
| largest residue in the 19 (`403_crossword_puzzle`, G = 17.50) | **4.11 pt** |
| residue ≥ the check's 1.5 pt tolerance floor | **3 of 19** |
| residue < 1.5 pt (below the check's own floor, so unactionable) | **16 of 19** |
| residue on 4 documents with no spacer at all | 0.00 pt |

That is the whole of `18_displacement` these 19 have left in the gap family: **at most 4.11 pt on one
document, and under 1.5 pt on sixteen.**

---

## 5. The one change, its predicted clean count, and what would prove it wrong

### 5.1 The change

> **Rule, for every document: no vertical advance may be declared in `w:line`. Every gap the page drew is
> carried in `w:before` and only in `w:before`, because Google draws `2.5873 × max(L/240, 0.06)` pt of an exact
> line box — 21.6 % of what is asked — and honours `w:before` 1:1.**

In the engine that is one constant: **`DocxWriter.java:58`, `SPACER_SPEND_FRAC` 0.70 → 1.00**, which at `:6171`
makes `spendTw = wantTw` and leaves the one-twip hairline (`:6155`) in `w:line`. It is a rule and not a
per-document special case: it is stated over the property, not over a document or a class, and it applies to
every spacer the engine emits, on every document, in every renderer — `before + line` is unchanged to the twip,
so Word and LibreOffice lay the identical page and only Google's delivery changes.

I am naming this one rather than a different one because it is the **most aggressive member of the family the
law defines**: `SPACER_SPEND_FRAC = 1.00` is the algebraically complete compensation
(`s + 0.216(G − s) = G ⇒ s = G`), so its effect **bounds the whole family**. If the strongest member clears
nothing, no value of the constant clears anything.

### 5.2 Predicted clean count: **0 of 19**

Per document, the change moves everything below each spacer **down** by `0.235 × G`, so
`med_dy_after = med_dy + 0.235·G`:

| document | `med_dy` now | 0.235·G | `med_dy` after | tolerance | verdict |
|:--|--:|--:|--:|--:|:--|
| `403_crossword_puzzle` | −7.7 | +4.11 | **−3.58** | 2.45 | still out |
| `306_clinical_protocol_synopsis` | −0.4 | +2.86 | **+2.46** | 2.62 | median only just in; `worst_dy` 6.6 is 2.5 × tol and the change is uniform, so the tail does not move relative to the median |
| `eway-bill` | −2.7 | +2.21 | **−0.49** | 2.45 | median in; `worst_dy` 4.7 already 1.9 × tol |
| the other 16 | — | **0.00–1.41** | moves by under 1.5 pt | 2.17–3.22 | below the check's own 1.5 pt floor |

Three independent reasons the count is 0, each of which would have to be wrong:

1. **16 of 19 cannot move by more than 1.41 pt**, which is less than the check's minimum tolerance (1.5 pt) and
   less than a third of these documents' tolerances (2.17–3.22 pt).
2. **The failure is in the tail, not the median.** 12 of 19 already have `|med_dy|` inside tolerance and 7 fire
   the tail clause. A uniform translation cannot reduce a spread; `worst_dy − |med_dy|` is 0.5 pt on one
   document and **61.2 pt** on `table-inside-two-column-page`.
3. **The full spend has already been measured once, on the one document where it could matter.** The 28 Nov
   run (`tools/p2w-bench/FINDINGS/18-DISPLACEMENT-SPACER-MODEL-REFUTED-DRIFT-IS-THE-LEAD-28NOV-fixer.md`) put
   the whole 58.15 pt gap in `w:before` on `403_crossword_puzzle`: `med_dy` **−7.7 → +3.1**, `worst_dy` 5.9,
   **still fails**. My arithmetic predicts −7.7 + 4.11 = −3.58 from 0.70 → 1.00 on the *spacer* alone; the
   28 Nov run moved it further (+10.8) because it also removed the gap's other carriers. Either way the
   document does not land inside a 2.45 pt tolerance.

The same finding already records the reason this family is a dead end at HEAD: at engine `a05b20eb05fe0fc8`
the exact-line leg delivers **22.9 %** of the ask, not 3.9 % (`position = 346.12 + 0.2288·gap`, r = 1.0000,
max residual 0.002 pt, on `403_crossword_puzzle`), so `0.961 × gap − 0.58` is a law of an engine that no longer
exists — and the correction it implies was built and measured worth **0.29 pt of movement and 0 documents**.

### 5.3 What would prove this prediction wrong

Any one of these, and §5.2 is wrong:

1. **A Google render of one of the 19 at `SPACER_SPEND_FRAC = 1.00` coming back CLEAN.** One document is
   enough; the prediction is a count of zero.
2. **A within-document Google slope near 0.96 on the exact-line leg** at this engine — i.e. a re-measurement of
   the five-export probe on `403_crossword_puzzle` giving `shift ≈ 0.961·gap` instead of the recorded
   `0.2288·gap`. That would restore the law and void §3 as well.
3. **A `w:before`-after-a-page-break measurement inside these 19.** If any of them is found to emit a page
   break in the `.docx` the store scored, then §2's "zero page breaks" is wrong and the law's real population is
   not empty. **I tried to settle this by hash and could not**: `benchmarks/DOCX-HASHES.json` was recorded
   **2026-11-25T03:37:02** (an engine three days older than the store's `a05b20eb05fe0fc8`), and all **19 of 19**
   of my freshly built `.docx` differ from it — and the hash is not even reproducible run-to-run, because the
   zip carries the conversion timestamp: two conversions of `eway-bill` differ at **byte 11** (the local-header
   mtime) while `word/document.xml` is **sha256-identical** (126,210 bytes both). So a hash mismatch proves
   nothing here, and §2-§3 describe the bytes this engine emits today at `eb4512f8`, not a proven copy of the
   bytes the store scored.
4. **A per-line Google `dy` for any of the 19 showing a constant offset below the spacer** rather than the ramp
   §3.3 shows on `35_four_typefaces`. The law's shape, not its level, is what §3 refutes.
5. **A corpus `gverify` on the patched engine in which any of the 19 goes 41/42 → 42/42** (or 46/47 → 47/47).

### 5.4 What the census does say the target is — stated as a measurement, not as a change

The 19 are a **residue**, and the numbers say what kind: `|med_dy|` ≤ 8 pt on every one, two-signed, 12 of 19
already inside their own tolerance, 7 failing on the tail with `worst_dy` up to 69.2 pt. Nothing in the gap
family reaches that, and the two constructs that could — the per-line exact-line box (`HAIRLINE_EM`, `:113`)
and the row rung (`ROW_RUNG_UNDER_TW`, `:54`) — are both already tuned to the best values the record has
(`ROW_RUNG_UNDER_TW = 0` was measured **4 better, 63 worse**; `LINE_BASE` 0.8 → 0.312 was measured **1 clean,
4 unmoved, 2 worse**). `FINDINGS/18dA-03-…` supplies the mechanism the medians actually look like: the check's
`dy` is a **bbox-top** difference (`verify_google.py:268`, `:5874`), so it charges
`ascent(built face) − ascent(source face)` as displacement — a constant per document, two-signed by face, which
is exactly the shape of the 19's medians and not the shape of any gap law. **That is a finding about the
instrument, not a licence to change it**, and §5.3's item 1 is still the only thing that would settle a change.

---

## 6. What could not be measured, and what blocked it

| wanted | status | why |
|:--|:--|:--|
| per-line Google `dy` for the 19 | **not measured** | `gverify.py:494-499` persists only the check's `detail` dict (`med_dy`, `worst_dy`, `med_dx`, `bad_pages`, `runs_matched`). No per-run or per-page `dy` is stored for any document, and `verify_google.py` reduces `ds` in-process (`:5887-5894`). The 18 cannot be recovered without re-rendering each in Google. |
| per-row Google `dy` | measured for **1 of 19** (`35_four_typefaces_one_page`, §3.3, from the committed export) | the rest would need a fresh Drive round trip |
| a fresh Google render of any of the 19 | **not measured** | this task class cannot put a `.docx` into Drive: the four Drive write tools take an `s3key` minted by the platform `upload` action, which is not reachable from a delegated task (reproduced at length in `/scratch/input/18d-WLINE-GOOGLE-MEASURED.md` §3). Every `dy` in §3 is therefore the **stored** Google measurement of 27-28 Nov at engine `a05b20eb05fe0fc8`, not a render I made. |
| LibreOffice `dy` for the 19 | deliberately not used as evidence | the two renderers disagree in sign on documents in this set (`35_four_typefaces`: LO +6.12, Google −1.96), so a LO number cannot test a Google law. Two documents were rendered to LO in §5.1's absence only to confirm the *face* metrics, and no LO number is used in §3 or §5. |

---

## 7. Provenance — every number above and the script that produced it

| artefact | what it is |
|:--|:--|
| `/scratch/work/CS` | `git clone --depth 1 https://github.com/kavopdf/app`, HEAD `eb4512f8`, 2026-11-28 03:44:34 +0000 |
| `/scratch/work/gaps.py` | walks `word/document.xml` of each of the 19; writes the two gap CSVs |
| `/scratch/work/gapcsv/paragraphs.csv` | **1,920 rows**, one per paragraph (body and cell), with `w:before`, `w:after`, `w:line`, `w:lineRule`, page-break flag, `w:sz`, `pStyle`, `w:trHeight` + `hRule` |
| `/scratch/work/gapcsv/documents.csv` | one row per document: paragraph/table/row counts, page breaks, spacer sums, cell sums, `w:trHeight` values |
| `/scratch/work/lawtest.py` → `gapcsv/law-test.csv` | the law's prediction per document, against the stored `med_dy`, plus the source geometry read from the corpus PDF with PyMuPDF |
| `/scratch/work/final.py` → `gapcsv/final.csv` | the residual table, the tolerance per document, and the full-spend projection |
| `/scratch/work/p2w/out/*.docx` | the 19 shipped `.docx`, built by `ConvertOne` at `eb4512f8`; re-conversion of `eway-bill` gives a byte-identical `word/document.xml` |
| sources read | `tools/p2w-bench/FIXER-BRIEF.md` (1-200), `SETTLED.md` (last six sections, incl. `:497`), `FINDINGS/18prize-01-…-28NOV-agent.md`, `FINDINGS/18DISPLACEMENT-COUNT-0125-27NOV.md`, `FINDINGS/18dA-03-ASCENT-NOT-DISPLACEMENT-MEASURED-27NOV-relay.md`, `tools/p2w-bench/FINDINGS/18-DISPLACEMENT-SPACER-MODEL-REFUTED-DRIFT-IS-THE-LEAD-28NOV-fixer.md`, `tools/p2w-bench/FINDINGS/DOCS-ROOT-CAUSES-24NOV.md:609`, `/scratch/input/18d-WLINE-GOOGLE-MEASURED.md`, `benchmarks/gverify/*.json`, `benchmarks/DISP-TABLE.csv`, `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, `tools/p2w-bench/verify_google.py`, `tools/p2w-bench/gverify.py`, `tools/p2w-bench/classpick.py` |

**Ledger.** No engine file was edited (`git status app/` empty; `DocxWriter.java` sha256 `eac6dbed…`); nothing
was committed, pushed or deleted; nothing was written outside `/scratch/work` and `/scratch/output`.

---

## Open questions

1. **Why the census of 04:12 saw 18 and the store at HEAD sees 19.** The difference is exactly
   `341_shipping_manifest`, whose record was rewritten at 2026-11-28 00:00:25. Which snapshot the next run
   should treat as canonical is a pipeline decision, not a measurement.
2. **Are my 19 `.docx` the bytes the store scored?** **Not verifiable from this repo.** The committed
   `benchmarks/DOCX-HASHES.json` is dated 2026-11-25T03:37:02 and all 19 differ from it; and the hash cannot
   settle it anyway, because the package carries the conversion timestamp (two runs of `ConvertOne` on the same
   PDF differ at byte 11 of the zip and agree exactly in `word/document.xml`). A reproducible document hash
   would have to be taken over `word/document.xml`, not over the zip.
3. **Is the residual an engine defect at all?** `18dA-03` shows the check charges the *ascent difference
   between the built face and the source face* as displacement, and that the built face cannot be made to match
   on `31_times_body_arial_headings`. If that is also true of the 19, their medians are an instrument reading,
   and the honest count of documents a *gap* change can clean is 0 by a different route than §5.2's.
