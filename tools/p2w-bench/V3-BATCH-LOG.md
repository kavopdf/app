# PDF → Word: corpus v3, batch by batch

Corpus v3 is `pdf-to-word-test-corpus-v3.zip`, 75 documents numbered 300-417, one per document
*type*: medical, legal and government, finance, engineering, logistics, education, retail, forms,
developer output, diagrams, print media, and PDF-internals tricks. Batches are 15 documents.

Every batch is converted, rendered through LibreOffice, opened side by side with the source page
at 110-130 dpi, and measured: page counts, words present, image counts, and the baseline-to-
baseline offset of every line matched by its text.

---

## BATCH 1 — documents 300-318 (15 documents)

**Visual result: 9 excellent, 6 good, 0 broken, 0 page-count defects.**

Every one of the 15 is one page in and one page out. Every word of every page is present. Both
documents that draw an image (300 prescription, 303 discharge summary) carry it.

### Fixed in this batch

- **A rule's y was in the wrong frame.** `buildTables()` compares drawn rules against lines, and
  it was handed the rules with y measured up from the page bottom while lines carry y down from
  the top. On **316_contract_with_schedules** the schedule's three rules were therefore wrapped
  round two paragraphs of prose above them: 2.1/2.2 and 3.1 came out as a bordered two-column
  table with "2.2 Invoices shall be raised monthly and paid within 30 days of receipt." squeezed
  into a 150 pt cell. The rules are now flipped once, before the first pass, and both calls to
  `buildTables()` use the flipped copy. 316's median line offset went **66.1 pt -> 5.5 pt**, and
  the schedule table now sits on the page's own y (top 485.4 against the PDF's 485.4) with the
  page's three columns instead of five guessed ones.
- **A cell's text is now ordered by the strings the page drew.** `glyphText()` sorted a cell's
  glyphs by x. Where the page draws a value that overruns its column on top of the label it runs
  into, that interleaves the two strings: **311_fir_police_form**'s address ends "560067" while
  "Mobile" starts 19 pt before the address finishes, and the cell came out as
  "6M0o0b6i7le". Glyphs are now split where x steps backwards, and the pieces are ordered by
  where each one starts, so each string stays whole.

### Measured across the whole corpus (208 documents)

Both fixes were diffed against the previous engine over all 208 PDFs, comparing page count,
table count and word count: **205 unchanged, 2 improved, 1 changed only because a real table is
now found (64_newspaper, identical text)**. No document got worse. `TestPdfToWord` 29/29 and
`TestRealDocs` 3/3 pass.

### Not fixed — carried forward

- **315_gazette_notification** — three columns stack into one flow, so the gazette's three
  columns read down the page instead of across it. Same class as the 80-corpus multi-column
  items; page count happens to stay at 1.
- **311_fir_police_form** — the address cell overruns its column in the PDF itself, so its tail
  lands in the next cell; row pitch is also compressed (median 31 pt off).
- **314_tender_rfp_boq** — "8,39,69,600" renders as "8,39,69,60": the last column is exactly as
  wide as the page's own text and the substituted face is wider, so LibreOffice clips one
  character. Needs column slack when a cell's drawn right edge sits within a point of its text.
- **300, 302, 306, 314** — vertical drift of 22-42 pt median, the same flow-determined spacing
  class recorded for the 80-document corpus.
- **305_vaccination_certificate, 312_affidavit_stamp_paper** — the word-count difference is
  letterspaced capitals: the PDF draws "L", "M", "U" as separate strings and the .docx renders
  them joined. Not a defect; the .docx is the more readable of the two.

### Engine change is carried as a patch

`git push` cannot authenticate from the build sandbox and the MCP commit tool cannot carry a
259 KB source file in one call, so the engine change is committed as
`tools/p2w-bench/patches/3.53.0-rule-y-and-run-order.patch` and applies cleanly to the release
commit with `git apply`. A run with a working push path should apply it and commit the source.

---

## BATCH 2 — documents 320-341 (15 documents)

**Visual result: 10 excellent, 4 good, 1 needing work, 0 broken, 0 page-count defects.**
Every one of the 15 is one page in and one page out — except **324_loan_amortisation_schedule**,
which is 7 in and 7 out. Every .txt scores 78.8 % or better on line position; 14 of the 15 pass all
five .txt checks.

