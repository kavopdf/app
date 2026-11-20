# t01_word_accuracy: where the five stand, with three of them measured this run

20 Nov 2026, fixer run claimed 00:57. No engine change landed. This is the census the next run
needs so it does not re-diagnose the class from scratch, which had cost seven attempts before this
run. Four of the five now have a measured cause: three are the reference's, one is the engine's.

## The five documents, and which side each fault is on

| document | check(s) | side | status |
|---|---|---|---|
| `411_nested_xobject_transforms` | t01 | **reference** | **proven this run** - see `411-nested-xobject-matrix-1940.md` |
| `39_small_caps_letter_spacing` | t01 + t12 | **reference** | **proven this run** - see `39-small-caps-gap-threshold-0150-fixer.md` |
| `601_fillable_admission_form` | t01 | **engine** | proven 20 Nov 23:42 - `601-tick-is-a-widget-appearance-2342.md`. The only engine-side one left |
| `77_arabic_rtl_document` | t01 + t12 | open | carried from the t12 census: RTL segmentation, no proof yet |
| `38_faux_bold_italic_synthesised` | t01 + t07 | **reference** | **proven this run, third attempt** - see `38-faux-bold-TRIPLE-DRAW-0225-fixer.md` |

## The three that are now proven, in one line each

**411.** The handed diagnosis - pymupdf and PDFBox disagree about a nested form's matrix and the
rotated line runs off the page - is **wrong**. Both parsers compute the same CTM to the digit,
`[0 1 -1 0 60 700]`, det +1, and PDFBox returns all 32 glyphs of the rotated line. pymupdf's
`get_texttrace()` also returns all 32. Only `page.get_text()` returns 2, because
`fitz.TEXTFLAGS_TEXT` includes `TEXT_MEDIABOX_CLIP` and that path drops a line crossing the page
edge. The .txt carries the 28 on-page glyphs and is right; the reference invents the words `S` and
`O`. Turning that one flag off leaves 211 of 213 rows byte-identical and moves `411` and
`12_stamp_across_page_break` (same defect, charged `U` and `G`).

**39.** Letter spacing is not `Tc`, not `Tz` and not a kerning number - it is the `TD` x-coordinates
of single-glyph `TJ` arrays with a real space glyph between letters. The writer's word-break
threshold is `0.18 x 8.00 = 1.440 pt`; the reference splits at the drawn `1.200 pt` gap. The writer
emits `570 005`, which is what the page draws; the reference reads `57 0 0 05` and charges the
difference in both directions. A writer patch that fixes this scores **97.4 -> 58.5 on t01 and
2 -> 22 on t12**: the better text file scores worse, which is the proof that the fault is the
reference's.

**38.** The page draws each of its two headings three times at the identical position - two fill
spans and one stroke span, same font, same size, same baseline, the faux-bold idiom.
`page.get_text()` reads the fill copies and counts each line twice: 201 words against 186 with
identical-position spans collapsed. That is the `t01` charge on a 99 % threshold, and the doubled
em dash is the `t07` charge. A walk over every page of all 213 PDFs finds identical-position
duplicate spans on exactly this one document, so a same-place-same-string dedupe on the source side
has a blast radius of one.

## What the next run should do

`601_fillable_admission_form` is the only engine-side document left in `t01`, and its fix is already
named: a glyph walk over each widget's `/AP /N` stream, the shape `formValuesOf` and `widgetValue`
already have on the engine side and `_ap_stream_text` already has on the instrument side. Take that
one. Do not spend a slot on 411, 39 or 38 - all three are the instrument's, and all three are written up
with the measurement that proves it. Two of them (`411`, `38`) are one sanctioned source-side
correction away, with a corpus-wide restamp; the proposal and its measured blast radius are in
`INSTRUMENT-PROPOSAL-clip-flag-NOT-APPLIED-0210-fixer.md`.

`t08_line_order` (10 documents) is the largest class still entirely open, and `t12_word_invention`
(9) is next.

## Standing rule this run did not break

`verify_txt.py` was not edited. Both findings say what a correct reference would do; neither moves a
number. That is the brief's rule and it is the reason the two results above are worth anything.
