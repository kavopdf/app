# The MediaBox clip: independently confirmed, and the class table it left stale

21 Nov 2026, relay fixer slot 14:11. This run found the slot stale, claimed it, and picked the same
lead the `:50` run landed at 14:21 (`d2ea491`). Its commit is the one in the tree; this note is the
independent second measurement of it, the three witnesses, the class table that commit left behind,
and two writer changes the agents measured and killed.

## The clip, confirmed from three sides

`verify_txt.glyph_truth()` read the source string with `pg.get_text()`, whose `TEXTFLAGS_TEXT` includes
`TEXT_MEDIABOX_CLIP`. MuPDF's clipped path drops the glyphs of a line crossing the page boundary. On
`411_nested_xobject_transforms` page 1 the page draws one string twice, the second copy at 10 pt rotated
90 deg by a nested form's `cm`, 21.94 pt past the top of the MediaBox. Read this run:

| witness | what it says |
|---|---|
| `pg.get_text()` (clip on) | `- S O 90` - the line reduced to two one-character fragments |
| `pg.get_text()` (clip off) | `NESTED FORM - scaled and rotated` / `NESTED FORM - scaled and rot` |
| the engine's `.txt` | `NESTED FORM - scaled and rotated` / `NESTED FORM - scaled and rot` |

The `.txt` and the unclipped declaration are word-for-word identical. The clipped one asserts `S` and
`O`, which the page never draws as words, so t01 charged the correct file for losing them. That is the
whole defect, and it was in the reference the whole time.

**Independent A/B, this run.** Corpus downloaded from `corpus-v1`, engine built with `build-engine.sh`,
one `ConvertAll` pass to produce 211 `.txt`, then the SAME `.txt` scored twice - stock verifier and
patched verifier, nothing else differing:

    rows that differ : 2 of 211
    improved         : 2
    worse            : 0

    411_nested_xobject_transforms   3/4  -> 4/4    (t01 clears)
    12_stamp_across_page_break      9/10 -> 10/10  (t12 clears)

Same two documents, same direction, same magnitude as `d2ea491`'s 213-document measurement. Two
independent builds and two independent harnesses agreeing is the reason to believe it.

## The class table that commit left behind

`d2ea491` rewrote two rows of `RANKING-TXT.csv` and stopped there. `DEFECT-CLASSES-TXT.md` - the file
`classpick.py` and `round.py` actually read - was still the pre-fix table: **`t01_word_accuracy` 5
documents, `t12_word_invention` 9, 25 failing**. A round cannot close on a table that says OPEN for a
document that passes, and the next run would have been sent back to 411.

Regenerated from the committed ranking this run (`classify_txt.py`, no re-scoring, no engine change):

    before : 6 classes, 25 failing documents, t01 5, t12 9
    after  : 6 classes, 24 failing documents, t01 3, t12 8
    ranking: 189 clean of 213, 24 failing

`t01_word_accuracy` now holds three documents - `39_small_caps_letter_spacing`,
`601_fillable_admission_form`, `77_arabic_rtl_document`.

## Two writer changes measured and killed

Two agents measured the four other t01 documents. Both candidate WRITER changes make their document
worse, and neither is worth retrying:

| document | candidate | measured |
|---|---|---|
| `39_small_caps_letter_spacing` | `gs = g.sizePt` -> `g.size` at `PdfToWord.java:4305` and `:5529` | t01 **97.4 -> 78.8**, t12 2 -> 14 |
| `38_faux_bold_italic_synthesised` | `dedupe()` window 40 -> 200 glyphs at `PdfToWord.java:3190` | t01 **98.0 -> 93.0**, and t12 gains an invented word |

The `39` number is the important one: a hand-corrected `.txt`, the file a reader would produce, scores
**58.2** where the broken one scores 97.4. The reference rewards the wrong file by about 39 points,
because `get_text()`'s own gap heuristic shatters a real word gap (`570 005` arrives as `57 0 0 05`)
while the page draws a genuine space glyph at x = 355.8. That is the same shape of defect as the clip:
a MuPDF heuristic standing in for what the page draws. **The lead: derive the source word boundaries
from the drawn space glyphs in `get_texttrace()`, not from `get_text()`.** Not built - it is a bigger
change than one line and needs the whole corpus to prove.

The `38` negative is a prediction that came true in the other direction: widening the dedupe window
regresses it, and the commit that actually cleared `38` at 14:47 (`2d44a3a`, "a line drawn more than
once at one place is one line") is the position-aware rule - span-identical **and** position-identical
- which is the version the agent said would be defensible and did not build. The class table above is
the first table that shows it landed.

## A gate hole this run walked through

`regress.py --check` PASSED a duplicate of this fix with `scope of the change: nothing`, `txt: not
re-measured - the tree is the engine the table was measured on`. The engine did not change - only the
verifier did - and the gate's fingerprint tracks the ENGINE, not the instrument's body. So an edit to
`verify_txt.py` lands without the gate asking for a re-measure.

It was not a hole for `d2ea491` (that run measured all 213 by hand) and it was not one for this run
(the same, twice). It is a hole for the next run that edits a check and does not. Written up rather
than fixed, because fixing the gate is not this class.
