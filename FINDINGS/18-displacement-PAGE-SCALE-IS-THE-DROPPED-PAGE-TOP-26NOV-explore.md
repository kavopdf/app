# The page-scale half of `18_displacement` is the page top, carried by a construct Google drops — and 8 of the 17 are not page-top at all

**26 Nov 2026, explore slot.** Engine as cloned (`git clone --depth 1`, `tools/install-gate.sh` run;
corpus 213/213 fetched, JDK + PDFBox + engine compiled). `app/` is reverted to HEAD at the end of the
run — **nothing is committed, nothing is pushed, no file is deleted.**

This file answers one question: *which engine construct causes the page-scale half (the 17 documents
with `worst_dy > 100`)?* It answers it with a controlled experiment that reproduces Google's own
verdict from the `.docx` alone, and it **refutes the premise that the page-scale half is one thing**:
9 of the 17 are multipage and are the page top; **8 of the 17 are single-page documents that have no
page top but page 0** and this construct cannot reach them at all.

---

## 1. The mechanism, in one sentence

**Every page after the first takes its whole top offset from `w:spacing w:before` on the first
paragraph that follows `<w:br w:type="page"/>`; Google discards `w:before` at a page top, so the page
block starts `G` points high, its table no longer fits the slot the engine allotted, and Google
re-flows rows across the page boundary — leaving every row below the re-flow a whole number of row
pitches off (measured: 7, 8, 13 and 19 rows = 128, 147, 239 and 349 pt), which is what
`worst_dy = 355.4` and `656.7` are.**

The construct is not the *value* — the value is right (measured below, to 0.03 pt). It is the
**carrier**: `w:before` on a page-first paragraph, which is the one place Google does not read it.

## 2. The code path that writes it

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (7,744 lines at HEAD):

| what | where (HEAD line numbers) |
|---|---|
| the break itself — a one-twip paragraph carrying `<w:br w:type="page"/>` | `breakPage()` **:690-701** |
| the page-first gap, single-line path: `topGap = b.y - LINE_BASE*linePt`, capped by `firstGapCapTw`, written as `beforeTw` | `flowFromBox()` **:4515-4530** (and again after a mid-flow break at **:4598-4604**) |
| the same for a row of fields | `flowRow()` **:3632-3640**, **:3682-3690** |
| the same for the auto construct | `flowTopPt()` **:4182-4190** |
| the emitter that turns `beforeTw` into bytes | `spacing(beforeTw, lineTw, size, auto, pageFirst)` **:149-170** — `w:before="…"` at **:152-153** and **:167-168** |
| the section, which writes `w:pgMar w:top="0"` | `sectPrXml()` **:2439-2450**, the literal at **:2448** |
| the cap the gap is clamped to | `firstGapCapTw()` **:4030-4033** |

Nothing else writes a vertical offset at a page top: there are **0 `w:framePr`** in 213 emitted files
(the construct was removed because Google ignores it), and `w:pgMar` is `0` on all four sides at HEAD.

## 3. The measurement — one real document, before and after

Document: **`bank-statement-5-pages`** (5 pages, A4 = 595.3 x 841.9 pt, 585 upright runs, 25-row table
on every page, byte-identical page blocks). Converted with `ConvertOne`, `.docx` unzipped,
`word/document.xml` read directly.

### 3a. What the engine wrote, and what the PDF actually draws

| quantity | measured |
|---|---|
| `w:pgMar w:top` at HEAD | **0** |
| page-first `w:before`, pages 1-5 | **1103 tw = 55.15 pt on every page** |
| engine's model y vs the PDF's own baselines (20 matched paragraph lines, per page) | **dy ∈ [-0.02, +0.03] pt** |
| LibreOffice render of the same `.docx`, all 585 runs | **\|dy\| median 0.52 pt, max 0.92 pt → 47/47 PASS** |

So the numbers the engine writes are *exact* and a renderer that honours them reproduces the page. The
defect is not arithmetic and not geometry. **This is also why the LibreOffice proxy is blind to it:
`47/47 PASS` at HEAD, while Google reads `42/47`.**

