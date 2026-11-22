# 18_displacement — the eleven non-ruled documents are THREE faults, not one. Six of them share a single engine term (the table gap spacer) and it is already measured to clear all six.

**22 Nov 2026 · census run · engine HEAD built in-sandbox (`tools/p2w-bench/build-engine.sh`, 39 s) ·
no engine code changed, no Drive document created · every displacement number below is either a live
Google round trip recorded in `FINDINGS/`, or a LibreOffice measurement of a build this run made, or a
derivation from the measured `w:line` charge — each row says which.**

## The question, and the answer in one line

Of the 16 documents that fail `18_displacement` and nothing else, 5 are ruled tables with a sub-point
row pitch. The other 11 are this census. **They do not share one construct.** They split

| group | construct | documents | n |
|:--|:--|:--|--:|
| **A** | the table **gap spacer** written as `w:line` on a 1 pt mark — Google charges it at 22 % of its written value | `16_right_aligned_amounts_txtpos`, `22_invoice_four_columns_txtpos`, `29_dot_leaders_txtpos`, `41_coloured_headings_white_bg`, `68_journal_wide_table_spanning`, `73_marksheet_subject_marks_grade` | **6** |
| **B** | `w:trHeight hRule="atLeast"` **row growth** — Google lays the row to the cell's own line box, a fraction of a point per row, accumulated down the table | `362_price_list_dense`, `72_bank_statement_no_rules_right_amounts` | **2** |
| **C** | a **placement offset** of a block's first line (`w:before` + hairline `w:line`, `LINE_BASE`) — present in LibreOffice too, so not a Google-only term | `31_times_body_arial_headings`, `71_invoice_space_aligned_no_rules`, `balance-sheet-two-columns-of-figures` | **3** |

Group A is one construct, it is the majority, and it is already bracketed by measurement: moving the
spacer's gap from `w:line` to `w:before` took **all six** of those documents to **42/42 clean in
Google** on one build (`FINDINGS/18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md`).
The other five are not reachable that way and are not one fault between them.

## The discriminator is not the rule count. It is who owns the rules.

The census that produced "four or fewer horizontal rules" is right about 9 of the 11 and wrong about
two: `16_right_aligned_amounts_txtpos` draws **17** rules (a header rule at 80, a second at 140, then
15 light-grey 0.3 pt hairlines from 161 to 395 at a 19.00 pt pitch — a fully ruled ledger) and
`balance-sheet-two-columns-of-figures` draws **5**. Counted with the instrument's own definition
(`verify_google._rules`: thin ≤ 4 pt, long ≥ 10 pt, isolated ≥ 3 pt), this run measured:

    16 ......... 17     22 ......... 4     29 ......... 3     31 ......... 2
    362 ......... 0     41 ......... 2     68 ......... 4     71 ......... 2
    72 .......... 2     73 ......... 2     balance-sheet  5

**The property that actually separates the 11 from the 5 is the carrier, not the count.** In all 11
the rules leave the engine as floating `<w:drawing>` shapes and the table is emitted with every one of
its six `tblBorders` set to `nil`; in the ruled 5 the rules leave as **cell borders**. Measured on
documents converted this run:

| document | `tblBorders` | `insideH w:val="single"` | `<w:drawing>` |
|:--|:--|--:|--:|
| `16_right_aligned_amounts_txtpos` | all `nil` | **0** | 17 |
| `68_journal_wide_table_spanning` | all `nil` | **0** | 14 |
| `balance-sheet-two-columns-of-figures` | all `nil` | **0** | 5 |
| `mobile-bill` (one of the ruled 5) | — | **3** | 15 |
| `table-with-no-header-row` (ruled 5) | — | **1** | 2 |

A cell border is a length Google adds **on top of** `w:trHeight`; a floating shape is not a length at
all. That is why the 5 fail on pitch and the 11 do not — and it is a better statement of the boundary
than the rule count, because `16` and `balance-sheet` cross it on the count and do not cross it on the
carrier.

## The eleven, one row each

Displacement columns are `dy = render_ry − src_ry`, negative = drawn **higher** on the page, the sign
`18_displacement` uses. `first text` / `first rule` are device-y on page 1.

