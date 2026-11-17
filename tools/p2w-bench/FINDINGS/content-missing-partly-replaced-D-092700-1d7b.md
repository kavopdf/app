# content-missing-partly-replaced / D - blast radius of the firstX weld defect

Asked: how many documents in the benchmark corpus contain at least one table cell whose welded
       text was built from lines whose LEFTMOST visible x is more than 20 pt left of the FIRST
       line's visible x — and per document, how many such cells and on which page?

Claim: **6 of 213 documents**, 12 cells in total. Both first-line definitions (topmost line of
       the cell, and first line in document/content-stream order — the order the engine's loop
       actually sees) return the same 6 documents and the same 12 cells. The worst instance is
       the known one: `041122-Account_Opening_Form.pdf` page 7, where a cell takes its
       `firstX` from the right-aligned `Annexure-1` at x 513.6 while the cell also holds lines
       starting at x 46.3 — a 467.26 pt indent, which is the 28-line 58 pt column that
       `content-missing-partly-replaced-B` already measured.

**This is an APPROXIMATION, not the engine.** The engine was not built. A standalone PyMuPDF
harness (`/scratch/work/scan3.py`, nothing imported or ported from Java) re-implements
`PdfToWord.buildTables()` (PdfToWord.java:8535+) structurally: h-rules >= 12 pt, v-rules >= 6 pt,
grouping horizontal rules by >= 0.6 x shorter-overlap, rows from merged rule y's (1.6 pt),
columns = region edges plus v-rules crossing >= 50 % of the region, `band()` with its 1.5 pt
slack, cells keyed on the line's CENTER x, `firstX` from the first line the loop sees, cells
welded space-joined. What is approximated is only the two INPUTS: rules come from PyMuPDF
`get_drawings()` edges instead of the engine's own stroke collector, and lines come from
PyMuPDF text lines instead of the engine's glyph clustering. See over/under-counting below.

## (1) Corpus and population

    corpus path   /scratch/work/corpus
    PDFs scanned  213 of 213  (0 unreadable)
    composition   211 synthetic from release corpus-v1 (four zips: p2w-all-groups 53,
                  p2w-batch-1 80, pdf-to-word-test-corpus-v3 75, p2w-round2-additions)
                  + 2 PDFs from benchmarks/realworld/
    source        the clone does not carry the synthetic PDFs. INSTRUMENT.md names the corpus
                  as release `corpus-v1` on kavopdf/app; benchmarks/p2w.py:479 fetches exactly
                  those four assets with `gh release download`, which is what was done here.
                  All four assets downloaded; 213 reached, which is the corpus INSTRUMENT.md
                  declares ("213 total").