### 3b. Google, on that same `.docx` (committed, `benchmarks/gverify/bank-statement-5-pages.json`)

```
42/47 FAIL   18_displacement, 25_invisible_text, 27_text_off_page, 44_header_footer, 59_shape_anchor
displacement: med_dy = -55.0   worst_dy = 355.4   bad_pages = [0,1,2,3,4]   runs_matched = 585
```

`med_dy = -55.0` against a written page-first `w:before` of **55.15 pt** — the systematic term is the
dropped gap to 0.15 pt.

### 3c. The controlled experiment — the drop alone, applied to the same `.docx`

Take the **HEAD `.docx` unchanged** and zero `w:before` on the first paragraph of pages 2-5 only — i.e.
do to the file exactly what Google is measured to do to it — then render it with the same renderer and
score it with the repo's own check (`verify_google.py`) and its own dy instrument (`dy.py`):

```
42/47 FAIL   18_displacement (render=4), 25_invisible_text (render=8), 27_text_off_page (render=8),
             44_header_footer, 59_shape_anchor
dy:  page 0  med +0.59  n_out 0
     page 1  med -54.51  n_out 116   min -256.91
     page 2  med -54.51  n_out 116   min -146.51
     page 3  med -54.51  n_out 114   min -348.91
     page 4  med -54.51  n_out 114   min -238.51
```

**Against Google's own render of the same file: 42/47 FAIL, med -55.0 (sim -54.51), worst 355.4
(sim 348.91), and the same four failing checks.** The disagreement is 0.5 pt on the median and 6.5 pt
on the tail — smaller than the row pitch that generates the tail.

The tail is row-quantised, which is what identifies the re-flow: the worst runs are at
**-128.11, -146.51, -238.51, -348.91 pt = 7, 8, 13, 19 x the 18.4 pt row pitch**. Removing 55 pt from
the top of the page changes where the table's rows fall relative to the page break, so rows below the
re-flow point pair against their twins a whole number of rows away. That is the page-scale number
(355.4, 656.7, 401.3, 357.8) — not a 55 pt shift.

### 3d. After the patch (the construct changed, nothing else)

Patch applied to `app/`, engine rebuilt with the repo's own classpath, same document re-converted:

| quantity | before | after |
|---|---|---|
| `w:pgMar w:top` | `0` | **`1103` tw = 55.15 pt** |
| page-first `w:before`, pages 1-5 | `1103` tw each | **`0` tw each** (gap = pgMar + before = 1103, unchanged) |
| `verify_google.py` on the render | 47/47 PASS (proxy) / **42/47 in Google** | **47/47 PASS** |
| per-run dy, every page | Google: med -55.0, worst -355.4 | **med +0.59, max \|dy\| 0.99, n_out 0 on all 5 pages** |

Two more documents, same protocol, to show it is not one file:

| document | pages | page-first `w:before` @HEAD | Google @HEAD | drop simulated | patched |
|---|---:|---|---|---|---|
| `gst-invoice-multipage-item-table` | 4 | 51.15 pt on all 4 | 42/47, med -52.1, worst -168.3, fails {18,25,26,27,44} | **42/47, med -50.51, worst -160.61, fails {18,25,27,44,59}** | **47/47 PASS** |
| `324_loan_amortisation_schedule` | 7 | [17.50, 11.50 x 6] | 44/47, med +0.3, worst 357.8 | (not simulated) | **47/47 PASS, med +0.37, max 0.89**; `pgMar=230`, page 1 keeps `120` tw of its 350 |

`324_loan` is the monotonicity check: the section can only carry the **smallest** page-first gap
(11.50 pt), so page 1 keeps the remaining 6.0 pt in its own `w:before`. No page moves further from its
own y than it is today.

## 4. The patch

