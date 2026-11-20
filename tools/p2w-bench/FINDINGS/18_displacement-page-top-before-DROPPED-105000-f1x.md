# 18_displacement / PROBE - Google DROPS w:before at the top of a page, and a 1x1 table row is the construct it does honour

Asked: why does the same .docx put a page's whole text block 48-68 pt HIGHER in Google Docs than
       in the source PDF, while LibreOffice puts it where the source did? Two agents named the
       table-spacer paragraph as the suspect. This probe tests that and finds the real construct.

Claim: **`w:before` is DROPPED ENTIRELY by Google Docs on the first paragraph of a page.** The
       engine carries a page's top gap (the distance from the paper edge to the first line) as
       `w:spacing w:before="<gap>"` on the first paragraph after `<w:br w:type="page"/>`.
       LibreOffice honours it; Google renders the line at the paper's top edge instead. That is
       the uniform upward shift - constant in points, header included, magnitude equal to that
       page's own top gap.
       **The construct Google does honour, at the top of a page, for a length in points, is a
       single-cell table row with `w:trHeight w:val="G" w:hRule="exact"`.** Measured: 55.83 pt of
       the 55.15 pt asked, against 0.33 pt for `w:before`.

Evidence - controlled probe, one hand-built .docx, five variants, each on its own page, gap asked
1103 twips = 55.15 pt, `w:pgMar` all zeros, page height 16838 twips. Marker is the word TOPx.

| variant | construct carrying the 55.15 pt page-top gap | LibreOffice y | Google y |
|---|---|---:|---:|
| TOPA | `w:before="1103"` on the first paragraph after the page break | 56.80 | **0.33** |
| TOPB | empty paragraph, `w:line="1103" w:lineRule="exact"`, mark `w:sz=2` (1 pt) | 56.80 | 12.22 |
| TOPC | empty paragraph, `w:line="240" w:lineRule="auto"`, mark `w:sz=1103` (55.15 pt) | 752.80 | 589.08 |
| TOPD | 1x1 `w:tbl`, `w:trHeight w:val="1103" w:hRule="exact"`, then the text paragraph | 56.80 | **55.83** |
| TOPE | `w:before="1103"` + `w:line="240" w:lineRule="auto"`, mark 55.15 pt | 807.90 | 589.08 |

Reading it:
  - TOPA is the defect. LibreOffice places TOPA at 56.80, the gap it asked for. Google places it at
    0.33 - the top edge. The whole 55.15 pt is gone, and everything under it moves up with it,
    header included. **That is the shape the dy census reports**: uniform, constant in points, not
    proportional to type size, and equal to the page's own top gap.
  - TOPB shows the table-spacer construct is NOT a fix: Google reads `w:line` as a multiple of the
    paragraph mark's line height, so 1103 twips asked buys 11.89 pt - 21.6 % of the gap. This is
    the mechanism REMAINING-DEFECTS.md already recorded.
  - TOPD is the fix. Both renderers read `w:trHeight ... hRule="exact"` as a length in twips at
    the top of a page: LibreOffice exact, Google 0.97 pt short.
  - TOPC and TOPE show that an `auto` line box is not a length either - it is a multiple of a face's
    line height, and both renderers scale it by their own face metrics. Unusable for placement.

Corroboration on the real corpus, unpatched engine, `bank-statement-5-pages`:
  - first paragraph after each page break is emitted as
    `<w:spacing ... w:before="1103" w:after="0" w:line="13" w:lineRule="exact"/>`
    (word/document.xml, immediately after `<w:br w:type="page"/>`) - 1103 twips = 55.15 pt.
  - measured dy on that document, Google, per page: p1 -56.9, p2 -57.1, p3 -57.1, p4 -57.1 pt.
    The page's own top gap is 55.15 pt. The two numbers are the same number.

