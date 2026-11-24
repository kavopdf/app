# Are the page-height guards why no table-top spacer is ever spent on the `18_displacement` documents?

**Answer, up front: no, not as the question is framed — and the part of it that is true is smaller than the row-excess story implies.**

* The premise "no table-top spacer can ever be spent on the documents that fail `18_displacement`" is **false**. Of the 14 documents whose `failed` list is exactly `["18_displacement"]`, **5 carry a spacer that the guard DID spend** (`w:before` + a 1-twip `w:line`) and they still fail the check.
* Of the **7** that carry a refused (unspendable) spacer, the row-excess charge is the term that decides the boolean in **6**; in **1** (`68_journal_wide_table_spanning`) the page has no room for the gap at all.
* Of those 6, the charge is **unfounded on 2** (the tables draw no rule, so there is no rule to pay) → verdict **(b)**. On the other **4** the charge is founded and the page really cannot hold gap + row growth → verdict **(c)**.
* **The decisive falsifier:** opening the guard on the (b) documents does **not** make them pass. Both available live Google measurements say so — a full spend at 11 tw/row left `72_bank` at 41/42 (`FINDINGS/ROW-EXCESS-11-TW-PER-ROW-PROBE-1707-relay.md`), and a partial spend left `72_bank` and `two-tables-stacked-with-no-gap` at 41/42 (`FINDINGS/18_displacement-PARTIAL-SPEND-IS-INERT-AND-COSTS-68-JOURNAL-2315-fixer.md`). So the guard is the reason the spacer is *unspent*, and it is **not** the reason the document *fails*.

**Tally over the 14 documents:** (a) genuinely no page room — **1**; (b) guard over-charges a rule the page does not draw — **2**; (c) charge correct, page genuinely full — **4**; no spacer decision at all, or already spent — **7** (5 spent + 2 with no table-top gap).

---

## 0. Provenance, and what is measured vs. recorded

Nothing in this report is guessed. Three kinds of number appear, labelled:

* **MEASURED (this run)** — produced in this sandbox from the tree under analysis.
* **RECORDED** — a Google round trip already in `FINDINGS/`, quoted with its file.
* **DERIVED** — arithmetic on the two above, shown so it can be checked.

**There is no built `word/document.xml` in the repository.** `find . -name document.xml` → 0 hits, `find . -name '*.docx'` → 0 hits, and the 14 source PDFs are not in the repo either (`benchmarks/` carries only `corpus-extra/` 600–602 and `realworld/`). So the emitter's arithmetic alone cannot answer the question — the inputs (`spacerTw`, `pageRowCount`, `pageInkBottomPt`) come from the page. Both were obtained instead:

1. **Corpus** fetched with the repo's own script path (`gh release download corpus-v1 --repo kavopdf/app`, the four zips named in `tools/p2w-bench/corpus-fetch.sh:40`), 219 PDFs; all 14 present.
2. **Engine built from this tree** with `tools/p2w-bench/build-engine.sh` (43 s). Engine fingerprint of this tree, from `tools/p2w-bench/regress.py:73` (`engine_fingerprint`): **docx `3e7f7c4475343a35`**, all-source `b97d8172ce642eb0`. That is the same engine the 22:00 guard finding measured, which is why the XML below matches its census to the twip.
3. **XML** from `ConvertOne` on each of the 14 (`tools/engine-verify/ConvertOne.java`), read out of `word/document.xml`.
4. **The guard's own variables** are not in the XML, so they were traced: a *copy* of the engine tree (`/scratch/work/inst`) got one `System.err.println` inserted after `DocxWriter.java:6098` and nothing else. Nothing in `/scratch/work/CS` was modified. **The instrumentation is inert, proven by bytes**: for all 14 documents the instrumented build's `word/document.xml` is byte-identical to the pristine build's (`identical=True` ×14).
5. **Cross-check of the trace against the XML**: the traced `pageRowCount` equals the `<w:tr>` count in the emitted table for all 12 documents where the guard printed a decision (13/13, 29/29, 7/7, 7/7, 18/18, 10/10, 16/16, 33/33, 22/22, 24/24, 26/26, 13/13). The thirteenth table-bearing document, `71_invoice_space_aligned_no_rules` (14 rows), printed no decision because it emits no spacer at all.

