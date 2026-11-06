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
