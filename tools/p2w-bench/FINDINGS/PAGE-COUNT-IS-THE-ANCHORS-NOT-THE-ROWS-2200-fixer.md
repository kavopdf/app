# `00_page_count` is not rows, spacer, wrapping or paragraph spacing. It is the anchored shapes.

24 Nov 2026, fixer, second subagent. No Drive access in the subagent pod, so every Google-side number
here is either a recorded page count from `benchmarks/gverify/*.json` or a law already in `FINDINGS/`;
every other number is tagged with the renderer it came from. Full tables in the subagent report.

## The population

23 documents are `status=page_count_refused` in `benchmarks/gverify/*.json`. **21 are one-page source
PDFs that Google lays on two.** The other two (`041122-Account_Opening_Form`,
`Account_Opening_Form_Fillable_filled`) are 9-page sources that LibreOffice already lays on 10 and 11 —
a pagination fault, not a one-page overflow, and they belong with `18_displacement`.

`00_page_count` is worth **23 clean documents** in `classpick.py --leverage`, the second-largest check in
the corpus. None of those 23 can be scored at all until it passes, so the 23 are currently invisible to
every other number the report prints.

## The four components the class was assumed to be: measured, and they are all zero

Decomposed per document off `word/document.xml` and the LibreOffice render:

| component | how measured | result over the 21 |
|---|---|---|
| (a) rows Google lays taller than declared | `Σ max(0, max(trHeight, 1.15·sz) − max(trHeight, content_LO))` over 391 `trHeight` rows | **0.00 pt** — minimum clearance +2.95 pt, the floor never binds. Rendering every `trHeight` raised to the floor changes page count and bottom ink by nothing, to 0.05 pt |
| (b) the table-top spacer | `Σ (2.5873·max(L/240,0.06) − L/20)` | **negative on 6** (`403` −45.61, `332` −23.45, `341` −14.83, `390` −11.53): the spacer currently buys Google room |
| (c) text that wraps an extra line under Google's substitute face | Liberation Sans (= Arial) vs DejaVu, per line, against the line's real width | **0.00 pt** — the substitute is *narrower*: widest line 0.976 of its width, and it *removes* wraps (`05_round` 6→0, `price-list` 52→42). Rewriting every `w:rFonts` to Liberation Sans renders identical to 0.05 pt |
| (d) paragraph spacing | 0 paragraphs inherit `docDefaults` spacing, 0 use a non-exact line rule | **0.00 by construction** |

On 16 documents (a)+(b)+(c)+(d) = 0.00 pt; on 6 it is negative; on one (`314_tender_rfp_boq`) +0.11 pt.

## What is left: 7,939 anchored shapes across the 23, and 0 inline

`0 <wp:inline>` and **7,939 `<wp:anchor>`**. LibreOffice charges an anchored shape nothing in the flow.
Google rasterises it and keeps a box. That is the recorded C1 census, and it is proved on
`60_page_border`: 62 anchors → a page 2 carrying 0 characters; remove the shapes and write the frame as
`w:pgBorders` → 1 page, 689 characters.

The constant a fix has to beat is the flow slack divided by the anchor count — the size of the box
Google must be charging per shape:

| document | eff. slack pt | anchors | min pt per anchor to spill |
|---|--:|--:|--:|
| `351_omr_answer_sheet` | 36.59 | 381 | **0.10** |
| `390_wide_data_appendix` | 45.46 | 400 | **0.11** |
| `341_shipping_manifest` | 34.76 | 301 | **0.12** |
| `305_vaccination_certificate` | 57.49 | 276 | **0.21** |
| `price-list-2col-dense-right-aligned` | 29.89 | 85 | 0.35 |
| `bank-statement-horizontal-rules-only` | 25.39 | 39 | 0.65 |
| `boq-horizontal-rules-only` | 25.39 | 33 | 0.77 |
| `401_trifold_brochure` | 348.63 | 26 | 13.41 |
| `350_question_paper` | 4.89 | 1 | 4.89 |

Median **0.57 pt per anchored shape** across the 19 comparable documents, range 0.10–0.96. A sub-point
box is invisible in LibreOffice and fatal in Google — which is exactly why this class never showed up in
the LibreOffice table.

## The cheapest real construct, and the one that must not be tried first

**`332_bom_on_drawing` — 35 of its 58 anchors are redundant.** The table already declares
`insideV single sz=3`; the engine emits each of the 35 vertical row rules again as its own anchor
(5 cell edges × 7 rows). Removing an anchor whose rule the table's own borders already draw changes the
visible table in neither renderer. 43.38 pt ÷ 58 = 0.75 pt per shape is all that has to go. Google-only;
LibreOffice is 1 page, 585.30 pt of ink, identical under both variants.

This is a **de-duplication**, not a change of construct: it is the same rule drawn twice, once as a
border and once as a floating shape. It is the smallest unit of the anchor class that can be landed and
measured on its own.

**Do not charge the spacer to this class first.** On `332`, `341`, `390`, `403` and the two bank forms the
spacer is currently worth −11.53 to −538.95 pt *in Google's favour*; handing it back before the anchors
are dealt with turns those documents over.

## What would settle the constant

One Drive round trip on `bank-statement-horizontal-rules-only` (39 hairlines, Σ cy 19.2 pt, 25.39 pt of
slack) fixes the per-shape box size, and the same trip on `332` measures the de-duplication. Neither was
run this slot: the subagent had no Drive, and the fixer's slot went to the `18_displacement` guard.

## Still open

- Whether Google floors a `w:line` below the type box — the last candidate for `350_question_paper`
  (3.39 pt, 1 anchor, 4.89 pt slack), falsifiable in one round trip.
- `405_sheet_music_lyrics`, `head(LO)` 76.59 pt, the largest in the class; the recorded C2 law predicts
  +131.8 pt and was not re-derived.
- The ranking is by measured LibreOffice headroom, which is a **lower bound** on Google's overflow.
