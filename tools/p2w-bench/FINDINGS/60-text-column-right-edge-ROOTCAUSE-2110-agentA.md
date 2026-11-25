# `60_text_column_right_edge` — root cause and engine patch spec

**26 Nov 2026 · agent A, read-only · store engine `981ff1fa35e2cf67` · repo HEAD from `repo-src.tar.gz`, 195 emitted `.docx` from `emitted-docx.tar.gz`**

Every claim is tagged **MEASURED** (read out of the verdict store, the emitted
`word/document.xml`, or arithmetic on the two) or **INFERRED** (a hypothesis about Google Docs,
which this sandbox cannot render). There is no Google Docs access, no JDK and no source PDFs
here, so **no Google-side claim in this file is a measurement.** The `.docx` files match the
store's rows; the store's per-page verdict plus the engine's recorded x/width in the `.docx` are
the source-side evidence.

## 1. The check — exact predicate, tolerance, fields read

`tools/p2w-bench/verify_google.py:2626-2786`, one block. It compares the **source PDF** against
**Google Docs' own PDF export** of the engine's `.docx`. It never reads the `.docx` and never
reads the engine's model.

Constants, `verify_google.py:2653-2658`, quoted:

```python
BAND = 0.06             # header / footer band, as a fraction of page height
RIGHT_OVERRUN = 6.0
RIGHT_UNDERRUN = 8.0
COL_MIN_LINES = 3       # a left-edge cluster is a column if it holds this many lines
COL_MIN_SHARE = 0.05    # ... or this share of the page's body lines, if larger
SLACK_CAP = 40.0        # one word wider than this is a token, not a word - see edge()
```

Fields read (`:2660-2669` `page_lines`, `:2671-2702` `columns`, `:2704-2740` `edge`): line bbox
`(x0,y0,x1,y1)` from `page.get_text("dict")["blocks"][*]["lines"][*]["bbox"]` on both pages; word
bboxes from `page.get_text("words")` on both pages; `page.rect.height` and `page.page_count`.
Units are PDF points (1/72 in) throughout — this is not a pixel check.

The predicate, verbatim (`:2770-2774`):

```python
            if rg > rs + RIGHT_OVERRUN + slack:
                over += 1
                break
            if rg < rs - RIGHT_UNDERRUN - slack:
                under += 1
                break
```

and the verdict (`:2786`):

```python
    c["60_text_column_right_edge"] = (over, under, over == 0 and under == 0)
```

with, from `edge()` (`:2727-2740`):

```python
        v = sorted(b[2] for b in col)
        w = sorted(b[2] - b[0] for b in words if abs(b[0] - left) <= 10)
        one_word = w[len(w) // 2] if w else 0.0
        return v[-1], min(SLACK_CAP, one_word)
```

So `rs` = the column's widest source line, `rg` = the same in the render, `slack` = the median
word width of that column's own text capped at 40 pt (word p50 over the corpus = 24.0 pt, per
the docstring at `:2722`). A page fails `over` if `rg > rs + 6 + slack`, `under` if
`rg < rs − 8 − slack`. **`source` in the stored tuple is the count of pages that OVERRUN and
`render` is the count that UNDER-RUN** (`:2784-2785`) — the two names are the two sides of the
comparison, not the two renderers. A safety net at `:2776-2782` adds one `over` when two or more
render lines end past `s_max + 18 pt`.

## 2. Which documents fail it

Store: `benchmarks/gverify/*.json` (213 documents) and `benchmarks/gverify-lo/*.json` (the LO
render of the same 213); there is no `tools/p2w-bench/benchmarks/` at HEAD — the stores are at
the repo root. `benchmarks/RANKING.csv` carries no per-check column. **MEASURED: 64 fail in the Google store, 20 in the LibreOffice store, 17 in both, 47
Google-only, 3 LO-only** (`03_stamp_vertical_90deg`, `50_invoice_coloured_total_row`,
`69_two_col_legal_numbered_clauses`). Shapes: **14 `60` alone, 31 `18`+`60`, 6 `60`+`59`, 13
`18`+`59`+`60`.** The 24 Nov context quote (12 / 6 / 4) is one engine behind the store.