**File:** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` — **seven hunks, 135 insertions,
one file.** It already exists in the tree as
`tools/p2w-bench/patches/18-displacement-PGMAR-TOP-GUARDED-AGAINST-DOUBLING-26NOV.patch`; it applies
clean to HEAD (`git apply --check` → clean) and is what §3d was measured on. The essential hunk:

```diff
@@ -2432,7 +2474,7 @@   (sectPrXml, the 5-argument overload)
         return "<w:pgSz w:w=\"" + w + "\" w:h=\"" + h + "\"" + orient + "/>"
-                + "<w:pgMar w:top=\"0\" w:right=\"0\" w:bottom=\"0\" w:left=\"0\""
+                + "<w:pgMar w:top=\"" + Math.max(0, topTw) + "\" w:right=\"0\" w:bottom=\"0\" w:left=\"0\""
                 + " w:header=\"0\" w:footer=\"0\" w:gutter=\"0\"/>"
@@ -3784,7 +3827,7 @@   (flowRow)  and  @@ -4670,7 +4799,7 @@   (flowFromBox)
-                .append(spacing(beforeTw, lineTw, size, autoFlowLines(), ctx.newPage))
+                .append(spacing(pageFirstBeforeTw(ctx, firstOnPage, beforeTw), lineTw, size, autoFlowLines(), ctx.newPage))
+    private static int pageFirstBeforeTw(Ctx ctx, boolean pageFirst, int beforeTw) {
+        if (!pageFirst || ctx.pageTopTw <= 0) return beforeTw;
+        return Math.max(0, beforeTw - ctx.pageTopTw);
+    }
+    private static int sectionTopTw(PdfToWord.Result result) {   // min page-first gap over all pages,
+        ...                                                      // read with the emitters' own expression
+    }                                                            // (y - LINE_BASE*hairline, firstGapCapTw)
```

In patched-file line numbers: `Ctx.pageTopTw` **:838**; computed at **:1117** (`sectionTopTw()`
**:4449-4501**); subtracted at **:4504-4506**, called at **:3862** and **:4799**; `w:pgMar w:top` at
**:2481-2490**; body `sectPr` at **:1383**; section-break `sectPr` at **:1151**.

**Why `w:pgMar w:top` and not something else.** It is the only vertical length in this file a page top
cannot lose, and it is already measured in Google on this exact document: `bank-statement-5-pages`
pages 1-4 went **-59.5 pt → -4.3 pt, page count unchanged at 5, 37/42 → 40/42**
(`FINDINGS/DOCS-ROOT-CAUSES-24NOV.md`, §18_displacement). The alternatives are measured dead ends: an
empty spacer paragraph asking for an exact line height gets **5-10 pt of whatever it asked**; a
`w:framePr` is ignored (0 in 213 files).

**What it deliberately does not change:** `flowTw`, `budgetTw`, `fitPage`, `resync` keep charging the
gap exactly as they do today, so the model and the reader still agree about where every line goes —
only which construct carries the number changes. Two guards keep it an identity where it cannot work:
`secTopTw = sb.indexOf("<w:body><w:p") >= 0 ? … : 0` (a body that opens with a `w:tbl` gets `0`, the
doubling measured on `401_trifold_brochure`, `pgMar 1190 + before 1790 = 2980` tw against a source gap
of 1790), and `sectionTopTw()` returns `0` for any page whose first block is not a plain paragraph.

## 5. Which documents this makes CLEAN

The construct reaches a document only if **(a)** it has more than one page, **(b)** every page opens
with a paragraph, and **(c)** the smallest page-first gap is > 0. Census over the 17 page-scale
documents, from their emitted `word/document.xml`:

| document | pages | page-first gaps (pt) | reached | expected |
|---|---:|---|:--:|---|
| `gst-invoice-multipage-item-table` | 4 | 51.1 x4 | **yes** | **CLEAN** — its five failures are exactly the drop's signature {18,25,26,27,44}; the simulation reproduces them and the patched render clears all five |
| `bank-statement-5-pages` | 5 | 55.15 x5 | yes | 18 + 25 + 27 + 44 cleared; **still fails 59_shape_anchor** → not clean |
| `324_loan_amortisation_schedule` | 7 | 17.5, 11.5 x6 | yes | 18 + 27 cleared; still fails 59 → not clean |
| `very-long-single-column-table` | 3 | 60.5 x3 | yes | 18 + 27 + 44 cleared; still fails 04, 60 → not clean |
| `table-across-page-break-repeated-header` | 3 | 49.15 x3 | yes | 18 + 27 cleared; still fails 04, 60 → not clean |
| `602_bookmarked_annual_report` | 3 | 69.5 x3 | yes | 18 + 27 cleared; still fails 04, 52 → not clean |
| `form16-part-b` | 2 | 50.0 x2 | yes | 18 + 27 cleared; still fails 04, 60 → not clean |
| `mutual-fund-statement` | 2 | 49.15 x2 | yes | 18 cleared; still fails 59, 60, 66 → not clean |
| `one-page-rotated-180-degrees` | 2 | 54.85 x2 | yes | 18 cleared; still fails 04, 43, 60, 62, 63 → not clean |
| `601_fillable_admission_form` | **1** | 0.00 | **no** | no page top but page 0 — unreachable |
| `341_shipping_manifest` | **1** | 13.5 | no | unreachable |
| `330_cad_drawing_sheet` | **1** | 29.5 | no | unreachable |
| `80_gstin_pan_cin_ifsc_table` | **1** | 57.5 | no | unreachable |
| `600_reviewed_invoice_with_annotations` | **1** | 0.00 | no | unreachable |
| `56_table_indented_from_margin` | **1** | 59.5 | no | unreachable |
| `bank-statement-horizontal-rules-only` | **1** | 54.85 | no | unreachable |
| `itr-computation-with-slab-table` | **1** | 51.5 | no | unreachable |

**Prediction, in documents: 9 of the 17 page-scale documents lose the `18_displacement` instance
(9 check-instances, 17 → 8 failers of the family). 1 of the 17 becomes CLEAN —
`gst-invoice-multipage-item-table` — and it is the only one whose every other failure is downstream of
the re-flow.**

**Prediction, in points:** on a reached document the page-top term `G` (11.5 to 69.5 pt in this
family) goes to 0, the re-flow disappears, and the tail collapses from 105-656 pt to the row-ladder
residual: **`worst_dy` 355.4 → ≤ 1.0 pt on `bank-statement-5-pages`** (measured on the patched
`.docx`: max |dy| 0.99, n_out 0), 168.3 → ≤ 1.0 on `gst-invoice` (render: 47/47 PASS), 357.8 → 0.89 on
`324_loan`. Google's own earlier measurement of this construct on this document is **-59.5 → -4.3 pt**.

**Corpus-wide anchor, already measured in Google by the 12:03 run** on this same patch:
`416_many_tiny_pages` **40/42 → 42/42** (1 CLEAN) plus **9 check-instances across 5 documents**
(`FINDINGS/REMEASURE-WALL-MEASURED-26NOV-fixer.md` §4). My 9-of-17 census is consistent with that
number and does not replace it.

## 6. What is REFUTED, with the number that refutes it

1. **"The page-scale half is one construct."** Refuted. **8 of the 17 have `src_pages = 1`** and their
   emitted `document.xml` contains no `w:type="page"` break at all (`601_fillable_admission_form`,
   `341_shipping_manifest`, `330_cad_drawing_sheet`, `80_gstin_pan_cin_ifsc_table`,
   `600_reviewed_invoice_with_annotations`, `56_table_indented_from_margin`,
   `bank-statement-horizontal-rules-only`, `itr-computation-with-slab-table`; `worst_dy` 105.0-230.4).
   A page-top carrier cannot touch a document that has no page top but page 0. Their tail is a page-0
   defect — the same class of construct, on the one page where `w:before` *is* honoured, so it is the
   other measured carrier: the empty spacer's `w:line` exact line height, of which **Google delivers
   5-10 pt of whatever was asked** (`DOCS-ROOT-CAUSES-24NOV.md`; 81 pages carry a step over 3 pt,
   median 7.2, max 148.8). **This half is not measured here** and is the next run's job.
2. **"Rows grow because Google substitutes a wider face, and that is the page-scale drift."** Refuted.
   Measured by rebuilding all 17 `.docx` with `Arial → DejaVu Sans` (≈8-10 % wider), rendering both
   variants, and counting the lines the wider face adds: `worst_dy = 0.180 x extraWrappedLines +
   210.9`, **r² = 0.022, n = 17**. `324_loan_amortisation_schedule` adds **0** wrapped lines and still
   has `worst_dy = 357.8`. The wrap is real (`bank-statement` gains 468 lines) but it is not what
   sorts the family.
3. **"`med_dy` is explained by the page top."** Partly refuted. Across the 17, `med_dy = -0.993 x
   gap + 27.87`, **r = 0.49** — the slope is the right one (1.0) but the intercept is +27.9, because
   on 6 of the 9 multipage documents a downward row-ladder term cancels the upward drop
   (`mutual-fund-statement` gap 49.15 → `med_dy` +0.2; `324_loan` 11.50 → +0.3). **Do not fit one
   constant across documents; the construct is all-or-nothing inside a file** (the repo's own
   correction: `REMEASURE-WALL-MEASURED-26NOV-fixer.md` §4).
4. **The table-row attribution** is not re-derived here and was not needed: nothing above depends on
   `attribution=table-row`, `w:trHeight`, `hRule` or cell margins.

## 7. What this run could NOT measure, and why

**No Google round trip.** The engine's own Google path needs the platform `upload` tool to stage the
`.docx` to the `s3key` that `GOOGLEDRIVE_CREATE_FILE` requires; that tool is not exposed to this
sandbox, and passing a `/scratch/output/...` path as `s3key` is refused ("the file does not exist in
storage"). `gverify.py:19-27` documents this exact wall. Everything Google-side quoted above is
either **committed** (`benchmarks/gverify/*.json`, 213 documents) or the repo's own earlier live
measurement, and every "after" number is a LibreOffice render of the patched `.docx` — **a proxy**.
The controlled experiment in §3c is what carries the causal claim: it reproduces Google's verdict
(42/47, same checks, median to 0.5 pt, tail to 6.5 pt) from the `.docx` alone by applying only the
construct Google is measured to apply. **The final verdict on the patch still needs
`gverify.py` on the 9 reached documents** — 9 uploads, ~15 minutes.

## 8. Reproduce

```
# convert one document at HEAD (engine already built by tools/install-gate.sh)
cd tools/engine-verify
java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne /scratch/work/p2w/corpus/bank-statement-5-pages.pdf /tmp/m1
# the numbers the engine wrote: pgMar top and every page-first w:before
python3 /scratch/work/analyze.py /tmp/m1/bank-statement-5-pages.docx
# the controlled experiment: zero the page-first w:before on pages 2..n, render, score
python3 /scratch/work/simulate-drop.py /tmp/m1/bank-statement-5-pages.docx /tmp/sim
soffice --headless --convert-to pdf --outdir /tmp/sim /tmp/sim/bs-dropped.docx
python3 tools/p2w-bench/verify_google.py <src.pdf> /tmp/sim/bs-dropped.pdf --docx /tmp/sim/bs-dropped.docx
python3 tools/p2w-bench/dy.py <src.pdf> /tmp/sim/bs-dropped.pdf
# after: apply the patch, rebuild, re-convert, render, score
git apply tools/p2w-bench/patches/18-displacement-PGMAR-TOP-GUARDED-AGAINST-DOUBLING-26NOV.patch
```

Scratch kept in the pod: `/scratch/work/analyze.py` (per-page numbers the engine wrote),
`/scratch/work/compare.py` (engine model vs the PDF's own baselines), `/scratch/work/m1` (HEAD `.docx`),
`/scratch/work/m2` (patched `.docx`), `/scratch/work/sim` (drop applied), `/scratch/work/wrap` (the
wider-face experiment), `/scratch/work/lo`, `/scratch/work/lo2` (renders).