Page geometry, identical on every document (all are one A4 page): `budgetTw = 16836` (`DocxWriter.java:1136`: `round(ph*20) - PAGE_ROUNDING_TW`, with `PAGE_ROUNDING_TW = 2` at `:377`) = 841.8 pt.

---

## 1. The population, and the spacer census (question 1)

The 14 documents whose `benchmarks/gverify/*.json` has `"failed": ["18_displacement"]` exactly:

`16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings`, `362_price_list_dense`, `36_embedded_subset_font`, `68_journal_wide_table_spanning`, `71_invoice_space_aligned_no_rules`, `72_bank_statement_no_rules_right_amounts`, `74_balance_sheet_indented_subitems`, `balance-sheet-two-columns-of-figures`, `bus-timetable-station-left-times-right`, `insurance-policy-schedule`, `mobile-bill`, `table-with-no-header-row`, `two-tables-stacked-with-no-gap`.

The spacer paragraph is `<w:p>` with the `w:sz w:val="2"` mark and no text run (`DocxWriter.java:6100-6111`). One other emitter writes the same shape and is **not** a table-top spacer: the post-table carrier at `:7007-7013` (`w:before="0"`, `w:line` = `POST_TABLE_TW` = 80 twips, or `POST_TABLE_TW_STACKED` = 1 twip when the next block is another table — `:7221`, `:7230`). `balance-sheet-two-columns-of-figures` carries one of those (`(0, 1)`, between its two stacked tables) and it is excluded from the census below. **MEASURED (this run)**, as emitted by this tree:

| document | tables | spacer `(w:before, w:line)` | form | nil border sides | `pageRowCount` |
|:--|--:|:--|:--|--:|--:|
| `16_right_aligned_amounts_txtpos` | 1 | (92, 1) | **spent** | 6 | 13 |
| `362_price_list_dense` | 1 | (303, 1) | **spent** | 6 | 29 |
| `36_embedded_subset_font` | 1 | (267, 1) | **spent** | 6 | 7 |
| `74_balance_sheet_indented_subitems` | 2 | (64, 1), (65, 1) | **spent ×2** | 6 + 6 | 10 |
| `balance-sheet-two-columns-of-figures` | 2 | (251, 1) | **spent** (one spacer decision only) | 6 + 6 | 16 |
| `68_journal_wide_table_spanning` | 1 | **(0, 2880)** | unspendable | 6 | 7 |
| `72_bank_statement_no_rules_right_amounts` | 1 | **(0, 366)** | unspendable | 6 | 18 |
| `bus-timetable-station-left-times-right` | 1 | **(0, 127)** | unspendable | 6 | 33 |
| `insurance-policy-schedule` | 3 | **(0, 288), (0, 128), (0, 120)** | unspendable ×3 | 0 + 0 + 0 | 22 |
| `mobile-bill` | 3 | **(0, 248), (0, 128), (0, 124)** | unspendable ×3 | 0 + 0 + 0 | 24 |
| `table-with-no-header-row` | 1 | **(0, 247)** | unspendable | 0 | 26 |
| `two-tables-stacked-with-no-gap` | 1 | **(0, 247)** | unspendable | 0 | 13 |
| `71_invoice_space_aligned_no_rules` | 2 | none emitted | — (no gap worth a paragraph, `:6046`) | 6 + 6 | 14 |
| `31_times_body_arial_headings` | **0** | none | — (no table at all) | — | 0 |

**Counts: 7 documents carry at least one unspendable spacer — 11 unspendable spacers in total — and 5 documents carry only spent ones. 2 have no spacer decision at all.** So the census is 7/14, not 14/14.

The "nil border sides" column is measured from the table's own `<w:tblBorders>`: `w:val="nil"` on all six sides means the table draws no rule. This matters below, because the guard's charge is a *rule* charge.

The declared gap converted to what Google actually delivers, using the law the engine itself states (`DocxWriter.java:6075-6081`: `2.5873 * max(L/240, 0.06)` pt for `w:line = L` twips):

