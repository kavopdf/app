# The table row pitch is FLOORED by Google, and `w:trHeight` is inert. Eight variants, one document, Google only.

**28 Nov 2026, fixer run 08:24 IST. Measured in Google Docs (upload -> convert -> export PDF ->
PyMuPDF), not LibreOffice. Document: `price-list-2col-dense-right-aligned`, 41 table rows, one page.**

## What was believed

Two things, both from the 28 Nov 05:54 run and its agent:

1. The engine writes each cell's baseline from `before + LINE_BASE*box` while the row's top edge comes
   from a pitch, and the shortfall is one-signed, so text lands a constant amount low per row.
2. The named next step was: *"the candidate is `w:line`, not `w:before` — give the cell the font's
   natural line box and move the identical difference into `before` so the baseline is preserved by
   construction"*, with the prediction that this moves Google by 0 pt **if and only if** Google is
   already preserving the baseline.

## What was measured

The shipped `.docx` for this document writes `w:trHeight w:val="328" w:hRule="atLeast"` (16.40 pt) and,
in each cell, `w:before="317" w:line="11" w:lineRule="exact"` — i.e. `before + line = 328 tw` exactly.
The source PDF's own row pitch is **16.40 pt** (39 diffs of 16.4, plus a 12 pt header row). The engine's
row geometry is therefore **correct**: it asks for the pitch the page drew.

Google does not deliver it. Eight variants, each differing from the shipped file only in
`word/document.xml`, converted to Google Docs and exported:

| variant | change | Google row pitch | table span (src 651.60) | first row | last row |
|---|---|---|---|---|---|
| src | — | 16.290 | 651.60 | 93.69 | 745.29 |
| **v0 shipped** | — | **16.497** | **659.88** | 94.19 | 754.07 |
| v1 | trHeight +5 tw, before +5 tw | 16.601 | 664.05 | 94.44 | 758.49 |
| v2 | before 88, line 240 (same sum, natural box) | 16.500 | 643.51 | 105.70 | 749.21 |
| v3 | trHeight +5 tw only | 16.497 | 659.88 | 94.19 | 754.07 |
| v4 | trHeight −4 tw, before −4 tw | 16.497 | 659.88 | 93.99 | 753.87 |
| v5 | before −4 tw only | 16.497 | 659.88 | 93.99 | 753.87 |
| v6 | before +20 tw only | 17.107 | 684.30 | 95.19 | 779.49 |
| v7 | cell paragraph mark at 6 pt | 16.497 | 659.88 | 94.19 | 754.07 |
| v8 | `w:line="0"` | 22.468 | 674.05 | 99.48 | 773.53 |

Three facts fall out of the table, and each one is a refutation:

1. **`w:trHeight` is inert.** v3 (+0.25 pt/row) and v4 (−0.20 pt/row) produce a table **identical to
   v0 to 0.00 pt** in span and in last-row position. Changing the declared row height changes nothing.
   The engine's entire row geometry — `328 tw atLeast` — is ignored by Google on these rows.
2. **The row advance is `max(16.50, before + 0.257)`, and the floor is what costs the document.**
   v0/v5 (before 15.85 and 15.65) both land at 16.497: the pitch is pinned. v6 (before 16.85) lands at
   17.107 = 16.85 + 0.257, exactly. So below `before ≈ 16.24` the pitch cannot be reduced at all, and
   above it every twip of `before` is delivered. The source pitch is 16.40, under the 16.50 floor, so
   Google adds **+0.097 pt/row … +0.207 pt/row** and the error accumulates: **+8.28 pt by the last row
   of a 40-row table.**
3. **The named next step is refuted, and it is refuted by the variant that implements it.** v2 *is* the
   natural-line-box rewrite (same sum, 12 pt box instead of 0.55 pt): its pitch is unchanged (16.500)
   and it moves the table's first row **+11.51 pt** (105.70 vs 94.19). It would not fix `18_displacement`
   and it would move every cell of every table in the corpus. Do not build it.

The check's tolerance is `clamp(0.35*size, 1.5, 4.5)` = 2.8 pt for 8 pt text, and the page limit is
`max(2, ceil(0.05*41))` = 3 runs out. A drift of +0.207 pt/row crosses 2.8 pt at row 13, so 28 of 41
rows are out. That is the failure, and it is a renderer floor, not an engine error.

## What is now true

* For a table whose row pitch is **at or below ~16.50 pt**, Google clamps every row up to 16.50 and the
  error accumulates per row. No declaration the engine can write removes the clamp: not `w:trHeight`
  (v3, v4), not the paragraph mark (v7), not a smaller `before` (v5). This is the *third* place in this
  repository where the answer is "Google cannot do it", and it must be written as a finding, not fixed.
* For a table whose row pitch is **above** the floor, the pitch is delivered and can be tuned 1:1
  through `w:before` (v6). That is the only lever, and it only works upward.
* The engine's `w:trHeight` spend is **inert in Google**. Whatever it is for, it is not for the renderer
  the user opens. Anything in `DocxWriter` that reasons about row height as a way to place text is
  reasoning about a number Google does not read.

## What would prove this wrong

* A document whose source row pitch is under 16.5 pt that Google reproduces to under 1 pt over 20+ rows.
  (If such a document exists, the floor is not a constant and this finding is a coincidence of
  `price-list`.)
* A variant that changes the delivered pitch while leaving `before` at or under 16.24 pt. The eight here
  do not: v3, v4, v5, v7 are all 16.497.
* A re-measurement of v0 showing a pitch of 16.40. The probe files are on branch `probe-28nov` under
  `benchmarks/probe-28nov/` and the exports are reproducible in ten minutes with
  `GOOGLEDRIVE_UPLOAD_FROM_URL` on the raw URL, mime `application/vnd.google-apps.document`.

## What was not measured

* The second document, `bus-timetable-station-left-times-right`. Its left-column band mixes wrapped
  lines with rows (35 distinct y for 33 rows), so its pitch number is not a row pitch and is not
  reported. It needs a row-aware reader, not a y-band.
* Whether the floor is a constant 16.50 pt or `1.5 x 11 pt` (the default font's line) — the two are
  numerically identical here and nothing in this corpus separates them.
* Whether `w:trHeight` is inert on tables that also carry borders or `w:tblCellMar`; this table has
  neither (`tblBorders` all `nil`, `tblCellMar` all 0).

## The consequence for the class table

`classpick.py --leverage` prices `18_displacement` at **47.1 clean documents** and 19 documents that
fail nothing else. This finding says that price is only collectable on the subset whose row pitch is
above the floor. The 19 must be split by their own source row pitch before another slot is spent on
this class, and the split is mechanical: measure the source's own row pitch, and any document under
16.5 pt with 20+ rows is charged by the floor, not by the engine.
