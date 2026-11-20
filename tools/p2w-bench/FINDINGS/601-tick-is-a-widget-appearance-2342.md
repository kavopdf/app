# A ticked checkbox is lost: the mark is drawn in the widget's appearance stream

**20 Nov, fixer run 22:54, second attempt — measured, no code changed.**

`601_fillable_admission_form` fails `t01_word_accuracy` at 96.4 % (83 source words, 3 lost) and is
one of the five documents left in the t01 class. The three lost tokens are `3`, `3` and `General`.

## The ticks are real, and they are not in the page content stream

pymupdf reports two spans, both `ZapfDingbats` at 9 pt, both the single character `3`:

    48.9, 326.5   48.9, 346.5

The page's own resources name only two fonts:

    /Resources << /Font << /hebo 5 0 R /helv 7 0 R >> >>

No page content stream names a Zapf face, and scanning every decoded stream in the file for
`Zapf` finds nothing. The marks are in the **checkbox widgets' appearance streams** — xrefs 51
and 57, four streams in all:

    q
    0 w
    BT
    0 g
    .9 1.7999992 Td
    /ZaDb 9 Tf
    (3) Tj
    ET
    Q

`/ZaDb` is ZapfDingbats and code 0x33 is its checkmark. So the page draws a tick, twice, and the
document is a filled form whose answers include two ticked boxes.

## PDFBox never sees them, and that is the engine's loss

`PDFTextStripper` walks the page's content streams. It does **not** process annotation appearance
streams, so the widget marks never reach `processTextPosition`. Measured with a probe over the
whole document: **530 glyphs, every one Helvetica or Helvetica-Bold, no Zapf face at all.**

So the engine drops a character the page draws, and the user's .docx has two blank checkboxes
where the form was answered. This is content loss, not a measurement artefact.

The source side is also wrong, and in the other direction: pymupdf reads the tick and calls it
`3`, which is the ZapfDingbats CODE, not the character. A tick is not the digit three. Both sides
need the same answer or neither is honest: the engine must read the appearance stream and emit
something for a tick, and the source must stop calling it `3`.

## The fix, named for the next run

The engine already has the shape of it. `PdfToWord.formValuesOf()` reads `/V` from the field
dictionary and `widgetValue()` turns a `/Btn` state into text; `PdfToWord` also reads `/Contents`
from FreeText annotations. What is missing is the glyph walk over a widget's `/AP /N` stream,
which is the one place a tick lives.

On the instrument side `verify_txt._ap_stream_text()` already reads that stream for the VALUE
checks, so the two sides can be made to agree with one rule: a `/ZaDb` glyph inside a widget
appearance is a tick, and both sides should call it one.

**Not implemented this run** — the slot went to the two bank forms, and a change here needs both
sides plus a restamp to be worth anything. What this attempt buys the next run is the proof that
the tokens are recoverable at all, and exactly where they are.