| document | declared | declared pt | Google delivers | lost = 0.784 × declared |
|:--|--:|--:|--:|--:|
| `68_journal_wide_table_spanning` | 2880 tw | 144.00 | 31.05 | **112.95** |
| `72_bank_statement_no_rules_right_amounts` | 366 | 18.30 | 3.95 | **14.35** |
| `bus-timetable-station-left-times-right` | 127 | 6.35 | 1.37 | **4.98** |
| `insurance-policy-schedule` | 288 / 128 / 120 | 14.40 / 6.40 / 6.00 | 3.10 / 1.38 / 1.29 | **11.30 / 5.02 / 4.71** |
| `mobile-bill` | 248 / 128 / 124 | 12.40 / 6.40 / 6.20 | 2.67 / 1.38 / 1.34 | **9.73 / 5.02 / 4.86** |
| `table-with-no-header-row` | 247 | 12.35 | 2.66 | **9.69** |
| `two-tables-stacked-with-no-gap` | 247 | 12.35 | 2.66 | **9.69** |

Against the committed Google measurements (`benchmarks/gverify/*.json`): `72_bank` `med_dy` −13.0 / `worst_dy` 28.2; `bus-timetable` −3.0 / 4.9; `insurance-policy-schedule` −7.7 / 47.8; `table-with-no-header-row` −0.5 / 9.0; `two-tables-stacked-with-no-gap` −4.7 / 10.2. `68_journal` and `mobile-bill` carry **no** `displacement` object in their JSON (`null`); for `mobile-bill` the three steps −8.76, −4.19, −4.08 are RECORDED in `FINDINGS/18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md`, and for `68_journal` the step is **not stated** anywhere I found — its 2880-twip spacer predicts 112.95 pt, which is the largest number in this class and is unmeasured.

---

## 2. What `slackTw` would have to be, against what it is (question 2)

The guard (`DocxWriter.java:6092-6098`):

```java
int spacerHairTw = 1;                                                        // :6092
int rowExcessTw  = 15 * Math.max(0, ctx.pageRowCount);                       // :6093
int slackTw      = ctx.budgetTw - Math.round(ctx.pageInkBottomPt * 20f);     // :6094
int roomWantTw   = Math.max(0, spacerTw - 20);                               // :6095
int wantTw       = Math.max(0, spacerTw - spacerHairTw);                     // :6096
boolean spendable = slackTw > 0
        && ctx.spacerSplitTw + roomWantTw + rowExcessTw <= slackTw;          // :6097-6098
```

So the required slack is exactly

    requiredSlack = spacerSplitTw + roomWantTw + rowExcessTw

**MEASURED (this run)**, traced at each decision, in twips (1 pt = 20 tw). `gapAlone = spacerSplitTw + roomWantTw` is what the page would need if the row charge were not there:

| document (spacer) | `spacerSplitTw` | `roomWantTw` | `rowExcessTw` | **required slack** | **actual `slackTw`** | **deficit** | deficit in pt |
|:--|--:|--:|--:|--:|--:|--:|--:|
| `68_journal_wide_table_spanning` | 0 | 2860 | 105 | **2965** | **568** | **2397** | **119.85** |
| `72_bank_statement_no_rules_right_amounts` | 0 | 346 | 270 | **616** | **558** | **58** | **2.90** |
| `bus-timetable-station-left-times-right` | 0 | 107 | 495 | **602** | **547** | **55** | **2.75** |
| `insurance-policy-schedule` #1 | 0 | 268 | 330 | **598** | **380** | **218** | **10.90** |
| `insurance-policy-schedule` #2 | 0 | 108 | 330 | **438** | **380** | **58** | **2.90** |
| `insurance-policy-schedule` #3 | 0 | 100 | 330 | **430** | **380** | **50** | **2.50** |
| `mobile-bill` #1 | 0 | 228 | 360 | **588** | **380** | **208** | **10.40** |
| `mobile-bill` #2 | 0 | 108 | 360 | **468** | **380** | **88** | **4.40** |
| `mobile-bill` #3 | 0 | 104 | 360 | **464** | **380** | **84** | **4.20** |
| `table-with-no-header-row` | 0 | 227 | 390 | **617** | **380** | **237** | **11.85** |
| `two-tables-stacked-with-no-gap` | 0 | 227 | 195 | **422** | **380** | **42** | **2.10** |