## (2) Documents with >= 1 such cell

    **6 of 213**  (12 cells across 7 pages)

    first-line = topmost   -> 6 docs / 12 cells
    first-line = flow      -> 6 docs / 12 cells   (same documents; only 330's worst differs)

    Of these 6, two are the same form: `041122-Account_Opening_Form.pdf` and
    `Account_Opening_Form_Fillable_filled.pdf` return identical numbers (2 cells, 467.26 pt,
    page 7). Counting them as one document, the answer is **5 independent documents / 10 cells**.
    Both numbers are given because the corpus genuinely holds both files.

## (3) The documents

| # | document | page | cells | worst x-diff (pt) | what the cell is |
|---|----------|------|-------|-------------------|------------------|
| 1 | 041122-Account_Opening_Form.pdf | 7 | 2 | 467.26 | right-aligned `Annexure-1` (x 513.6) welded with the centred title block (lines to x 46.3); second cell is the `Verification` block, heading at x 271.4 welded with body/notes to x 28.3 (243.1) |
| 2 | Account_Opening_Form_Fillable_filled.pdf | 7 | 2 | 467.26 | same form, same page, same two cells |
| 3 | bank-statement-5-pages.pdf | 1,2,3,4,5 | 1 per page (5) | 35.47 | right-aligned `STATEMENT OF ACCOUNT` (x 444.6) over a longer right-aligned subtitle (x 409.2); identical header on all five pages |
| 4 | 330_cad_drawing_sheet.pdf | 1 | 1 | 72.07 (top) / 135.0 (flow) | drawing-sheet dimension callouts — `N` at x 517.1 welded with `30000` at x 445.0 |
| 5 | balance-sheet-and-profit-loss.pdf | 2 | 1 | 48.50 | right-aligned `For and on behalf of the Board` (x 450.9) over a longer signature line (x 402.4) |
| 6 | 63_three_column_brochure.pdf | 1 | 1 | 23.24 | right-aligned `CROP 2024-25` (x 717.5) over `Price list and estate notes` (x 694.3) |

Reading of the population: the dominant real shape is **a right-aligned stack** — the first line
is the shorter one, so `firstX` is taken from its left edge and the paragraph is indented by the
difference. 4 of the 6 documents are that. Only the two bank forms reach the severity that
overflows a page. `330_cad_drawing_sheet` is the weakest case: the engine's own comment at
PdfToWord.java:8535 notes that a drawing sheet's frame produces spurious grids, and these are
dimension annotations rather than table content.

## (4) The exact command

    python3 /scratch/work/scan3.py /scratch/work/corpus top
    python3 /scratch/work/scan3.py /scratch/work/corpus flow      # first-line = document order

Corpus built with:

    gh release download corpus-v1 --repo kavopdf/app -p '<z>.zip' -O cache/<z>.zip --clobber
    for z in cache/*.zip; do unzip -oq $z -d x; done
    find x -iname '*.pdf' -exec cp {} corpus/ \;
    cp app/benchmarks/realworld/*.pdf corpus/

## Over- and under-counting

**Can over-count** — the rules are PyMuPDF drawing edges, not the engine's strokes. Filled
decorative rectangles contribute four edges here; the engine collects rules only from
`lineTo` segments (PdfToWord.java:6340-6352, `dy <= 0.8 && dx > 2`), so a filled box with no
stroke may or may not yield rules there. Measured sensitivity: restricting to stroked paths
(dropping `type == "f"` fills) drops the answer from **6 documents to 4** — it removes
`bank-statement-5-pages` and `63_three_column_brochure`, the two weakest instances. The 6 is
the figure quoted because a PDF `re` becomes moveTo + four lineTo in the engine's path
consumer, so rectangle edges do become rules there; the 4 is the conservative floor.
Also over-counted by the naive alternative method (below), and a cell that the engine would
drop as a non-table (`keep.size() < 2`) is already excluded here.

**Can under-count** — PyMuPDF line splitting is not the engine's glyph clustering, so a cell the
engine welds from several glyph runs may arrive here as more, shorter lines, or one line where
the engine had two; a cell whose lines agree in x under my extraction but not the engine's is
missed. `band()`'s 1.5 pt slack and the 1.6 pt row/column merge are reproduced but the y used is
the span origin, not the engine's line.y, so a line near a band edge can land in a different
cell. Rotated lines are dropped on both sides (the engine drops `ln.rotated` at :8542), so a
stamp's text is correctly invisible — but a page whose table rules are themselves rotated is
not measured. Finally the 20 pt bar is applied to MY cell geometry: the only ground-truth
instance available (`041122` p7) IS reproduced, but at 467.26 pt rather than the engine's own
number, so the per-document counts are trustworthy while the pt values are approximate.

## What I ruled out

- **The direct-pattern method the brief offers as the cheap alternative.** Clustering text lines
  into rows by y and splitting on x-gaps > max(9 pt, 1.1 x font size) returns 3 documents and
  **misses `041122` page 7 entirely** — it never forms a multi-line cell there, because
  clustering by y makes every text line its own row, while the engine's rows come from sparse
  drawn rules and can span a whole block. Its 3 hits were all artifacts: a logo monogram (`DP`,
  `K`, `M`) absorbed into a masthead because a 13-16 pt font inflated the gap threshold. The
  row-grid port is not optional; the pattern detector measures a different population.
- **Rotated stamp text.** `01_stamp_rotated_15deg_upright`, `43_red_stamp_over_black_text`,
  `05_round_company_seal_curved_text`, `07_stamp_over_table` and `305_vaccination_certificate`
  fired only under the naive detector. With `dir` checked and rotated lines dropped, they are
  clean. A stamp is not a table row.
- **That the defect is a real-world/bank-form problem.** Only 2 of the 6 are real-world; 4 are
  synthetic corpus members. The corpus can see this defect.
- **That the two bank forms are independent evidence.** They are the same form; the fillable
  variant returns byte-identical geometry. Count them once and the radius is 5.
- **That the 20 pt bar is picking up paragraph first-line indents.** Every one of the 12 cells
  was dumped and read by hand. None is a prose indent; all are vertically stacked lines that
  the engine's grid puts in one cell.
- **That the count is an artifact of one first-line definition.** Both definitions give the same
  6 documents and 12 cells.

## What would prove me wrong

1. **Build the engine and count `w:ind` against the source.** `java ConvertAll` on these 6 PDFs,
   unzip `word/document.xml`, and compare each table cell's `w:ind w:left` to the leftmost x of
   that cell's source lines. If the engine writes a correct indent on a cell I flagged, my rule
   extraction invented the region. This is the only test that settles it and it was not run —
   the brief said not to build the engine.
2. **A different rule threshold changes the set.** If the engine's `lineTo` test
   (`dy <= 0.8 && dx > 2`) admits segments my 0.6 pt tolerance rejects, or vice versa, regions
   merge or split. The stroked-only run already moved the answer 6 -> 4, so the count is
   demonstrably sensitive to exactly this input.
3. **A third first-line order.** The engine's `lines` list order is its own glyph-cluster order;
   I approximated it with PyMuPDF document order. If the real order differs, the borderline
   cells (23.24 and 35.47 pt) can cross the 20 pt line in either direction.
4. **The writer may clamp the indent.** If `DocxWriter` clamps `w:ind` to the column width, a
   flagged cell may not produce a visible defect — the cells exist, the damage may not. The
   question asked about cells, not damage.
5. **`330_cad_drawing_sheet` is genuinely ambiguous** and its worst value is mode-dependent
   (72.07 vs 135.0). If drawing-sheet dimension text is excluded as not-a-table, the radius is
   5 documents (or 4 independent).

## Not measured

- The engine's own per-cell `firstX` values — **not measured** (engine not built).
- Rendered page-count impact per document — **not measured**; only `041122`'s 9 -> 10 pages is
  known, and that comes from the sibling finding, not from this run.
- Whether `bank-statement-5-pages` and `63_three_column_brochure` are true positives under the
  engine's own rule collector — **not measured** (this is the 6-vs-4 sensitivity above).

Status: complete for the question asked; the count is an approximation and is labelled as one.
