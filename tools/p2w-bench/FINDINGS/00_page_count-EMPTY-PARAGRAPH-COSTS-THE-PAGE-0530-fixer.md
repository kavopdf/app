# 00_page_count — the page is spent on empty paragraphs, not on the rules they carry

**Class:** `00_page_count` (23 documents refused, 23.0 clean-document leverage)
**Engine:** `cb0f54d4` (live tree, `build-engine.sh`, 36 s)
**Measured:** 23 Nov 2026, 04:56–05:55 IST. Eight Google round trips (upload → convert to a Google Doc
→ export PDF → read the PDF), one LibreOffice render, and one independent re-measurement of every
number below by a second agent working from the exported files only.

## The question

23 of 213 documents are `page_count_refused`: Google reflows them onto a different number of pages, so
`gverify.py --collect` refuses them and **every one of the 42 checks on them is unknown**. 20 of the 23
are one-page sources Google renders onto two (`pages: 2, want: 1`); the two bank forms go 9 → 14.

No finding in this repository had ever explained one of them, and the leverage table scores the class at
23.0 clean documents — a refused document fails exactly one thing.

## What was believed

*"Rules are written as floating `<w:drawing>`s and Google drops the shape while keeping its anchor"*
(`FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`). A dropped shape costs nothing, so the refusal had
to come from somewhere else.

## What is measured, on `301_lab_report_panel` (1 page, 76 text paragraphs, 108 drawing-only paragraphs)

| build | Google pages | vector drawings p1 | image placements p1 / p2 |
|:--|--:|--:|:--|
| source PDF | 1 | 108 | 0 / – |
| our `.docx`, unpatched | **2** | 22 | 58 / 50 |
| same `.docx` in LibreOffice | **1** | – | – |

1. **Google does not drop the shape.** It rasterises it: 108 vector drawings in the source become 108
   image placements, painted at their source page coordinates (page-1 images run y −0.4 → 300.9,
   page-2 images sit at y 285–722). The 22 vector rules that survive are the ones Google could keep as
   vectors.
2. **The images are passengers. The flow cost is the empty paragraph that carries each one.** Summed
   shape height is 2026 pt, but the whole trailing block costs **89.9 pt** — about **0.83 pt per
   paragraph**, the line box of a `w:sz=2` run under `w:line="1" w:lineRule="exact"` (2.25 pt × 0.35),
   not the 0.1552 pt the exact line asks for. Measured directly: deleting one of the 108 moved the
   page-2 block from 40.7 → 39.9 pt.
3. **The arithmetic closes.** Page 1 has ~44.5 pt free at the bottom; the 108 empty paragraphs cost
   89.9 pt; the last text line already lands 9.5 pt lower than its source line (786.5 vs 777.0). The
   source has 58 pt of slack there and we spend all of it, then 45 pt more.
4. **The control.** Delete the 108 drawing-only paragraphs and the same document renders **one page**,
   with the text at exactly the same y (797.5). So the text is not the cause and the drift is not the
   cause; the empty paragraphs are.

## The class, sized from the built `.docx`s, not from a sample

All 23 refused documents were converted with `ConvertOne` (one JVM each) and their paragraphs counted:

| document | drawing-only paras | of which after the last text para |
|:--|--:|--:|
| 041122-Account_Opening_Form / _Fillable_filled | 2464 | 618 |
| 375_attendance_register | 456 | 456 |
| 390_wide_data_appendix | 400 | 400 |
| 351_omr_answer_sheet | 381 | 381 |
| 341_shipping_manifest | 301 | 301 |
| 305_vaccination_certificate | 228 | 228 |
| 403_crossword_puzzle | 169 | 169 |
| 405_sheet_music_lyrics | 144 | 144 |
| 333_datasheet_spec_tables | 132 | 132 |
| 301_lab_report_panel | 108 | 108 |
| 361 / 326 / price-list-2col / 320 / 314 / 332 | 91 / 88 / 85 / 80 / 79 / 58 | all |
| bank-statement-horizontal-rules-only | 39 | 39 |
| boq-horizontal-rules-only | 33 | 33 |
| 401_trifold_brochure | 21 | 21 |
| 60_page_border | 15 | 15 |
| 05_round_company_seal_curved_text | 7 | 7 |
| 350_question_paper | 1 | 1 |