| # | document | what the source page actually holds | measured displacement | hypothesis (one line) |
|--:|:--|:--|:--|:--|
| 1 | `16_right_aligned_amounts_txtpos` | 1 page A4. A ruled job-work ledger: 17 stroked rules (navy 1.0/0.8 pt at 80/140, then 15 grey 0.3 pt hairlines 161→395 at 19.00 pt pitch), five right-aligned numeric columns, 21 text lines, no image. Engine: borderless 13-row table + 17 floating drawings. | first text 49.14 → 50.40 (**+1.26**, LO); first rule 80.00 → 80.00 (**0.00**, LO). Google [live, PAGETOP finding]: **+0.2 at the top → −7.0 at the foot**, a ramp of ≈ 0.13 pt/row. | the 4.65 pt gap above the table is written as `w:line` on a 1 pt mark and Google charges it at 22 % — the ledger below starts high and the error accumulates down the rows. |
| 2 | `22_invoice_four_columns_txtpos` | 1 page A4 invoice, four columns (description/qty/rate/amount), 4 rules (navy 80 and 174, grey 414, footer 793.9), 27 text lines. Engine: two borderless tables, 12 and 4 rows. | first text 49.14 → 50.40 (**+1.26**, LO); first rule **0.00**. Google: not individually reported; spacer written **6.65 pt** (133 tw) ⇒ model step **−5.2** at the table top. | same spacer. **Proven**: this document scored **42/42 CLEAN** with the spacer alone moved to `w:before`. |
| 3 | `29_dot_leaders_txtpos` | 1 page restaurant bill: 12 dot-leader lines with right-aligned amounts (17 distinct x clusters), 3 rules (80, 394, footer), one 5-row table. No image. | first text 49.14 → 50.40 (**+1.26**, LO); first rule **0.00**. Google: not individually reported; spacer written **15.85 pt** (317 tw) ⇒ model step **−12.4**. | same spacer, one table, one gap. **Proven**: 42/42 CLEAN with the spacer alone. |
| 4 | `31_times_body_arial_headings` | 1 page AGM notice — **plain paragraphs**, 29 lines in one column (3 distinct x), 2 rules (94, footer 793.9). **No table at all and no spacer** in the emitted docx. | first text 49.16 → 52.40 (**+3.24**, LO); whole page **+2.48 − 0.00031 y**, med +2.70, span 1.55 (LO). Google [live, spacer-fix residual]: **+2.62, slope +0.00291** — the same offset, not a new one. | every line is advanced by `w:before` plus a hairline `w:line` (= 1.38 × size), so the page is placed at `LINE_BASE` of a 0.65 pt box: the whole notice sits 2.6–3.2 pt low in **both** renderers. |
| 5 | `362_price_list_dense` | 1 page dense price list: **zero rules**, 258 text runs, a 29-row × 9-column table at an **8.40 pt** pitch (260 cells), 6.5–7 pt type. No image. | first text 31.64 → 31.20 (**−0.44**, LO); LO med **+0.01**, 3 runs out of 258. Google [live, PAGETOP]: **−3.5 top → −19.4 foot**, non-monotone (−3.5 → −10.8 → −14.6 → −18.7); after the spacer fix **−2.76, slope −0.01474**. | `hRule="atLeast"` on a sub-10 pt pitch: Google grows each row to the cell's natural line box and lays it ~1.5 % **shorter** than the page's 8.40 pt, which over 29 rows is the whole residual. |
| 6 | `41_coloured_headings_white_bg` | 1 page catalogue: three coloured heading bands over three borderless price tables (4 + 5 + 3 rows at 18.00 pt pitch), 2 rules (84, footer), 23 text lines. | first text 50.24 → 51.60 (**+1.36**, LO); first rule **0.00**. Google [live]: med **−4.13**, min −6.84, max +0.88, 21/36 runs out. Spacers written **3.50 / 3.45 / 3.45 pt** (70/69/69 tw) — one per table. | same spacer, three of them; each table starts ~0.75 pt high and the third table's block carries all three. **Proven**: 42/42 CLEAN with the spacer alone. |
| 7 | `68_journal_wide_table_spanning` | 1 page of a journal: two-column prose above, then a 7-row × 7-column table whose black 0.5 pt rules sit at 344/363/382/401/420/439/458 (19.00 pt pitch) and whose width (558) runs past the text column (539). | first text 47.75 → 48.80 (**+1.05**, LO); first rule **0.00**. Google [live]: **0.0 down to y = 185, then −114.8 for everything below**; med **−114.28**, min −115.03, max +1.31, 61/74 out. LO also fails: med −3.09, 46/74 out. | same spacer at its largest: the page draws a **148.07 pt** gap, the engine writes **144.0 pt** (2880-twip cap) as `w:line` on a 1 pt mark, and Google charges 22 % of it — 0.78 × 144 = **−112.3** predicted against **−114.28** measured. **Proven**: −114.28 → −3.08 with the spacer as `w:before`, then CLEAN with the cap raised. |
| 8 | `71_invoice_space_aligned_no_rules` | 1 page invoice with **no drawn table rules at all** — the columns are held by spaces, and the page's only rules are the header rule at 84 and the footer. 26 text lines, one 14-row borderless table. | first text 51.14 → 52.40 (**+1.26**, LO); then LO **med +2.32 but the table's rows uniformly +9.52 and the `Total` line +24.42**, span 32.0 — it fails `18_displacement` in LibreOffice too. Google [live]: med **+1.06**, min +0.12, max **+6.69**, 29/72 out. **No spacer in the document.** | a block **placement** offset, not a pitch: the 18.00 pt row pitch is exact in the render and the rows are nonetheless drawn 9.5 pt low, so the table's top is placed from the wrong flow position while its rows are right. |
| 9 | `72_bank_statement_no_rules_right_amounts` | 1 page bank statement, no rules but the header rule at 84 and the footer; 26 text lines, one 18-row borderless table at a **17.00 pt** pitch with right-aligned amounts, 5 columns. | first text 51.14 → 52.40 (**+1.26**, LO); LO med **+0.87**, clean. Google [live, spacer-fix residual]: **+1.18, slope +0.00932** ⇒ rows ~0.16 pt taller each, +2.9 pt over 18 rows. Spacer written **18.30 pt** (366 tw) ⇒ model step −14.3 before the fix. | `atLeast` row growth, the `362` term with the opposite sign: at a whole-point pitch Google's natural row is a fraction of a point **taller**, and 18 of them is over the count budget. |
| 10 | `73_marksheet_subject_marks_grade` | 1 page marksheet: header block, then a 9-row borderless subject table at 19.00 pt pitch (code/subject/max/secured/grade/result), 2 rules (84, footer), 17 text lines. | first text 48.42 → 49.60 (**+1.18**, LO); first rule **0.00**. Google [live]: med **−12.85**, min −145.35, max +6.40, 60/64 out. Spacer written **16.70 pt** (334 tw) ⇒ model step **−13.0** against **−12.85** measured. | same spacer. **Proven**: 42/42 CLEAN with the spacer alone. |
| 11 | `balance-sheet-two-columns-of-figures` | 1 page balance sheet: two side-by-side columns of figures (equity/liabilities left, assets right), 5 rules (101.4; a pair at 119.4; a pair at 302.2), 37 text lines, two borderless tables (5 and 11 rows) at an 11.60 pt pitch. | first text 44.25 → 43.80 (**−0.45**, LO); LO med **+0.10** but the two column-header rows (`EQUITY AND LIABILITIES`, `ASSETS`, 7.4 pt) sit **+3.69**, 6/94 out — it fails in LibreOffice too. Google: fails; spacer written **12.60 pt** (252 tw) is a second term on top. | the first row of a table places its cell text by `w:before` measured from the row's own top box, so the header row lands 3.7 pt low while rows 2+ land within 0.4 pt. |

