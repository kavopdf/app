# A widget-AP glyph walk would fire on exactly 2 of 213 documents, measured

21 Nov 2026, fixer run claimed 00:57, fourth attempt. Read-only measurement with pymupdf over the
corpus rebuilt from the corpus-v1 release (213 PDFs). No engine change, no tree change.

The next run's engine attempt on `601_fillable_admission_form` is the one engine-side document left
in `t01_word_accuracy`. Its shape is known - a glyph walk over each widget's `/AP /N`, the shape
`formValuesOf` and `_ap_stream_text` already have on both sides - and what was missing is the blast
radius. This is it.

## What was measured

Every page's `/Annots` array of all 213 PDFs was walked, each object with `/Subtype /Widget`
counted, and each widget's `/AP` dictionary resolved to its `/N` stream and searched for text
operators.

| document | widgets | widgets whose `/AP /N` carries text | sample |
|---|---:|---:|---|
| `Account_Opening_Form_Fillable_filled` | 352 | **137** | `(12/01/2000) Tj`, `(jalapur) Tj` |
| `601_fillable_admission_form` | 11 | **1** | `(General) Tj` |
| every other document | 0 | 0 | - |

**Total: 2 of 213.** A rule that reads widget appearance text therefore fires on those two
documents and on nothing else in the corpus.

## Two things the next run should know before it builds this

1. **The blast radius is small but the second document is not.** `601` is the document the fix is
   for, and one of its widgets carries the word `General` - a token the check already reports as
   lost. `Account_Opening_Form_Fillable_filled` is the one to watch: 137 of its 352 widgets carry
   text, including dates and a name, so a glyph walk there will add a lot of text to a document
   whose .txt currently passes `t01`. That is the document to measure first, not last, and the
   rule should be gated on it before it is kept.

2. **pymupdf's own annotation API does not see these, and that matters for the instrument.** Two
   scans this run returned zero widgets before the third found eleven, because
   `page.annots()` does not return widget annotations and `Document.widgets()` does not exist in
   pymupdf 2.1. Only walking `/Annots` and reading the xref objects finds them. Any instrument-side
   check of the same thing must walk `/Annots` too, or it will report a clean corpus.

## What this does not establish

* Whether the checkbox ticks themselves - the two ticked boxes that made `601` fail - are `Tj`
  text in the appearance stream or drawn as a form glyph some other way. Only one widget on `601`
  matched a text operator, and the earlier finding quotes `BT /ZaDb 9 Tf (3) Tj ET` at two xrefs,
  so the tick streams are there and the walk found fewer of them than expected. **Count the ticks
  with the same walk before building the rule on it** - this run measured the `/AP /N` reach, not
  the tick's own encoding.
* Whether the engine's existing `widgetValue`/`formValuesOf` already emits `General` for that
  field. That is an engine question and needs the build.
