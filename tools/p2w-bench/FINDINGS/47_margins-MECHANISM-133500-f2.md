# 47_margins is a left-ink-edge check, and both of its sub-mechanisms are Google-only

Written 20 Nov 2026, 13:35 IST, by the fixer run that took `47_margins` on the rotation.
Two constructs were built and measured; neither is kept. The diffs are beside this file. Read this
before spending a run on the class.

## The definition - found, not guessed

`tools/p2w-bench/verify_google.py:3960-4170`, verdict at `:4169`. `47_margins` is **not** a
four-margin check and there is no 12 pt page-bbox tolerance. It compares, per page, **horizontally
only** (vertical is explicitly out of scope):

- **(a) the page anchor.** The page's anchor is the leftmost rounded left edge shared by at least
  `max(3, 5%)` of the page's lines. Fail if the source and the render differ by more than 3.0 pt on
  any page.
- **(b) the indent structure.** On matched run pairs (upright on both sides),
  `d = render.xink - source.xink`; a line is unregistered at `|d| > 2.0 pt`; the budget is
  `max(2, round(5% n))`; fail if the budget is exceeded, or if two or more lines are unregistered and
  `max|d| > 24.0 pt`.

A document against itself scores `(0.0, 0)` on this check for 13 of 13 class documents, so the
verifier is sound and the defect is real.

## `w:pgMar` is zero and is not the mechanism

`DocxWriter.java:2268-2269` (inside `sectPrXml`, `:2259-2272`, called at `:1058` and `:1284`) writes
`w:pgMar` as **0 on all four sides, a hard constant**, for every section of every document. `w:pgSz`
is per-section and is the page's own size. No code path reads a margin from the source, so "constant
versus per-document average" does not arise. Google places a line's ink at `pgMar + ind`, so with
pgMar 0 a left-aligned line is pinned by its `w:ind w:left` and the anchor clause is satisfied. Do
not spend a run on the margin numbers.

## The lever is `flowFromBox`

`DocxWriter.java:4159-4188` and `:4391-4392`. Left-aligned lines pin their ink absolutely. Centred
and right-aligned lines delegate their left edge to the renderer's own text width. That single fact
produces both failures:

1. **Centred lines** move rightwards under face substitution by half the width the narrower face
   loses. 317_rti_response's three centred paragraphs move 5.7 to 45.6 pt.
2. **Space-led lines** - an R console's column headings, a shell transcript's continuation - are
   emitted as a run beginning with n ASCII spaces, so the indent is n x the space advance of
   whichever face renders them. 392_statistical_console_output's "Estimate Std. Error" row is 20
   spaces: 79.5 pt of ink offset in DejaVu Sans Mono, 36.2 pt in Liberation Sans, ink landing at 64.2
   instead of 107.5.

## Construct 1 - pin the centred line's extent (REVERTED)

Drop `w:jc` and pin `[b.x, b.right]`. Diff: `47_margins-centred-left-pin-133500.diff`.
Under the substitution proxy 317 goes `(0.1, 3)` to `(0.1, 0)` - the check passes - and 392 and 76
are untouched. But pinning the left edge moves a centred line's whole width error onto its right
end, and `share@5px` dislikes it: screen over all 13 class documents gave **11 same, 0 better, 2
worse** - 317 `0.65 -> 2.54`, 318 `0.00 -> 0.71`. A patch that moves the number up and looks worse
is not a fix. Not kept.

## Construct 2 - the spaces are an indent, not text (REVERTED, and the one to carry forward)

Strip the leading ASCII spaces from the run text and add `inkX - b.x` as a real `w:ind w:left`, where
`inkX` is the ink left edge of the first non-space glyph. `PdfToWord.Box` had no such field, so the
diff adds `Box.inkX = visibleX(line.glyphs, line.x)` in `PdfToWord` (`visibleX` is already at
`PdfToWord.java:8149`) - this is not a DocxWriter-only change. Diff:
`47_margins-indent-space-construct-133500.diff`.

Measured, pristine engine `6bec2f2` against `6bec2f2` plus the patch:

| document | share@5px before | after |
|:--|--:|--:|
| 392_statistical_console_output | 1.61 | 1.48 |
| 78_mixed_english_devanagari_line | 1.73 | 1.73 |
| 40_devanagari_shaping_font | 10.48 | 10.48 |
| 76_devanagari_table | 7.91 | 7.91 |
| academic-paper-ieee-2col-abstract | 5.66 | 5.66 |
| 330_cad_drawing_sheet, 331_pid_diagram, 318_court_summons_form, table-with-rotated-header, 317_rti_response | - | same, 0 better, 0 worse |

**Nothing got worse anywhere.** Line and page counts unchanged on all 13 documents; the 12 changed
paragraphs differ only by their leading spaces. Position in the declared face moves by at most 0.31
pt, and 392's 20-space line moves 1.2 pt *closer* (twenty rendered advances accumulate 1.09 pt of
shortfall; a pinned indent does not). `p2w.py --validate` prints GATE PASS on the patched engine.

Under the face-substitution proxy the check's own counter goes to zero: 392 `2 -> 0`, 380 `3 -> 0`,
383 `7 -> 0`, FAIL to PASS on all three.

**Why it is still not kept.** It reaches `flowFromBox` in only 3 of the 13 documents. 40, 77 and 78
have leading-space lines that are anchored, in a cell, or merged, and their .docx is byte-identical
under the patch. Three of fourteen is under the quarter the outcome rule needs, and the corpus
measurement cannot see the rest of the effect because the defect only appears under a face Google
substitutes and the local instrument renders with the declared face. It is a Google-only mechanism,
so the local `share@5px` is flat by construction - the only document it can move is 392, by 0.13.

## What the next run should do with it

The construct is position-neutral in the declared face and it drives the Google check's own counter
to zero, so it is a legitimate candidate for a class whose whole defect is invisible to LibreOffice.
Landing it needs what this run did not have: a full corpus pass (`benchmarks/gate.py --budget 250`,
which produced no output and no `RANKING.csv` update in 295 s here) plus `regress.py --check`, then
one Google check. The 295 s attempt wrote nothing, so budget a separate call for it and confirm
`benchmarks/RANKING.csv`'s mtime moved before believing it ran.

The one extension worth trying, which is what would take the reach from 3 to more: the same
strip-and-pin applied where the line is emitted inside a table cell rather than through
`flowFromBox`, which is where 40, 77 and 78's space-led lines live.

## Corrections to the capability table

The class row reads LO-fails 12 / Google-only 14. From the stored JSONs it is **LO fails 16,
Google-only 13**. The 13 are: 317_rti_response, 318_court_summons_form, 330_cad_drawing_sheet,
331_pid_diagram, 380_runbook_terminal_output, 383_api_docs_page, 392_statistical_console_output,
40_devanagari_shaping_font, 76_devanagari_table, 77_arabic_rtl_document,
78_mixed_english_devanagari_line, academic-paper-ieee-2col-abstract, table-with-rotated-header.
76_devanagari_table fails 47_margins in LibreOffice on the current engine, so it is no longer
Google-only.
