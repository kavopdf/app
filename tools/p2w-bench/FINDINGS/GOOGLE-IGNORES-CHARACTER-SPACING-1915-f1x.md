# Google Docs ignores `w:spacing` character spacing - measured, not inferred

**22 Nov 2026, fixer slot 19:00.** Three controlled `.docx` probes through the real Google round
trip (upload -> Google Doc -> PDF export -> PyMuPDF line boxes).

## Why it matters

Engine commit `4147d540` ("a justified line is written justified - 7 documents newly clean") carries
a justified line's shortfall as **`w:spacing` (character spacing) in `w:rPr`**, written from
`DocxWriter.flowFromBox()` / `lineParagraph()`. Its evidence was the LibreOffice signature. 22 of the
213 documents carry that construct today.

`60_text_column_right_edge` fails on exactly two documents and nothing else -
`313_power_of_attorney` and `321_auditors_report` - and both are justified prose whose lines the
source stretched to its measure.

## The probe

One page, text area 481.6 pt, DejaVuSerif 9 pt, five paragraphs, identical text per pair:

| variant | line width |
|:--|--:|
| left, character spacing 0 | 252.2 pt |
| left, character spacing 20 tw | 276.9 pt |
| left, character spacing 60 tw | **277.4 pt** |
| justify (`w:jc=both`), single-line paragraph | 258.2 pt |
| distribute (`w:jc=distribute`), single-line paragraph | 276.7 pt |

Spacing 20 and spacing 60 land within 0.5 pt of each other. The 24.7 pt between the first two rows is
the label text ("B left+sp20: " is five characters longer than "A left: "), not the attribute.

**`w:spacing` in `w:rPr` is a no-op in Google Docs. `w:jc=distribute` is a no-op. `w:jc=both` does not
stretch a paragraph's only line** (Google, like Word, does not justify a last line, and a one-line
paragraph's line is its last).

## What it means

`313_power_of_attorney` measured through Google: source widest line 538.6 pt, render 480.1 pt - 58.5 pt
narrow, with **identical line breaks and identical text**. The words did not change; the stretch did
not arrive. `60_text_column_right_edge` reads `under=1` because the render's column is 58.5 pt
narrower than the source's.

So the engine's justification construct cannot work in the renderer the user opens, and the two
`60_text_column_right_edge` documents cannot be closed by it. A construct Google honours is needed:
justification across a *multi-line* paragraph (measured: a two-line `w:jc=both` paragraph has its
first line stretched, its last line not), or font-size compensation, which `10_font_sizes` forbids.

## Not yet decided

Whether to emit the page's lines as one justified multi-line paragraph when the source's lines are
stretched - trading the engine's exact per-line breaks for the right edge - is a real design choice
and is not made here. What is measured is that the current construct buys nothing in Google, so any
LibreOffice number it produces is a proxy artefact.
