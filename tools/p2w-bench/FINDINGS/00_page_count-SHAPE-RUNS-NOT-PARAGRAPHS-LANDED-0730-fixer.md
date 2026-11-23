# 00_page_count — the shape joins the paragraph that already exists, and the page comes back

**Class:** `00_page_count` (23 refused, 23.0 clean-document leverage)
**Engine:** tree `4a607e4b793fb348`, from `cb0f54d4fc908f18`
**Measured:** 23 Nov 2026, 06:55–07:35 IST. One Google round trip (upload → convert to a Google Doc →
export PDF → read), one LibreOffice render, and a full 213-document corpus re-measure.

## Why this and not `18_displacement`

`classpick.py --leverage` prices `18_displacement` at 34.2 and `classpick.py` suggests it, on the
strength of the 06:15 lead. I did not take it. `FINDINGS/18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-
SEVEN-MECHANISMS-0630-fixer.md` measured that the documents failing that check alone in the measurable
renderer resolve into **seven distinct mechanisms**, and the last two runs spent their whole slot on it
for 0 kept moves. `00_page_count` is worth 23.0, and the mechanism is **one** construct with a measured
cost per unit and a build that was never actually run (row 6 of
`00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md` is VOID — a slicing bug, not a refutation).
One mechanism, one build, 22 documents carrying it: that is the cheaper 23.

## What was measured, before

On `301_lab_report_panel`: 193 paragraphs in `word/document.xml`, of which **108 are drawing-only**
(one page-positioned floating `<w:drawing>`, no text), and all 108 sit after the last text paragraph.
Google renders it on **2 pages** and `gverify.py` refuses it (`page_count_refused`), so all 42 checks on
it are unknown.

## The change

`DocxWriter.shape()` wrote each shape as its own `<w:p>` with `w:spacing w:line="1" exact` and an
`sz=2` run. Google keeps that paragraph and bills it the line box of the tiny run (~0.83 pt) because it
does not honour the exact line rule. The shape itself is anchored to the **paper**
(`wp:positionH/V relativeFrom="page"`, `wp:wrapNone`, `behindDoc=1`) — it never consults the paragraph
it is written in, so the paragraph buys nothing.

So: `shape()` is now `SHAPE_PARA_PPR` + `shapeRun()`, and `pageBody()` writes a shape as a **bare run
appended to the last paragraph already on that page** (`shapeRun` into `sb` before its `</w:p>`). A shape
above the page's first line of text is held and joined to the first paragraph that arrives. Only a page
with no paragraph at all gets one carrier paragraph, and it carries every shape on that page.

## What was measured, after

| | before | after |
|:--|--:|--:|
| `301_lab_report_panel` paragraphs in document.xml | 193 | **85** |
| drawing-only paragraphs | 108 | **0** |
| `<w:drawing>` elements | 108 | **108** (unchanged) |
| Google pages | **2** (refused) | **1** |
| Google 42 checks | refused, all unknown | **39/42** |
| Google images on page 1 | 58 on p1 + 50 on p2 | **108 on p1** |
| LibreOffice 47 checks | 42/42 PASS | **42/42 PASS** |

The drawings are all still there and all still at their source coordinates — the render carries 108
images, the same 108 the page draws.

## The corpus, measured whole (this is what makes it landable)

`benchmarks/gate.py` over 213 documents on the new engine: **no regressions against baseline**, 0
documents worse, `regress.py --check` PASS on both formats, `measure_gate.py` READY (212/213 scored, 1
exempt). The `.txt` layer re-measured with `restamp_txt.py --run`: **213 scored, 0 newly clean, 0 newly
failing, 213 unchanged** — the patch touches `DocxWriter` only, and the `.txt` says so.

`301_lab_report_panel` share@5px moves 0.02 → 0.02: in the LibreOffice proxy this document was already
clean, which is exactly why the proxy hid the defect. The movement is in the renderer the user opens.

## The three checks still failing on 301, and what they are

`18_displacement` (render 1), `25_invisible_text` (render 2), `60_text_column_right_edge` (render 1).
`25_invisible_text` is the white masthead: `METROPOLIS PATHOLOGY LAB` (13 pt, `#FFFFFF`) and the
accreditation line (7.5 pt, `#FFFFFF`) are white type over a dark band that Google rasterises, so the
span has no ink behind it. That is a different construct from this one and is not introduced here — the
band is rasterised either way. This document is now **measurable and 3 checks from clean**, where it was
unmeasurable and 42 checks from anything.

## What would prove this wrong

* A document whose LibreOffice page count goes UP with this patch. None did: 0 documents worse across
  213.
* A Google render where a shape moved, or a `<w:drawing>` went missing. On 301 all 108 are present at
  their source positions.
* A second document in this class that stays on two pages. Not yet measured in Google — see below.

## For the next run

1. **Measure a second and third document of the class in Google** (`375_attendance_register` with 456
   drawing-only paragraphs, and `041122-Account_Opening_Form` with 2464) to confirm the carrier
   paragraph does not choke at scale. One document is one document.
2. The remaining page-count refuses that this does not explain: `350_question_paper` has **1**
   drawing-only paragraph and is not explained by this mechanism (its refusal is a separate cause).
3. `w:tcBorders`/`w:tblBorders` through the table writer is still the second lever for `32_stroke_lines`
   and `05_chars_extra` — the same construct as this one, one mechanism three check families.

## Second document, and the A/B that attributes the residual

`375_attendance_register` carries **456** drawing-only paragraphs (916 paragraphs before, 460 after).
Both engines were built and rendered through Google on the same source, so this is a controlled pair,
not a before-and-after across time:

| | previous engine | this engine |
|:--|--:|--:|
| paragraphs in document.xml | 916 | **460** |
| drawing-only paragraphs | 456 | **0** |
| Google pages | **2** | **1** |
| page-1 images / drawings | 37 / 51, page 2: 419 | **456 / 51 on page 1** |
| Google 42 checks | 35/42 | **37/42** |

Failing set, previous engine: `01_page_count`, `18_displacement`, `25_invisible_text`,
`43_within_10pt_x`, `47_margins`, `55_orientation_mix`, `59_shape_anchor`.
Failing set, this engine: `18_displacement`, `25_invisible_text`, `43_within_10pt_x`, `47_margins`,
`59_shape_anchor`.

**No check that passed before fails now.** The two that disappear are `01_page_count` and
`55_orientation_mix`, and `55` disappears because the second sheet is gone, not because anything was
hidden. The five that remain were already failing on the previous engine with the same values
(`47_margins` render 382 both times) — they are other constructs, not this one, and this measurement is
the attribution. `301_lab_report_panel`'s three residual failures are the same population
(`18_displacement`, `25_invisible_text`, `60_text_column_right_edge`).

## What this buys, stated as documents

22 of the 23 `page_count_refused` documents carry drawing-only paragraphs and every one of them emits
them after the last text paragraph. Each of those documents was scoring **zero of 42 known checks**
because `gverify.py --collect` refuses a page-count mismatch. After this change the page count is a
function of the flow the page actually needs, so they become measurable — two of them are now measured
and both are 1 page.

This is not yet "clean": the class moves from *unmeasurable* to *2–5 checks from clean*, which is the
only way those 22 documents can ever be scored at all. `350_question_paper` (1 drawing-only paragraph) is
**not** explained by this mechanism and is still refused.