Ruled out, with measurement:
  - **the table-spacer paragraph** (DocxWriter ~line 5826, the construct two agents named).
    bank-statement-5-pages carries 9 spacers totalling 81.0 pt across 5 pages, max 16.2 pt per
    page - at most 16 pt against a 57 pt shift, and in the wrong place. Applied anyway and
    measured: moving the gap from `w:line` into `w:before` took GOOGLE from 40/47 to **36/47**
    (worse; `27_text_off_page` 0 -> 12 as the added space overflowed the page) with LibreOffice
    unchanged at 47/47. Reverted.
  - the general per-line `w:line ... lineRule="exact"` path: TOPB/TOPD show `w:line` exact is
    honoured exactly by LibreOffice, so it cannot be the source of a LibreOffice-passes /
    Google-fails split; and where Google mis-reads it the error is a fraction, not 57 pt.
  - page margins: `w:pgMar` is all zeros and both renderers honour zero. Not the lever.

How to test it: in the flow's page-first path (`DocxWriter.spacing(..., pageFirst)` and the caller
that sets `pageFirst`), when a paragraph opens a page, emit the gap as a 1x1 table row with
`w:trHeight w:val="<gapTw>" w:hRule="exact"` immediately after the page break and set that
paragraph's `w:before` to 0. Then:
    python3 benchmarks/p2w.py --force          # rebuild the corpus
    bash tools/p2w-bench/screen.py --class "18_displacement"
and confirm with the Drive round on `bank-statement-5-pages` - its p1-p4 dy must go from -57 to
inside the clamp(0.35 em, 1.5, 4.5) pt tolerance. Do NOT judge it on LibreOffice: LO already
places TOPA correctly, so LO cannot see this fix at all. It is a Google-only change.

Confidence: high for the mechanism (a controlled probe, one variable, both renderers, five
variants, and the 57 pt matches the emitted 1103 twips on a real document). Medium for the fix
being sufficient: the probe proves the construct, not that every page-top gap in the corpus is
emitted the same way. Some pages may open with a table rather than a paragraph, and a table's first
row is already a row.

Scope of the measurement: 1 probe document (5 pages) + 1 corpus document (5 pages) through Google,
plus 3 corpus documents through LibreOffice for the regression side.

Status: complete

## Second result, 20 Nov: the construct swap fixes the displacement but overflows the page

The construct was applied to a REAL document by hand - `bank-statement-5-pages`, the four
page-top `w:before` gaps replaced with 1x1 `w:trHeight hRule="exact"` table rows and each
paragraph's `w:before` zeroed - and measured through Drive. No engine code was touched.

  LibreOffice   5 pages, first line of every page at y=45.30 (source 45.60). Unchanged.
  Google, before  6 pages, words/page 257, 0, 245, 247, 228, 253
                  per-page dy median 8.6 / LOST / -53.8 / LOST / -54.9
  Google, after  10 pages, words/page 257, 0, 245, 0, 247, 0, 228, 0, 253, 0
                  per-page dy median 8.6 / LOST / +0.8 / LOST / +0.6

Read it in two halves, because they say different things.

1. **The displacement itself is fixed.** On the pages that still have enough matched runs, the
   median dy goes from -53.8 to +0.8 and from -54.9 to +0.6, against a tolerance of 1.5-4.5 pt.
   The construct does what the probe said it would.

2. **It cannot be landed as a construct swap.** The document goes from 6 pages to 10 with a blank
   page after every real one. Two causes, both measured:
   - the baseline ALREADY emits a blank page 1 in Google (words/page 257, **0**, 245, ...), so this
     document's page-break construct is producing an empty page on its own. That is a separate
     defect and it is why `31_pages_lost_their_text` reads source=5 render=1.
   - the 55 pt page-top gap costs 55 pt of page capacity. The flow's fill budget assumed that gap
     was free, because in Google it was: the content fitted. Make the gap real and every page
     overflows by its own top gap.

So the next run's job is not "swap the construct". It is: make the gap real **and** charge it to
the page's fill budget, and deal with the blank page the break paragraph already produces. Both
are engine work and both need the full corpus ratchet, which no probe can substitute for.

Status: complete. Two attempts on 18_displacement this run, both reverted, both carrying numbers.
