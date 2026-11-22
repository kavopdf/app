# 18_displacement — the page-top gap, built and measured in Google. It fixes 55 pt and converts none of the 16.

22 Nov 06:54–07:20 IST. Engine at `6c6cf642e13b7ed2`. Every Google number below is a live round trip
(ConvertOne → `GOOGLEDRIVE_CREATE_FILE` as a Google Doc in `KavoPDF-Verify` → `EXPORT_GOOGLE_WORKSPACE_FILE`
as PDF → `verify_google.py`), probe deleted after use.

## The construct, and where it goes

`FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md` proved with a five-variant controlled probe
that Google **drops `w:spacing w:before` on the first paragraph of a page** (55.15 pt asked, 0.33 pt rendered)
and **honours a 1×1 `w:trHeight w:hRule="exact"` row in the same position** (55.83 pt of 55.15 asked).

That construct is now written, as `DocxWriter.topGapRow(sb, gapTw)`, emitted immediately before the first
paragraph of a page. The paragraph then writes `w:before="0"`. `beforeTw` keeps its value for `fitPage`,
`resync`, `traceLine` and `shaveToFit`, so the page's measured height and every page break are unchanged —
`spacingTw` already sums `w:trHeight` at any depth. The change is flow-neutral **by construction**, and
LibreOffice's page count confirmed it (5 pages before, 5 after).

It has to be written in **two** places: `flowFromBox` (:4335) and `flowRow` (:3453). `bank-statement-5-pages`
opens every page with a *row* of fields, so a patch to `flowFromBox` alone changed nothing at all — the file
came out byte-identical and the trap is easy to fall into.

**The guard is the whole difference between a fix and a regression.** The row may only be written where the
page was opened by a break:

    if (TOPGAP_ROW && (ctx.pageNo > 1 || ctx.brokePage > 0)) topGapRowTw = beforeTw;

Without it, a table becomes the first element of `<w:body>`, and Google charges about 15 pt for that: on
`bank-statement-5-pages` page 1's first line went 44.1 → **59.0**, page 1 overflowed, a **blank page 2**
appeared, the document went 5 → 6 pages and the score went 42/47 → **38/47** with `17_matched_runs` 585 → 220.
Page 1 does not need the construct at all: with no preceding page break Google honours its `w:before` (44.1
against a source first line at 45.6).

## Measurement — `bank-statement-5-pages`, 5 pages, Google

| | before (HEAD) | after (row, pageNo>1) |
|:--|:--|:--|
| `verify_google.py` | **42/47** | **45/47** |
| page count | 5 | 5 |
| first line y, p1 | 44.1 | 44.1 |
| first line y, p2–p5 | **−11.0** (above the paper) | **44.5** |
| text-matched median dy, p2–p5 | **−59.5 pt** | **−4.0 pt** |
| lines out at 4.5 pt, p2–p5 | 109 of 109 | 67 of 109 |

Source first line is at 45.6. The 55 pt uniform lift is gone and the residual is a separate, pre-existing
−4 pt that page 1 has too (−4.3), i.e. it is not the page-top construct.

`25_invisible_text` reads 2 → 10 and this is **not** a regression: the eight extra runs are the same
white-on-white "HDFC BANK / STATEMENT OF ACCOUNT" header text on pages 2–5, which the check could not count
before only because those runs sat at y = −11, outside every fill rect. The check fails in both states
(2 > 0 and 10 > 0); no check flipped PASS → FAIL.

## The decisive negative: none of the 16 can be fixed this way

`18_displacement` is worth 38.7 clean documents and 16 documents fail it **alone** at 41/42. Every one of
those 16 is **ONE PAGE**:

    16_right_aligned_amounts_txtpos   1 page     362_price_list_dense            1 page
    22_invoice_four_columns_txtpos    1 page     41_coloured_headings_white_bg    1 page
    29_dot_leaders_txtpos             1 page     68_journal_wide_table_spanning   1 page
    31_times_body_arial_headings      1 page     71_invoice_space_aligned_no_rules 1 page
    72_bank_statement_no_rules_right_amounts 1 page   73_marksheet_subject_marks_grade 1 page
    balance-sheet-two-columns-of-figures     1 page   bus-timetable-station-left-times-right 1 page
    insurance-policy-schedule         1 page     mobile-bill                      1 page
    table-with-no-header-row          1 page     two-tables-stacked-with-no-gap    1 page

