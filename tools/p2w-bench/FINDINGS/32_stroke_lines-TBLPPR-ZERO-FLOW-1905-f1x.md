# `w:tblpPr` is honoured by Google Docs and costs ZERO flow space — the rule carrier is now complete

**21 Nov 2026 · relay/fixer slot 18:17 · measured through Google Docs, one 3-page `.docx`, one export**

## The answer

The last blocker on `32_stroke_lines` — worth **36.3 clean documents**, the largest single prize in the
pipeline — was that a table carrying a cell-border rule occupies flow space and pushes the following text
down. It does not have to. **A floating table (`w:tblpPr`) is honoured by Google, renders its rule, and
costs 0.00 pt of flow.**

## The measurement

One `.docx`, three pages, each page `ABOVE` / carrier / `BELOW`. Uploaded to Drive as a Google Doc,
exported back as PDF, ink read with PyMuPDF.

| page | carrier | `ABOVE` y | `BELOW` y | displacement vs control | rule drawn |
|:--|:--|--:|--:|--:|:--|
| 1 | **none** (control) | 0.42 | **11.92** | — | none |
| 2 | inline, `w:trHeight w:val="1" w:hRule="exact"` | 0.42 | **12.83** | **+0.91 pt** | x 122.0 → 222.0, y 11.5 |
| 3 | **floating**, `w:tblpPr` `tblpY="8000"` | 0.42 | **11.92** | **0.00 pt** | x 122.0 → 222.0, **y 399.5** |

Four things are settled by those three rows.

1. **Google honours `w:tblpPr`.** Page 3 asked for `tblpY` 8000 twips = 400.0 pt and the rule was drawn at
   **y = 399.5** — 0.5 pt from the request, and 388 pt away from where the same table lands inline on
   page 2. Nothing else explains a rule moving 388 pt on its own.
2. **A floating table costs nothing in the flow.** `BELOW` on page 3 sits at **11.92**, the control's value
   to 0.00 pt. On page 2 the same table inline costs 0.91 pt.
3. **The rule is the right size and in the right place.** x 122.0 → 222.0 is **100.00 pt** wide —
   `tblpX` 1000 twips (50 pt) measured from a 72 pt margin gives exactly 122.0 — against a requested
   2000-twip fixed grid column. This reproduces the earlier finding's exactness for `w:tblInd` and
   `tblLayout="fixed"` through a *floating* table, which is a different placement path.
4. **`w:trHeight w:val="0"` fails because zero is not a legal height.** The legal near-zero row,
   `w:val="1" w:hRule="exact"` (0.05 pt), costs **0.91 pt** — not the 38 pt the `val="0"` row cost. That
   is the explanation for this run's earlier measurement: a discarded `trHeight` leaves a row sized to its
   content, which is where the 38 pt came from.

## The construct to emit

    <w:tblPr>
      <w:tblpPr w:vertAnchor="margin" w:horzAnchor="margin"
                w:tblpX="<x>" w:tblpY="<y>"
                w:leftFromText="0" w:rightFromText="0"
                w:topFromText="0" w:bottomFromText="0"/>
      <w:tblW w:w="<len>" w:type="dxa"/>
      <w:tblLayout w:type="fixed"/>
      ... every tblBorders edge nil ...
    </w:tblPr>
    <w:tblGrid><w:gridCol w:w="<len>"/></w:tblGrid>
    ... one cell, w:tcW = <len>, w:tcBorders carrying the ONE edge that is the rule ...

with `w:tblpX`/`w:tblpY` in twips from the **margin**, and the length in a **fixed** layout with an
explicit `w:tblGrid`. `w:tblW` alone is ignored; `w:tblInd` is unnecessary on a floating table because
`tblpX` places it.

## Traps, all measured or spec-backed, all of which would have cost a run

* **`w:vertAnchor="page"` is dropped**, silently, by the renderer used for the proxy — the spec default is
  also the naive choice. Use `"margin"`.
* **A `tblpPr` that is all zeros is discarded.** `tblpX=0 + tblpY=0 + horzAnchor="text"` with a non-text
  vertical anchor makes Word throw the element away; emit explicit non-zero offsets or a margin anchor.
* **`w:tblPr` child order is fatal.** The schema is a sequence, not a set. `tblpPr` comes before `tblW`,
  `tblLayout` after `tblW`, `tblBorders` before `tblInd`.
* **`w:trHeight w:val="0"` is not a zero-height row.** It is discarded and the row is sized to its
  content. Use `w:val="1" w:hRule="exact"` if an inline carrier is ever wanted — it costs 0.91 pt.
* **A table cannot live inside a paragraph.** `w:tbl` is not a legal child of `w:p`; only `txbxContent`
  gets you there, and Google drops that drawing.

## What is still not measured

Stated plainly, because this is the point where a construct usually turns out to be half-right:

* **Only one floating table, one page, one offset.** `tblpY` 400 pt on a 792 pt page. Not tested: a table
  floating into a region the text already occupies — the wrap-collision case, where the text may be pushed
  aside instead of down, which would trade a displacement for a horizontal shift.
* **Not tested with real content in the cell.** The carrier here is a 1 × 1 table with a single border and
  an empty cell. `32_stroke_lines` needs one of these per source rule; a document with 46 rules needs 46
  floating tables, and nothing here says what 46 of them do to each other or to the page count.
* **Not tested on a multi-page document.** A floating table anchored to the margin on page 1 of 6 is not
  the same problem as one on page 4.
* **Not tested whether `w:tblpPr` survives Google's import of a *large* document.** It survived this one.

The next run should convert one real `32_stroke_lines` document with the floating carrier and score it.
`394_map_with_legend` (3 rules, fails `32_stroke_lines` alone, 41/42) is the cheapest: if it goes to 42/42
with three floating tables, the construct is proven on a real document and the rest is repetition.

## How to repeat it

The probe is `probe-flow-zero.docx` (three pages, as in the table above). Upload to Drive as
`application/vnd.google-apps.document`, export as PDF, then:

    pymupdf: page.get_text("dict") -> spans -> find ABOVE / BELOW, read bbox[1]
             page.get_drawings() -> the thin segment, read rect.y0

The `.docx` was built by the Explore sub-agent that also wrote
`/scratch/input/table-flow-zero.md`, which carries the ECMA-376 quotes for `tblpPr`, the attribute list,
and the reasons the nested-table and paragraph-container routes are closed.

**Cleanup.** One probe document created in Drive, deleted.