Format: `name | dir | src | ren | LO60 | 18 | 59 | .docx | ΔR`, two rows per line. `dir` = which
term fired (`over` = `source>0`, `under` = `render>0`); `LO60` = same check in `gverify-lo`;
`18`/`59` = `F`ail or `.`; `.docx` = present in the tarball; `ΔR` = §4's widest-line advance
delta in pt, `n/s` = not computable (the document carries `w:txbxContent`, which breaks a flat
paragraph scan — 18 of 195). `src`/`ren` are the check's own reported counts; it reports counts,
not points, so `ΔR` is mine (§4 says how).

```
041122-Account_Opening_Form            |both |1|7|FAIL|F|F|yes|  n/s          balance-sheet-and-profit-loss          |under|0|1|FAIL|F|.|yes|+16.9
Account_Opening_Form_Fillable_filled   |both |1|8|FAIL|F|F|yes|  n/s          boq-tender-bill-of-quantities          |under|0|1|FAIL|F|.|yes|  0.0
14_stamp_chars_positioned_td           |under|0|1|pass|.|.|yes|  n/s          gst-invoice-horizontal-rules-only      |under|0|1|FAIL|F|.|yes|  n/s
25_signature_block_underscores_txtpos  |under|0|1|pass|F|.|yes|  0.0          magazine-2col-pullquote-spanning       |under|0|1|pass|.|.|yes|  n/s
301_lab_report_panel                   |under|0|1|pass|F|.|yes|-92.4          one-page-rotated-180-degrees           |under|0|1|FAIL|F|.| NO|  n/s
302_radiology_report                   |under|0|1|pass|.|.|yes|-15.3          policy-2col-spanning-section-heading   |under|0|1|pass|.|F|yes|  n/s
310_court_judgment                     |under|0|1|pass|.|.|yes|-107.8         28_value_overflows_cell_txtpos         |over |1|0|FAIL|.|F|yes|  0.0
311_fir_police_form                    |under|0|1|pass|F|.|yes|  n/s          305_vaccination_certificate            |over |1|0|pass|F|.|yes|  n/s
312_affidavit_stamp_paper              |under|0|1|pass|.|.|yes|  n/s          332_bom_on_drawing                     |over |1|0|pass|F|.|yes|-31.3
313_power_of_attorney                  |under|0|1|pass|.|.|yes|-94.2          341_shipping_manifest                  |over |1|0|pass|F|.|yes|-43.3
314_tender_rfp_boq                     |under|0|1|pass|F|F|yes|-115.5         342_packing_list                       |over |1|0|pass|F|.|yes|-62.5
316_contract_with_schedules            |under|0|1|pass|.|.|yes|-104.1         360_restaurant_menu                   |over |1|0|FAIL|F|.|yes|-34.6
317_rti_response                       |under|0|1|pass|.|.|yes|-100.2         38_faux_bold_italic_synthesised        |over |1|0|FAIL|.|.|yes|  0.0
318_court_summons_form                 |under|0|1|FAIL|.|F|yes|  n/s          393_spectrum_peak_table                |over |1|0|pass|.|F|yes|-33.8
321_auditors_report                    |under|0|1|pass|.|.|yes|-103.6         406_passport_mrz_page                  |over |1|0|pass|F|.|yes| -2.3
322_mutual_fund_factsheet              |under|0|1|pass|F|F|yes|  n/s          56_table_indented_from_margin          |over |1|0|pass|F|F|yes|  0.0
323_credit_card_statement              |under|0|1|FAIL|F|.|yes|  n/s          77_arabic_rtl_document                 |over |1|0|FAIL|F|F|yes|  n/s
326_itr_computation                    |under|0|1|pass|F|.|yes|-108.5         79_inr_indian_digit_grouping_table     |over |1|0|FAIL|.|.|yes|  0.0
335_msds_safety_data_sheet             |under|0|1|pass|.|.|yes|-117.1         academic-paper-ieee-2col-abstract      |over |1|0|pass|F|.|yes|  n/s
340_bill_of_lading                     |under|0|1|pass|F|F|yes|-114.8         delivery-challan                       |over |1|0|FAIL|F|.|yes|  n/s
343_air_waybill                        |under|0|1|pass|F|F|yes|-10.9          form16-part-b                          |over |1|0|pass|F|.|yes|  0.0
344_customs_declaration                |under|0|1|pass|F|F|yes|  n/s          gst-invoice-3line-items                |over |1|0|pass|F|.|yes|  0.0
350_question_paper                     |under|0|1|pass|F|.|yes|-91.1          landscape-page-inside-portrait-document|over |1|0|pass|F|.|yes|  0.0
352_certificate_ornate_border          |under|0|1|pass|.|.|yes|  n/s          marksheet-university-consolidated      |over |1|0|pass|F|.|yes|  0.0
363_warranty_card                      |under|0|1|pass|F|.|yes|-95.4          purchase-order                         |over |1|0|FAIL|F|.|yes|  0.0
365_recipe_card                        |under|0|1|pass|.|.|yes|-64.2          question-paper-marks-right-margin      |over |1|0|FAIL|F|.|yes|  0.0
370_offer_letter                       |under|0|1|pass|F|.|yes|-94.4          mutual-fund-statement                  |over |1|0|pass|F|F| NO|  n/s
371_experience_certificate             |under|0|1|pass|.|F|yes|  n/s          salary-slip-factory-wages              |over |1|0|pass|F|F| NO|  n/s
373_leave_application_form             |under|0|1|pass|F|F|yes|-105.7         table-across-page-break-repeated-header|over |1|0|pass|F|.| NO|  n/s
381_incident_report_timeline           |under|0|1|pass|F|.|yes|-116.7         table-with-merged-cells                |over |1|0|pass|F|.| NO|  n/s
383_api_docs_page                      |under|0|1|pass|F|F|yes|  0.0          text-held-twice-shadow-text            |over |1|0|FAIL|F|.| NO|  n/s
65_two_col_full_width_figure_caption   |under|0|1|pass|.|F|yes|  n/s          very-long-single-column-table          |over |3|0|pass|F|.| NO|  n/s
```