For contrast, the five documents the guard **spends** on, same trace:

| document | required slack | actual `slackTw` | headroom |
|:--|--:|--:|--:|
| `16_right_aligned_amounts_txtpos` | 268 | 558 | 290 (14.50 pt) |
| `362_price_list_dense` | 719 | 798 | 79 (**3.95 pt**) |
| `36_embedded_subset_font` | 353 | 558 | 205 (10.25 pt) |
| `74_balance_sheet_indented_subitems` #1 / #2 | 195 / 241 | 558 / 558 | 363 / 317 |
| `balance-sheet-two-columns-of-figures` | 472 | 660 | 188 (9.40 pt) |

`slackTw` is the page's own room: `budgetTw` (841.8 pt) minus the source page's lowest ink (`pageInkBottomPt`, `DocxWriter.java:2432-2446`). For the four refused one-page documents `pageInkBottomPt` is 813.89, 814.47, 822.78 and 822.78 pt — i.e. the source page draws to 2.8–28 pt above the paper's bottom. That is the whole of `slackTw`'s 380–568 twips.

---

## 3. Which of (a), (b), (c) — settled by arithmetic, document by document

Two tests separate the three answers, and both are pure arithmetic on the numbers above:

* **T1 (is there room for the gap at all?)** — `gapAlone = spacerSplitTw + roomWantTw` vs `slackTw`.
  If `gapAlone > slackTw`, the row charge is irrelevant and the answer is **(a)**.
* **T2 (is the row charge founded?)** — the 15 tw/row is the row's own rule. `DocxWriter.java:6227-6234`: *"The rule the writer draws is added to every row by the renderer … 0.375 pt of each into the row, 0.75 pt in all … **An unruled table draws no rule and keeps its full pitch**."* 15 twips = 0.75 pt. If the page's tables draw no rule (all six sides `nil`), the charge is charging for something that is not there → **(b)**. If the tables are ruled, the charge is the renderer's real behaviour → **(c)**.

### `68_journal_wide_table_spanning` → **(a) genuinely no page room**

`gapAlone = 2860`, `slackTw = 568`. The gap alone is **2292 tw = 114.6 pt** bigger than the room the page has, before any row charge is applied. Setting `rowExcessTw = 0` leaves `2860 > 568` — **measured**: the patched build traces `rowExcessTw=0 … needTw=2860 spendable=false`, and its `document.xml` is byte-identical to the unpatched one. The row charge is 105 tw, i.e. **3.5 %** of the 2965 required. This document is a 144 pt gap on a page with 28.4 pt of room; no guard arithmetic can spend it. (It is also the document whose partial spend cost a check outright — `59_shape_anchor` 49 → 0, RECORDED in the 23:15 partial-spend finding.)

### `72_bank_statement_no_rules_right_amounts` → **(b) the charge is the whole deficit, and the charge is unfounded**

* `gapAlone = 346 ≤ slackTw = 558` → the page **has** room for the gap. T1 passes.
* `requiredSlack = 616 > 558` → the boolean is false **only** because of the 270-twip row charge. The deficit is 58 tw = **2.90 pt**, which is **21.5 %** of the 270-tw charge. Drop the charge and the condition is satisfied with 212 tw (10.6 pt) to spare.
* The charge is unfounded here: this document's table is `nil` on all six sides (measured, 6 nil sides). Per `:6234` an unruled table draws no rule and keeps its full pitch, so 15 tw/row is charged for a rule that is not drawn.

### `mobile-bill` → **(c) the charge is founded and the page really is full**

