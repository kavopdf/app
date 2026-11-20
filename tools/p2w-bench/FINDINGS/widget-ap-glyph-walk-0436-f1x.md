# A widget's appearance stream is the only place a tick lives - and the walk closes it

**21 Nov, fixer run 03:57, attempt 13 on `t01_word_accuracy` - measured, engine reverted.**

`601_fillable_admission_form` was the first carry-over. It lost three tokens (`3`, `3`, `General`)
because PDFBox's `PDFTextStripper` never walks annotation appearance streams. The patch walks them.

## What the patch does

`PdfToWord.readAnnotationAppearances()` skipped every `PDAnnotationWidget`, on a comment saying the
widget's appearance "is the field's `/V` … already painted onto the page by `paintField`".

**There is no `paintField` in the file.** Grep finds no such method. A widget's text was read from
`/V` by `widgetValue()` and from nowhere else, so the skip was not a duplicate guard, it was the loss.

Three changes, nothing else:

1. stop skipping `PDAnnotationWidget`;
2. resolve `/AP /N` **through `/AS`** when `/N` is a state dictionary (`601`'s checkboxes are
   `<< /Off 49 0 R /Yes 51 0 R >>`; a blind `/N` read gets the blank `/Off` stream);
3. an unfilled `() Tj` yields an empty string and registers nothing, so the 128 of 145 widgets that
   carry text operators but draw nothing stay silent.

Mutual exclusivity with `/V` is kept because an emitted widget registers its text in `drawn`, and
`drawnByAppearance()` then suppresses the `/V` hoist.

## Measured, same tree, same run, pristine HEAD against patched

Engine `ada9ce9`, `build-engine.sh`, `soffice` render, the docx checks from `verify_google.py`,
`verify_txt.py` on the same conversion. Both sides built and scored inside this run.

| document | before | after |
|:--|--:|--:|
| `601_fillable_admission_form` docx checks | 37/42 FAIL | **42/42 PASS** |
| `601_fillable_admission_form` t01 | 96.4 | 98.8 |
| `Account_Opening_Form_Fillable_filled` docx checks | 21/47 | 25/47 |
| `Account_Opening_Form_Fillable_filled` t01 | pass | pass |

Per-check on 601, all five moved the right way: `04_chars_missing` 0/2 → 0/0,
`18_displacement` 0/1 → 0/0, `51_field_values` 3/0 → 3/3, `53_embedded_faces` 2/1 → 2/2,
`59_shape_anchor` 3/0 → 3/3.

On the Account form seven checks fixed and **two newly fail**: `42_justification_edges` 0/3 → 22/6
and `63_table_rows` 23/0 → 24/1. Both are denominator effects of a much larger matched population
(`17_matched_runs` 272 → 803, `59_shape_anchor` 13 → 299), not new bad layout - but that is an
inference, not a measurement, and the Account form is the document that must be measured first.

## Why t01 still does not reach 100 on 601, and it is the instrument

The tick is counted as the ASCII digit `3`. `verify_txt._ap_stream_text()` reads the widget stream,
looks for an Annex D table, finds none for ZapfDingbats **by explicit decision** (`:103-107`), and
appends the raw character. So the instrument's answer for `(3) Tj` under `/ZaDb` is `3`.

`glyph_truth()` then double-counts the text field: it builds `declared_page` from pymupdf's page
text, and `page.get_text()` **already synthesises the widget appearance** - on 601 it returns
`General` and two `3`s while no page content stream in the file contains `General` at all (33
`/Contents` xrefs scanned; the word exists only in xref 38, the widget's `/AP /N`). `glyph_truth()`
then appends `_ap_stream_text()` on top, so `General` is declared twice.

A faithful engine that emits each drawn glyph once therefore cannot reach 100 % on 601. The variant
that does reach 100 % (do not register the widget text in `drawn`, so `/V` emits it as well) drops
601's docx checks to 37/42. **The correct fix is instrument-side** - do not append `_ap_stream_text`
for a widget whose text pymupdf already folded into the page text - and a fixer may not make it.
That decision belongs to a person; it is the same class of decision as the 01:43 blocker row.

## Blast radius, measured over all 213 documents

A census of every page annotation and every `/AP /N` (PyMuPDF, `page.widgets()` - `page.annots()`
returns no widgets at all, which produced a false "no blast radius" on the first pass):

| | |
|:--|--:|
| documents | 213 |
| pages | 563 |
| widgets | 363 |
| widgets whose selected `/N` has BT + Tj/TJ | 145 |
| widgets emitting non-empty characters | **17** |
| documents with widget text | **2** |
| widget text already in the page text layer | **0** |

The two are `601_fillable_admission_form` (1 text field, 2 ticks) and
`Account_Opening_Form_Fillable_filled.pdf` (9 text fields, 5 ticks). 210 documents have no
annotations. A walk over all annotations rather than widgets only would add a third,
`600_reviewed_invoice_with_annotations` (one FreeText, one Stamp).

Ten of the 17 strings are byte-identical to the widget's `/V`, so they are already reachable through
`formValuesOf()`; only the 7 ticks are genuinely unreachable today. The patch emits each once.

## Why the engine was reverted

`p2w.py` builds the engine from `origin main`, not from a working tree, so a corpus measurement of
this patch is only possible after it is pushed - and `regress.py --check` refuses an engine whose
fingerprint is not the one the table was measured on. That is the same wall the 03:36 run hit on the
cell-border patch. The patch is `FINDINGS/widget-ap-glyph-walk-0436-f1x.patch`; it forward-applies to
`ada9ce9` and reverse-applies cleanly.

**Google was not measured this run.** Nothing landed, so no gate decision depended on it, and the
slot went to the census and the two-build measurement. The next run that pushes this patch must
measure 601 through Drive before and after, and the Account form's two new failures with it.