**Totals: 26 over / 36 under / 2 both in the store; of the 57 with a `.docx` here, 20 over / 35
under / 2 both.** Seven failing documents have no `.docx` in the tarball
(`one-page-rotated-180-degrees`, `mutual-fund-statement`, `salary-slip-factory-wages`,
`table-across-page-break-repeated-header`, `table-with-merged-cells`,
`text-held-twice-shadow-text`, `very-long-single-column-table`); 18 store documents have none.

## 3. The XML census — what the engine emits, and what it does not

195 `word/document.xml` parsed. `F` = the 57 failing documents with a `.docx`; `P` = the 138
passing ones. **All MEASURED.**

| construct | emitted at | F | P |
|---|---|---|---|
| `w:pgSz` | `:2433` | A4 11906 twips in 173 docs, landscape 16838 in 13, 11900 in 9 | — |
| `w:pgMar` all four `0` | `:2435` | **195/195 documents, every section, every margin 0** | 195/195 |
| `w:docGrid w:linePitch="360"` | `:2439` | 195/195 | 195/195 |
| `w:tblCellSpacing` | never written | **0** | **0** |
| `w:tblLayout w:type="fixed"` | `:6223`, `:2198` | 44/44 table docs | 81/81 table docs |
| `w:tblCellMar` all four 0 | `:6227-6230` | 44/44 | 81/81 |
| `w:tblW` == Σ`w:gridCol` | `:6201`, `:6233` | every table | every table |
| `w:ind w:right` ≠ 0 anywhere | `:4412-4441` | **1** doc | **2** docs |
| `w:jc` any | `:4641-4642`, `:4661-4662` | 11 (`center` 10, +`right` 1) | 20 (`center` 16, `right` 3, both 1) |
| `w:jc="both"` / `"distribute"` | never written | **0** | **0** |
| `w:rPr/w:spacing` | `:4753-4754` via `stretchTw:4685` | 18 docs / 196 runs, **1-10 twips** | 18 docs total |

Three of those answer "which construct does Google honour differently": **(1)** `w:pgMar` right
= 0 in every document (`:2435`), so the text area is the whole sheet and **every paragraph's
right boundary is the paper edge (595.3 pt), never the source column's edge**; **(2)**
`w:ind w:right` is a literal `0` on every left-aligned line — `flowFromBox:4412` sets
`int rightTw = 0;`, only the centred-off-centre branch (`:4431-4437`) and the right-aligned
branch (`:4438-4441`) raise it, and `p.align == 0` falls through with 0 emitted at `:4638-4640`,
so every `w:pPr` in all 195 documents carries `w:right="0"`; **(3)** the one construct that can
carry the edge, `w:rPr/w:spacing`, is on 18 of 195 documents at 1-10 twips per character
(0.05-0.5 pt), because `stretchTw:4685-4697` is gated on `b.stretchPt >= 3f` and `stretchPt` is
`PdfToWord.stretchOf()`'s measure of the *page's own* justification extra, not of any face
difference. The engine writes the right construct and it carries almost nothing.

