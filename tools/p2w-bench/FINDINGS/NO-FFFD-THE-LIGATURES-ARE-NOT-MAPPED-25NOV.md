# 258 of the corpus's 310 "invented" txt words are one unmapped ligature, and it reaches the .docx

**Measured 25 Nov 11:47-12:20 IST, attempt 2 of the 10:56 fixer slot.** Lead: root cause located,
population named, fix not landed (an engine edit needs the full two-table re-measure).

## What was measured

For all 8 documents failing `t12_word_invention`, the excess token multiset `txt_w - src_w` was
recomputed independently (PyMuPDF page text as the source, `verify_txt._words/_strip_punct` for
tokenising) and every excess token classified three ways:

| class | tokens | documents |
|:--|--:|:--|
| **NOVEL** - no such characters anywhere on the page | **258** | 2 |
| over-counted - the word exists in the source, the .txt repeats it | 34 | 6 |
| tokenisation - the characters are on the page, split or joined differently | 18 | 4 |

The 258 are **127 and 131 occurrences of `U+FFFD` in two documents that are the same form**:
`041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled`. The page says "Please fill
up in BLOCK letters only"; the output says:

```
Please �ll up in BLOCK letters only      (txt, 127 occurrences of U+FFFD)
Please �ll up in BLOCK letters only      (docx body, 86 occurrences of U+FFFD)
```

**The page carries zero U+FFFD. The .docx carries 86.** `fill`, `office`, `affix`, `stamp`,
`qualification`, `differently` - every `fi`/`ff`/`ffi` ligature in the form becomes a replacement
character, in the renderer the user opens. This is not a `.txt`-only defect and not an instrument
artifact: it is an engine defect in the ligature-to-Unicode mapping, and it is worth two whole
documents.

## Why `t12` reports only 5 on a document with 127 broken words

The verifier's own count for `041122-Account_Opening_Form` is `source=48845 render=5`, while the
excess multiset recomputed here is 132 tokens. `_words()` drops the `U+FFFD` tokens, so the check
that exists to catch a word the page never drew cannot see the one corruption that dominates the
document. `t06_encoding` does fail on it, which is why the document is not silently "clean" - but
`t12`'s number is not the size of the problem and must not be read as one.

## The rest, per document

| document | excess | what it is |
|:--|--:|:--|
| `600_reviewed_invoice_with_annotations` | 21 | 18 = the annotation `/Contents` construct the saved patch fixes; 2 novel = that note's own words |
| `77_arabic_rtl_document` | 11 | 10 tokenisation (Arabic words and digits re-split), 1 duplicate |
| `journal-2col-with-footnotes` | 6 | 4 duplicates of `1 2 3 cent`, 2 tokenisation |
| `05_round_company_seal_curved_text` | 4 | single letters `i n t` - the seal's curved text re-split |
| `311_fir_police_form` | 2 | `60067mobile` joined |
| `39_small_caps_letter_spacing` | 2 | `570` `005` split |

So the honest split of the 8 is **2 documents from one ligature defect, 1 from the annotation
construct, 5 from tokenisation** - not the "5 instrument / 3 engine" the 10:10 run's agent reported.
Its three "engine" documents were two tokenisation cases and the annotation one.

## The fix this implies, and why it did not land

Map `U+FB00`-`U+FB06` (and `U+0132`-`U+0133`, `U+FB01`) to their ASCII expansions at the point the
engine builds a run's text, or fail the glyph-to-Unicode lookup over to the font's ligature
substitution table. That is `PdfToWord.java`/`DocxWriter.java` territory, so it moves both fingerprints
and needs the same full pass the annotation patch needs: **213 documents, five `corpus-slice.py`
slices (~16 min measured today), then ~56 min of docx render+score.** It cannot land in a slot that is
already 80 minutes in.

## CORRECTION, measured 25 Nov 11:52 - the page's own text layer is corrupt too

The falsifier above was the right one to write, and it fires. The page does not extract as "fill":

```
PyMuPDF page 1, raw:   'Please Ĥll up in BLOCK letters only and '
                       (U+0124 = LATIN CAPITAL LETTER H WITH CIRCUMFLEX, i.e. a mis-mapped glyph)
PDFBox (the engine):   'Please �ll up ...'      -> U+FFFD in the .txt (127) and the .docx (86)
```

**Zero `U+FFFD` in the source is true but it is not the same claim as "the page says fill".** The
subset font's `/ToUnicode` CMap maps the `fi`-ligature glyph to `U+0124`, and the two readers answer
differently: PyMuPDF passes the garbage through, PDFBox substitutes the replacement character. Neither
recovers "fill" from `/ToUnicode`.

So the honest reading of the 258 tokens changes: they are **not 258 words the engine invented from
nothing** - the page's text layer is broken for that glyph, `t12`'s "no such characters on the page"
is technically correct, and the user-visible damage (`Please �ll up`) is still real in the
renderer they open.

The recoverable path is therefore **not** a ligature-to-ASCII table. It is: when `toUnicode` yields
`U+FFFD` (or a glyph whose name is a known ligature), fall back to the **glyph name** - PDFBox exposes
it per glyph - and expand `fi`/`ff`/`ffi`/`fl` from there. That is a narrower, better-evidenced change
than the one this finding first proposed, and it is the same code region.

The attempt recorded in `ATTEMPTS.json` (attempt 20) carries the earlier, stronger wording in its
reason. This paragraph supersedes it; the numbers in it are unchanged.
