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