`w:tblCellSpacing` is never emitted and cannot be the mechanism. `tblLayout`/`tblCellMar`/`tblW`
vs `gridCol` are consistent on every table and do not separate F from P (77 % of F carry a
table, 59 % of P do). **No single emitted construct separates failing from passing** — which is
why the answer is a quantity, not a tag.

## 4. The population splits in two, and only one half is the face

`ΔR` (§2): for every paragraph in `word/document.xml` take `x = w:ind w:left / 20`, the runs'
text, `w:sz`/2 and `w:ascii`; measure the advance in the declared face (DejaVu\* from
`/usr/share/fonts/truetype/dejavu/`; Arial / Times New Roman / Courier New from the
metric-compatible Liberation set), then re-measure the same text in the face a renderer without
DejaVu resolves (Liberation Sans / Serif / Mono). `ΔR` = widest-line right edge under the
substitute − under the declared face. **MEASURED** (arithmetic on the emitted XML plus installed
font metrics, PIL 13.0.0). `w:txbxContent` documents excluded (18 of 195).

Advance ratio over every line ≥ 60 pt wide, whole corpus (**MEASURED**):

| declared face | n lines | median advance ratio (substitute ÷ declared) |
|---|---|---|
| `Arial` | 1355 | **1.0000** |
| `Times New Roman` | 278 | **1.0000** |
| `DejaVuSans` | 191 | **0.8867** |
| `DejaVuSerif` | 102 | **0.8190** |

The substitute is **11.3 % narrower** than DejaVu Sans and **18.1 % narrower** than DejaVu Serif,
and exactly as wide as Arial and Times. That is the mechanism in one table. Cross-tabulated
(**MEASURED**):

| direction | n (.docx) | DejaVu declared | table doc | widest-line ΔR median | ΔR < −8 pt |
|---|---|---|---|---|---|
| `under` | 35 | **27** | 23 | −100.3 | 18 of 22 computable |
| `over` | 20 | 7 | **19** | 0.00 | 5 of 16 computable |
| `pass` | 138 | 37 | 81 | 0.00 | 24 of 108 computable |

Document level, all 195 (**MEASURED**): of 71 documents declaring a DejaVu face, **34 fail
(48 %)**; of 124 that do not, **23 fail (19 %)**.

## 5. The mechanism

### M1 — `under` (35 docs, 27 DejaVu): the right edge is the resolved face's advance

**MEASURED:** `w:pgMar` right is 0 and `w:ind w:right` is 0 on every left-aligned line, so the
only right-hand constraint on a body paragraph is the paper edge, and the line's right edge is
whatever advance the resolved face produces. On 18 of the 22 computable `under` documents the
resolved face is **narrower than the declared one by 10.9 to 117.1 pt on the column's widest
line** (median −94.9 pt) — 1.4× to 3.7× the whole `8 + min(40, one word)` tolerance, which is
32 pt at the corpus median word. The store's `render=1` on those 18 is what that arithmetic
predicts. **INFERRED:** Google has no DejaVu face and substitutes one; LibreOffice has DejaVu and
resolves the declared face — why 42 of the 64 pass in `gverify-lo`. The magnitude holds for any
substitute ≥ 3 % off; the identity of the substitute is the hypothesis.

The 4 computable `under` documents with `ΔR = 0` (`25_signature_block_underscores_txtpos`,
`383_api_docs_page`, `boq-tender-bill-of-quantities`, `balance-sheet-and-profit-loss`) are **not**
this mechanism; `balance-sheet` is **+16.9**, which no narrower face can produce.

### M2 — `over` (20 docs, 19 table docs): NOT root-caused here

