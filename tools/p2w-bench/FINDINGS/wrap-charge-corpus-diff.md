# THE WRAP CHARGE, MEASURED ON THE WHOLE CORPUS — 42 of 213, and it regresses

Asked (HANDOFF, carry-over): do the corpus diff on the wrap charge before measuring a single
document — it touches every ruled table, not four documents. The answer decides whether it fits
in a slot at all. If it is most of the corpus, that is a ratchet job, not a fixer slot.

Answer: **42 of 213 documents change (20 %), 400 rows, and not one document's docx page-break
count moves.** It fits in a slot. It was measured, and it must not be kept: the documents it
touches are not the class it was aimed at, and on the ones where it fires hardest it turns a
clean document into a spilled one.

## What was built (patches/wrap-charge-helvetica.patch, 251 lines, applies to 76f01b2)

Exactly the mechanism the handoff named, in `DocxWriter.table()`:

- a Helvetica advance-width helper, `PDType1Font.HELVETICA / HELVETICA_BOLD` (standard-14 AFM
  metrics PDFBox ships; measured in this sandbox: `"Hello"` = 2278/1000 em, 828 characters of
  prose = 377.4 em);
- each cell's text split on its own `\n` paragraph breaks, every paragraph charged
  `ceil(textWidth / (spanTw - insetTw))`, with the span taken from the page's own cell
  rectangle and the inset from `insetTw()` — the same two numbers the cell writer uses;
- the row charged `max(declared rowHeightTw, wrapped lines x rowLineTw)` and written into
  `w:trHeight` with `hRule="atLeast"`, i.e. a floor;
- the charge is taken BEFORE `writtenRowsTw` is accumulated, so the page budget sees the row
  the renderer will lay out.

Two corrections were needed to get even this close: the inset-overflow correction the cell
writer already makes (`inset = spanTw - ceil(textR) - 20` when the page's own text is wider than
the room its inset leaves), and a cast that the first build got wrong. Without the first, 43
rows of `price-list-right-aligned-amounts` read as two lines.

## The corpus diff

    A = engine at 76f01b2, 213 documents converted (81 s)
    B = same engine + the wrap charge, 213 documents converted (90 s)
    diff on word/document.xml, entry by entry

    documents differing      42 of 213   (20 %)
    rows whose w:trHeight changed   ~400
    docx page-break changes   0 in every one of the 42

Top movers by rows changed: `price-list-2col-dense-right-aligned` 40 of 41 rows,
`price-list-right-aligned-amounts` 38 of 38, `041122-Account_Opening_Form` 33 of 87,
`Account_Opening_Form_Fillable_filled` 33 of 87, `72_bank_statement_no_rules_right_amounts`
18 of 18, `03_stamp_vertical_90deg` 17 of 19, `22_invoice_four_columns_txtpos` 16 of 16.

## What it does to the numbers (measured, both directions, same code, same sandbox)

| document | before (A) | after (B) | pages A -> B |
|---|---|---|---|
| `price-list-right-aligned-amounts` | **1.79** | **81.15** | 1 -> 2 |
| `price-list-2col-dense-right-aligned` | **2.69** | **81.69** | 1 -> 2 |
| `01_stamp_rotated_15deg_upright` | 0.0 | 9.3 | 1 -> 1 |
| `03_stamp_vertical_90deg` | 16.98 | 23.19 | 1 -> 1 |
| `041122-Account_Opening_Form` | 99.02 | could not be rendered within a 280 s call | 11 -> ? |

`share5` is `p2w.measure_doc`'s worst-page share at 5 px, both builds measured by this run.

**The two price lists are the finding.** Both are dense right-aligned ruled tables whose only
defect on the page is alignment: 1.79 and 2.69, i.e. nearly clean. The wrap charge reads the
amount column as needing two lines (row `w:trHeight` 312 -> 440 or 624 tw, i.e. 1.4x and 2.0x),
doubles 38 of 38 and 40 of 41 rows, and the table spills its page. The page's own pitch is the
truth there; the charge is not.

**041122 does not move where it was supposed to.** In the first build (before the inset
correction) the target document rendered 11 pages at share5 99.02 on both sides — the charge
changed 42 rows and nothing else. After the correction, the B version of that document takes
longer than 150 s for soffice to lay out and did not finish inside `measure_doc`'s deadline,
so its after-number is unmeasured. Whatever the charge is doing there, it is not the +28 pt on
one row the earlier run described: it is a cascade across 33 rows of a 24-row table plus the
page-fit squeeze the larger charge triggers (`writtenRowsTw` grows, `ctx.squeeze` shrinks every
row of the page, which is why 540 tw rows read 519 tw in the same file).

## Ruled out

- "It is most of the corpus, so it needs a ratchet run": **no** — 42 of 213, 20 %, and zero
  page-break changes in the .docx. The blast radius is slot-sized.
- "It closes 041122": **no** — measured, it does not; the document was 11 pages before and the
  charge does not make it 10.
- "It is neutral elsewhere": **no** — it costs two documents 79 points each and spills both.

## What would have to be true for this to be keepable

The charge has to fire only where the RENDERER wraps, and the renderer wraps on the width it is
given, not on the width the page's inset implies. A gate on the rendered width (the cell's own
`w:tcW` less the inset actually written, compared against the Helvetica advance of the whole
paragraph) would leave both price lists alone — their text fits the cell the writer emits. The
number that then still needs closing on 041122 is the one the writer's page budget does not see:
nine paragraphs charged as nine line boxes when the render draws thirteen. That is a paragraph
count, not a width, and the wrap charge conflates the two.

Patch kept at `patches/wrap-charge-helvetica.patch`. Engine at HEAD (reverted). No engine change
is carried by this run.

## Second build: the same charge with a 4 % metric tolerance (patches/wrap-charge-gated-1.04.patch)

The first build's spurious wraps were blamed on the Helvetica/DejaVu mismatch (a few per cent),
so the charge was gated: a paragraph is one line unless the Helvetica advance exceeds the
available width by more than 4 %. Rebuilt, re-converted all 213, re-diffed:

    documents differing      41 of 213   (was 42)
    rows whose w:trHeight changed   ~370
    docx page-break changes   0

`price-list-right-aligned-amounts` drops from 38 changed rows to 16 — but the rows that remain
still go 312 -> 440 tw, i.e. exactly two lines at its 220 tw row line. So the excess there is
not a few per cent of a metric mismatch: some cell in that table is being measured against a
width the renderer never uses, and the tolerance does not reach it. The gate is therefore not
the fix either, and this build was not measured (no time in the slot for 41 documents both
ways) and was reverted with the first. Both patches are kept; the engine is at HEAD.

What the next run should read first: the 312 -> 440 rows. Pull the emitted `<w:tc>` for row 0
of `price-list-right-aligned-amounts` out of `outA` (the .docx this run converted, 213 files,
in `/scratch/work/p2w/outA` on the run's pod) and compare its `w:tcW`, `w:ind` and cell text
against what `wrappedRowLines` computes for it. The answer is in that one row.
