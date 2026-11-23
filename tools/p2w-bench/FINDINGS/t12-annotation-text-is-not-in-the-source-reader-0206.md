# t12_word_invention: the source reader cannot see a printed annotation, and the writer
# transcribes it twice

**Measured 24 Nov 2026, fixer slot claimed 00:56 IST.** Engine HEAD, corpus fresh (213 PDFs).

## What the numbers are

`t12_word_invention` is the largest open `.txt` class: **8 of the 14** documents that still
fail a `.txt` check fail it. On `600_reviewed_invoice_with_annotations` it reported **21
invented words**. Reading the page's annotation dictionary splits them into three faults:

| annotation | type | prints? | `/Contents` |
|---|---|---|---|
| Highlight / Underline / StrikeOut | 8, 9, 11 | no text | empty |
| Text (sticky note) | 0 | **no** | `Rate for HSN 8536 confirmed with PO.` |
| FreeText | 2 | **yes** | `Checked against PO 4471. Quantity on line 3 raised from 20 to 25.` |
| Stamp | 13 | **yes** | `Approved` |

1. **7 words the writer invented** - `rate for hsn 8536 confirmed with po`. A sticky note
   never prints; the `.txt` carries its comment body. **Writer fault.**
2. **13 words the writer transcribed twice** - `checked against po 4471 quantity on line 3
   raised from 20 to 25`. This FreeText note *is* in the content stream: `src.count("4471")
   == 1`, `"Checked against" in src == True`, and `txt.count("4471") == 2`,
   `txt.count("raised") == 2`. **Writer fault - a duplicate, not an invention.**
3. **1 word the source could not see** - `approved`. The Stamp prints, and
   `get_text("dict")` returns nothing from an annotation's appearance stream. **Reader fault.**

## What changed, and what it moved

`verify_txt.py:glyph_truth()` now appends the `/Contents` of the **printing** types only
(2 FreeText, 13 Stamp), with the same `not already in walked` guard the widget block above
it uses and for the same reason.

`/Text` and the markup types stay out **deliberately**: adding them would bless fault 1
instead of finding it.

| document | t12 before | t12 after | verdict |
|---|---|---|---|
| 600_reviewed_invoice_with_annotations | 21 | **20** | still FAIL |

**Blast radius, measured over all 213 PDFs: exactly one document carries a printing
annotation** (`600`, two of them). Every other document is byte-identical by construction.
No document can get worse, and none did. This change moves **no verdict** - it is an
instrument correction, not a fix.

## What closes 600

`600` fails **only** `t12`. Faults 1 and 2 are in the converter's text extraction, not in
`TxtWriter.java` (which has no annotation code - grep `annot` in it returns only prose).
The construct: whatever in `PdfEngine`/`PdfToWord` adds an annotation's `/Contents` to the
page text must add **only types that print** and **only when the content stream did not
already draw them** - the identical rule `glyph_truth()` already applies to widget
appearance streams, which fixed `601_fillable_admission_form` from 98.8% to 100.0% on 21 Nov.
The widget case and this one are the same bug in two places.

Expected: 20 invented words -> **0**, and `600` becomes the 200th `.txt`-clean document.
One `verify_txt.py` run falsifies it.

## Two more, measured, not this document

- `311_fir_police_form` invents `60067mobile` - a number and a word concatenated with no
  separator. Writer fault, one token.
- `39_small_caps_letter_spacing` invents `570` and `005` - the source splits letter-spaced
  digits into runs and the `.txt` joins them. **Reader** fault, same shape as fault 3.
