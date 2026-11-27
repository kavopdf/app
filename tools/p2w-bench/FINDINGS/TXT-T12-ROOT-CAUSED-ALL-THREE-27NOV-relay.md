# The `.txt` half: `t12_word_invention` is two constructs, not one, and both are measured

**Run:** 27 Nov 2026, relay slot 09:28 IST. **Scope:** the 8 documents still failing a `.txt` check.
**Outcome: measured lead on all three `t12` documents. No engine change — the fix for one of them is a
table port, not a line.**

---

## 1. The eight, and the check that travels

`tools/p2w-bench/txt/RANKING-TXT.csv` at this engine:

    041122-Account_Opening_Form            t06_encoding t09_page_furniture t12_word_invention
    Account_Opening_Form_Fillable_filled   t06_encoding t09_page_furniture t12_word_invention
    600_reviewed_invoice_with_annotations  t12_word_invention
    305_vaccination_certificate            t08_line_order
    39_small_caps_letter_spacing           t01_word_accuracy
    601_fillable_admission_form            t01_word_accuracy
    74_balance_sheet_indented_subitems     t02_position
    77_arabic_rtl_document                 t01_word_accuracy

`t12` is the most common failure and the only one with three documents, so it is the one this run
root-caused. It is **two constructs**, and they share nothing.

## 2. Construct A — a symbol face the writer cannot decode: 127 characters, 2 documents

`t12` compares the non-space character multisets of the source and the `.txt`. On both
`Account_Opening_Form` documents the difference is exact and it is one-to-one:

| | count |
|:--|--:|
| U+FFFD in the `.txt` | **127** |
| characters in the source the `.txt` does not carry | **127** — `Ĥ` 89, `Ħ` 23, `ģ` 13, `ħ` 2 |

Every one of the 127 is a **symbol-font checkbox glyph**. The page draws them from a symbol face whose
codes have no `/ToUnicode`; the source side decodes them because the verifier walks the face through the
published Annex D table for it (`verify_txt.py`'s own header: *"decodes a standard symbol face through
the published Annex D table for that face"*), and the writer substitutes U+FFFD because PDFBox's
`PDFont.toUnicode` returns the replacement character for a code the font does not map.

**So the engine and the instrument disagree about the same glyphs, and the instrument is the one that is
right** - `Ĥ`/`Ħ`/`ģ`/`ħ` are what the page draws. This is also why `t06_encoding` fails on both: the
replacement character is not the UTF-8 the writer declares.

**The fix is a port, not a patch.** The Annex D table the verifier already carries has to reach the
writer's glyph decode, used only where `toUnicode` yields U+FFFD. That is a table plus one call site, and
it must be measured on the corpus before it lands - but it is a known quantity, not a hypothesis: the
verifier's copy is the reference, and agreement with it is the test.

## 3. Construct B — annotation `/Contents` hoisted onto a page that already has text: 1 document

`600_reviewed_invoice_with_annotations` carries six annotations and the `.txt` is **730 non-space
characters against the source's 639** - 91 extra, **0 missing**. Every extra character is annotation
text the page never draws:

| annotation | `/Contents` | drawn on the page? | in the `.txt`? |
|:--|:--|:--|:--|
| Text (sticky note) | "Rate for HSN 8536 confirmed with PO." | **no** - the note draws an icon only | **yes, at the top** |
| FreeText | "Checked against PO 4471. Quantity on line 3 raised from 20 to 25." | yes, as page text | yes, twice |
| Stamp | "Approved" | yes, the `/AP` draws `APPROVED` | yes, twice |

`PdfToWord` (around the `chars >= MIN_TEXT_CHARS` branch) hoists `formValuesOf` and `annotationRuns`
into paragraphs at `top = 0` unless the page's own flattened text already contains the string, or
`drawnByAppearance(apDrawn, v)` says the appearance draws it. The FreeText is caught by the first test.
**The stamp is not caught by the second**, although its appearance does draw `APPROVED` - that is a
defect in `drawnByAppearance`, not a design decision. The sticky note is a design decision: its words are
not on the page, and the comment above the code says they were hoisted deliberately because
"RECEIVED", "APPROVED" and every reviewer comment were being dropped.

**So construct B is a conflict between two checks, and it must be decided, not patched.**
`t12_word_invention` says *"the `.txt` carries no character the source never drew"*; the hoist says *an
annotation's words must survive*. A page with a text layer is the case where both cannot hold. The
narrow fix that would satisfy both is the one the code already half-implements: **hoist only what the
appearance does not draw, and fix `drawnByAppearance` so it recognises a stamp whose `/AP` draws its own
`/Contents`.** That removes the duplicate `APPROVED` (8 characters) and would leave the sticky note
alone - and the sticky note alone still fails `t12`, so this construct cannot be closed by the hoist
alone. Whichever way it is decided, `50_annotation_text` is the check on the other side and it must be
re-measured in the same pass.

## 4. What would prove this wrong

For A: a document whose symbol glyphs decode correctly today. If the writer already maps some symbol
faces, the U+FFFD population is narrower than 127 and the table is smaller than this note assumes.
For B: a page where the appearance draws the same words as `/Contents` and `drawnByAppearance` returns
true - that would mean the stamp case is a one-off and not a class.

## 5. Why nothing was changed

Neither construct is a one-line change: A needs the Annex D table ported into the engine and a
full-corpus measurement, and B needs a decision between two checks that are both in the catalogue. Both
are written up rather than half-built, which is the charter's rule for a change that cannot be measured
inside its slot.
