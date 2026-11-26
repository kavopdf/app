# Page-scale displacement is an unearned page break: the block is 97 % of the page and rows can grow

**26 Nov 2026, relay slot 14:18.** Read from the emitted `word/document.xml` of the eight documents with
the largest `worst_dy` in the corpus. No Drive calls, no engine change.

## What the writer actually does

It never lets a table flow across a page and trust the renderer. Every source page is a hand-built
block — furniture paragraphs, then one table fragment, then spacer paragraphs — terminated by a
one-twip paragraph carrying `<w:br w:type="page"/>` (`DocxWriter.java:690 breakPage()`). `w:pgMar` is
zero on all four sides and there is one `sectPr` per file, so no section break ever makes a page.

Two structural facts hold in every table of all eight documents:

- **every** `w:tr` carries `<w:cantSplit/>` — a row can never be cut, only moved whole;
- **every** `w:trHeight` is `w:hRule="atLeast"` with a value far below a page (max 380 twips = 19 pt
  against 16 838 twips of usable height), so no row forces a break by its declared size;
- `w:tblHeader` appears **zero** times. A table that spans a page does not repeat its header; the
  writer ends the table, writes the footer paragraph, writes the break carrier, and opens a *new*
  `w:tbl` whose first row is the header copied in as an ordinary data row.

## The numbers that make it a defect

| document | worst_dy | block stack vs 16 838 tw usable | `w:before` > 1000 tw |
|:--|--:|:--|--:|
| `very-long-single-column-table` | 656.7 | 16 330 (**97 %**) × 3 pages | 6 |
| `table-across-page-break-repeated-header` | 401.3 | 16 330 (97 %) × 3 | 3 (max 13 181 tw = 659 pt) |
| `bank-statement-5-pages` | 355.4 | 16 331 (97 %) × 5 | 10 |
| `gst-invoice-multipage-item-table` | 168.3 | 16 330 (97 %) × 4 | 9 (max 10 441 tw = 522 pt) |
| `341_shipping_manifest` | 222.7 | 11 507 of 11 906 landscape (97 %) | 1 |
| `330_cad_drawing_sheet` | 161.6 | 11 429 of 11 906 (96 %) | 3 |
| `324_loan_amortisation_schedule` | 357.8 | 11 823–12 103 (70–72 %) | 0 |
| `601_fillable_admission_form` | 230.4 | 10 323 (61 %) | 1 |

Five of the eight are placed at **97 % of the usable height with about 25 pt of slack per page.**

## The mechanism

A row is `atLeast` + `cantSplit`. The renderer is entitled to make it taller than the writer counted —
a cell that wraps to one more line grows the row, and the file's own note at `DocxWriter.java:6358` says
the row's border-box is `max(w:trHeight, cell content height + rule width)`. Once the content plus the
rules eats the ~25 pt of slack, the stack no longer fits, so the renderer breaks the page **before**
the writer's own break. The explicit `<w:br w:type="page"/>` then falls on a page that has already
started, and the whole following block — the footer spacer with its 522–659 pt `w:before`, the next
table fragment, everything — lands one block late. That is a displacement measured in hundreds of
points, which is exactly what these 17 documents show.

It also explains the two facts that made this family look impossible: the **page count stays right**
(the number of hard breaks is correct — 2, 2, 6, 4, 3 in the five multi-page files — only their
*position* is trusted rather than earned), and the **median line does not move** (the error is
per-page, not per-line, so most runs on most pages pair correctly).

## What this forbids, and what it licenses

- **Forbidden:** any per-line or per-row-height construct aimed at these documents. The rows are not
  accumulating error; the page break is in the wrong place.
- **Licensed, three candidates, cheapest first:**
  1. **Emit `w:hRule="exact"` on cell rows** so the renderer cannot grow them past what the writer
     counted. The row's height then cannot exceed its declaration, the 25 pt slack stays slack, and the
     explicit break is where the writer put it. Risk: a cell whose text genuinely wraps is clipped —
     so this must be measured on the five 97 % documents first, one document at a time.
  2. **Reserve slack** — place blocks at 94–95 % instead of 97 % so row growth cannot consume the fit.
     This is a placement change and it moves every line on the page, so it must be measured on the
     line-scale family too before it is believed.
  3. **Make the break earned rather than declared**: drop the explicit `w:br` on a page whose stack is
     over ~95 % and let the renderer break, then verify the page count still matches. Cheapest to
     falsify, because `00_page_count` is already measured for every document.

## Falsifier

Take `bank-statement-5-pages` (five pages, every block at 97 %, worst_dy 355.4, med_dy −55.0). Emit
`hRule="exact"` on its cell rows only, convert, upload, export and collect. If the mechanism is right,
`worst_dy` should fall below 100 pt and `18_displacement` should either pass or move to the line-scale
family; if `worst_dy` does not move, the break is not being pushed by row growth and candidate 1 is
refuted for the whole family at the cost of one document.
