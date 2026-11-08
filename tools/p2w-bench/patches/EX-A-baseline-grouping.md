# EX-A — one baseline, one paragraph (D-21)

**Result: patch ready, 208-document gate clean ("no document got worse"), 87 paragraphs of text removed from the corpus, and 61 pages that stacked a baseline vertically became 52. The five stamp documents and `23_timetable` / `62_two_col` do not move — §4.2 explains why, and the numbers there are the interesting part.**

Patch: `app/src/main/java/com/kavopdf/app/engine/PdfToWord.java`, +68 / −3, in §5 below.
Build tested: `PdfToWord.java` @ `9f3d54d` + this patch, PDFBox-Android 2.0.27.0 on Temurin 17.

---

## 1. How the measurement was taken

Everything here is measured, not estimated. Three independent instruments:

| instrument | what it does |
|---|---|
| `measure.py` (mine, in the sandbox) | per document: PDF side = distinct baselines per page (line boxes clustered within 3 pt) and page size from `w:pgSz`; DOCX side = paragraphs that carry text (leaves of the paragraph tree, table cells included, because that is what a word processor lays out), how many of them carry `w:tabs`, and the flow height = Σ(`w:before` + `w:line`) in points, split into *all paragraphs* and *body paragraphs only* (table cells excluded — a table row is laid out by the table, so summing its cells' `w:line` overstates the flow). |
| instrumented engine | `sameRow` refactored into `sameRowWhy(...)` returning the **name of the clause that rejected the pair** (or `null` for accept). `toParagraphs` then dumps every pair of lines that share a baseline (within 3 pt, left line first, the order `sameRow` is called in) and, per page, lines / distinct baselines / paragraphs / paragraphs that merged more than one field. Built from the unmodified source and from the patched source, run over all 208 documents. 540 pages, 3 247 pairs compared. |
| `tools/p2w-bench/gate.py --check` | the 208-document regression gate against `base208.json`. |

Corpus: the three release assets (`pdf-to-word-test-corpus-v3.zip`, `p2w-batch-1.zip`, `p2w-all-groups.zip`) unzipped into one flat folder — 208 PDFs, keys identical to `base208.json` (0 missing, 0 extra).

---

## 2. Which `sameRow` clause rejects the pairs

`sameRow(prev, next, pageWidth, sofar)` is eleven clauses in a row; the first one that fires rejects the pair. Corpus-wide, over the 3 247 same-baseline pairs the page builders actually offer it:

| clause that fired | pairs before | pairs after |
|---|---:|---:|
| *(accepted)* | 2 629 | 2 730 |
| `across-column-gap` — `next.x − prev.right < max(40, size*3)` across a column boundary | 246 | 257 |
| `rotated` — either line is not on a horizontal baseline | 188 | **76** |
| `past-paper` — `next.right > pageWidth + 1` | 66 | 66 |
| `ACCEPT-inside` — fragment painted over the field before it | 44 | 44 |
| `baseline-dy` — |Δy| > max(1.2, size*0.25) | 43 | 43 |
| `gap-too-small` — `next.x − prev.right < max(1.5, size*0.15)` | 12 | 12 |
| `different-size-needs-12pt-gap` — sizes differ >1.3× and gap < 12 pt | 11 | 11 |
| `size-ratio-2.5` — one field 2.5× the other | 8 | 8 |
| **accept rate** | **81.0 %** | **84.1 %** |

So on this build the predicate is **not** the "fires for 10 of 78 paragraphs" story any more; it accepts four pairs in five. The two clauses that cost paragraphs are `across-column-gap` (which is usually *right* — it is what keeps a newspaper's two columns apart) and `rotated` (which was wrong on one whole class of page).

### 2.1 01_stamp page 1, pair by pair

29 pairs of lines share a baseline within 3 pt on that page:

* **28 accepted** — `sameRow` fires, the fields become one paragraph with a tab stop at each measured x. That is why the document carries 10 tab-stop paragraphs.
* **1 rejected** — clause `rotated`:
  `a = "AUTHORISED SIGNATORY"  x 176.8..357.2` vs `b = "For SUNRISE FASTENERS PVT LTD" x 356.0..491.0` at y = 503.49 — the 15° stamp's line against the signature line it is painted across. Correctly rejected: a stamp is an overlay, not a row.

### 2.2 The documents where the clause table bites

| document | pairs offered | rejected, by clause | paragraphs / baselines |
|---|---|---|---|
| `one-page-rotated-180-degrees` | 114 | **`rotated` 112** | 61 / 15 on page 2 |
| `newspaper-2col-fullwidth-headline` | 21 | `across-column-gap` 19 | 55 / 41 |
| `table-of-contents-dot-leaders` | 43 | `across-column-gap` 20, `different-size-needs-12pt-gap` 11 | 55 / 24 |
| `marksheet-subject-left-marks-right` | 175 | `past-paper` 66 (a grade column drawn at x 587–597 on a 595.3 pt page, 2 pt off the paper) | 13 / 8 |
| `21_form_labels_x60_values_x300_txtpos` | 55 | **none — all accepted** | 47 / 29 |
| `62_two_col_newsletter_pull_quote` | 9 | `across-column-gap` 5 | 29 / 27 |
| `23_timetable_grid_txtpos` | 2 | none | 8 / 8 |
| `01_stamp_rotated_15deg_upright` | 29 | `rotated` 1 | 25 / 25 |

Two of those rows are findings in their own right:

* **`one-page-rotated-180-degrees`** — a page whose text is drawn upside down. `TextPosition.getDir()` reports 180°, so every glyph is flagged `rotated`, so clause 2 refuses all 112 pairs, so the page's 15 baselines become 61 paragraphs, each with a full line box. That is the D-21 symptom exactly (one page → two), from the first clause of `sameRow`.
* **`21_form_labels`** — `sameRow` rejects *nothing*, and the page still has 47 paragraphs for 29 baselines. The loss is not in the predicate; it is in **what the predicate is asked to compare against** (§3.2).

### 2.3 Clauses I deliberately did not widen

* `across-column-gap` (246 pairs) — the gap it rejects is 19–27 pt in the TOC and in every newspaper; a gutter between two columns of prose is 20–30 pt too. There is no measurement that separates "page number 25 pt to the right of the dot leaders" from "second column 25 pt to the right of the first". Widening it merges newspaper columns, which is the defect it exists to prevent (`newspaper-2col-fullwidth-headline`, `62_two_col_newsletter_pull_quote`).
* `past-paper` (66 pairs) — the marksheet's grade columns really are drawn 2 pt past the paper. A tab stop there makes Word wrap the value onto the next line, which is the defect the merge exists to remove. Rejecting is right; the document's problem is its own over-wide table.
* `different-size-needs-12pt-gap` (11) and `size-ratio-2.5` (8) — the comment in the source records that these were tuned down from 30 % and 12 pt because loosening them changed row heights on `table-with-rotated-header` and moved rows off the page. I did not touch them.

---

## 3. What I changed

### 3.1 Clause `rotated` was firing on a whole page, not on a stamp

A page printed upside down is not a page of stamps. Every glyph on it is turned 180°, and a 180° baseline is a horizontal baseline — a reader turns the sheet, not each word. New `uprightIfPageIsUpsideDown(glyphs)` runs once per page, before `toLines`:

```java
private static void uprightIfPageIsUpsideDown(List<Glyph> glyphs) {
    int turned = 0;
    for (Glyph g : glyphs) {
        if (g.text == null || g.text.trim().isEmpty()) continue;
        if (!g.rotated) return;                     // an upright glyph: an ordinary page
        if (Math.abs(g.diry) > 0.25f) return;       // the baseline is not horizontal
        if (g.dirx >= 0f) return;                   // not turned round
        turned++;
    }
    if (turned == 0) return;
    for (Glyph g : glyphs) g.rotated = false;
}
```

It is page-level on purpose: a 180° stamp laid over an ordinary page (`04_stamp_180deg_upside_down`, `08_two_overlapping_stamps`) has upright glyphs beside it, so the function returns on its first upright glyph and the stamp keeps its flag, its overlay order and its rasterised appearance. Nothing in `sameRow` changed — the pairs it was already willing to accept are now offered to it as what they are.

Effect: page 2 of `one-page-rotated-180-degrees`, 61 paragraphs → 26 (24 of them merged rows), 120 → 86 paragraphs for the document, body flow 1 523.6 pt → 955.0 pt.

### 3.2 A row was measured against the wrong line of its own group

`toParagraphs` grows a group by comparing each new line against `group.get(size-1)`. Once `addRowMates` has attached a field from another column, that last element is a field on the **right**, and `sameRow` rejects any `next` that begins to the *left* of the one it is compared with (`if (next.x < prev.x - 0.5f) return false`). So a row whose left-hand fields arrived later in the column order was cut in two — one row plus its own tail, two paragraphs per baseline:

```
before:  "Account holder  Account no. 50100234567890"     (row)
         "NIRVAAN PACKAGING INDUSTRIES"                    (its own tail, a line lower)
after:   "Account holder  NIRVAAN PACKAGING INDUSTRIES  Account no. 50100234567890"
```

The fix is one line plus a helper: the row test is made against the group's last field that stands on the new line's baseline and ends before it begins; the prose test (`sameParagraph`) still compares against the line above, which is what a paragraph is. `sameRow` is untouched — nothing here widens what a row *is*, only which member of the row it is measured against.

```java
Line last = group.get(group.size() - 1);
if (sameRow(prevOnBaseline(group, line), line, pageWidth, rowWidth(group, line))) {
    group.add(line);
} else if (sameParagraph(last, line, pageWidth, blockRight)) {
```

(My first attempt passed the row reference to `sameParagraph` too. That stopped prose continuing — the line above and the field beside it share a baseline, so the y-gap a paragraph needs was zero — and 57 documents gained paragraphs. Measured, reverted, fixed.)

---

## 4. Measurement: paragraphs per baseline and flow height

### 4.1 The seven documents the brief names

`paras` = every paragraph carrying text, table cells included. `body` = paragraphs outside any `w:tbl` — the flow. `flow` = Σ(`w:before` + `w:line`) in points.

| document | PDF baselines | paras before → after | body paras before → after | tab-stop paras | flow before → after | body flow before → after | page height |
|---|---:|---:|---:|---:|---:|---:|---:|
| `01_stamp_rotated_15deg_upright` | 34 | 67 → 67 | 25 → 25 | 10 | 1147.0 → 1147.0 | 573.8 → 573.8 | 841.9 |
| `02_stamp_rotated_15deg_upleft` | 30 | 79 → 79 | 14 → 14 | 5 | 1416.0 → 1416.0 | 461.1 → 461.1 | 841.9 |
| `03_stamp_vertical_90deg` | 28 | 98 → 98 | 9 → 9 | 1 | 1552.6 → 1552.6 | 297.2 → 297.2 | 841.9 |
| `04_stamp_180deg_upside_down` | 24 | 43 → 43 | 16 → 16 | 4 | 851.2 → 851.2 | 476.2 → 476.2 | 841.9 |
| `05_round_company_seal_curved_text` | 36 | 80 → 80 | 80 → 80 | 3 | 1329.6 → 1329.6 | 1329.6 → 1329.6 | 841.9 |
| `23_timetable_grid_txtpos` | 15 | 64 → 64 | 8 → 8 | 2 | 2359.0 → 2359.0 | 273.1 → 273.1 | 595.3 |
| `62_two_col_newsletter_pull_quote` | 27 | 32 → 32 | 32 → 32 | 4 | 474.1 → 474.1 | 474.1 → 474.1 | 841.9 |

Before/line split, all paragraphs (01_stamp): 317.8 + 829.2 = 1147.0 pt; body only: 317.8 + 255.9 = 573.8 pt.

### 4.2 Why those seven do not move — and what the 78 was

This is the one place where my measurement disagrees with the brief's, so I am putting the evidence in front of you rather than quietly matching the number.

`base208.json` records **`lines: 67`** for `01_stamp_rotated_15deg_upright`, and the current build produces 67 paragraphs with text — not 78. The 78 (and the 1277 pt) is from a build before the item grid was being found as a table: on this build `01_stamp` emits **2 `w:tbl`s**, a 36-cell item grid and a 6-cell totals block, so 42 of the 67 paragraphs with text are **table cells**, not flow paragraphs. The other 25 body paragraphs sit against 34 distinct baselines, 10 of them carrying tab stops — which is the 1:1 the fix is for, already true here.

That is the honest reading of the same numbers: **on the current build the invoice grid is not the flow problem it was; the 35-cells-on-5-baselines case is handled by the table pass.** Summing `w:line` over table cells (as the 1147.0 figure does) counts a 7-column row seven times, so 1147.0 pt on an 841.9 pt page is not a page overflow for this document — the body flow is 573.8 pt.

Where the same defect *is* still live is §4.3 and §7.

### 4.3 Where the fix did bite — corpus, 208 documents

| metric | before | after |
|---|---:|---:|
| paragraphs with text (all, table cells included) | 16 520 | **16 433** (−87) |
| body paragraphs (outside tables) | 5 370 | **5 283** (−87) |
| body paragraphs carrying tab stops | 825 | **845** (+20) |
| Σ(`w:before`+`w:line`), all paragraphs | 345 841.2 pt | 346 474.8 pt |
| Σ(`w:before`+`w:line`), body paragraphs | 171 708.4 pt | 172 341.8 pt |
| pages where paragraphs-with-text > distinct baselines (engine-side, 540 pages) | 61 | **52** |
| documents where body paragraphs > PDF baselines | 43 | **41** |
| documents where body flow > page height × pages | 16 | **15** |
| same-baseline pairs accepted by `sameRow` | 81.0 % | **84.1 %** |

Eleven documents changed; **none gained a paragraph**:

| document | paras before → after |
|---|---|
| `one-page-rotated-180-degrees` | 120 → 86 |
| `bank-statement-5-pages` | 560 → 545 |
| `brochure-3col-with-sidebar-box` | 57 → 44 |
| `63_three_column_brochure` | 29 → 16 |
| `301_lab_report_panel` | 80 → 77 |
| `322_mutual_fund_factsheet` | 82 → 80 |
| `400_comic_page_speech_bubbles` | 17 → 15 |
| `gst-invoice-with-qr-code` | 90 → 88 |
| `323_credit_card_statement` | 74 → 73 |
| `40_devanagari_shaping_font` | 28 → 27 |
| `form16-part-b` | 107 → 106 |

Attribution (measured by rebuilding with each half disabled): the row-reference change alone gives 16 520 → 16 467 and touches ten documents; the upside-down page fix adds the other 34 paragraphs, all on `one-page-rotated-180-degrees`.

Flow rose on three documents while their paragraph count fell — `323_credit_card_statement` 198.3 → 576.8 pt, `form16-part-b` 864.3 → 1057.1 pt, `bank-statement-5-pages` 1 384.0 → 1 716.2 pt. That is the cost of a correct row: three fields of different sizes on one baseline become one line box as tall as the tallest, where before they were two boxes with a gap between them. All three stay inside their page budget except `form16-part-b`, which was already over it (864.3 > 841.9) before the change. This is a trade I would take — a row is a row — but it is a trade, and it is why the aggregate flow number moves up by 0.2 % while the paragraph count falls.

---

## 5. The patch

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
index 9f3d54d..f04c341 100644
--- a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
+++ b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
@@ -667,6 +667,7 @@ public final class PdfToWord {
                 starts.clear(); starts.addAll(ruleGutters);
             }
         }
+        uprightIfPageIsUpsideDown(glyphs);
         List<Line> lines = toLines(glyphs, asBands(starts));
         List<Line> ring = new ArrayList<>();
         for (java.util.Iterator<Line> it = lines.iterator(); it.hasNext(); ) {
@@ -2348,6 +2349,34 @@ public final class PdfToWord {
         return line;
     }
 
+    /**
+     * Clears the rotated flag when the WHOLE page is drawn upside down.
+     *
+     * <p>A page printed the wrong way up is not a page of stamps. Every glyph on it is turned
+     * 180 degrees, which {@code TextPosition.getDir()} reports as a non-zero direction, so every
+     * glyph was flagged {@link Glyph#rotated}: {@code sameRow} then refused all 112 pairs of
+     * fields that stood on a shared baseline, and the page's 15 baselines came out as 61
+     * paragraphs - one per field, stacked one above the other, which is the flow that runs off
+     * the sheet. A reader turns the sheet, not each word, and the baseline is horizontal either
+     * way, so the page's text is offered as upright.
+     *
+     * <p>Only when nothing on the page is upright: a 180-degree stamp laid over an ordinary page
+     * (04_stamp_180deg_upside_down, 08_two_overlapping_stamps) is still an overlay and keeps its
+     * flag, and so does any page whose text does not run along a horizontal baseline.
+     */
+    private static void uprightIfPageIsUpsideDown(List<Glyph> glyphs) {
+        int turned = 0;
+        for (Glyph g : glyphs) {
+            if (g.text == null || g.text.trim().isEmpty()) continue;
+            if (!g.rotated) return;                     // an upright glyph: an ordinary page
+            if (Math.abs(g.diry) > 0.25f) return;       // the baseline is not horizontal
+            if (g.dirx >= 0f) return;                   // not turned round
+            turned++;
+        }
+        if (turned == 0) return;
+        for (Glyph g : glyphs) g.rotated = false;
+    }
+
     private static List<Line> toLines(List<Glyph> glyphs, List<float[]> gutters) {
         // A seal drawn as a ring of characters is not a block of text and has no baseline to
         // cluster on: every character sits on its own tangent. It is taken out of the page's
@@ -3175,10 +3204,14 @@ public final class PdfToWord {
                 addRowMates(group, line);
                 continue;
             }
-            Line prev = group.get(group.size() - 1);
-            if (sameRow(prev, line, pageWidth, rowWidth(group, line))) {
+            Line last = group.get(group.size() - 1);
+            // A row is measured against its own field on this baseline; prose is measured
+            // against the line above it, which is what sameParagraph() is about. Using the
+            // row's field for both stopped a paragraph continuing: the line above and the
+            // field beside it share a baseline, so the y-gap a paragraph needs was zero.
+            if (sameRow(prevOnBaseline(group, line), line, pageWidth, rowWidth(group, line))) {
                 group.add(line);
-            } else if (sameParagraph(prev, line, pageWidth, blockRight)) {
+            } else if (sameParagraph(last, line, pageWidth, blockRight)) {
                 group.add(line);
             } else {
                 out.add(buildPara(group, pageWidth, bands));
@@ -3191,6 +3224,38 @@ public final class PdfToWord {
         return out;
     }
 
+    /**
+     * The line of {@code group} that a new line should be measured against.
+     *
+     * <p>Usually the last line added, and that is what this returns when the group holds no
+     * field to the left of the new line on its baseline. The exception is a row: once a field
+     * from another column has been attached to it, the group's last line is that field, and
+     * {@link #sameRow} rejects a field that begins to the LEFT of the one it is compared with.
+     * So a row whose left-hand fields came later in the column order - the "Account holder /
+     * NIRVAAN PACKAGING INDUSTRIES / Account no. 50100234567890" of a bank statement, the
+     * "NAV (GROWTH) / AUM / EXPENSE RATIO / FUND MANAGER" header of a fund factsheet - was cut
+     * in two, one row plus its own tail, one pair of paragraphs per baseline. Measuring the new
+     * line against the group's last field that stands on its baseline and ends before it begins
+     * lets a row grow to the right whatever order its fields were offered in.
+     *
+     * <p>Measured on the 208-document corpus: 16520 paragraphs with text became 16467, 10
+     * documents lost paragraphs, none gained one (bank-statement-5-pages 560 -> 545,
+     * 63_three_column_brochure 29 -> 16, brochure-3col-with-sidebar-box 57 -> 44,
+     * 322_mutual_fund_factsheet 82 -> 80). {@code sameRow} still decides what a row is;
+     * nothing here widens it.
+     */
+    private static Line prevOnBaseline(List<Line> group, Line next) {
+        Line last = group.get(group.size() - 1);
+        Line best = null;
+        for (Line g : group) {
+            if (g.x > next.x) continue;
+            float size = Math.max(g.size, next.size);
+            if (Math.abs(g.y - next.y) > Math.max(1.2f, size * 0.25f)) continue;
+            if (best == null || g.x > best.x) best = g;
+        }
+        return best == null ? last : best;
+    }
+
     /**
      * Puts the fields standing on {@code line}'s baseline into the paragraph it starts.
      *
```

Nothing in this patch depends on `w:lineRule="exact"`. Both changes decide only *which lines are one paragraph*; the line spacing the writer emits afterwards is untouched, so a reader that turns `exact` into `auto` on import (Google Docs) changes how tall each paragraph is, not how many there are — and there are now fewer.

---

## 6. Gate

```
$ python3 tools/p2w-bench/gate.py --corpus /scratch/work/corp/flat \
      --out /scratch/work/out-final --baseline tools/p2w-bench/base208.json --check
documents: 208
IMPROVED: 26 counts
JOINED: 12 line counts fell with no word lost
   301_lab_report_panel            lines   80 -> 77
   322_mutual_fund_factsheet       lines   82 -> 80
   323_credit_card_statement       lines   74 -> 73
   400_comic_page_speech_bubbles   lines   17 -> 15
   40_devanagari_shaping_font      lines   28 -> 27
   63_three_column_brochure        lines   29 -> 16
   bank-statement-5-pages          lines  560 -> 545
   brochure-3col-with-sidebar-box  lines   57 -> 44
   form16-part-b                   lines  107 -> 106
   gst-invoice-with-qr-code        lines   90 -> 88
   newspaper-2col-fullwidth-headline lines 61 -> 60
   one-page-rotated-180-degrees    lines  120 -> 86
no document got worse
```

Every one of the 87 paragraphs removed is reported by the gate as a **join** — a line count that fell with no word lost — which is the category the gate has for exactly this change. Page counts are unchanged on all 208 (no document's `pages` moved in either direction).

The engine's own tests, same classpath as `tools/verify-engine.sh`:

```
PDF2WORD TOTAL: 29 passed, 0 failed
REALDOCS TOTAL: 3 passed, 0 failed
```

---

## 7. Still broken, measured, not fixed

Three same-family defects survive, each with the number that says so. I did not fix them because each needs a decision the brief did not give me, and two of them are not `sameRow`'s to make.

1. **The seal ring — `05_round_company_seal_curved_text` still becomes two pages.** 80 body paragraphs for 36 baselines; flow 612.7 + 716.9 = **1329.6 pt on an 841.9 pt page**. 60 of the 80 paragraphs are one character each — the curved text of the round seal, emitted by `ringPara` one paragraph per character (`S R I V I N A Y A K A …`). A ring has no baseline, so `sameRow` cannot merge it, and each character carries a full line box. Fixing it means writing the ring as one paragraph of characters rather than one paragraph per character — a change to the stamp/seal model, not to baseline grouping, so I left it alone. **This is the one document in the brief's list that is still a one-page PDF that will come back as two pages.**
2. **`table-of-contents-dot-leaders` — 55 paragraphs for 24 baselines.** Each entry is `01` + `Board of Directors … . . . .` + `4` on one baseline. The number is rejected by `different-size-needs-12pt-gap` (same column, 7.5 pt gap), the page number by `across-column-gap` (19–27 pt gap — indistinguishable from a newspaper gutter). A dot-leader row needs its own rule ("a line whose right end is a bare page number and whose middle is leaders"), which is a new predicate, not a widening of this one.
3. **`21_form_labels_x60_values_x300_txtpos` — 47 paragraphs for 29 baselines, and `sameRow` rejects nothing.** The pre-pass attaches cross-column mates (`if (b.column == a.column) continue`), so same-column fields on a row are left to the group loop, and `addRowMates` only fires for a group of size 1 — a mate whose owner joins an existing group is dropped or orphaned. This one is worth a follow-up: it is the same "row cut in two" shape as §3.2, one level further out, and I could not make it move with a change that also kept the gate clean.

Also worth knowing, though it is not a grouping defect: `marksheet-subject-left-marks-right` draws its last grade column at x 587–597 on a 595.3 pt page, so 66 pairs are refused by `past-paper` and the rows stay split. The PDF itself overflows; the converter cannot place a tab stop past the paper without Word wrapping the value.

---

## 8. Reproducing this

```
git clone --depth 1 https://github.com/kavopdf/app W && cd W
git apply EX-A.patch                     # the diff in §5
bash tools/verify-engine.sh              # needs a JDK; downloads PDFBox-Android + BouncyCastle
# corpus: unzip pdf-to-word-test-corpus-v3.zip, p2w-batch-1.zip, p2w-all-groups.zip into one folder
CP=libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar:out
cd tools/engine-verify && javac -nowarn -cp "$CP" -d out ../../app/src/main/java/com/kavopdf/app/engine/*.java
javac -nowarn -cp "$CP" -d out ConvertAll.java
java -Djava.awt.headless=true -Dp2w.assets=libs/aar/assets -cp "$CP" ConvertAll <corpusdir> <outdir>
cd ../.. && python3 tools/p2w-bench/gate.py --corpus <corpusdir> --out <outdir> \
      --baseline tools/p2w-bench/base208.json --check
```

Sandbox note: the run above used a 640 MB heap. The `-Xmx900m` from the brief's command line is not usable in a 2 GB container — it died with `Native memory allocation (malloc) failed to allocate … Error detail: Chunk::new` after writing all 208 documents; `-Xmx640m -XX:MaxMetaspaceSize=320m` completes cleanly in 48 s.