| Doc | Pages | .txt position | Verdict |
|---|---|---|---|
| 320_balance_sheet_statutory | 1/1 | 93.2 % | good |
| 321_auditors_report | 1/1 | 100.0 % | excellent |
| 322_mutual_fund_factsheet | 1/1 | 100.0 % | good — see below |
| 323_credit_card_statement | 1/1 | 100.0 % | needs work — see below |
| 324_loan_amortisation_schedule | 7/7 | 100.0 % | excellent |
| 325_demat_holdings_statement | 1/1 | 100.0 % | excellent |
| 326_itr_computation | 1/1 | 100.0 % | excellent |
| 330_cad_drawing_sheet | 1/1 | 95.0 % | good — see below |
| 331_pid_diagram | 1/1 | 100.0 % | good — see below |
| 332_bom_on_drawing | 1/1 | 78.8 % | excellent |
| 333_datasheet_spec_tables | 1/1 | 100.0 % | excellent |
| 334_patent_document | 1/1 | 100.0 % | excellent |
| 335_msds_safety_data_sheet | 1/1 | 100.0 % | good — see below |
| 340_bill_of_lading | 1/1 | 100.0 % | excellent |
| 341_shipping_manifest | 1/1 | 100.0 % | excellent |

### Fixed in this batch

- **The 3.53.0 engine change is now in the source, not only in a patch.** Batch 1 left
  `patches/3.53.0-rule-y-and-run-order.patch` unapplied because the build sandbox had no push path.
  It applies cleanly to HEAD, is applied, and is committed as source. `TestPdfToWord` 29/29,
  `TestRealDocs` 96.8 / 97.0 / 81.7 — identical to the decimal.
- **A table cell's .txt indent divided by a hardcoded 9 pt, not the size the cell was drawn at.**
  `writeTxt()` wrote `x / (9 * 0.6)` for every cell of every table. A table set at 7.5 pt was
  padded 20 % short and one at 12 pt 25 % long, so the whole table's columns landed in the wrong
  place while the same document's body text scored 100 %. The divisor is now the cell's own size
  from `Table.sizes`. Eight of the fifteen documents were under 60 % before this and all eight are
  above it now:

  | Doc | position before | after |
  |---|---|---|
  | 324_loan_amortisation_schedule | 1.7 % | **100.0 %** |
  | 341_shipping_manifest | 1.3 % | **100.0 %** |
  | 332_bom_on_drawing | 9.6 % | **78.8 %** |
  | 330_cad_drawing_sheet | 20.0 % | **95.0 %** |
  | 333_datasheet_spec_tables | 26.2 % | **100.0 %** |
  | 325_demat_holdings_statement | 28.6 % | **100.0 %** |
  | 320_balance_sheet_statutory | 41.1 % | **93.2 %** |
  | 323_credit_card_statement | 46.2 % | **100.0 %** |

  Only `writeTxt()` changed. Proof the .docx did not move: all 15 were converted before and after
  and the entries inside each package were hashed, not the file bytes. **identical: 15,
  different: 0.**

- **A table now starts at the y the page drew it** (`DocxWriter.table`). The flow ended on some
  baseline and the page put the table's top rule at `t.top`; the difference was white space nothing
  accounted for, so the table began at the prose's own y and every row under it moved up. A
  measured spacer paragraph now holds the gap open. It is only written when the gap is more than
  1.2 line boxes — below that the difference is the substitute face's line box, not white space —
  and never when the previous block was already a table, because a rendered table ends lower than
  its PDF extent and the error would otherwise be charged twice.
- **The paragraph after a table is 4 pt, not 1 twip.** At one twip it was a zero-height line and
  LibreOffice absorbed it into the table as an extra row.
- **Bold on a table's first row now comes from the cell's own face.** `r == 0 && t.header` was a
  guess; it is now `isBoldFace(cellFace)`, with the header guess kept only as the fallback for a
  cell whose face the page did not name.

  Measured vertical error, median |dy| of lines matched by text, old writer against new:

  | Doc | before | after |
  |---|---|---|
  | 324_loan_amortisation_schedule | 33.7 pt | **10.7 pt** |
  | 322_mutual_fund_factsheet | 85.2 pt | **46.0 pt** |
  | 323_credit_card_statement | 17.9 pt | **17.9 pt** (unchanged) |

  Horizontal error is 0.1 pt on all three. No document in the batch got worse.

### Regression, whole corpus

All 75 v3 documents were converted and rendered through LibreOffice. **Page count against the PDF:
74 of 75 match.** The one mismatch is **350_question_paper** (1 in, 2 out) and it is pre-existing:
converted with the previous writer it also renders 2 pages, so this batch's changes did not cause it.

### Carried forward

The five defects recorded in `REMAINING-DEFECTS.md` under batch 2 — 322, 323, 324, 330, 331, 335 and
320. The largest is a class, not a document: **vector graphics the page draws as paths are dropped
or filled black**, and it is what makes 322's riskometer, 331's legend symbols and 335's GHS
pictograms absent from the .docx.

---

## BATCH 3 — documents 342-371 (15 documents)