* `gapAlone = 228 ≤ slackTw = 380` → T1 passes, so the row charge is again the deciding term (deficit 208 tw = 10.40 pt = **57.8 %** of the 360-tw charge).
* But the charge is **founded**: this document's three tables are ruled (0 nil sides). And the page's room is genuinely consumed by that rule: the row growth alone is 360 tw = **18.0 pt against 19.0 pt of room**. There is 1 pt of margin left; the gap wants 11.4 pt. Spending it must overflow, and that is what was measured — RECORDED, `FINDINGS/…-0323.md` and `:6061-6065`: spending unguarded took `mobile-bill` and `insurance-policy-schedule` from 46/47 on one page to 43/47 on two, content lost.
* Same arithmetic for `insurance-policy-schedule`: `gapAlone = 268 ≤ 380`, charge 330 = 16.5 pt of a 19.0 pt page, gap 13.4 pt.

### `bus-timetable-station-left-times-right` → **(b)**, and `table-with-no-header-row` / `two-tables-stacked-with-no-gap` → **(c)**

* `bus-timetable`: `gapAlone = 107 ≤ 547`, deficit 55 tw = **2.75 pt** = 11.1 % of the 495-tw charge, and the table is unruled (6 nil sides) → **(b)**. This is the most lopsided case in the set: 495 twips of rule charged to a table that draws none, to refuse a 107-twip gap on a page with 547 twips free.
* `two-tables-stacked-with-no-gap`: `gapAlone = 227 ≤ 380`, deficit 42 tw = **2.10 pt**, table **ruled** (0 nil) → charge founded → **(c)**, by the narrowest margin in the class.
* `table-with-no-header-row`: `gapAlone = 227 ≤ 380`, deficit 237 tw = 11.85 pt, table ruled → charge founded → **(c)**. Note the extra fact: its row charge (390 tw = 19.5 pt) *already exceeds the page's whole room* (380 tw = 19.0 pt), so this page is over-committed by its own rows whether or not the gap is spent. The guard's refusal does not rescue that page; it only declines to add to it.

### The premise, corrected