22 of 23 carry drawing-only paragraphs, and in every one of them every such paragraph is emitted
**after** the last text paragraph — i.e. charged to the page below the text, exactly where there is no
room. `350_question_paper` has one and is **not** explained by this; its refusal is a separate cause.

## The candidates

| # | variant | Google pages | status |
|:--|:--|--:|:--|
| 1 | remove the **last** drawing-only paragraph | 2 (block 40.7 → 39.9) | **refuted** — one paragraph of 108 |
| 2 | remove **all** 108 drawing-only paragraphs | **1** | the control that proves the cause; not a fix (it deletes every rule) |
| 3 | `custGeom` → `prstGeom prst="rect"` on all shapes | 2 (58 images, unchanged) | **refuted** — Google rasterises the preset too |
| 4 | `wp:wrapNone` → `wp:wrapSquare` | 2 (p1 images 58 → 16, p2 92) | **refuted** — it moves them, it does not stop them |
| 5 | `w:framePr` on the drawing-only paragraphs | 2 (output byte-identical) | **refuted** — Google ignores `w:framePr` |
| 6 | merge the 108 drawings into **one** paragraph | – | **VOID, not refuted** — the probe was built with a slicing bug: it kept all 108 original paragraphs *and* added a merged one, and the corrected rebuild was malformed XML (Google 400, LibreOffice "could not be loaded"). Neither run measured what the row claims. |
| 7 | attach the drawings to the existing text paragraphs | – | **VOID, not refuted** — same slicing bug (6 pages, but with the originals still present). |

Rows 6 and 7 are the two that were never actually tested, and row 6 is the interesting one: if the cost
is per empty paragraph, collapsing 108 into one saves 107 × 0.83 = **88.8 pt** against a measured need of
89.9 pt — a margin of about one point, so it is a coin flip that has to be measured, not assumed. Build
it properly (remove the originals, keep `</w:body>`), and check both renderers.

## What is now true

* A paragraph whose only content is a page-positioned floating `<w:drawing>` is charged to Google's flow
  at the line box of its own tiny run (~0.83 pt for `sz=2`), because Google's converter turns the shape
  into an image and keeps the paragraph. It is not dropped, and `w:line="1" exact` is not honoured.
* So the construct behind `32_stroke_lines` and `05_chars_extra` is the **same** construct that refuses
  these 23 documents: one mechanism, three check families. A document with 400 rules pays 330 pt of
  flow for them; that is a page, not a rounding error.
* Any fix must reduce the number of paragraphs in the flow or take the rules out of the flow: emit the
  rule as `w:pBdr` (the known-good patch, whose ceiling is the table writer —
  `FINDINGS/content-present-partly-displaced-rule-guard-was-not-the-blocker-100700-f1x.md`) or as
  `w:tcBorders`/`w:tblBorders` on the cell the rule belongs to.

## What would prove this wrong

* A document whose drawing-only paragraphs sit **before** its last text paragraph and still refuses at
  the same ratio.
* Two builds differing only in the number of trailing drawing-only paragraphs, same page count.
* A `w:pBdr` build of `301_lab_report_panel` that renders one page and still fails `32_stroke_lines`.

## For the next run

`DocxWriter.shape()` (DocxWriter.java:2726) emits one paragraph per shape, after the text. Two levers,
in order of evidence: (a) **merge** the drawing-only paragraphs of a page into one and measure — 88.8 pt
saved against 89.9 pt needed on this document, and it is the cheapest change in the writer; (b) route a
rule that belongs to a table cell through the table writer as `w:tcBorders`. Do not retry variants 1, 3,
4 or 5; each carries its measured number above.