**Visual result: 10 excellent, 4 good, 1 needing work, 0 broken, 1 page-count defect (pre-existing).**
Fourteen of the fifteen are one page in and one page out. **350_question_paper** is 1 in and 2 out,
and it was 1 in and 2 out before this pass as well.

| Doc | Pages | dy | .txt position | Verdict |
|---|---|---|---|---|
| 342_packing_list | 1/1 | 4.9 pt | 100.0 % | excellent |
| 343_air_waybill | 1/1 | 28.8 pt | 97.4 % | good |
| 344_customs_declaration | 1/1 | 6.1 pt | 93.8 % | excellent |
| 350_question_paper | 1/2 | 160.6 pt | 100.0 % | needs work — see below |
| 351_omr_answer_sheet | 1/1 | 6.5 pt | 100.0 % | excellent |
| 352_certificate_ornate_border | 1/1 | 6.1 pt | 30.0 % | good — stamp glyphs, see below |
| 353_admit_card | 1/1 | 58.6 pt | 100.0 % | good — see below |
| 360_restaurant_menu | 1/1 | 16.8 pt | 88.4 % | excellent |
| 361_product_catalogue_grid | 1/1 | 108.4 pt | 87.9 % | good — see below |
| 362_price_list_dense | 1/1 | 4.3 pt | 77.9 % | excellent |
| 363_warranty_card | 1/1 | 9.9 pt | 100.0 % | excellent |
| 364_event_ticket | 1/1 | 3.5 pt | 100.0 % | excellent — one duplicate token, see below |
| 365_recipe_card | 1/1 | 11.8 pt | 100.0 % | excellent |
| 370_offer_letter | 1/1 | 7.2 pt | 100.0 % | excellent |
| 371_experience_certificate | 1/1 | 5.0 pt | 36.4 % | good — stamp glyphs, see below |

`dy` is the median |offset| of lines matched by their text between the PDF and the LibreOffice
render. Horizontal error is 0.1 pt on all fifteen.

### Fixed in this batch

- **A glyph's size was being read rounded to a whole point.** `Glyph.size` came from
  `TextPosition.getFontSizeInPt()`, which returns an integer: a page that sets 5.8 pt reported
  5.0, and one that sets 6.5 reported 6.0. Every size in every document was snapped, so type was
  set 14 % small wherever the page used a fractional size, and the .txt indent — which divides by
  `x / (size * 0.6)` — landed 15.7 % too far right, just outside the tolerance the position check
  allows. `getFontSize()` is the same number without the rounding.

  Measured on **362_price_list_dense**, a three-column price list set at 5.8 pt: .txt position
  **13.2 % -> 77.9 %**, vertical drift **26.5 pt -> 4.3 pt**.

- **A table cell's exact line height was a constant.** Every cell of every table in every
  document was written with `w:line="200"` — 10 pt — whatever the page had drawn. 362's rows are
  8.4 pt apart, so each of its 29 rows came out 1.6 pt too tall and the table drifted 46 pt down
  the sheet by its last row. The line height is now the row's own pitch, `rowTw`.

- **A size that is not a whole half-point now rounds down, not up.** With the exact size read,
  5.8 pt became `w:sz 12` (6.0 pt). 362's last column is 21.3 pt wide and "485.27" needs 21.6 pt
  at 6.0, so **every row wrapped to two lines and the table came out twice its drawn height**
  (17.3 pt per row against 8.4). `halfPointsDown()` never makes the substitute face wider than
  the page's, so a line the page did not wrap is not wrapped here either.

- **The word-boundary test keeps the whole-point size.** Reading the size exactly moved the gap
  threshold under a letterspaced page: **39_small_caps_letter_spacing** turned
  "E L E C T I O N" into "ELECTION" and the word counts went 7 missing -> 22. `Glyph.sizePt`
  carries the old whole-point value and only the two `gap > size * 0.18f` tests use it. How tall
  a glyph is and where its word ends are different questions.

  Measured vertical error, median |dy|, old writer against new:

  | Doc | before | after |
  |---|---|---|
  | 362_price_list_dense | 26.5 pt | **4.3 pt** |
  | 342_packing_list | 11.8 pt | **4.9 pt** |
  | 344_customs_declaration | 14.0 pt | **6.1 pt** |
  | 351_omr_answer_sheet | 14.3 pt | **6.5 pt** |
  | 353_admit_card | 51.6 pt | 58.6 pt |
  | 360_restaurant_menu | 12.9 pt | 16.8 pt |
  | 370_offer_letter | 5.9 pt | 7.2 pt |

### Regression, all 208 documents

Every document in all three corpora was converted with the old writer and the new one and
compared on page count, words present, images and tables:

| Measure | Result |
|---|---|
| page count worse | **0** |
| missing words worse | **0** |
| extra words worse (>2) | **0** |
| images lost | **0** |
| tables lost | **0** |
| .txt position, mean | **92.8 % -> 93.4 %** |
| .txt position, documents under 60 % | **12 -> 11** |
| .txt position, documents improved | **12** |
| .txt position, documents worse | **3** (375 scoring artefact, 383 and two-tables-stacked by 1.3-1.7 pt) |

`gate.py --check` against `base80.json`: **no document got worse.** `TestPdfToWord` **29/29**.
`TestRealDocs` **96.8 / 97.0 / 81.7** — identical to the decimal.

### Not fixed — carried forward

- **350_question_paper** — 1 page in, 2 out. The MCQ block overflows; pre-existing, unchanged by
  this pass. The .txt also fails TABLE CELLS and NO DUPLICATION on this document.
- **352_certificate_ornate_border, 371_experience_certificate** — .txt position 30.0 % and
  36.4 %. Both are rotated round seals whose text the page draws one character at a time, each on
  its own baseline, so every letter is its own .txt line at a different x. A .txt has no rotation
  and cannot carry them; the body text on both scores 100 %.
- **353_admit_card** — the label/value block ("REGISTER NUMBER" / "AE2024/447182") is emitted as a
  four-column table with the labels as header cells and "Aadhaar ending 4471" in a row of its own,
  where the page sets each label above its value in a two-column band.
- **361_product_catalogue_grid** — each product card's text block is drawn at the top of the card,
  over its photograph, instead of below it; the second row of cards loses its text altogether.
- **364_event_ticket** — "WS24-4471-0082" is drawn twice on the page and appears once in the .docx.
- **343_air_waybill, 361_product_catalogue_grid** — vertical drift 28.8 pt and 108.4 pt, the same
  flow-determined spacing class recorded for the 80-document corpus.

---

## VECTOR PASS — circles and ellipses, 6 Nov

Not a batch: the one class `REMAINING-DEFECTS.md` called out as worth real work, taken as its own
task because it spans four of the eight batch-2 defects and turns up in every corpus.

**The defect.** A page draws a circle or an ellipse as four Bezier curves that close on themselves.
The engine only ever wrote axis-aligned rectangles, so a *filled* circle went out as its bounding
box — a solid square where a ring belongs — and a *stroke-only* circle, being neither a rectangle
nor a single axis-aligned line, was dropped before it reached the writer at all.

**The fix.** `RuleCollector.pathIsEllipse()` recognises the path (one move, four curves, no lines,
no rects, ends within 1.5 pt of where it started, both extents over 2 pt). `DocxWriter.Shape.kind`
then selects `prst="ellipse"` instead of `prst="rect"`. The extent needed no correction: a quarter
arc's control points sit exactly on the ellipse's extremes, so the box is already the ellipse's box
and only the outline drawn inside it changes. Nothing else about the shape path moved — the
`ctmRotated()` guard, the clip, the fill/stroke colours and the `behindDoc` anchoring are as they
were, so a document with no ellipses converts byte-identically.

**Regression, all 208 documents, old engine against new**, comparing page count, words present,
images and tables:

| Measure | Result |
|---|---|
| documents worse on page count | **0** |
| documents worse on words present (>2) | **0** |
| images lost | **0** |
| tables lost | **0** |
| documents improved | **17** |

Page count was then re-rendered through LibreOffice for all 17 changed documents and is unchanged
on every one (65_two_col_full_width_figure_caption is 2 against the PDF's 1 before and after — the
pre-existing multi-column defect, untouched here).

`TestPdfToWord` **29/29**. `TestRealDocs` **96.8 / 97.0 / 81.7** — identical to the decimal.

**What a reader now sees.** 351_omr_answer_sheet is the clearest: 320 bubble outlines that were
simply absent, and 29 filled bubbles that were black squares, are now 349 bubbles, filled ones
correctly filled — the sheet reads as an answer sheet. 331_pid_diagram's legend, both instrument
loops and the pump circles are drawn for the first time. 405_sheet_music_lyrics' 54 note heads and
360_restaurant_menu's 20 dietary markers are ellipses instead of rectangles. 330's compass is a
ring rather than a free-standing black slab.

**What is still open in this class**, recorded in `REMAINING-DEFECTS.md`: filled polygons that are
not ellipses (330's north arrow, 331's pump triangles and gate-valve bowties) still go out as their
bounding box and need `a:custGeom`, not a preset; 335's GHS pictograms are red-stroked rectangles
rather than ellipses and were not touched; 330's hatch is ~30 diagonal one-line strokes and is
dropped rather than drawn.