## What the numbers say about the mechanism (group A)

The engine writes the gap above a table as an empty paragraph whose gap is a `w:line` length on a
1 pt mark:

    <w:p><w:pPr><w:snapToGrid w:val="0"/><w:spacing … w:before="0" w:after="0"
      w:line="<spacerTw>" w:lineRule="exact"/><w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>

`w:line` with `lineRule="exact"` is a length to Word and LibreOffice and a **multiple of the mark's own
line height** to Google — and the mark is 1 pt, so Google's line box for it is a fraction of a point
and it charges **~22 %** of the written value. Everything below the spacer then moves **up** by the
78 % it did not charge. Two independent confirmations, both live round trips:

| document | spacer written | 0.78 × spacer | measured Google dy |
|:--|--:|--:|--:|
| `68_journal_wide_table_spanning` | 144.0 pt (capped; page draws 148.07) | −112.3 | **−114.28** |
| `73_marksheet_subject_marks_grade` | 16.70 pt | −13.0 | **−12.85** |

That is a dose-response across a factor of nine in the written value, and the sign, the magnitude and
the **block boundary** all match: on `68` the runs above the spacer read +0.09 and every run below it
−114 to −115.

**Where the term lives:** the value is computed at `DocxWriter.java:5852` (absolute branch) and
`:5866` (baseline branch), both capped at 2880 twips, and the spacer is emitted at
**`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:5869-5874`** — the `w:line` on a
`<w:sz w:val="2"/>` mark. The one-line change already measured on all 16 is `w:before="<spacerTw>"
w:line="1"` at that site, plus the cap raised 2880 → 4320 (one document needs it: `68`, whose real gap
is 2961 twips).

