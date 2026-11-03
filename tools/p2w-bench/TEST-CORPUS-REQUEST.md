# Documents that would actually help

The corpus has 215 files. Only 52 contain a table, and only four are genuinely
multi-column. That is thin for the two things still failing, and a fix tuned on four files
is a fix that fits four files.

So: yes, more documents would help — but only of specific kinds. Below is what is useful,
what is useless, and why, so the effort is not wasted.

## The one rule that matters

**Every document must have a real text layer.** If it was scanned, printed and re-scanned,
or exported as an image, it is useless for this benchmark: there is no text to compare
against and it lands in the OCR bucket instead. Check by opening it and trying to select
text — if you cannot select a word, do not send it.

The second rule: **the PDF must be the original export**, not a PDF printed from Word and
re-exported through three tools. Re-exporting changes the glyph layout and makes the file
test something nobody's real file does.

## Group A — multi-column, 10 files (highest value)

This is the worst benchmark (line order 79.82 %) and the corpus has four examples.

- 2-column newspaper page, with a full-width headline and a photo caption
- 3-column newsletter, with a full-width header and footer
- 2-column academic paper, IEEE style, abstract then two-column body
- 2-column magazine page with a pull quote spanning both columns
- 2-column price list, dense, amounts right-aligned
- 2-column document with a table spanning both columns
- 2-column with footnotes at the bottom of the page
- 2-column where one column is much shorter than the other
- 3-column with a sidebar box
- 2-column with a section heading that spans both columns

What makes these useful: the headline or header that spans both columns is exactly what
hides the gutter, and that is the case the detector currently fails.

## Group B — two fields on one baseline, 10 files

The second failure: a question and its marks, a product and its price, a label and its
value, all drawn at different x on the same line. Our engine welds them into one line; the
reference keeps them apart.

- university question paper, marks in brackets at the right margin
- price list with the amount right-aligned
- invoice line items with quantity, rate and amount in separate right-hand columns
- table of contents with dot leaders and right-aligned page numbers
- exam marksheet, subject names left and marks right
- payslip, label left and amount right
- product catalogue, code left and price right
- balance sheet with two columns of figures
- form with labels left and boxes right
- railway or bus timetable

What makes these useful: the two fields must be **far apart horizontally** with visible
white space between them, and both must be real text.

## Group C — Indian business documents with tables, 20 files

These are what people actually convert, and the corpus has one or two of each.

- GST invoice, 3-4 variants (with and without a logo, with and without a QR code)
- GST invoice with a multi-page item table
- income tax return computation, with the slab table
- Form 16
- salary slip, 2 variants
- bank statement, 2-3 variants (one of them 5+ pages)
- bill of quantities or tender BOQ, 2 variants
- purchase order
- delivery challan
- e-way bill
- balance sheet and profit & loss
- marksheet, 2 variants
- admit card
- land record or 7/12 extract
- property tax receipt
- insurance policy schedule
- mutual fund statement
- electricity bill
- mobile bill

What makes these useful: a real table with **more than four rows and more than three
columns**, and some of them drawn with **horizontal rules only** — no vertical lines. That
is the case 3.46.6 fixed and it needs more coverage than one file.

## Group D — deliberately awkward, 10 files

- table with merged cells
- table that continues across a page break, with a repeated header
- table inside a two-column page
- table with a rotated header
- text held twice in the file (shadow text, or the same text drawn in two positions)
- a landscape page inside a portrait document
- a document where one page is rotated 180 degrees
- a document with a very long single-column table
- a document with a table that has no header row
- a document with two tables stacked with almost no gap between them

## What is not needed

- scanned documents (no text layer) — these belong to the OCR benchmark, not this one
- anything under 3 rows or 3 columns — too small to measure anything
- password-protected files
- files over 20 MB — slow to process and nothing new is learned
- fifty variations of one invoice template — variety matters more than count

## How to send them

One zip per group, named `p2w-groupA.zip` through `p2w-groupD.zip`. Inside, keep the
original filenames — a name like `gst-invoice-3line-items.pdf` says what the file is testing
without opening it.

If a document is confidential, replace the names and amounts with made-up ones but keep the
**layout** identical. The layout is the test; the content is not.

## What will be done with them

Measure the current build on them first and report the numbers before changing anything.
Then fix, then measure again. A document that already scores 100 % is still useful — it is
the control that proves a fix did not break the easy cases.

Until they arrive, work continues on the existing corpus. Group A and Group B are the two
that would change what can be learned; Group C mostly adds coverage.
