# 18_displacement — the page-top gap: one construct PROVEN, one REFUTED, and the 16 solo-18 documents are not this class

**22 Nov 2026 · relay slot 07:14 → · measured on `bank-statement-5-pages` through Google Docs, three renders, same engine**

## Why this was measured

`benchmarks/gverify/*.json` says 16 documents fail `18_displacement` **alone** in Google. The recorded
lead (`FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md`) says the dominant Google
sub-shape is a **uniform page shift of ~55 pt** caused by Google dropping `w:before` on the first
paragraph after a page break, and that a 1×1 `trHeight`-exact row is honoured instead. That lead had
one known blocker: the row costs the page its own top gap, and attempt 3 overflowed 6 pages into 10.

This run tested both constructs on the live instrument, and then asked the question the lead never
asked: **do the 16 documents the class is worth actually have a page break?**

## The measurement

Engine `7112d766`, corpus PDF from `corpus-fetch.sh`, `.docx` from `ConvertOne`, render =
upload → `GOOGLEDRIVE_CREATE_FILE` (as `application/vnd.google-apps.document`) →
`GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` (PDF) → `verify_google.py` against the source PDF.
All three probe Google Docs were deleted after scoring; the `KavoPDF-Verify` folder is empty.

| variant | what changed in `word/document.xml` | pages | score | failing |
|:--|:--|---:|---:|:--|
| BASE | nothing (the engine's own output) | 5 | **37/42** | 18, 25, 27_text_off_page, 44, 59 |
| TABLEROW | each page-top `w:before="1103"` → 1×1 `w:tbl`, `w:trHeight w:val="1103" w:hRule="exact"`, `w:before="0"` | **6** | **33/42** | 01, 17, 18, 25, 31, 32, 44, 55, 59 |
| SECTMARGIN | `w:pgMar w:top="1103"`, every page-top `w:before="1103"` → `0` | **5** | **40/42** | 18, 25 |

Per-page matched-run dy (source baseline → render baseline, `difflib` on run text, 113 runs matched
per page):

| page | BASE median dy | SECTMARGIN median dy |
|---:|---:|---:|
| 0 | −4.3 | −4.3 |
| 1 | **−59.5** | −4.3 |
| 2 | **−59.5** | −4.3 |
| 3 | **−59.5** | −4.3 |
| 4 | **−59.5** | −4.3 |

## What this proves

1. **The 1×1 `trHeight` row is REFUTED, not merely blocked.** It does not overflow by a few points —
   it takes the document from 5 pages to 6, empties a page (`31_pages_lost_their_text` 5 → 1),
   drops matched runs 585 → 220, and adds six checks' worth of new failure. A table is a block that
   Google will not let sit inside the page's paragraph flow the way `w:before` does. Do not retry
   this construct on the strength of the TOPD probe: the probe measured one row in isolation, and
   in a real document the row restructures the page.

2. **The section top margin is PROVEN.** `w:pgMar w:top` delivers the page-top gap that Google drops
   from `w:before`, exactly: the −59.5 pt uniform shift on pages 1-4 collapses to the −4.3 pt the
   document already carries on page 1, page count is unchanged at 5, and three checks that were
   failing now pass (`27_text_off_page`, `44_header_footer`, `59_shape_anchor`) with nothing new
   failing. It is also the only one of the two constructs that costs the page exactly what the PDF
   spends — it moves space from the flow to the margin instead of adding a block.

3. **The residual is a different sub-construct.** After the margin the document still fails 18 with a
   median −4.3 and a spread −12.8 .. +2.9 on *every* page including page 1. That is row/line pitch,
   not page-top placement, and it is the same −4.3 page 1 has always had.

## The correction the next run needs

**All 16 documents that fail `18_displacement` alone are SINGLE-PAGE documents.** Measured, from the
source PDFs:

| document | pages | page-1 ink y |
|:--|--:|:--|
| 16_right_aligned_amounts_txtpos | 1 | 62.5 .. 807.6 |
| 22_invoice_four_columns_txtpos | 1 | 62.5 .. 807.6 |
| 29_dot_leaders_txtpos | 1 | 62.5 .. 807.6 |
| 31_times_body_arial_headings | 1 | 65.7 .. 808.1 |
| 362_price_list_dense | 1 | 42.6 .. 797.3 |
| 41_coloured_headings_white_bg | 1 | 64.7 .. 807.6 |
| 68_journal_wide_table_spanning | 1 | 60.5 .. 807.5 |
| 71_invoice_space_aligned_no_rules | 1 | 64.5 .. 807.6 |
| 72_bank_statement_no_rules_right_amounts | 1 | 64.5 .. 807.6 |
| 73_marksheet_subject_marks_grade | 1 | 62.8 .. 807.6 |
| balance-sheet-two-columns-of-figures | 1 | 56.3 .. 803.8 |
| bus-timetable-station-left-times-right | 1 | 52.1 .. 809.4 |
| insurance-policy-schedule | 1 | 54.8 .. 817.8 |
| mobile-bill | 1 | 54.8 .. 817.8 |
| table-with-no-header-row | 1 | 54.0 .. 817.8 |
| two-tables-stacked-with-no-gap | 1 | 54.0 .. 817.8 |

And the converted `.docx` of all 16 carries **zero** `<w:br w:type="page"/>` — there is no page break
in any of them for a page-top gap to sit on. So the page-top gap construct, proven as it now is,
**cannot make a single one of those 16 documents clean.** The lead that said "15 documents are 41/42
failing 18 alone, so the class is one build away" was reading a real measurement and drawing the
wrong conclusion from it: those documents are dense single-page tables, and their displacement is
row/line pitch inside the table body.

## Where the proven construct does pay

Multi-page documents with a table or header band at the top of each page: `bank-statement-5-pages`
(37 → 40/42, 3 checks), and the 15 of 28 probe pages the dy-shape finding called UNIFORM PAGE SHIFT.
Whether any of them reaches 42/42 is **not measured** — only `bank-statement-5-pages` was scored, and
it does not.

## The engine change this needs (not landed — no slot left to measure it)

Per-page, not per-document: the gap differs per page in general, and the engine already emits a
section break with its own `sectPr` at `DocxWriter.java:1053-1075` when the page size changes. The
build is to take that path for every page whose first block sits below the paper's top edge:

1. emit `<w:sectPr>` with `w:pgMar w:top` = that page's `topGap` twips and `w:type w:val="nextPage"`
   instead of the plain `<w:br w:type="page"/>` at `DocxWriter.java:1080-1086`;
2. set `beforeTw = 0` in the `ctx.newPage` branches (`DocxWriter.java:3395-3401`, `4277-4283`);
3. subtract the same twips from `ctx.budgetTw` (`DocxWriter.java:1116`) and from the height
   `pageFits(page, ph)` is asked about, so `fitPage` still accounts for the space it no longer
   spends as flow.

Steps 1-2 alone double the gap in LibreOffice, which honours `w:before`; step 3 is what keeps the
page count. That is why this is a build and not an edit, and why it must be scored in both renderers.