**Why it is not landed:** it is correct and it is blocked. Charging the spacer at its true value
removes slack that two *ruled* documents were living on, and `mobile-bill` and
`insurance-policy-schedule` overflow to two pages on it (41/42 → 38/42). Group A therefore cannot ship
alone; it ships with the row-height term for the ruled five. That is the measured state, not this
run's opinion.

## What this run measured, and what it did not

Measured this run, on a HEAD build, for all 11: the source page's geometry (rules via
`verify_google._rules`, text lines, columns, images, page size — all 11 are 1 page, 595.3 × 841.9, no
images); the emitted docx (tables, cells, `tblBorders`, `trHeight`/`hRule`, spacer paragraphs and their
values, `<w:drawing>` count); a LibreOffice render of that docx and `verify_google.py` source-vs-render
on it (the 11 reproduce the recorded `gverify-lo` verdicts **exactly**: 8 pass, `68`, `71`,
`balance-sheet` fail); and `dy.py` per-run displacement on that render.

**Not measured this run, and deliberately so: the Google side of the 8 documents whose drift exists
only in Google.** A Google number needs a Drive document, and this census was constrained to create
none. Every Google figure in the table above is therefore either (a) a live round trip already recorded
in `FINDINGS/` — `16`, `362`, `68`, `71`, `73`, `41` before the fix and `31`, `362`, `72` after it — or
(b) marked "model", i.e. 0.78 × the spacer value this run measured in the docx. `22` and `29` have no
recorded dy at all; what they have instead is a stronger fact, that they score 42/42 clean when the
spacer alone is moved.

## What would prove this wrong

1. **A group-A document that stays failing with the spacer as `w:before` and the cap raised.** The
   spacer run measured 6 clean and 8 still failing; if a rerun puts one of the six back, the construct
   is not the cause on that document and the census is wrong about it.
2. **A group-B document whose rows lay at the declared pitch in Google.** `362` and `72` are claimed to
   drift because Google's `atLeast` row is a fraction of a point off. One round trip reading the laid
   row pitch off the exported PDF (as the mobile-bill measurement did: 18.40 source, 19.10 Google)
   settles it either way.
3. **A group-C document whose offset disappears in Google.** `31`, `71` and `balance-sheet` are claimed
   to be engine-side because LibreOffice shows the same offset. If Google's dy is much smaller than
   the LibreOffice dy on the same build — `71` is the suspect: +9.52 in LO against +1.06 median in
   Google — then `71` belongs in a fourth group and this census is one group short.
4. **A spacer written on a mark larger than 1 pt.** If the 22 % is a property of the 1 pt mark and not
   of `w:line` itself, the charge should scale with the mark's size. It has never been probed.
