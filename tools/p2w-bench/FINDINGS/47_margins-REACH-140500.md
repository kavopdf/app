# What 47_margins can and cannot be reached by - measured on all 26 documents

Written 20 Nov 2026, 14:05 IST. Two runs have now built constructs for this class and neither was
kept, both for the same unmeasured reason: nobody counted how many documents the construct reaches.
This is that count. It costs one trace per document and it should have been taken first.

## The measurement

The writer names every line it emits when the engine is given `-Dp2w.traceLines=<file>`:

    cd tools/engine-verify
    java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
         -Dp2w.traceLines=/tmp/tr_<doc>.txt ConvertOne <corpus>/<doc>.pdf /tmp/out

Each row is `LINE <doc> p=<page> <writer> y= before= line= flowBefore= flowAfter= col= <text>`,
and the last field is the line's own text with its leading spaces intact. A line is space-led when
that field matches `^ +[^ ]`.

## The reach of every construct tried so far

| construct | writer | documents it reaches | of 26 |
|:--|:--|--:|--:|
| strip the leading spaces, pin inkX as w:ind | `flowFromBox` | 380, 383, 392 | **3** |
| strip the leading spaces, anchor at inkX | `anchorBox` | none - no anchored line in the class opens with a space | **0** |
| drop w:jc, pin the centred line's extent | `flowFromBox` | 07, 76, 317, 318, 404 (the only 5 with a centred line) | **5** |

The 25 % bar for a 26-document class is 7. The space construct is capped at 3 by the corpus itself,
and the centred construct at 5, and they do not overlap: 380/383/392 have no centred line and
07/76/317/318/404 have no space-led one. **Neither construct, nor both together, can keep an attempt
on this class.** That is arithmetic on a count, not an opinion, and it is why the previous run's
construct 2 could not be landed however well it worked on 392.

## anchorBox is not the second home of the space-led line

The handoff said to extend the construct "to the table-cell emitter, where 40/77/78's space-led lines
live". Both halves of that are wrong, and the trace says so:

- 40_devanagari_shaping_font, 77_arabic_rtl_document and 78_mixed_english_devanagari_line have **no
  space-led line anywhere** - not in `flowFromBox`, not in `anchorBox`, not in a cell.
- The cell emitters already trim. `PdfToWord.glyphText` (`:8347`), `parasOfLines` (`:8378`) and
  `line.text.trim()` (`:9029`) all drop leading white space before a cell paragraph is built, and the
  cell writes its position as `w:ind w:left = insetTw` (`DocxWriter:6607`, `:6897`, from `insetTw()`
  `:7040`). A run inside `w:tc` cannot begin with a space, so the construct is a no-op there by
  construction.
- The only writer that still emits leading spaces *and* pins `w:ind w:left="0"` is `anchorBox` ->
  `lineParagraph` (`DocxWriter:2619`, `:3559`). It is reached on 4 class documents and carries no
  space-led line on any of them. Diff measured and reverted:
  `47_margins-anchor-inkx-140000.diff`.

## Where the class's failure actually is

`verify_google.py --detail` now prints the two lists the check always computed and always threw away.
On the LibreOffice render of the current engine:

| document | median d | unregistered runs | worst | the page anchor |
|:--|--:|--:|--:|:--|
| 360_restaurant_menu | 0.1 pt | 9 | 11.9 pt | **source 52, render 40** |
| 39_small_caps_letter_spacing | 3.0 pt | 40 | 48.3 pt | same |
| 07_stamp_over_table | 0.1 pt | 4 | 144.4 pt | same |
| 21_form_labels_x60_values_x300_txtpos | 0.1 pt | 18 | 130.1 pt | same |

360 fails clause (a): the body column's left edge lands 12 pt left of the source's, on a page whose
`w:pgMar` is 0 on all four sides, so the whole difference is `w:ind w:left` - a real margin defect in
the class the class is named after. That is the thread to pull next, and it is not a substitution
artifact: it fails in LibreOffice as well as in Google.

## What this rules out, for good

Do not spend another run on the leading-space indent for 47_margins. It is a correct construct aimed
at a document shape this class has three of. Its reach belongs to a class that is full of console
transcripts and shell runbooks, and the right home for it is wherever those documents are, measured by
counting first.