Five of the 14 fail `18_displacement` **with a spent spacer in the file**: `16`, `362`, `36`, `74`, `balance-sheet-two-columns-of-figures`. Their committed residuals are `med_dy`/`worst_dy` −2.8/5.4, 1.7/3.5, 2.2/4.2, −2.3/5.1 (and `16`'s `displacement` object is `null` in its JSON). Those numbers are **1.7–5.4 pt**, an order of magnitude below the 9.7–14.4 pt that an unspent spacer costs on this class. So on those five the spacer is not the construct at all, and the class contains at least one other mechanism (the row half of the two-sub-defect split in `FINDINGS/18_displacement-STEP-IS-THE-UNSPENDABLE-SPACER-0323.md`, plus whatever moves `31_times_body_arial_headings`, which has **zero tables**).

---

## 4. If (b), what is the smallest source change — and is it LibreOffice-invariant?

The (b) population is exactly the 2 documents whose refused page charges 15 tw/row to an **unruled** table. The smallest change that removes that charge is one expression, plus the three declarations it needs. It is already written down in the repo, uncommitted, as `FINDINGS/18-guard-unruled-row-excess-2200.patch`; **it is not in the tree** — my trace shows the tree still computing `15 * pageRowCount`.

Four hunks, one line of behaviour:

```java
// 1. new Ctx field, next to `int pageRowCount;`
int pageRuledRowCount;

// 2. in pageBody, next to `ctx.pageRowCount = pageRows(page);`
ctx.pageRuledRowCount = pageRuledRows(page);

// 3. a new method, next to pageRows (DocxWriter.java:2424-2430)
private static int pageRuledRows(PdfToWord.Page page) {
    int n = 0;
    for (Object o : page.blocks) {
        if (!(o instanceof PdfToWord.Table)) continue;
        PdfToWord.Table t = (PdfToWord.Table) o;
        boolean ruled = t.ruled;
        for (int i = 0; !ruled && i < 6; i++) ruled = t.sideDrawn[i];
        if (ruled) n += t.rows.size();
    }
    return n;
}

// 4. the guard, DocxWriter.java:6093 — the only behaviour change
- int rowExcessTw = 15 * Math.max(0, ctx.pageRowCount);
+ int rowExcessTw = 15 * Math.max(0, ctx.pageRuledRowCount);
```

**Is it LibreOffice-invariant? Yes — and this is measured, not argued.** Two independent reasons:

1. **By construction.** Both arms write a paragraph whose `w:before + w:line` equals `spacerTw` to the twip: spendable is `before = spacerTw − 1, line = 1` (`:6100-6105`); unspendable is `before = 0, line = spacerTw` (`:6108-6111`). The file says so at `:6113-6115` ("The page is charged the same gap either way"). A renderer that lays `before + line` — LibreOffice and Word — therefore cannot see the flip. **MEASURED (this run):** the two documents that flip change from `(0, 366) → (365, 1)`, sum 366 → 366, and `(0, 127) → (126, 1)`, sum 127 → 127.
2. **By render.** Both arms were converted to PDF with LibreOffice and rasterised at 110 dpi: `72_bank` base and patched render to the **same sha256** (`f102749ba37416d4`), one page each; `bus-timetable` base and patched render to the **same sha256** (`cb19010b5a2d4324`), one page each. Pixel-identical.

**What it is worth, and it is not the class.** MEASURED (this run): of the 14 documents, exactly **2** change (`72_bank`, `bus-timetable`); the other 12 `document.xml` are byte-identical, including `68_journal` (which stays refused at `needTw = 2860` even with `rowExcessTw = 0`) and the four ruled (c) documents (whose `pageRuledRowCount` equals `pageRowCount`, so their charge is unchanged). The 22:00 finding measured the same 2-of-13 result over its 13-document population. And on Google the gain is small: RECORDED in `18-guard-charges-a-rule-an-unruled-table-does-not-draw-2200-fixer.md`, spending the gap adds `366 − 2.5873·(366/240) = 78.7 tw = 3.93 pt` on `72_bank` (against a recorded `med_dy` of −13.0) and `27.4 tw = 1.37 pt` on `bus-timetable` (against −3.0).

**Do not expect the two documents to go clean, and here is the falsifying measurement already on file.** The same flip was reached by lowering the constant rather than by excluding unruled rows: `FINDINGS/ROW-EXCESS-11-TW-PER-ROW-PROBE-1707-relay.md` (RECORDED, live Google round trip, 23 Nov 17:10) reports `72_bank` at **11 tw/row** → the guard opened, `w:before="365" w:line="1"` emitted, the table body landed at `dy +3.23` — **and the document stayed 41/42**, because the page then sat 4.85 pt low and 7 of 80 runs were over tolerance. That finding's conclusion is the one this analysis lands on independently: the gap the page needs is ~13.5 pt, not the 18.3 pt `extraAbs` computes, so the spacer is over-measured by ~4.5 pt on this document. `18_displacement-PARTIAL-SPEND-IS-INERT-AND-COSTS-68-JOURNAL-2315-fixer.md` (RECORDED) reached the same place from the other side: partial spend left `72_bank` and `two-tables-stacked-with-no-gap` at 41/42 — **unchanged**.

**The other candidate charge fix is inert.** A page with three spacers charges its whole row excess three times (`spacerSplitTw` accumulates `roomWantTw` only, `:6106`, and never nets off the charge). De-duplicating it would flip **nothing** on this population, arithmetically: on `insurance-policy-schedule` and `mobile-bill` the *first* spacer already fails (`598 > 380`, `588 > 380`), so `spacerSplitTw` stays 0 at the second and third and their required slack is unchanged (438 and 430, 468 and 464). The over-charge is real but currently harmless, which is why the 22:00 patch deliberately left it alone.

---

## 5. Verdict, stated so it can be falsified

1. **The guards are not why "no table-top spacer can ever be spent".** 5 of the 14 spend at HEAD (`16`, `362`, `36`, `74`, `balance-sheet-two-columns-of-figures`), and `362_price_list_dense` spends with only 3.95 pt of headroom. Any claim of the form "the guard refuses every one of these pages" is false on this tree.
2. **Among the 7 that do refuse, the row-excess charge is the deciding term on 6.** Remove `rowExcessTw` and all six satisfy `spacerSplitTw + roomWantTw <= slackTw`. Only `68_journal` survives the removal, short by 114.6 pt.
3. **The charge is unfounded on 2 of those 6** (`72_bank`, `bus-timetable`: all six sides `nil`, and `:6234` says an unruled table keeps its full pitch) — **(b)**. **It is founded on 4** (`mobile-bill`, `insurance-policy-schedule`, `table-with-no-header-row`, `two-tables-stacked-with-no-gap`: ruled tables, and on the first two the row growth alone eats 18.0/16.5 pt of a 19.0 pt page) — **(c)**.
4. **Removing the unfounded charge does not fix its two documents.** Predicted-clean vs measured: `72_bank` 41/42 → 41/42 (both the 11-tw probe and the partial spend), `bus-timetable` never measured after a flip — **not stated**. So (b) is a real defect in the guard, and it is **not** the reason `18_displacement` fails on those documents.
5. **Falsifiable predictions of this analysis, in order of cheapness.** (i) The 22:00 patch, applied to this tree, changes `document.xml` on exactly `72_bank` and `bus-timetable` among the 14 — *verified here by construction; re-check by byte diff*. (ii) `72_bank` stays 41/42 after it, with the table body inside tolerance and the page 4–5 pt low — *already measured at 11 tw/row, which reaches the same flip*. (iii) If `68_journal` were to pass after any guard-only change, this analysis is wrong, because its required slack (2860 tw) exceeds its room (568 tw) by a factor of 5.0 with the row charge set to zero. (iv) If `362_price_list_dense` (spent spacer, `worst_dy` 5.4 on 29 unruled rows) were shown to carry ~21.75 pt of accumulated row ramp, then the 15 tw/row charge would apply to unruled tables after all and (b) collapses into (c) for all 7 — this is the single measurement that would overturn point 3, and the committed numbers (5.4 pt worst on 29 rows) point the other way.

---

## 6. Not measured / not stated

* `68_journal_wide_table_spanning`'s Google displacement is `null` in its JSON and I found no recorded `med_dy` for it. Its 112.95 pt predicted loss is **not stated** as measured.
* `mobile-bill`'s JSON carries no `displacement` object; the three steps quoted (−8.76, −4.19, −4.08) are RECORDED in the 03:23 finding, not in the committed JSON. Its committed status (engine `b7699196`, measured 2026-11-23T17:15) is **46/47 failing `18_displacement`**, and the record also contains a contradictory live measurement — 47/47 CLEAN under the spacer patch, `FINDINGS/18-displacement-mobile-bill-47of47-and-a-refutation-that-does-not-reproduce-1612-relay.md`. I did not run a Google round trip, so I cannot adjudicate between them; I have taken the committed JSON as the status and flagged the conflict rather than picking a side.
* `bus-timetable` was not measured in Google after any guard flip. Whether it becomes clean is **not stated** anywhere in the repo.
* Whether the 15 tw/row applies to a *content-bound* row only — `DocxWriter.java:6236-6241` measured that a `w:trHeight`-bound row renders at its declared height with or without borders, and only a content-bound row pays the rule — is not resolved for the four (c) documents. If `mobile-bill`'s and `insurance-policy-schedule`'s rows are `w:trHeight`-bound (`atLeast 360/380`, per `FINDINGS/18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md`), their true excess is below 360/330 twips and their (c) verdict would soften toward (b). This is the one open discrimination in the (c) group.

## 7. Reproduction

```bash
gh release download corpus-v1 --repo kavopdf/app -p p2w-all-groups.zip        # + p2w-batch-1,
   # pdf-to-word-test-corpus-v3, p2w-round2-additions  (tools/p2w-bench/corpus-fetch.sh:40)
unzip -j -o corpuszips/*.zip -d corpus
bash tools/p2w-bench/build-engine.sh                                          # 43 s
cd tools/engine-verify && java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:\
libs/bcpkix.jar:libs/bcutil.jar" ConvertOne /scratch/work/corpus/<doc>.pdf /out
# spacer census: paragraphs with <w:sz w:val="2"/> and no text run; read w:before / w:line
# guard variables: copy the tree, add one System.err.println after DocxWriter.java:6098,
#   rebuild, run with -Dp2w.assets=<libs>/aar/assets; assert the document.xml is unchanged
```
