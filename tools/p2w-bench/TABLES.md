# Table accuracy — the metric that decides whether a conversion is usable

Tables are why people convert a PDF to Word. A wrong table means retyping the whole
document, so this is the benchmark to hold first, not last.

    python3 tools/p2w-bench/score_tables.py <folder-with-.docx>

Reference is pdfplumber's table extraction. Ours is the tables in the .docx. A reference
row counts as found when 95% of its words appear together in one of our rows.

## The reference must be validated first

pdfplumber returns a grid of empty cells wherever a logo, a QR code or a few stray glyphs
sit. Scoring against that penalises a correct conversion: `201_gst_invoice_logo_qr` was
marked **0%** while our output was perfect -

    ours:      ['#', 'Description of service', 'SAC', 'Qty', 'Rate', 'Taxable value']
               ['1', 'Warehouse handling charges - Pune', '996812', '1', '84,500.00', '84,500.00']
    pdfplumber: ['', 'e', '3', '', 'f', '2', 'a', '', '', '', '', 'b', 'c']
               ['', '', '', '0', '', '2', '', '', '', '', '', '', '']

A reference table is now kept only when at least half its cells are filled and it has six
or more filled cells. That is the difference between 87.09% and 90.98% on rows - and the
earlier figure was the wrong one.

## Floor at KavoPDF 3.46.5, 52 files with tables

    table count match    44/52   = 84.62 %
    table ROW accuracy  736/809  = 90.98 %
    table CELL accuracy 4914/5124 = 95.90 %

Earlier figures of 98.89% rows and 99.80% cells came from a different, laxer scorer. They
were not wrong for what they measured, but they did not measure this.

## What the failures actually are

Not wrong cells - **missing tables**. The rows are present in the document as paragraphs,
so nothing is lost, but the user has to rebuild the table by hand.

`314_tender_rfp_boq` - pdfplumber finds two tables, we find one. Table 0 matches exactly.
The 11-row bill of quantities is missing; "Earthwork in excavation in ordinary soil" is a
paragraph in our output.

`326_itr_computation` - pdfplumber finds two tables, we find one. Our table is actually
BETTER than the reference (we keep the `Amount (INR)` column pdfplumber dropped), but the
tax-slab table is missing; "3,00,001 to 6,00,000" is a paragraph.

## Where to look next

`buildTables` returns early when a page has fewer than two horizontal or two vertical
rules. That is not the cause here - the tender page has 18 horizontal and 79 vertical
rules - so the table is being detected and then dropped or merged. Instrument `findTables`
and the weak-table rejection on `314_tender_rfp_boq`, which has both a matching table and
a missing one on the same page.

## Worst files

    0.0%  129_rotated_table_on_portrait     (6 rows)
    0.0%  205_land_record_devanagari        (5 rows)
    0.0%   54_rtl_table_arabic              (4 rows)
   30.8%  383_api_docs_page                (13 rows)
   35.3%  314_tender_rfp_boq               (17 rows)
   47.4%  326_itr_computation              (19 rows)
   60.0%  202_bilingual_hindi_english_form (5 rows)
   60.5%  200_bank_statement_multipage     (38 rows)
   61.5%  333_datasheet_spec_tables        (26 rows)

## Root cause found (instrumented 3.46.5)

`314_tender_rfp_boq`, with prints at each stage:

    TBL cells=12 rows=6   medH=16.0     <- the summary table
    TBL cells=66 rows=11  medH=15.0     <- the bill of quantities
    CONT rows=6  containsAnother=false
    SOLID rows=6 inside=12 covered=12 pct=100
    CONT rows=8  containsAnother=false
    SOLID rows=8 inside=24 covered=24 pct=100
    BLOCK table rows=6  top=136
    BLOCK table rows=8  top=1003       <- off the page

Both tables are detected, both survive the contains-another filter, both pass the 60%
coverage rule, and **both reach `page.blocks`**. So nothing in the table logic loses them.

The second table is dropped in `DocxWriter.table()`:

    int cols = 0;
    for (List<String> row : t.rows) cols = Math.max(cols, row.size());
    if (cols == 0) return;              <- silently skipped

Its cells are empty, and they are empty because **`top=1003` on a page that is 842 pt
tall**. The table sits outside the page, so no glyph falls inside any of its cells and
every cell is the empty string.

So this is not a table-detection bug and not a rejection-rule bug. It is a **coordinate
bug**: the cells for the lower half of this page are placed with a y that was never
flipped back into page space. Fix that and the bill of quantities comes back, along with
every other table that sits low on a page.

Where to look: `cellsToTables` returns cell rectangles built from `intersectionsToCells`
on edges whose y came through `mergeEdges`. Compare the y of a cell on the lower half
against `pageH` - the first table's `top=136` is sane, the second's `1003` is not.

Also worth doing regardless: `DocxWriter` should not silently skip a table. A table with
no text is a bug worth seeing, not hiding.