**MEASURED:** `ΔR = 0.00` exactly on 10 of the 16 computable `over` documents, median 0.00 — the
face explains **none** of this population. 19 of 20 are table documents. Where the emitted grid
and the widest emitted line can be compared, the widest line lands on the table's right edge to
within 0.4 pt (`purchase-order` 552.7 vs 553.0; `form16-part-b` 552.7 / 553.0;
`marksheet-university-consolidated` 555.6 / 556.0; `gst-invoice-3line-items` 555.5 / 556.0;
`boq-tender-bill-of-quantities` 555.4 / 556.0) — a cell line drawn to the last grid column's
right edge, while the source drew its own last column to the left of it:
`DOCS-ROOT-CAUSES-24NOV.md:287` records `purchase-order` at 553.0 against a source column ending
at 449.7, a 103 pt discrepancy.

**INFERRED:** the grid is wider than the source's table, so a cell's line breaks later. **I could
not confirm the origin of the extra width.** The candidates in `table()` are `colTw` from
`t.colX` (`:5981-5993`) and the last-column widening loop (`:6001-6012`,
`colTw[cols-1] = max(colTw[cols-1], inset + textR + 20)`). The only XML signature available — a
last `gridCol` off the 5-twip grid — fires on 20 % of `over` tables against 36 % of `pass`, i.e.
**it does not discriminate and is not the mechanism**; and `colX` is present for essentially
every table (the equal-width fallback at `:5992-5994` fires on 2 of 160), so it is not that
either. M2 needs the source PDFs.

**Consequence: the leverage table's 22.9 clean documents are not one class.** 20 of the 64 are
M2 and must not be patched on this evidence.

## 6. Already refuted — do not rebuild

| construct | verdict | source |
|---|---|---|
| `w:jc="distribute"` + per-line `w:ind w:right` at the line's ink edge (the "right pin") | **REFUTED in Google**: 21 paragraphs written, `60` unchanged `(0,1,False)`, `17_matched_runs` 33→21, 28 lines wrapped | `FINDINGS/RIGHT-PIN-WRAPS-IN-GOOGLE-INERT-IN-LO-0126-relay.md` |
| right indent from the source margin, no alignment change | **REFUTED**: total passes fall 11, 7 worse / 1 better, `60` 43→45 | `REMAINING-DEFECTS.md:197` |
| size emulation (+5.8 % `w:sz`) | moves the edge (+29.43 → +0.26 pt) but changes the type size | `DOCS-ROOT-CAUSES-24NOV.md` §60 |
| naming a Google face instead of DejaVu | inert in Google (it already substitutes to it), makes LibreOffice wrong | `DOCS-ROOT-CAUSES-24NOV.md` §60 |

The pin failed for a reason worth keeping: it pinned to **each line's own ink edge**, a
*compression* wherever the render's natural width exceeds it, and `distribute` cannot compress —
it re-breaks. The patch below never compresses.

## 7. Patch spec