A one-page document has no page break, so it keeps its `w:before` and the construct never fires. **If this
works, zero documents become clean** — so it cannot be the fix for this class, whatever its leverage.

Three of the 16 were re-converted at HEAD and taken through Google to find out what their displacement
actually is. All three: **41/42, failing `18_displacement` alone.** Three different mechanisms:

| document | dy profile | mechanism |
|:--|:--|:--|
| `16_right_aligned_amounts_txtpos` | +0.2 at the top → −7.0 at the bottom | accumulation, ~0.13 pt/row |
| `362_price_list_dense` | −3.5 at the top → −19.4 at the bottom, non-monotone (−3.5 → −10.8 → −14.6 → −18.7) | accumulation plus discrete steps |
| `68_journal_wide_table_spanning` | 0.0 down to y=185, then **−114.8 for everything below** | one block displaced as a whole |

`68` is the cheapest of the three: a single block jump of 115 pt is one construct, not a ramp.

## Where the drift probably is, from the emitted XML of `362_price_list_dense`

    w:line="8" w:lineRule="exact"   253 of 258      (hairline, mark 11 pt outside / 10 pt in cells)
    w:trHeight w:val="168" w:hRule="atLeast"  28 of 29 rows;  one row at 240
    every one of the 260 cells holds exactly ONE <w:p>

`w:trHeight ... hRule="atLeast"` (`DocxWriter.table()` :6317) is the only per-row length whose *rendered*
height Google decides for itself: it may grow the row to its content's line box, which is the substituted
face's box and not the PDF's. The cheapest discriminating experiment needs no build — take the emitted
`.docx`, change `w:hRule="atLeast"` to `"exact"` on the 29 rows, upload, re-run the dy census. LibreOffice
is a built-in control on the same file.

## What the next run should do

1. **Do not spend a slot enabling the page-top row for `18_displacement`.** It is real and it is worth
   having — every multi-page document in the corpus carries the 55 pt lift — but it converts none of the 16.
   The patch is `patches/PATCH-topgap-row-MEASURED-0654.patch`; it applies to `6c6cf642e13b7ed2`, is gated on
   `-Dp2w.topgaprow=1`, and needs a **full corpus pass** before it lands. Two slices of `p2w.py --force` were
   spent getting 168 of 213 `.docx` converted and the pass was abandoned for slot time, not for evidence.
2. **Work `68_journal_wide_table_spanning` first.** A −114.8 pt block jump on one page is one construct.
3. **Then the `atLeast` experiment** on `362_price_list_dense`, which is one `sed` and one round trip.
4. A round trip is ~90 s a document, not the 4 min the 05:45 finding recorded, once the export is collected
   from the `artifacts[0].workspace_path` the export call returns.

Status: construct measured, no engine change landed (reverted to HEAD so the tree is the engine the tables
describe). Outcome `lead`.

## Reconciliation with the 07:14 relay, and why its 6-page result and mine differ

The relay measured the same construct unguarded and got 6 pages / 33/42 where I got 5 pages / 45/47.
**Both are right; the difference is the guard.** Their variant put the row on every page including
page 1, which makes a table the first element of `<w:body>`; Google charges about 15 pt for that,
page 1 overflows, a blank page 2 appears and `17_matched_runs` collapses (585 → 220 on my run). With
`ctx.pageNo > 1 || ctx.brokePage > 0` the row is written only where a page break opened the page, and
the document stays at 5 pages. The two runs agree on everything else and their check counts differ
only because I passed `--docx` to `verify_google.py` (47 checks) and they did not (42).

**And their table-top-spacer lead is corroborated by my independent dy census.** I measured
`68_journal_wide_table_spanning` at HEAD through Google: dy is 0.0 down to y=185 and then **−114.8 pt
for every line below**. The relay's candidate is a 144.0 pt spacer at `DocxWriter.java:5869-5881`
that Google may charge at 13.74 pt — a −130.3 pt error on exactly that block. Same sign, same order,
same block boundary. That probe is the cheapest thing in the class and should be the next run's first
call: an empty `<w:p>` with `w:sz=2` and `w:line="2880" w:lineRule="exact"`, one Drive upload, and
read the y back.