**File:** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`
**Function:** `stretchTw(PdfToWord.Box b)` at `:4685-4697`, plus one new helper.
**Call sites unchanged:** `:3828` and `:4644`, both already `p.align == 0 ? stretchTw(b) : 0`,
feeding `runXml(..., spacingTw)` → `:4753-4754`.

**In words.** `stretchTw` today returns the spacing that restores the *page's own* justification
extra (`b.stretchPt`), and nothing under 3 pt. Add the **face-substitution shortfall**: the
line's advance `b.right − b.x` is at the declared face's metrics because the PDF drew it there,
and a renderer without that face draws it at `ratio ×` that; the shortfall
`(1 − ratio) × (b.right − b.x)` points is spread over the line's characters exactly as
`stretchPt` already is. The ratio is §4's calibration — one constant per declared family, 1.0
for every face the renderer shares, which is every non-DejaVu face here.

```diff
@@ -4682,12 +4682,32 @@
-    private static int stretchTw(PdfToWord.Box b) {
-        if (b == null || b.rotated || !(b.stretchPt >= 3f)) return 0;
-        String t = b.text();
-        if (t.length() < 2) return 0;
-        long tw = Math.round(b.stretchPt * TWIPS_PER_PT / t.length());
+    /**
+     * How much wider the PDF's own face is than the face the RENDERER will resolve.
+     *
+     * <p>1.0 means the renderer has the face and its advance is the PDF's. Below 1.0 the
+     * renderer substitutes a narrower face and every line it draws ends short of the edge
+     * the PDF drew it to. Measured over every line 60 pt wide or more in the 195-document
+     * emitted corpus: Liberation Serif is 0.819 of DejaVu Serif's advance (n = 102),
+     * Liberation Sans 0.887 of DejaVu Sans's (n = 191), and Liberation is exactly 1.000 of
+     * Arial's (n = 1355) and of Times New Roman's (n = 278). A face this table does not
+     * know stays at 1.0: it must not move a document.
+     */
+    private static float faceRatio(PdfToWord.Box b) {
+        if (b == null || b.runs == null) return 1f;
+        for (PdfToWord.Run r : b.runs) {
+            if (r == null || r.text == null || r.text.trim().isEmpty()) continue;
+            String f = faceName(r.font == null ? "" : r.font);
+            if (f.startsWith("DejaVuSerif")) return 0.819f;
+            if (f.startsWith("DejaVuSansMono")) return 1f;
+            if (f.startsWith("DejaVuSans")) return 0.887f;
+            return 1f;
+        }
+        return 1f;
+    }
+
+    private static int stretchTw(PdfToWord.Box b) {
+        if (b == null || b.rotated) return 0;
+        String t = b.text();
+        if (t.length() < 2) return 0;
+        // The page's own justification extra, then the width the substitute face loses. The
+        // second term is zero for every face the renderer shares with the PDF, so a document
+        // in Arial, Times or Courier is byte-identical to today's.
+        float ratio = faceRatio(b);
+        float facePt = ratio < 1f ? (1f - ratio) * (b.right - b.x) : 0f;
+        float totalPt = Math.max(0f, b.stretchPt) + facePt;
+        if (totalPt < 3f) return 0;
+        long tw = Math.round(totalPt * TWIPS_PER_PT / t.length());
         long cap = Math.max(1L, Math.round(b.size * 0.30f * TWIPS_PER_PT));
         return (int) Math.max(0L, Math.min(tw, cap));
     }
```

Three properties this shape has on purpose:

- **It cannot compress and cannot wrap.** `w:spacing` only *adds* advance, and the amount added
  is exactly the width missing against the edge the PDF itself drew the line to. The line ends
  where the source's ink ended and never past it — the difference between this and the refuted
  pin.
- **It is inert on every document that does not declare a DejaVu face.** `faceRatio` returns
  1.0, `facePt` is 0, `totalPt == b.stretchPt`: the emitted bytes are unchanged. 124 of 195
  documents are in that set.
- **The cap does not bind.** The existing cap is `0.30 em` per character (54 twips at 9 pt); the
  largest term added here is `0.181 × 484 / 95 ≈ 0.92 pt ≈ 18 twips` per character on
  `310_court_judgment`. Do not raise the cap.

**A second consequence is unavoidable and must be declared before landing.** LibreOffice honours
`w:rPr/w:spacing` and LO *has* DejaVu, so on a DejaVu-declaring document LO will now draw every
line 11-18 % too wide and `60` will fail in the LO store where it passes today. **The patch is
correct for Google and wrong for the LO proxy by construction**, because the two disagree about
the face and that disagreement is the defect. Land it with `regress.py` / the LO corpus pass told
to expect `60` to move on the DejaVu set, or it will be refused as a proxy regression. No
construct can be right in both renderers when they resolve different faces.

## 8. Predicted effect, in check-instances

Predicted from §4/§5 arithmetic, not measured:

| population | n | predicted |
|---|---|---|
| `under`, DejaVu declared, computable | 18 | `60` `(0,1,False)` → `(0,0,True)`: **+18 documents clean of 60** |
| `under`, DejaVu declared, text-box docs (not computable) | 9 | same construct applies; no prediction offered |
| `under`, no DejaVu declared (M2) | 8 | **0 moved** |
| `over` (M2) | 20 | **0 moved** |
| any document not declaring DejaVu | 124 | **byte-identical**, 0 moved by construction |

Residual after the per-family constant (**MEASURED**, the ratio's own spread): serif lines land
within median 6.2 pt / p90 11.7 pt of the true edge, sans within 3.9 pt / p90 35.5 pt. Against
32 pt serif is inside at p90 and sans is borderline — **expect a handful of sans documents to
stay failing**, `302_radiology_report` (−15.3) and `343_air_waybill` (−10.9) to go clean first
and the long-line sans documents last. The honest ceiling: this reaches the ~27 DejaVu `under`
documents, **not** the 22.9 the leverage table prices, because 20 of the 64 are `over`/M2 and 8
are `under` on a non-DejaVu face.

## 9. The measurement that proves it, and the one that refutes it

**Proves it — one Google round trip, one document, one variable.** `302_radiology_report` (fails
`60` alone, `.txt` clean, `ΔR = −15.3`, store `(0,1,False)`, 41/42): build with the patch and
without, same engine otherwise, convert, upload, export, run `verify_google.py` on the pair.

- **the claim:** `60` goes `(0,1,False)` → `(0,0,True)` and the widest line's right edge moves
  from ≈ 551.6 pt to ≈ 566.9 pt (§4's arithmetic on that document).
- **the construct must be in the file:** count `w:rPr/w:spacing` in `word/document.xml` — **0
  today on `302`** (it is not among the 18), one per non-empty line after.
- **nothing else may move:** `17_matched_runs` (33/33 today), `26_text_overlap` (2 today),
  `23_line_pitch`, `18` `med_dy`, `00_page_count`, `04`/`05`.
- **`43_within_10pt_x` should IMPROVE** — a second, independent prediction of the same
  mechanism: today every word after the first sits at `0.887 ×` its source offset and the added
  spacing moves it back onto it. If `43` worsens, the mechanism is wrong even if `60` passes.

**Refutes it — any one of these, same pair:**

1. `w:rPr/w:spacing` is written and the column edge does not move by ≥ 10 pt. Then Google
   normalises or drops character spacing on import, `DOCS-ROOT-CAUSES-24NOV.md`'s parenthetical
   ("what Google does to the stretch") is right, and **the whole `under` population is
   unreachable from the `.docx`** — stop proposing engine patches for it and move to the
   check-side attribution rule that file already drafts (render face ≠ declared `w:rFonts` ⇒ the
   edge is not comparable, `53_embedded_faces`' residual, ~25 documents).
2. `60` passes but `17`, `26` or `43` gets worse: the line is now over-wide, i.e. the ratio is too
   large for that face and the constant is wrong in the unsafe direction. Halve it and
   re-measure; do not widen.
3. `00_page_count` rises: a stretched line crossed the paper edge. Gate the term on
   `b.right <= ctx.pageWidthPt` (true for every line the PDF drew inside its page) and re-run.

**Cheapest falsification first:** whether the construct exists in Google is one boolean and costs
one round trip on `302`. Everything else in this file is downstream of it.

## 10. MEASURED / INFERRED index

**MEASURED** — the predicate, constants and fields (§1); the 64/20/17/47/3 store counts and the 14/31/6/13 shape counts (§2); every §2 row except the `n/s` cells; the whole XML census in §3 (195 documents); the advance ratios and direction cross-tab in §4; the `ΔR` values and widest-line-vs-grid-edge equalities in §5; the refutations in §6 as recorded by the files cited; the ratio-residual figures in §8.

**INFERRED** — that Google substitutes a face for DejaVu (the magnitude holds for any substitute ≥ 3 % off; the identity of the substitute does not); that Google honours `w:rPr/w:spacing` on import; that `w:spacing` moves the exported PDF's line bbox and not just the glyphs; M2's origin entirely.

**NOT VERIFIED AT ALL** — no Google Docs render, no JDK, no Gradle, no source PDFs. No Google-side verdict here was produced by me; **the patch does not compile here** (written against the source text read at the cited lines); `RANKING.csv` was not used for per-check data because it carries none; no `p2w.py` / `gate.py` run was possible (both need corpus and JDK).

## Open questions

1. **Which face does Google Docs resolve for `DejaVuSerif` / `DejaVuSans`?** Constants 0.819 and 0.887 assume Liberation/Arial metrics; one round trip reading the exported PDF's embedded faces (`53_embedded_faces` already does this) replaces both with a measurement.
2. **Does Google honour `w:rPr/w:spacing`?** One boolean, one round trip on `302`; every predicted effect in §8 depends on it.
3. **What sets the table grid's right edge on the `over` documents?** Needs the source PDFs for `purchase-order`, `delivery-challan`, `form16-part-b`, `gst-invoice-3line-items` — the engine writes 553.0/556.0 where `DOCS-ROOT-CAUSES-24NOV.md:287` records the source's column at 449.7.
4. **Is the LO-store movement acceptable?** §7's consequence makes `60` fail in LO on the DejaVu set by construction; whether that is a permitted proxy movement or a charter violation ("no document may get worse") is a project decision, not mine.
